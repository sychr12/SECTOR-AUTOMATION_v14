# -*- coding: utf-8 -*-
import os
import re
import io
import sys
import subprocess
import tempfile
from datetime import datetime
from tkinter import filedialog, messagebox
from PIL import Image

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors


class CarteiraController:
    def __init__(self, usuario, repo):
        self.usuario = usuario or "Desconhecido"
        self.repo = repo

        self.IMG_FRENTE = "images/FRENTE E VERSO DO CARTAO/frente.png"
        self.IMG_VERSO  = "images/FRENTE E VERSO DO CARTAO/verso.png"
        self.CARD_W, self.CARD_H = 420, 240

        self._validar_imagens()

    def _validar_imagens(self):
        if not os.path.exists(self.IMG_FRENTE):
            raise FileNotFoundError(f"Imagem da frente não encontrada: {self.IMG_FRENTE}")
        if not os.path.exists(self.IMG_VERSO):
            raise FileNotFoundError(f"Imagem do verso não encontrada: {self.IMG_VERSO}")

    # ──────────────────────────────────────────────────────────────────────────
    # CPF
    # ──────────────────────────────────────────────────────────────────────────
    def validar_cpf(self, cpf):
        if not cpf:
            return True
        return len(re.sub(r'\D', '', cpf)) == 11

    def formatar_cpf_exibicao(self, cpf):
        if not cpf:
            return ""
        d = re.sub(r'\D', '', cpf)
        if len(d) == 11:
            return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"
        return cpf

    # ──────────────────────────────────────────────────────────────────────────
    # Validação
    # ──────────────────────────────────────────────────────────────────────────
    def validar_dados(self, dados):
        erros = []
        nome = dados.get('nome', '').strip()
        cpf  = dados.get('cpf',  '').strip()
        if not nome:
            erros.append("• Nome do produtor é obrigatório")
        if not cpf:
            erros.append("• CPF é obrigatório")
        elif not self.validar_cpf(cpf):
            erros.append("• CPF inválido (deve conter 11 dígitos)")
        if len(nome) > 200:
            erros.append("• Nome muito longo (máximo 200 caracteres)")
        return erros

    # ──────────────────────────────────────────────────────────────────────────
    # Foto
    # ──────────────────────────────────────────────────────────────────────────
    def ler_foto_binaria(self, caminho):
        if caminho and os.path.exists(caminho):
            try:
                with open(caminho, 'rb') as f:
                    return f.read()
            except Exception as e:
                print(f"Aviso: Erro ao ler foto: {e}")
        return None

    # ──────────────────────────────────────────────────────────────────────────
    # PDF
    # ──────────────────────────────────────────────────────────────────────────
    def _draw_paragraph(self, c, text, x, y, w, size=8, bold=False):
        style = getSampleStyleSheet()["Normal"]
        style.fontName  = "Helvetica-Bold" if bold else "Helvetica"
        style.fontSize  = size
        style.leading   = size + 1
        style.textColor = colors.black
        text = str(text).strip() if text else "&nbsp;"
        if not text:
            text = "&nbsp;"
        try:
            p = Paragraph(text, style)
            p.wrapOn(c, w, 100)
            p.drawOn(c, x, y)
        except Exception as e:
            print(f"Aviso PDF: {e}")
            c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
            c.drawString(x, y, text if text != "&nbsp;" else "")

    def gerar_pdf(self, dados, fotos):
        try:
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            W, H = A4

            c.drawImage(self.IMG_FRENTE, 2*cm, H-11*cm, 16*cm, 9*cm)
            self._draw_paragraph(c, dados.get('registro'),   3.1*cm, H-6.1*cm,  6*cm,  size=14)
            self._draw_paragraph(c, dados.get('cpf'),        10.3*cm, H-6.1*cm, 5*cm,  size=14)
            self._draw_paragraph(c, dados.get('nome'),       3.1*cm, H-7.4*cm,  12*cm, size=14, bold=True)
            self._draw_paragraph(c, dados.get('propriedade'),3.1*cm, H-8.7*cm,  14*cm, size=12)
            self._draw_paragraph(c, dados.get('unloc'),      3.1*cm, H-10.4*cm, 3*cm,  size=14)
            self._draw_paragraph(c, dados.get('inicio'),     9.3*cm, H-10.4*cm, 3*cm,  size=14)
            self._draw_paragraph(c, dados.get('validade'),   13.5*cm,H-10.4*cm, 3*cm,  size=14)

            y_off = 12*cm
            c.drawImage(self.IMG_VERSO, 2*cm, H-11*cm-y_off, 16*cm, 9*cm)
            self._draw_paragraph(c, dados.get('endereco'),   3*cm, H-5.3*cm-y_off,  12*cm, size=14)
            self._draw_paragraph(c, dados.get('atividade1'), 3*cm, H-7.1*cm-y_off,  12*cm, size=14)
            self._draw_paragraph(c, dados.get('atividade2'), 3*cm, H-8.6*cm-y_off,  12*cm, size=14)
            self._draw_paragraph(c, dados.get('georef'),     3*cm, H-10*cm-y_off,   12*cm, size=14)
            c.showPage()

            for foto_path in fotos.values():
                if foto_path and os.path.exists(foto_path):
                    self._pagina_foto(c, W, H, foto_path)

            c.save()
            return buffer.getvalue()
        except Exception as e:
            raise RuntimeError(f"Erro ao gerar PDF: {e}")

    def _pagina_foto(self, c, W, H, path):
        c.setFillColorRGB(1, 1, 1)
        c.rect(0, 0, W, H, fill=True, stroke=False)
        try:
            img = Image.open(path)
            ow, oh = img.size
            esc = min((W - 4*cm) / ow, (H - 6*cm) / oh)
            nw, nh = ow*esc, oh*esc
            c.drawImage(path, (W-nw)/2, (H-nh)/2,
                        width=nw, height=nh, preserveAspectRatio=True)
        except Exception as e:
            c.setFont("Helvetica", 10)
            c.setFillColorRGB(0.8, 0, 0)
            c.drawCentredString(W/2, H/2, f"Erro: {str(e)[:50]}")
        c.showPage()

    # ──────────────────────────────────────────────────────────────────────────
    # Salvar
    # ──────────────────────────────────────────────────────────────────────────
    def salvar_carteira(self, dados, fotos):
        erros = self.validar_dados(dados)
        if erros:
            return False, "Corrija os seguintes erros:\n\n" + "\n".join(erros)
        try:
            pdf = self.gerar_pdf(dados, fotos)
            self.repo.salvar(
                registro    = dados.get('registro'),
                cpf         = dados.get('cpf'),
                nome        = dados.get('nome'),
                propriedade = dados.get('propriedade'),
                unloc       = dados.get('unloc'),
                inicio      = dados.get('inicio'),
                validade    = dados.get('validade'),
                endereco    = dados.get('endereco'),
                atividade1  = dados.get('atividade1'),
                atividade2  = dados.get('atividade2'),
                georef      = dados.get('georef'),
                pdf_conteudo= pdf,
                foto1       = self.ler_foto_binaria(fotos.get('foto1')),
                foto2       = self.ler_foto_binaria(fotos.get('foto2')),
                foto3       = self.ler_foto_binaria(fotos.get('foto3')),
                usuario     = self.usuario,
            )
            return True, "Carteira digital salva no banco com sucesso!"
        except Exception as e:
            return False, f"Erro ao salvar no banco:\n{str(e)}"

    # ──────────────────────────────────────────────────────────────────────────
    # Visualizar / Baixar / Abrir PDF
    # ──────────────────────────────────────────────────────────────────────────
    def visualizar_pdf(self, carteira_id):
        if not carteira_id:
            return False, "ID não encontrado."
        try:
            res = self.repo.buscar_pdf_por_id(carteira_id)
            if not res or not res.get('pdf_conteudo'):
                return False, "PDF não encontrado."
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                tmp.write(res['pdf_conteudo'])
                tmp_path = tmp.name
            self._abrir_sistema(tmp_path)
            return True, "PDF aberto."
        except Exception as e:
            return False, f"Erro ao abrir PDF:\n{e}"

    def baixar_pdf(self, carteira_id, nome):
        if not carteira_id:
            return False, "ID não encontrado."
        try:
            res = self.repo.buscar_pdf_por_id(carteira_id)
            if not res or not res.get('pdf_conteudo'):
                return False, "PDF não encontrado."
            nome_limpo = re.sub(r'[<>:"/\\|?*]', '_', nome)
            caminho = filedialog.asksaveasfilename(
                title="Salvar PDF",
                defaultextension=".pdf",
                initialfile=f"Carteira_{nome_limpo}.pdf",
                filetypes=[("PDF", "*.pdf"), ("Todos", "*.*")],
            )
            if not caminho:
                return False, "Operação cancelada"
            with open(caminho, 'wb') as f:
                f.write(res['pdf_conteudo'])
            return True, caminho
        except Exception as e:
            return False, f"Erro ao baixar PDF:\n{e}"

    def abrir_pdf(self, caminho):
        try:
            self._abrir_sistema(caminho)
            return True, "PDF aberto."
        except Exception as e:
            return False, f"Erro ao abrir PDF:\n{e}"

    @staticmethod
    def _abrir_sistema(path):
        if sys.platform.startswith("win"):
            os.startfile(path)
        elif sys.platform.startswith("darwin"):
            subprocess.call(["open", path])
        else:
            subprocess.call(["xdg-open", path])

    # ──────────────────────────────────────────────────────────────────────────
    # Histórico
    # ──────────────────────────────────────────────────────────────────────────
    def carregar_historico(self, termo="", periodo="TODOS", usuario="TODOS"):
        try:
            return self.repo.buscar_com_filtros(termo, periodo, usuario)
        except Exception as e:
            raise Exception(f"Erro ao carregar histórico: {e}")

    def contar_total_carteiras(self):
        try:
            return self.repo.contar_total()
        except Exception:
            return 0

    def buscar_usuarios_unicos(self):
        try:
            return self.repo.buscar_usuarios_unicos()
        except Exception:
            return []