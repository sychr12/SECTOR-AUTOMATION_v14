# -*- coding: utf-8 -*-
"""
Serviço para geração de PDFs
"""

import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm


class PDFService:
    """Serviço para geração de documentos PDF"""
    
    def __init__(self, pasta_saida=None):
        """
        Inicializa o serviço de PDF
        
        Args:
            pasta_saida: Pasta onde os PDFs serão salvos
        """
        if pasta_saida:
            self.pasta_saida = pasta_saida
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            self.pasta_saida = os.path.join(base_dir, "assets", "data", "pdfs")

        os.makedirs(self.pasta_saida, exist_ok=True)

    def gerar_pdf_lancamento(self, conteudo_texto: str) -> str:
        """
        Gera um PDF de lançamento
        
        Args:
            conteudo_texto: Texto a ser incluído no PDF
            
        Returns:
            Caminho do arquivo PDF gerado
        """
        nome_arquivo = self._gerar_nome_arquivo("lancamento")
        caminho_pdf = os.path.join(self.pasta_saida, nome_arquivo)

        self._criar_pdf_simples(caminho_pdf, conteudo_texto)

        return caminho_pdf

    def _criar_pdf_simples(self, caminho_pdf, texto):
        """
        Cria um PDF simples com texto
        
        Args:
            caminho_pdf: Caminho onde salvar o PDF
            texto: Texto a ser incluído
        """
        c = canvas.Canvas(caminho_pdf, pagesize=A4)
        largura, altura = A4

        x = 20 * mm
        y = altura - 20 * mm

        c.setFont("Helvetica", 10)

        for linha in texto.splitlines():
            if y < 20 * mm:
                c.showPage()
                c.setFont("Helvetica", 10)
                y = altura - 20 * mm

            c.drawString(x, y, linha)
            y -= 12

        c.showPage()
        c.save()

    def _gerar_nome_arquivo(self, prefixo):
        """
        Gera nome de arquivo com timestamp
        
        Args:
            prefixo: Prefixo do arquivo
            
        Returns:
            Nome do arquivo com timestamp
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefixo}_{timestamp}.pdf"