# -*- coding: utf-8 -*-
"""Interface de Carteira Digital do Produtor Rural."""
import io
import os
import re
import sys
import time
import textwrap
import tempfile
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, Image as PILImage, ImageDraw, ImageFont
import PyPDF2

from ui.base_ui import BaseUI
from app.theme import AppTheme
from .controller import CarteiraController
from .services import CarteiraService
from .views.historico_view import HistoricoView
<<<<<<< HEAD
from .views.batch_view import BatchCarteiraView   # ← aba de lote separada

=======
from .views.batch_view import BatchCarteiraView 


>>>>>>> f4a3e3b (.)
MAX_FILENAME_DISPLAY    = 30
DEBOUNCE_DELAY          = 120
SUPPORTED_IMAGE_FORMATS = [
    ("Imagens", "*.png *.jpg *.jpeg *.bmp *.webp"),
    ("Todos",   "*.*"),
]

_VERDE  = "#22c55e"
_VERDEH = "#16a34a"
_AZUL   = "#3b82f6"
_AZULH  = "#2563eb"
_MUTED  = "#64748b"
_VERM   = "#ef4444"
_AMBER  = "#f59e0b"

# ── Paths dos assets ──────────────────────────────────────────────────────────
IMG_FRENTE = r"Q:\ARQUIVOS CPCPR\SECTOR AUTOMATION\images\frente.png"
IMG_VERSO  = r"Q:\ARQUIVOS CPCPR\SECTOR AUTOMATION\images\verso.png"
FONTE_PATH = r"Q:\ARQUIVOS CPCPR\fabio jr\CARTAO-DIGITAL\Roboto-Regular.ttf"
SEFAZ_URL  = "http://sistemas.sefaz.am.gov.br/gcc/entrada.do"

# ── Mapeamento UNLOC ──────────────────────────────────────────────────────────
UNLOC_MAP = {
    "BAE":     "BAR",
    "MTS-ATZ": "ATZ-MTS", "MTS": "ATZ-MTS",
    "NRO-ITR": "ITR-NRO", "NRO": "ITR-NRO",
    "MTP-MNX": "MNX-MTP", "MTP": "MNX-MTP",
    "VE-LBR":  "LBR-VE",  "VE":  "LBR-VE",
    "VRC-MPU": "MPU-VRC", "VRC": "MPU-VRC",
    "BNA-PRF": "PRF-BNA", "BNA": "PRF-BNA",
    "VDL-ITR": "ITR-VDL", "VDL": "ITR-VDL",
    "RLD-HIA": "HIA-RLD", "RLD": "HIA-RLD",
    "CAN-SUL": "SUL-CAN",
    "ZL-MAO":  "MAO-ZL",  "ZL":  "MAO-ZL",
}


def _normalizar_unloc(unloc: str) -> str:
    return UNLOC_MAP.get(unloc, unloc)


def _limitar_texto(texto: str, n: int) -> str:
    return texto[:n - 3] + "..." if len(texto) > n else texto


def _desenhar_texto_quebrado(draw, coordenadas, texto, fonte, largura_max, altura_max):
    x, y = coordenadas
    for linha in textwrap.wrap(texto or "", width=largura_max // 9):
        if y >= altura_max:
            break
        draw.text((x, y), linha, fill=(0, 0, 0), font=fonte)
        y += 40


def _gerar_pdf_lote(dados: dict) -> bytes:
    """
    Replica APP_SETOR.fazer_carteiras:
    Desenha frente + verso com Pillow, mescla com PyPDF2.
    """
    largura_max    = 540
    fonte          = ImageFont.truetype(FONTE_PATH, 41)
    fonte_endereco = ImageFont.truetype(FONTE_PATH, 38)

    nome        = dados.get("nome", "")
    rp          = dados.get("rp", "")
    cpf         = dados.get("cpf", "")
    propriedade = dados.get("propriedade", "")
    unloc       = dados.get("unloc", "")
    inicioatv   = dados.get("inicioatv", "")
    validade    = dados.get("validade", "")
    endereco    = _limitar_texto(dados.get("endereco", ""), 50)
    atv1        = dados.get("atv1", "")
    atv2        = _limitar_texto(dados.get("atv2", ""), 60)
    cnae1       = dados.get("cnae1", "")
    cnae2       = dados.get("cnae2", "") if atv2 else ""
    latitude    = dados.get("latitude", "")
    longitude   = dados.get("longitude", "")

    # FRENTE
    modelo  = PILImage.open(IMG_FRENTE)
    desenho = ImageDraw.Draw(modelo)
    desenho.text((217, 393),  rp,          fill=(0, 0, 0), font=fonte)
    desenho.text((95,  518),  nome,        fill=(0, 0, 0), font=fonte)
    desenho.text((864, 392),  cpf,         fill=(0, 0, 0), font=fonte)
    desenho.text((100, 660),  propriedade, fill=(0, 0, 0), font=fonte)
    desenho.text((212, 824),  unloc,       fill=(0, 0, 0), font=fonte)
    desenho.text((751, 824),  inicioatv,   fill=(0, 0, 0), font=fonte)
    desenho.text((1063, 825), validade,    fill=(0, 0, 0), font=fonte)

    # VERSO
    modelo_verso  = PILImage.open(IMG_VERSO)
    desenho_verso = ImageDraw.Draw(modelo_verso)
    altura_verso  = modelo_verso.size[1]

    linhas_endereco = textwrap.wrap(endereco, largura_max)
    coord_end = [89, 285]
    for linha in linhas_endereco:
        for lq in textwrap.wrap(linha, width=largura_max // 9):
            if coord_end[1] < altura_verso:
                desenho_verso.text(tuple(coord_end), lq,
                                   fill=(0, 0, 0), font=fonte_endereco)
                coord_end[1] += 40

    _desenhar_texto_quebrado(
        desenho_verso, (89, 473),
        f"{cnae1} - {atv1}" if cnae1 else atv1,
        fonte, largura_max, altura_verso)

    if atv2:
        _desenhar_texto_quebrado(
            desenho_verso, (89, 631),
            f"{cnae2} - {atv2}" if cnae2 else atv2,
            fonte, largura_max, altura_verso)

    _desenhar_texto_quebrado(
        desenho_verso, (382, 804),
        f"{latitude}  {longitude}",
        fonte, largura_max, altura_verso)

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tf:
        path_frente = tf.name
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tv:
        path_verso = tv.name
    try:
        modelo.save(path_frente, format="PDF")
        modelo_verso.save(path_verso, format="PDF")
        merger = PyPDF2.PdfMerger()
        merger.append(PyPDF2.PdfReader(path_frente))
        merger.append(PyPDF2.PdfReader(path_verso))
        buf = io.BytesIO()
        merger.write(buf)
        merger.close()
        return buf.getvalue()
    finally:
        for p in (path_frente, path_verso):
            try:
                os.remove(p)
            except OSError:
                pass


class CarteiraDigitalUI(BaseUI):

    def __init__(self, master, usuario):
        super().__init__(master)
        self.usuario    = usuario
        self.service    = CarteiraService()
        self.controller = CarteiraController(usuario, self.service)

        self.lado        = "frente"
        self._after_id   = None
        self._pdf_path   = None
        self.fotos       = {"foto1": None, "foto2": None, "foto3": None}
        self._lbl_fotos  = {}
        self._labels_frente = {}
        self._labels_verso  = {}

        self.configure(fg_color=AppTheme.BG_APP)
        self._layout()
        self._configurar_atalhos()

    # ── Atalhos ───────────────────────────────────────────────────────────────
    def _configurar_atalhos(self):
        self.bind("<Control-s>", lambda _: self._salvar_banco())
        self.bind("<Control-l>", lambda _: self._confirmar_limpar())
        self.bind("<F5>",        lambda _: self._virar_cartao())
        self.focus_set()

    # ── Layout: notebook com 2 abas ───────────────────────────────────────────
    def _layout(self):
        from tkinter import ttk

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Cart.TNotebook",
                        background=AppTheme.BG_APP, borderwidth=0)
        style.configure("Cart.TNotebook.Tab",
                        background=AppTheme.BG_CARD,
                        foreground=_MUTED,
                        font=("Segoe UI", 12),
                        padding=(22, 10))
        style.map("Cart.TNotebook.Tab",
                  background=[("selected", AppTheme.BG_INPUT)],
                  foreground=[("selected", AppTheme.TXT_MAIN)])

        nb = ttk.Notebook(self, style="Cart.TNotebook")
        nb.pack(fill="both", expand=True)

        # Aba 1 — Gerar em Lote (BatchCarteiraView)
        aba1 = ctk.CTkFrame(nb, fg_color=AppTheme.BG_APP)
        nb.add(aba1, text="  Gerar em Lote  ")

        # Instancia a view de lote passando repo e sefaz_repo do service
        sefaz_repo = getattr(self.service, "sefaz_repo", None)
        BatchCarteiraView(
            aba1,
            usuario    = self.usuario,
            repo       = self.service,
            sefaz_repo = sefaz_repo,
        ).pack(fill="both", expand=True)

        # Aba 2 — Cadastro Individual
        aba2 = ctk.CTkFrame(nb, fg_color=AppTheme.BG_APP)
        nb.add(aba2, text="  Cadastro Individual  ")
        self._build_individual(aba2)

    # =========================================================================
    # ABA 2 — CADASTRO INDIVIDUAL
    # =========================================================================
    def _build_individual(self, parent):
        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=36, pady=28)
        wrap.grid_columnconfigure(0, weight=0)
        wrap.grid_columnconfigure(1, weight=1)
        self._coluna_cartao(wrap)
        self._coluna_formulario(wrap)

    # ── Coluna esquerda: cartão + botões ──────────────────────────────────────
    def _coluna_cartao(self, parent):
        col = ctk.CTkFrame(parent, fg_color="transparent")
        col.grid(row=0, column=0, sticky="n", padx=(0, 28))

        ctk.CTkLabel(col, text="PRÉVIA DO CARTÃO",
                     font=("Segoe UI", 10, "bold"),
                     text_color=_MUTED).pack(anchor="w", pady=(0, 8))

        shell = ctk.CTkFrame(col, fg_color=AppTheme.BG_CARD,
                             corner_radius=16,
                             border_width=1, border_color=AppTheme.BORDER)
        shell.pack()

        self.card = ctk.CTkFrame(
            shell,
            width=self.controller.CARD_W,
            height=self.controller.CARD_H,
            fg_color="transparent",
        )
        self.card.pack(padx=12, pady=12)
        self.card.pack_propagate(False)

        self.lbl_bg = ctk.CTkLabel(self.card, text="")
        self.lbl_bg.place(x=0, y=0)
        self._render_cartao()

        W = self.controller.CARD_W
        for txt, cor, corh, cmd, bold in [
            ("🔄  Virar cartão",       AppTheme.BG_INPUT, AppTheme.BORDER, self._virar_cartao,    False),
            ("💾  Salvar no Banco",     _VERDE,            _VERDEH,         self._salvar_banco,    True),
            ("📜  Histórico",           _AZUL,             _AZULH,          self.abrir_historico,  False),
            ("🗑️  Limpar Formulário",  AppTheme.BG_INPUT, AppTheme.BORDER, self._confirmar_limpar, False),
        ]:
            ctk.CTkButton(
                col, text=txt,
                width=W, height=40, corner_radius=10,
                fg_color=cor, hover_color=corh,
                text_color=AppTheme.TXT_MAIN,
                font=("Segoe UI", 11, "bold") if bold else ("Segoe UI", 11),
                command=cmd,
            ).pack(pady=(6, 0))

    def _render_cartao(self):
        img_path = (self.controller.IMG_FRENTE
                    if self.lado == "frente" else self.controller.IMG_VERSO)
        try:
            img = Image.open(img_path).resize(
                (self.controller.CARD_W, self.controller.CARD_H))
            ctk_img = ctk.CTkImage(
                light_image=img,
                size=(self.controller.CARD_W, self.controller.CARD_H))
            self.lbl_bg.configure(image=ctk_img, text="")
            self.lbl_bg.image = ctk_img
        except Exception:
            self.lbl_bg.configure(
                image=None,
                text=f"[ {'FRENTE' if self.lado == 'frente' else 'VERSO'} ]",
                font=("Segoe UI", 14),
                text_color=AppTheme.TXT_MUTED,
            )
        for w in self.card.winfo_children():
            if w is not self.lbl_bg:
                w.destroy()
        self._labels_frente.clear()
        self._labels_verso.clear()
        if self.lado == "frente":
            self._conteudo_frente()
        else:
            self._conteudo_verso()

    def _txt(self, parent, x, y, w, text="---", font=("Segoe UI", 8)):
        frame = ctk.CTkFrame(parent, width=w, height=18, fg_color="transparent")
        frame.place(x=x, y=y)
        frame.pack_propagate(False)
        lbl = ctk.CTkLabel(frame, text=text, font=font,
                           text_color=AppTheme.TXT_MAIN, anchor="w")
        lbl.pack(fill="x")
        return lbl

    def _conteudo_frente(self):
        self._labels_frente = {
            "registro":    self._txt(self.card, 27,  100, 180, font=("Segoe UI", 12)),
            "cpf":         self._txt(self.card, 211, 100, 190, font=("Segoe UI", 12)),
            "nome":        self._txt(self.card, 27,  136, 370, font=("Segoe UI", 12, "bold")),
            "propriedade": self._txt(self.card, 27,  173, 370, font=("Segoe UI", 12)),
            "unloc":       self._txt(self.card, 26,  210, 124, font=("Segoe UI", 12)),
            "inicio":      self._txt(self.card, 190, 210, 106, font=("Segoe UI", 12)),
            "validade":    self._txt(self.card, 300, 210, 140, font=("Segoe UI", 12)),
        }

    def _conteudo_verso(self):
        self._labels_verso = {
            "endereco":   self._txt(self.card, 21, 73,  385, font=("Segoe UI", 12)),
            "atividade1": self._txt(self.card, 21, 127, 385, font=("Segoe UI", 12)),
            "atividade2": self._txt(self.card, 21, 167, 385, font=("Segoe UI", 12)),
            "georef":     self._txt(self.card, 21, 206, 385, font=("Segoe UI", 12)),
        }

    # ── Coluna direita: formulário ────────────────────────────────────────────
    def _coluna_formulario(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.grid(row=0, column=1, sticky="nsew")

        self._secao(scroll, "DADOS DO PRODUTOR")
        p1 = self._painel(scroll)
        self.registro    = self._campo(p1, "Registro estadual")
        self.cpf         = self._campo(p1, "CPF", tipo="cpf")
        self.nome        = self._campo(p1, "Nome do produtor")
        self.propriedade = self._campo(p1, "Propriedade")

        linha = ctk.CTkFrame(p1, fg_color="transparent")
        linha.pack(fill="x", padx=16)
        linha.grid_columnconfigure((0, 1, 2), weight=1)
        self.unloc    = self._campo_grid(linha, "UNLOC",    0)
        self.inicio   = self._campo_grid(linha, "Início",   1, tipo="data")
        self.validade = self._campo_grid(linha, "Validade", 2, tipo="data")

        self._secao(scroll, "INFORMAÇÕES COMPLEMENTARES")
        p2 = self._painel(scroll)
        self.endereco   = self._campo(p2, "Endereço")
        self.atividade1 = self._campo(p2, "Atividade primária")
        self.atividade2 = self._campo(p2, "Atividade secundária")
        self.georef     = self._campo(p2, "Georreferenciamento")

        self._secao(scroll, "IMPORTAR PDF DA CARTEIRA")
        p_pdf = self._painel(scroll)
        self._build_importar_pdf(p_pdf)

        self._secao(scroll, "FOTOS")
        p3 = self._painel(scroll)
        for i in range(1, 4):
            chave = f"foto{i}"
            row = ctk.CTkFrame(p3, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=5)
            ctk.CTkButton(
                row, text=f"📷 Foto {i}", width=120,
                fg_color=_AZUL, hover_color=_AZULH,
                text_color="#fff", corner_radius=8,
                command=lambda c=chave: self._selecionar_foto(c),
            ).pack(side="left")
            lbl = ctk.CTkLabel(row, text="—", text_color=_MUTED,
                               font=("Segoe UI", 11))
            lbl.pack(side="left", padx=10)
            self._lbl_fotos[chave] = lbl

    def _secao(self, parent, txt):
        ctk.CTkLabel(parent, text=txt,
                     font=("Segoe UI", 10, "bold"),
                     text_color=_VERDE).pack(anchor="w", pady=(18, 4))

    def _painel(self, parent):
        p = ctk.CTkFrame(parent, fg_color=AppTheme.BG_INPUT,
                         corner_radius=12,
                         border_width=1, border_color=AppTheme.BORDER)
        p.pack(fill="x")
        return p

    def _campo(self, parent, placeholder, tipo=None):
        e = ctk.CTkEntry(
            parent, placeholder_text=placeholder,
            fg_color=AppTheme.BG_INPUT, border_color=AppTheme.BORDER,
            text_color=AppTheme.TXT_MAIN, height=36, corner_radius=8,
        )
        e.pack(fill="x", padx=16, pady=4)
        e.bind("<KeyRelease>", self._debounce_preview)
        if tipo == "cpf":
            e.bind("<KeyRelease>", lambda _: self._fmt_cpf(e), add="+")
        elif tipo == "data":
            e.bind("<KeyRelease>", lambda _: self._fmt_data(e), add="+")
        return e

    def _campo_grid(self, parent, placeholder, col, tipo=None):
        e = ctk.CTkEntry(
            parent, placeholder_text=placeholder,
            fg_color=AppTheme.BG_INPUT, border_color=AppTheme.BORDER,
            text_color=AppTheme.TXT_MAIN, height=36, corner_radius=8,
        )
        e.grid(row=0, column=col, sticky="ew", padx=4, pady=4)
        e.bind("<KeyRelease>", self._debounce_preview)
        if tipo == "data":
            e.bind("<KeyRelease>", lambda _: self._fmt_data(e), add="+")
        return e

    def _fmt_cpf(self, entry):
        try:
            d = re.sub(r"\D", "", entry.get())[:11]
            if   len(d) <= 3: r = d
            elif len(d) <= 6: r = f"{d[:3]}.{d[3:]}"
            elif len(d) <= 9: r = f"{d[:3]}.{d[3:6]}.{d[6:]}"
            else:             r = f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"
            if r != entry.get():
                entry.delete(0, "end")
                entry.insert(0, r)
        except Exception:
            pass

    def _fmt_data(self, entry):
        try:
            d = re.sub(r"\D", "", entry.get())[:8]
            if   len(d) <= 2: r = d
            elif len(d) <= 4: r = f"{d[:2]}/{d[2:]}"
            else:             r = f"{d[:2]}/{d[2:4]}/{d[4:]}"
            if r != entry.get():
                entry.delete(0, "end")
                entry.insert(0, r)
        except Exception:
            pass

    def _debounce_preview(self, *_):
        if self._after_id:
            self.after_cancel(self._after_id)
        self._after_id = self.after(DEBOUNCE_DELAY, self._atualizar_preview)

    def _safe_set(self, lbl, val):
        try:
            if lbl and lbl.winfo_exists():
                lbl.configure(text=str(val).strip() if val else "---")
        except Exception:
            pass

    def _atualizar_preview(self):
        if self.lado == "frente":
            lf = self._labels_frente
            self._safe_set(lf.get("registro"),    self.registro.get())
            self._safe_set(lf.get("cpf"),         self.controller.formatar_cpf_exibicao(self.cpf.get()))
            self._safe_set(lf.get("nome"),        self.nome.get())
            self._safe_set(lf.get("propriedade"), self.propriedade.get())
            self._safe_set(lf.get("unloc"),       self.unloc.get())
            self._safe_set(lf.get("inicio"),      self.inicio.get())
            self._safe_set(lf.get("validade"),    self.validade.get())
        else:
            lv = self._labels_verso
            self._safe_set(lv.get("endereco"),   self.endereco.get())
            self._safe_set(lv.get("atividade1"), self.atividade1.get())
            self._safe_set(lv.get("atividade2"), self.atividade2.get())
            self._safe_set(lv.get("georef"),     self.georef.get())

    def _virar_cartao(self):
        self.lado = "verso" if self.lado == "frente" else "frente"
        self._render_cartao()
        self._atualizar_preview()

    def _selecionar_foto(self, chave):
        caminho = filedialog.askopenfilename(
            title=f"Selecionar {chave.replace('foto', 'Foto ')}",
            filetypes=SUPPORTED_IMAGE_FORMATS,
        )
        if not caminho or not os.path.exists(caminho):
            return
        mb = os.path.getsize(caminho) / (1024 * 1024)
        if mb > 10:
            messagebox.showerror("Erro",
                                  f"Arquivo muito grande ({mb:.1f} MB). Máximo: 10 MB")
            return
        try:
            with Image.open(caminho) as img:
                img.verify()
            with Image.open(caminho) as img:
                w, h = img.size
                fmt = img.format
        except Exception as exc:
            messagebox.showerror("Erro", f"Imagem inválida:\n{exc}")
            return
        self.fotos[chave] = caminho
        nome = os.path.basename(caminho)
        if len(nome) > MAX_FILENAME_DISPLAY:
            nome = nome[:MAX_FILENAME_DISPLAY - 3] + "..."
        self._lbl_fotos[chave].configure(
            text=f"✓ {nome} ({w}×{h}, {fmt})", text_color=_VERDE)

    def _build_importar_pdf(self, parent):
        row1 = ctk.CTkFrame(parent, fg_color="transparent")
        row1.pack(fill="x", padx=16, pady=(12, 6))
        self._btn_importar_pdf = ctk.CTkButton(
            row1, text="📄 Selecionar PDF",
            width=160, height=38, corner_radius=8,
            fg_color=_AZUL, hover_color=_AZULH,
            text_color="#fff", font=("Segoe UI", 12, "bold"),
            command=self._selecionar_pdf)
        self._btn_importar_pdf.pack(side="left")
        self._lbl_pdf = ctk.CTkLabel(
            row1, text="Nenhum PDF selecionado",
            font=("Segoe UI", 11), text_color=_MUTED)
        self._lbl_pdf.pack(side="left", padx=12)

        row2 = ctk.CTkFrame(parent, fg_color="transparent")
        row2.pack(fill="x", padx=16, pady=(0, 12))
        self._btn_extrair = ctk.CTkButton(
            row2, text="🔍 Extrair Informações do PDF",
            width=220, height=38, corner_radius=8,
            fg_color=AppTheme.BG_INPUT, hover_color=AppTheme.BORDER,
            text_color=AppTheme.TXT_MAIN, font=("Segoe UI", 11),
            command=self._extrair_pdf, state="disabled")
        self._btn_extrair.pack(side="left")
        self._lbl_extrair_status = ctk.CTkLabel(
            row2, text="", font=("Segoe UI", 11), text_color=_MUTED)
        self._lbl_extrair_status.pack(side="left", padx=12)
        self._pdf_path = None

    def _selecionar_pdf(self):
        caminho = filedialog.askopenfilename(
            title="Selecionar PDF da Carteira",
            filetypes=[("PDF", "*.pdf"), ("Todos", "*.*")])
        if not caminho or not os.path.exists(caminho):
            return
        self._pdf_path = caminho
        nome = os.path.basename(caminho)
        if len(nome) > MAX_FILENAME_DISPLAY:
            nome = nome[:MAX_FILENAME_DISPLAY - 3] + "..."
        self._lbl_pdf.configure(text=f"✓ {nome}", text_color=_VERDE)
        self._btn_extrair.configure(state="normal")
        self._lbl_extrair_status.configure(text="")

    def _extrair_pdf(self):
        if not self._pdf_path:
            return
        self._btn_extrair.configure(state="disabled", text="⏳ Extraindo...")
        self._lbl_extrair_status.configure(text="Lendo PDF...", text_color=_MUTED)
        threading.Thread(target=self._worker_extrair_pdf, daemon=True).start()

    def _worker_extrair_pdf(self):
        try:
            texto = self._ler_texto_pdf(self._pdf_path)
            if not texto.strip():
                self.after(0, self._exibir_resultado_extracao,
                           None, "PDF sem texto legível (pode ser imagem escaneada).")
                return
            dados = self._parsear_texto_carteira(texto)
            self.after(0, self._exibir_resultado_extracao, dados, None)
        except Exception as e:
            self.after(0, self._exibir_resultado_extracao, None, str(e))

    def _ler_texto_pdf(self, caminho: str) -> str:
        texto = ""
        try:
            import pypdf
            with open(caminho, "rb") as f:
                for page in pypdf.PdfReader(f).pages:
                    texto += (page.extract_text() or "") + "\n"
            return texto
        except ImportError:
            pass
        with open(caminho, "rb") as f:
            for page in PyPDF2.PdfReader(f).pages:
                texto += (page.extract_text() or "") + "\n"
        return texto

    def _parsear_texto_carteira(self, texto: str) -> dict:
        dados = {}
        texto_upper = texto.upper()

        cpf_m = re.search(r"\b(\d{3}[\.\ ]?\d{3}[\.\ ]?\d{3}[-\ ]?\d{2})\b", texto)
        if cpf_m:
            d = re.sub(r"\D", "", cpf_m.group(1))
            dados["cpf"] = f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"

        for k, pattern in [
            ("registro",   r"(?:REGISTRO|R\.P\.|RP|IE|INSCRIÇÃO ESTADUAL)[:\s]+([0-9\-\.\/]+)"),
            ("propriedade",r"(?:PROPRIEDADE|NOME DA PROPRIEDADE|IMÓVEL)[:\s]+([^\n\r]+)"),
            ("unloc",      r"PR-([A-Z\-]+)/(\d+)"),
            ("validade",   r"(?:VALIDADE|VÁLIDO ATÉ|VENCIMENTO)[:\s]*(\d{2}[\/\-]\d{2}[\/\-]\d{4})"),
            ("inicio",     r"(?:INÍCIO|INICIO|ANO DE INÍCIO)[:\s]*(\d{2}[\/\-]\d{2}[\/\-]\d{4}|\d{4})"),
            ("endereco",   r"(?:ENDEREÇO|ENDERECO|END\.)[:\s]+([^\n\r]+)"),
            ("atividade1", r"(?:ATIVIDADE PRINCIPAL|CNAE PRINCIPAL|ATV\.?\s*1)[:\s]+([^\n\r]+)"),
            ("atividade2", r"(?:ATIVIDADE SECUNDÁRIA|CNAE SECUNDÁRIO|ATV\.?\s*2)[:\s]+([^\n\r]+)"),
        ]:
            m = re.search(pattern, texto_upper)
            if m:
                val = m.group(1).strip()
                dados[k] = (f"PR-{m.group(1)}/{m.group(2)}"
                            if k == "unloc"
                            else val.title() if k in ("propriedade","endereco","atividade1","atividade2")
                            else val.replace("-", "/"))

        nome_m = re.search(
            r"(?:NOME|PRODUTOR)[:\s]+([A-ZÁÀÂÃÉÈÊÍÏÓÔÕÚÜÇ][A-ZÁÀÂÃÉÈÊÍÏÓÔÕÚÜÇa-záàâãéèêíïóôõúüç\s]+)",
            texto_upper)
        if nome_m:
            dados["nome"] = nome_m.group(1).strip().title()

        geo_m = re.search(r"(-?\d{1,3}[,\.]\d+)\s+(-?\d{1,3}[,\.]\d+)", texto)
        if geo_m:
            dados["georef"] = f"{geo_m.group(1)}  {geo_m.group(2)}"

        return dados

    def _exibir_resultado_extracao(self, dados: dict, erro: str):
        self._btn_extrair.configure(state="normal",
                                    text="🔍 Extrair Informações do PDF")
        if erro:
            self._lbl_extrair_status.configure(
                text=f"❌ {erro[:60]}", text_color=_VERM)
            messagebox.showerror("Erro ao extrair PDF", erro)
            return
        if not dados:
            self._lbl_extrair_status.configure(
                text="⚠️ Nenhum campo identificado.", text_color=_VERM)
            return
        mapa = {
            "registro":   self.registro,   "cpf":        self.cpf,
            "nome":       self.nome,       "propriedade":self.propriedade,
            "unloc":      self.unloc,      "inicio":     self.inicio,
            "validade":   self.validade,   "endereco":   self.endereco,
            "atividade1": self.atividade1, "atividade2": self.atividade2,
            "georef":     self.georef,
        }
        preenchidos = 0
        for chave, entry in mapa.items():
            valor = dados.get(chave, "")
            if valor:
                entry.delete(0, "end")
                entry.insert(0, valor)
                preenchidos += 1
        self._atualizar_preview()
        total = len(mapa)
        cor = _VERDE if preenchidos >= total // 2 else _MUTED
        self._lbl_extrair_status.configure(
            text=f"✅ {preenchidos}/{total} campos preenchidos", text_color=cor)
        if preenchidos == 0:
            messagebox.showwarning(
                "Extração",
                "Nenhum campo identificado automaticamente.\n"
                "Preencha os campos manualmente.")
        elif preenchidos < total // 2:
            messagebox.showinfo(
                "Extração parcial",
                f"{preenchidos} campo(s) preenchido(s) automaticamente.\n"
                "Verifique e complete os campos restantes.")

    def _salvar_banco(self):
        dados = {
            "registro":    self.registro.get().strip(),
            "cpf":         self.cpf.get().strip(),
            "nome":        self.nome.get().strip(),
            "propriedade": self.propriedade.get().strip(),
            "unloc":       self.unloc.get().strip(),
            "inicio":      self.inicio.get().strip(),
            "validade":    self.validade.get().strip(),
            "endereco":    self.endereco.get().strip(),
            "atividade1":  self.atividade1.get().strip(),
            "atividade2":  self.atividade2.get().strip(),
            "georef":      self.georef.get().strip(),
        }
        vazios = [n for c, n in [
            ("registro", "Registro Estadual"), ("cpf", "CPF"),
            ("nome", "Nome do Produtor"),      ("propriedade", "Propriedade"),
        ] if not dados.get(c)]
        if vazios:
            messagebox.showwarning("Validação",
                                    "Campos obrigatórios:\n• " + "\n• ".join(vazios))
            return
        if len(re.sub(r"\D", "", dados["cpf"])) != 11:
            messagebox.showwarning("Validação", "CPF deve ter 11 dígitos.")
            return
        for campo, nome in [("inicio", "Início"), ("validade", "Validade")]:
            v = dados.get(campo, "")
            if v and not re.match(r"^\d{2}/\d{2}/\d{4}$", v):
                messagebox.showwarning("Validação",
                                        f"{nome} inválida. Use dd/mm/aaaa.")
                return
        if not any(self.fotos.values()):
            if not messagebox.askyesno("Aviso",
                                        "Nenhuma foto selecionada. Continuar mesmo assim?"):
                return
        ok, msg = self.controller.salvar_carteira(dados, self.fotos)
        if ok:
            messagebox.showinfo("Sucesso", msg)
            self._limpar_formulario()
        else:
            messagebox.showerror("Erro", msg)

    def _limpar_formulario(self):
        for e in [self.registro, self.cpf, self.nome, self.propriedade,
                  self.unloc, self.inicio, self.validade,
                  self.endereco, self.atividade1, self.atividade2, self.georef]:
            e.delete(0, "end")
        self.fotos = {"foto1": None, "foto2": None, "foto3": None}
        for lbl in self._lbl_fotos.values():
            lbl.configure(text="—", text_color=_MUTED)
        if self.lado == "verso":
            self.lado = "frente"
            self._render_cartao()
        self._atualizar_preview()

    def _confirmar_limpar(self):
        tem = any([
            self.registro.get().strip(),
            self.cpf.get().strip(),
            self.nome.get().strip(),
            any(self.fotos.values()),
        ])
        if tem and not messagebox.askyesno("Confirmação", "Limpar todos os campos?"):
            return
        self._limpar_formulario()

    def abrir_historico(self):
        HistoricoView(self, self.usuario, self.controller).grab_set()