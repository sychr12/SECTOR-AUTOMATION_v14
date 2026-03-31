# app/ui/abas/Carteira/utils/pdf_parser.py
# -*- coding: utf-8 -*-
"""
Extração e parsing de dados de PDF
"""

import re
from typing import Dict, Optional
import PyPDF2


class PDFParser:
    """Parser para extrair dados de PDFs da carteira"""
    
    def __init__(self):
        self.patterns = {
            "registro": r"(?:REGISTRO|R\.P\.|RP|IE|INSCRIÇÃO ESTADUAL)[:\s]+([0-9\-\.\/]+)",
            "cpf": r"\b(\d{3}[\.\\ ]?\d{3}[\.\\ ]?\d{3}[-\\ ]?\d{2})\b",
            "nome": r"(?:NOME|PRODUTOR)[:\s]+([A-ZÁÀÂÃÉÈÊÍÏÓÔÕÚÜÇ][A-ZÁÀÂÃÉÈÊÍÏÓÔÕÚÜÇa-záàâãéèêíïóôõúüç\s]+)",
            "propriedade": r"(?:PROPRIEDADE|NOME DA PROPRIEDADE|IMÓVEL)[:\s]+([^\n\r]+)",
            "unloc": r"PR-([A-Z\-]+)/(\d+)",
            "validade": r"(?:VALIDADE|VÁLIDO ATÉ|VENCIMENTO)[:\s]*(\d{2}[\/\-]\d{2}[\/\-]\d{4})",
            "inicio": r"(?:INÍCIO|INICIO|ANO DE INÍCIO)[:\s]*(\d{2}[\/\-]\d{2}[\/\-]\d{4}|\d{4})",
            "endereco": r"(?:ENDEREÇO|ENDERECO|END\.)[:\s]+([^\n\r]+)",
            "atividade1": r"(?:ATIVIDADE PRINCIPAL|CNAE PRINCIPAL|ATV\.?\s*1)[:\s]+([^\n\r]+)",
            "atividade2": r"(?:ATIVIDADE SECUNDÁRIA|CNAE SECUNDÁRIO|ATV\.?\s*2)[:\s]+([^\n\r]+)",
            "georef": r"(-?\d{1,3}[,\.]\d+)\s+(-?\d{1,3}[,\.]\d+)"
        }
    
    def extract_text(self, pdf_path: str) -> str:
        """Extrai texto do PDF"""
        text = ""
        try:
            with open(pdf_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += (page.extract_text() or "") + "\n"
        except Exception:
            # Tenta com pypdf se disponível
            try:
                import pypdf
                with open(pdf_path, "rb") as f:
                    reader = pypdf.PdfReader(f)
                    for page in reader.pages:
                        text += (page.extract_text() or "") + "\n"
            except ImportError:
                pass
        return text
    
    def parse(self, text: str) -> Dict[str, str]:
        """Parseia o texto e extrai dados"""
        if not text:
            return {}
        
        dados = {}
        text_upper = text.upper()
        
        # Extrai cada campo
        for key, pattern in self.patterns.items():
            match = re.search(pattern, text_upper if key != "georef" else text)
            if match:
                value = match.group(1) if key != "unloc" else f"PR-{match.group(1)}/{match.group(2)}"
                
                # Formatações específicas
                if key == "cpf":
                    digits = re.sub(r"\D", "", value)
                    value = f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
                elif key in ("propriedade", "endereco", "atividade1", "atividade2"):
                    value = value.strip().title()
                elif key == "validade" or key == "inicio":
                    value = value.replace("-", "/")
                elif key == "georef" and match:
                    value = f"{match.group(1)}  {match.group(2)}"
                
                dados[key] = value
        
        return dados
    
    def extract_and_parse(self, pdf_path: str) -> Dict[str, str]:
        """Extrai texto e parseia em uma única operação"""
        text = self.extract_text(pdf_path)
        return self.parse(text)