# controller.py
# -*- coding: utf-8 -*-
"""
controller.py — Controller do cadastro individual de Carteira Digital.
Local: app/ui/abas/Carteira/controller.py
"""
import io
import os
import re
import sys
import subprocess
import tempfile
from PyQt6.QtWidgets import QFileDialog
from PIL import Image

# Tenta importar bibliotecas de PDF
PDF_AVAILABLE = False
try:
    from pypdf import PdfReader, PdfWriter
    PDF_AVAILABLE = True
except ImportError:
    try:
        from PyPDF2 import PdfReader, PdfWriter
        PDF_AVAILABLE = True
    except ImportError:
        PdfReader = None
        PdfWriter = None

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from .assets import get_img_frente, get_img_verso


class CarteiraController:
    """Controller da carteira digital"""

    CARD_W = 420
    CARD_H = 240

    def __init__(self, usuario, repo):
        self.usuario = usuario or "Desconhecido"
        self.repo = repo

        self.IMG_FRENTE = get_img_frente()
        self.IMG_VERSO = get_img_verso()

        self._validar_imagens()

    def _validar_imagens(self):
        """Valida se imagens foram encontradas"""
        if not self.IMG_FRENTE:
            print("[Carteira] Aviso: 'frente.png' não encontrada.")
        if not self.IMG_VERSO:
            print("[Carteira] Aviso: 'verso.png' não encontrada.")

    def validar_cpf(self, cpf):
        """Valida CPF"""
        if not cpf:
            return True
        return len(re.sub(r"\D", "", cpf)) == 11

    def formatar_cpf_exibicao(self, cpf):
        """Formata CPF para exibição"""
        if not cpf:
            return ""
        d = re.sub(r"\D", "", cpf)
        if len(d) == 11:
            return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"
        return cpf

    def validar_dados(self, dados):
        """Valida dados do formulário"""
        erros = []
        nome = dados.get("nome", "").strip()
        cpf = dados.get("cpf", "").strip()
        
        if not nome:
            erros.append("• Nome do produtor é obrigatório")
        if not cpf:
            erros.append("• CPF é obrigatório")
        elif not self.validar_cpf(cpf):
            erros.append("• CPF inválido (deve conter 11 dígitos)")
        if len(nome) > 200:
            erros.append("• Nome muito longo (máximo 200 caracteres)")
        
        return erros

    def ler_foto_binaria(self, caminho):
        """Lê foto como binário"""
        if caminho and os.path.exists(caminho):
            try:
                with open(caminho, "rb") as f:
                    return f.read()
            except Exception as e:
                print(f"Aviso: Erro ao ler foto: {e}")
        return None

    def gerar_pdf(self, dados, fotos, pdf_original_path=None):
        """Gera PDF da carteira e anexa o PDF original importado (se houver)."""
        print("=" * 60)
        print("[gerar_pdf] INICIANDO GERAÇÃO DO PDF")
        
        pdf_original_existe = pdf_original_path and os.path.exists(pdf_original_path)
        
        try:
            # ========== 1. GERAR PDF DA CARTEIRA ==========
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            W, H = A4

            # Página 1: FRENTE
            if self.IMG_FRENTE and os.path.exists(self.IMG_FRENTE):
                c.drawImage(self.IMG_FRENTE, 2*cm, H-11*cm, 16*cm, 9*cm)
            else:
                self._placeholder_pdf(c, 2*cm, H-11*cm, 16*cm, 9*cm, "FRENTE")

            self._draw_paragraph(c, dados.get("registro"), 3.1*cm, H-6.1*cm, 6*cm, size=14)
            self._draw_paragraph(c, dados.get("cpf"), 10.3*cm, H-6.1*cm, 5*cm, size=14)
            self._draw_paragraph(c, dados.get("nome"), 3.1*cm, H-7.4*cm, 12*cm, size=14, bold=True)
            self._draw_paragraph(c, dados.get("propriedade"), 3.1*cm, H-8.7*cm, 14*cm, size=12)
            self._draw_paragraph(c, dados.get("unloc"), 3.1*cm, H-10.4*cm, 3*cm, size=14)
            self._draw_paragraph(c, dados.get("inicio"), 9.3*cm, H-10.4*cm, 3*cm, size=14)
            self._draw_paragraph(c, dados.get("validade"), 13.5*cm, H-10.4*cm, 3*cm, size=14)
            c.showPage()

            # Página 2: VERSO
            y_off = 12*cm
            if self.IMG_VERSO and os.path.exists(self.IMG_VERSO):
                c.drawImage(self.IMG_VERSO, 2*cm, H-11*cm-y_off, 16*cm, 9*cm)
            else:
                self._placeholder_pdf(c, 2*cm, H-11*cm-y_off, 16*cm, 9*cm, "VERSO")

            self._draw_paragraph(c, dados.get("endereco"), 3*cm, H-5.3*cm-y_off, 12*cm, size=14)
            self._draw_paragraph(c, dados.get("atividade1"), 3*cm, H-7.1*cm-y_off, 12*cm, size=14)
            self._draw_paragraph(c, dados.get("atividade2"), 3*cm, H-8.6*cm-y_off, 12*cm, size=14)
            self._draw_paragraph(c, dados.get("georef"), 3*cm, H-10*cm-y_off, 12*cm, size=14)
            c.showPage()

            # Páginas de FOTOS
            for i, foto_path in enumerate(fotos.values(), 1):
                if foto_path and os.path.exists(foto_path):
                    self._pagina_foto(c, W, H, foto_path)

            c.save()
            carteira_bytes = buffer.getvalue()

            # ========== 2. ANEXAR PDF SCANEADO SE EXISTIR ==========
            if pdf_original_existe and PDF_AVAILABLE:
                try:
                    carteira_reader = PdfReader(io.BytesIO(carteira_bytes))
                    with open(pdf_original_path, "rb") as f:
                        original_bytes = f.read()
                    original_reader = PdfReader(io.BytesIO(original_bytes))
                    
                    writer = PdfWriter()
                    for page in carteira_reader.pages:
                        writer.add_page(page)
                    for page in original_reader.pages:
                        writer.add_page(page)
                    
                    output_buffer = io.BytesIO()
                    writer.write(output_buffer)
                    carteira_bytes = output_buffer.getvalue()
                except Exception as e:
                    print(f"[gerar_pdf] Erro no merge: {e}")

            return carteira_bytes
            
        except Exception as e:
            raise RuntimeError(f"Erro ao gerar PDF: {e}")

    def _draw_paragraph(self, c, text, x, y, w, size=8, bold=False):
        """Desenha parágrafo no PDF"""
        style = getSampleStyleSheet()["Normal"]
        style.fontName = "Helvetica-Bold" if bold else "Helvetica"
        style.fontSize = size
        style.leading = size + 1
        style.textColor = colors.black
        text = str(text).strip() if text else "&nbsp;"
        
        try:
            p = Paragraph(text, style)
            p.wrapOn(c, w, 100)
            p.drawOn(c, x, y)
        except Exception:
            c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
            safe = text if text != "&nbsp;" else ""
            c.drawString(x, y, safe)

    @staticmethod
    def _placeholder_pdf(c, x, y, w, h, label):
        """Desenha placeholder para imagem faltante"""
        c.setStrokeColorRGB(0.6, 0.6, 0.7)
        c.setFillColorRGB(0.93, 0.93, 0.96)
        c.rect(x, y, w, h, fill=True, stroke=True)
        c.setFillColorRGB(0.5, 0.5, 0.6)
        c.setFont("Helvetica", 10)
        c.drawCentredString(x + w / 2, y + h / 2, f"[ {label} — imagem não encontrada ]")

    def _pagina_foto(self, c, W, H, path):
        """Adiciona página de foto"""
        c.setFillColorRGB(1, 1, 1)
        c.rect(0, 0, W, H, fill=True, stroke=False)
        try:
            img = Image.open(path)
            ow, oh = img.size
            esc = min((W - 4*cm) / ow, (H - 6*cm) / oh)
            nw, nh = ow*esc, oh*esc
            c.drawImage(path, (W-nw)/2, (H-nh)/2, width=nw, height=nh, preserveAspectRatio=True)
        except Exception as e:
            c.setFont("Helvetica", 10)
            c.setFillColorRGB(0.8, 0, 0)
            c.drawCentredString(W/2, H/2, f"Erro: {str(e)[:50]}")
        c.showPage()

    def salvar_carteira(self, dados, fotos, pdf_original_path=None):
        """Salva carteira no banco"""
        erros = self.validar_dados(dados)
        if erros:
            return False, "Corrija os seguintes erros:\n\n" + "\n".join(erros)
        
        try:
            pdf = self.gerar_pdf(dados, fotos, pdf_original_path=pdf_original_path)
            
            self.repo.salvar(
                registro=dados.get("registro"),
                cpf=dados.get("cpf"),
                nome=dados.get("nome"),
                propriedade=dados.get("propriedade"),
                unloc=dados.get("unloc"),
                inicio=dados.get("inicio"),
                validade=dados.get("validade"),
                endereco=dados.get("endereco"),
                atividade1=dados.get("atividade1"),
                atividade2=dados.get("atividade2"),
                georef=dados.get("georef"),
                pdf_conteudo=pdf,
                foto1=self.ler_foto_binaria(fotos.get("foto1")),
                foto2=self.ler_foto_binaria(fotos.get("foto2")),
                foto3=self.ler_foto_binaria(fotos.get("foto3")),
                usuario=self.usuario,
            )
            return True, "Carteira digital salva no banco com sucesso!"
        except Exception as e:
            return False, f"Erro ao salvar no banco:\n{str(e)}"

    def visualizar_pdf(self, carteira_id):
        """Visualiza PDF salvo"""
        if not carteira_id:
            return False, "ID não encontrado."
        
        try:
            res = self.repo.buscar_pdf_por_id(carteira_id)
            if not res or not res.get("pdf_conteudo"):
                return False, "PDF não encontrado no banco."
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(res["pdf_conteudo"])
                tmp_path = tmp.name
            
            self._abrir_sistema(tmp_path)
            return True, "PDF aberto."
        except Exception as e:
            return False, f"Erro ao abrir PDF:\n{e}"

    def baixar_pdf(self, carteira_id, nome):
        """Baixa PDF para disco"""
        if not carteira_id:
            return False, "ID não encontrado."
        
        try:
            res = self.repo.buscar_pdf_por_id(carteira_id)
            if not res or not res.get("pdf_conteudo"):
                return False, "PDF não encontrado no banco."
            
            nome_limpo = re.sub(r'[<>:"/\\|?*]', "_", nome or "Carteira")
            caminho, _ = QFileDialog.getSaveFileName(
                None,
                "Salvar PDF",
                f"Carteira_{nome_limpo}.pdf",
                "PDF Files (*.pdf);;All Files (*.*)"
            )
            if not caminho:
                return False, "Operação cancelada"
            
            with open(caminho, "wb") as f:
                f.write(res["pdf_conteudo"])
            return True, caminho
        except Exception as e:
            return False, f"Erro ao baixar PDF:\n{e}"

    def abrir_pdf(self, caminho):
        """Abre PDF no visualizador padrão"""
        try:
            self._abrir_sistema(caminho)
            return True, "PDF aberto."
        except Exception as e:
            return False, f"Erro ao abrir PDF:\n{e}"

    @staticmethod
    def _abrir_sistema(path):
        """Abre arquivo no sistema operacional"""
        if sys.platform.startswith("win"):
            os.startfile(path)
        elif sys.platform.startswith("darwin"):
            subprocess.call(["open", path])
        else:
            subprocess.call(["xdg-open", path])

    def carregar_historico(self, termo="", periodo="TODOS", usuario="TODOS"):
        """Carrega histórico"""
        try:
            return self.repo.buscar_com_filtros(termo, periodo, usuario)
        except Exception as e:
            raise Exception(f"Erro ao carregar histórico: {e}")

    def contar_total_carteiras(self):
        """Conta total de carteiras"""
        try:
            return self.repo.contar_total()
        except Exception:
            return 0

    def buscar_usuarios_unicos(self):
        """Busca usuários únicos"""
        try:
            return self.repo.buscar_usuarios_unicos()
        except Exception:
            return []

    def buscar_por_cpf(self, cpf: str):
        """Busca dados de carteira por CPF"""
        if not cpf:
            return None
        try:
            return self.repo.buscar_por_cpf(cpf)
        except Exception:
            return None