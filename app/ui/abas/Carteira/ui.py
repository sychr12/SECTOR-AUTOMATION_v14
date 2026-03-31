# ui.py
# -*- coding: utf-8 -*-
"""
ui.py — Interface principal da Carteira Digital do Produtor Rural.
Local: app/ui/abas/Carteira/ui.py
"""
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
from PIL import Image, ImageDraw
import PyPDF2

from ui.base_ui import BaseUI
from app.theme import AppTheme
from .controller import CarteiraController
from .carteira_service import CarteiraService
from .views.historico_view import HistoricoView
from .views.batch_view import BatchCarteiraView
from .assets import get_img_frente, get_img_verso, get_pil_font, open_image
from .utils.constants import *
from .utils.formatters import format_cpf, format_date


MAX_FILENAME_DISPLAY = 30
DEBOUNCE_DELAY = 120
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

    # ── Layout ────────────────────────────────────────────────────────────────

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

        # Aba 1 — Gerar em Lote
        aba1 = ctk.CTkFrame(nb, fg_color=AppTheme.BG_APP)
        nb.add(aba1, text="  Gerar em Lote  ")
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

    # ── Aba 2: Cadastro Individual ────────────────────────────────────────────

    def _build_individual(self, parent):
        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=36, pady=28)
        wrap.grid_columnconfigure(0, weight=0)
        wrap.grid_columnconfigure(1, weight=1)
        self._coluna_cartao(wrap)
        self._coluna_formulario(wrap)

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
            ("🔄  Virar cartão",      AppTheme.BG_INPUT, AppTheme.BORDER, self._virar_cartao,     False),
            ("💾  Salvar no Banco",    _VERDE,            _VERDEH,         self._salvar_banco,     True),
            ("📜  Histórico",          _AZUL,             _AZULH,          self.abrir_historico,   False),
            ("🗑️  Limpar Formulário", AppTheme.BG_INPUT, AppTheme.BORDER, self._confirmar_limpar, False),
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
        """Renderiza a prévia do cartão. Nunca lança exceção."""
        img_path = (self.controller.IMG_FRENTE
                    if self.lado == "frente" else self.controller.IMG_VERSO)
        try:
            pil_img = open_image(img_path,
                                 "FRENTE" if self.lado == "frente" else "VERSO")
            pil_img = pil_img.resize(
                (self.controller.CARD_W, self.controller.CARD_H), Image.Resampling.LANCZOS)
            ctk_img = ctk.CTkImage(
                light_image=pil_img,
                size=(self.controller.CARD_W, self.controller.CARD_H))
            self.lbl_bg.configure(image=ctk_img, text="")
            self.lbl_bg.image = ctk_img
        except Exception:
            label = "FRENTE" if self.lado == "frente" else "VERSO"
            self.lbl_bg.configure(
                image=None,
                text=f"[ {label} ]",
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

    def _coluna_formulario(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.grid(row=0, column=1, sticky="nsew")

        self._secao(scroll, "DADOS DO PRODUTOR")
        p1 = self._painel(scroll)
        self.registro    = self._campo(p1, "Registro estadual")

        cpf_row = ctk.CTkFrame(p1, fg_color="transparent")
        cpf_row.pack(fill="x", padx=16, pady=4)

        self.cpf = ctk.CTkEntry(
            cpf_row,
            placeholder_text="CPF",
            fg_color=AppTheme.BG_INPUT,
            border_color=AppTheme.BORDER,
            text_color=AppTheme.TXT_MAIN,
            height=36,
            corner_radius=8,
        )
        self.cpf.pack(side="left", fill="x", expand=True)
        self.cpf.bind("<KeyRelease>", self._debounce_preview)

        self._btn_buscar_cpf = ctk.CTkButton(
            cpf_row,
            text="🔍 Buscar CPF",
            width=130,
            height=36,
            corner_radius=8,
            fg_color=_AZUL,
            hover_color=_AZULH,
            text_color="#fff",
            font=("Segoe UI", 10, "bold"),
            command=self._buscar_por_cpf,
        )
        self._btn_buscar_cpf.pack(side="left", padx=(8, 0))

        self._lbl_buscar_status = ctk.CTkLabel(
            cpf_row,
            text="",
            font=("Segoe UI", 9),
            text_color=_MUTED,
        )
        self._lbl_buscar_status.pack(side="left", padx=(8, 0))

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
            lbl = ctk.CTkLabel(row, text="—",
                               text_color=_MUTED, font=("Segoe UI", 11))
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
        return e

    def _campo_grid(self, parent, placeholder, col, tipo=None):
        e = ctk.CTkEntry(
            parent, placeholder_text=placeholder,
            fg_color=AppTheme.BG_INPUT, border_color=AppTheme.BORDER,
            text_color=AppTheme.TXT_MAIN, height=36, corner_radius=8,
        )
        e.grid(row=0, column=col, sticky="ew", padx=4, pady=4)
        e.bind("<KeyRelease>", self._debounce_preview)
        return e

    def _fmt_cpf(self, entry):
        """Apenas valida e deixa a exibição como está (sem delete/insert)."""
        try:
            d = re.sub(r"\D", "", entry.get())
            if len(d) > 11:
                d = d[:11]
                entry.delete(0, "end")
                entry.insert(0, d)
        except Exception:
            pass

    def _fmt_data(self, entry):
        """Apenas valida e limita a 8 dígitos se necessário"""
        try:
            d = re.sub(r"\D", "", entry.get())
            if len(d) > 8:
                entry.delete(0, "end")
                entry.insert(0, d[:8])
        except Exception:
            pass

    def _buscar_por_cpf(self):
        cpf_text = self.cpf.get().strip()
        cpf_limpo = re.sub(r"\D", "", cpf_text)

        if not cpf_limpo:
            messagebox.showwarning("CPF obrigatório", "Digite um CPF antes de pesquisar.")
            return

        if len(cpf_limpo) != 11:
            messagebox.showwarning("CPF inválido", "CPF deve ter 11 dígitos.")
            return

        self._btn_buscar_cpf.configure(state="disabled")
        self._lbl_buscar_status.configure(text="Pesquisando...")

        self.after(700, lambda: self._buscar_por_cpf_exec(cpf_limpo))

    def _buscar_por_cpf_exec(self, cpf_limpo):
        try:
            resultado = self.controller.buscar_por_cpf(cpf_limpo)

            if not resultado:
                messagebox.showinfo("Não encontrado", "Nenhum cadastro encontrado para este CPF.")
                return

            self.registro.delete(0, "end")
            self.registro.insert(0, resultado.get("registro", ""))
            self.cpf.delete(0, "end")
            self.cpf.insert(0, format_cpf(resultado.get("cpf", "")))
            self.nome.delete(0, "end")
            self.nome.insert(0, resultado.get("nome", ""))
            self.propriedade.delete(0, "end")
            self.propriedade.insert(0, resultado.get("propriedade", ""))
            self.unloc.delete(0, "end")
            self.unloc.insert(0, resultado.get("unloc", ""))
            self.inicio.delete(0, "end")
            self.inicio.insert(0, resultado.get("inicio", ""))
            self.validade.delete(0, "end")
            self.validade.insert(0, resultado.get("validade", ""))
            self.endereco.delete(0, "end")
            self.endereco.insert(0, resultado.get("endereco", ""))
            self.atividade1.delete(0, "end")
            self.atividade1.insert(0, resultado.get("atividade1", ""))
            self.atividade2.delete(0, "end")
            self.atividade2.insert(0, resultado.get("atividade2", ""))
            self.georef.delete(0, "end")
            self.georef.insert(0, resultado.get("georef", ""))

            self._atualizar_preview()
            messagebox.showinfo("Encontrado", "Dados carregados a partir do CPF encontrado.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao buscar CPF:\n{e}")
        finally:
            self._btn_buscar_cpf.configure(state="normal")
            self._lbl_buscar_status.configure(text="")

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
            self._safe_set(lf.get("cpf"),
                           format_cpf(self.cpf.get()))
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
            messagebox.showerror(
                "Erro", f"Arquivo muito grande ({mb:.1f} MB). Máximo: 10 MB")
            return
        try:
            with Image.open(caminho) as img:
                img.verify()
            with Image.open(caminho) as img:
                w, h = img.size
                fmt  = img.format
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
            from .utils.pdf_parser import PDFParser
            parser = PDFParser()
            dados = parser.extract_and_parse(self._pdf_path)
            if not dados:
                self.after(0, self._exibir_resultado_extracao,
                           None, "PDF sem texto legível (pode ser imagem escaneada).")
                return
            self.after(0, self._exibir_resultado_extracao, dados, None)
        except Exception as e:
            self.after(0, self._exibir_resultado_extracao, None, str(e))

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
        cor   = _VERDE if preenchidos >= total // 2 else _MUTED
        self._lbl_extrair_status.configure(
            text=f"✅ {preenchidos}/{total} campos preenchidos", text_color=cor)

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
            ("registro", "Registro Estadual"), ("cpf",  "CPF"),
            ("nome",     "Nome do Produtor"),  ("propriedade", "Propriedade"),
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
            if not messagebox.askyesno(
                    "Aviso",
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
        if tem and not messagebox.askyesno("Confirmação",
                                            "Limpar todos os campos?"):
            return
        self._limpar_formulario()

    def abrir_historico(self):
        HistoricoView(self, self.usuario, self.controller).grab_set()