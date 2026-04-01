# -*- coding: utf-8 -*-
import customtkinter as ctk
from tkinter import messagebox
import inspect
import sys
import os
import threading
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(current_dir)
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from theme import apply_theme, AppTheme
from ui.abas.Consultar   import ConsultarUI
from ui.abas.bancoantigo import ConsultaBancoUI
from ui.abas.Email       import BaixarEmailUI
from ui.abas.Analises    import AnaliseUI
from ui.abas.lancamentos import LancamentoUI
from ui.abas.memorando   import MemorandoUI
from ui.abas.anexar      import AnexarUI
from ui.abas.relatorios  import RelatoriosUI
from ui.abas.senha.senha import SenhaUI
from ui.abas.analiseap   import AnaliseapUI
from ui.abas.Carteira    import CarteiraDigitalUI
from services.database   import get_connection


# ── Paleta Corporativa ──────────────────────────────────────────────────────────
_AZUL_PRIMARY   = "#2c5f8a"      # Azul corporativo principal
_AZUL_DARK      = "#1e3a5f"      # Azul mais escuro
_AZUL_LIGHT     = "#e8f0f7"      # Azul muito claro para fundos
_AZUL_ACCENT    = "#3b82f6"      # Azul de destaque
_AZUL_HOVER     = "#e0eef9"      # Azul para hover
_SIDEBAR_BG     = "#1a2c3e"      # Azul escuro/cinza para sidebar
_SIDEBAR_ITEM   = "#2a3f54"      # Item da sidebar
_SIDEBAR_ATIV   = "#2c5f8a"      # Item ativo
_BRANCO         = "#ffffff"
_CINZA_BG       = "#f8fafc"      # Fundo cinza muito claro
_CINZA_BORDER   = "#e2e8f0"      # Cinza para bordas
_CINZA_MEDIO    = "#64748b"      # Cinza médio para textos secundários
_CINZA_TEXTO    = "#1e293b"      # Cinza escuro para textos principais
_VERDE_STATUS   = "#10b981"      # Verde para status online
_VERDE_HOVER    = "#d1fae5"      # Verde claro para hover
_DANGER         = "#ef4444"      # Vermelho para ações destrutivas
_DANGER_DK      = "#dc2626"      # Vermelho escuro

# Textos e elementos
_TEXT_SIDEBAR   = "#cbd5e1"      # Texto inativo na sidebar
_TEXT_SECTION   = "#60a5fa"      # Azul claro para rótulos de seção
_TEXT_MUTED     = "#64748b"      # Cinza para textos secundários
_CARD_BORDER    = "#e2e8f0"      # Borda dos cards
_HEADER_BG      = "#ffffff"      # Fundo do header


# ── Grupos de navegação ──────────────────────────────────────────────────────
_GRUPOS = [
    ("CONSULTAS", [
        ("🔍", "Consulta",      ConsultarUI,      "Consultas avançadas"),
        ("🗄️",  "Banco Antigo", ConsultaBancoUI,  "Dados históricos"),
        ("📈", "Análises",      AnaliseUI,         "Análise de dados"),
    ]),
    ("OPERAÇÕES", [
        ("📥", "E-mails",       BaixarEmailUI,     "Gerenciar emails"),
        ("📋", "Lançamento",    LancamentoUI,      "Novos lançamentos"),
        ("💳", "Carteira",      CarteiraDigitalUI, "Gestão financeira"),
    ]),
    ("DOCUMENTOS", [
        ("📄", "Memorando",     MemorandoUI,       "Documentos internos"),
        ("📎", "Anexar",        AnexarUI,          "Gerenciar anexos"),
        ("📊", "Relatórios",    RelatoriosUI,      "Gerar relatórios"),
    ]),
    ("SISTEMA", [
        ("🔒", "Senha",         SenhaUI,           "Alterar senha"),
    ]),
]

SIDEBAR_W = 280


# ── Item de navegação ────────────────────────────────────────────────────────
class NavItem(ctk.CTkFrame):
    """Item de menu com indicador lateral e estados visuais."""

    def __init__(self, parent, icon: str, label: str, command, is_active=False):
        super().__init__(parent, fg_color="transparent", height=44)
        self.pack(fill="x", padx=12, pady=2)
        self.pack_propagate(False)

        self._cmd    = command
        self._active = is_active

        # Barra indicadora lateral
        self._indicator = ctk.CTkFrame(
            self, width=3,
            fg_color=_AZUL_ACCENT if is_active else "transparent",
            corner_radius=2,
        )
        self._indicator.pack(side="left", fill="y")

        # Fundo do item
        self._bg = ctk.CTkFrame(
            self,
            fg_color=_SIDEBAR_ATIV if is_active else "transparent",
            corner_radius=8,
        )
        self._bg.pack(side="left", fill="both", expand=True, padx=(6, 0))

        # Ícone
        self._icon = ctk.CTkLabel(
            self._bg, text=icon,
            font=("Segoe UI", 15),
            text_color=_BRANCO if is_active else _TEXT_SIDEBAR,
            width=32,
        )
        self._icon.pack(side="left", padx=(12, 8))

        # Texto
        self._text = ctk.CTkLabel(
            self._bg, text=label,
            font=("Segoe UI", 12, "bold" if is_active else "normal"),
            text_color=_BRANCO if is_active else _TEXT_SIDEBAR,
            anchor="w",
        )
        self._text.pack(side="left", fill="x", expand=True)

        # Ponto de status
        self._dot = ctk.CTkFrame(
            self._bg, width=6, height=6, corner_radius=3,
            fg_color=_AZUL_ACCENT if is_active else "transparent",
        )
        self._dot.pack(side="right", padx=(0, 12))

        for w in (self, self._bg, self._icon, self._text):
            w.bind("<Enter>",    self._enter)
            w.bind("<Leave>",    self._leave)
            w.bind("<Button-1>", self._click)

    def set_active(self, val: bool):
        self._active = val
        if val:
            self._indicator.configure(fg_color=_AZUL_ACCENT)
            self._bg.configure(fg_color=_SIDEBAR_ATIV)
            self._icon.configure(text_color=_BRANCO)
            self._text.configure(text_color=_BRANCO, font=("Segoe UI", 12, "bold"))
            self._dot.configure(fg_color=_AZUL_ACCENT)
        else:
            self._indicator.configure(fg_color="transparent")
            self._bg.configure(fg_color="transparent")
            self._icon.configure(text_color=_TEXT_SIDEBAR)
            self._text.configure(text_color=_TEXT_SIDEBAR,
                                 font=("Segoe UI", 12, "normal"))
            self._dot.configure(fg_color="transparent")

    def _enter(self, _=None):
        if not self._active:
            self._bg.configure(fg_color=_SIDEBAR_ITEM)
            self._icon.configure(text_color=_BRANCO)
            self._text.configure(text_color=_BRANCO)

    def _leave(self, _=None):
        if not self._active:
            self._bg.configure(fg_color="transparent")
            self._icon.configure(text_color=_TEXT_SIDEBAR)
            self._text.configure(text_color=_TEXT_SIDEBAR)

    def _click(self, _=None):
        if self._cmd:
            self._cmd()


# ── Janela principal ─────────────────────────────────────────────────────────
class AppPrincipal(ctk.CTkToplevel):

    def __init__(self, usuario_dados, master=None):
        apply_theme()
        super().__init__(master)
        self.title("Sector Automation — Sistema Corporativo")
        self.geometry("1440x900")
        self.minsize(1200, 700)
        self.configure(fg_color=_CINZA_BG)

        try:
            self.iconbitmap(os.path.join(current_dir, "assets", "icon.ico"))
        except Exception:
            pass

        self.usuario    = usuario_dados["username"]
        self.perfil     = usuario_dados.get("perfil", "usuario")
        self.tela_atual = None
        self.nav_items: list[tuple[str, NavItem]] = []
        self.carregando = False

        self._build()
        self._abrir(ConsultarUI, "Consulta")

    # ── BD ───────────────────────────────────────────────────────────────────
    def conectar_bd(self):
        try:
            return get_connection()
        except Exception as exc:
            messagebox.showerror("Conexão", str(exc))
            return None

    # ── Layout raiz ──────────────────────────────────────────────────────────
    def _build(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar com design moderno
        self.sidebar = ctk.CTkFrame(
            self, width=SIDEBAR_W,
            fg_color=_SIDEBAR_BG, corner_radius=0,
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        self.right = ctk.CTkFrame(self, fg_color=_CINZA_BG, corner_radius=0)
        self.right.grid(row=0, column=1, sticky="nsew")
        self.right.grid_columnconfigure(0, weight=1)
        self.right.grid_rowconfigure(1, weight=1)

        self._build_sidebar()
        self._build_topbar()

        wrap = ctk.CTkFrame(self.right, fg_color="transparent")
        wrap.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        wrap.grid_columnconfigure(0, weight=1)
        wrap.grid_rowconfigure(0, weight=1)

        # Card principal com borda sutil
        self.main = ctk.CTkFrame(
            wrap,
            fg_color=_BRANCO,
            corner_radius=12,
            border_width=1,
            border_color=_CARD_BORDER,
        )
        self.main.grid(row=0, column=0, sticky="nsew")

    # ── Sidebar ──────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        # Logo com design corporativo
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=80)
        logo_frame.pack(fill="x", padx=20, pady=(24, 0))
        logo_frame.pack_propagate(False)

        # Ícone da marca
        icon_pill = ctk.CTkFrame(
            logo_frame, width=44, height=44, corner_radius=12,
            fg_color=_AZUL_PRIMARY,
        )
        icon_pill.pack(side="left")
        icon_pill.pack_propagate(False)
        
        ctk.CTkLabel(
            icon_pill, text="S",
            font=("Segoe UI", 22, "bold"),
            text_color=_BRANCO,
        ).place(relx=0.5, rely=0.5, anchor="center")

        name_col = ctk.CTkFrame(logo_frame, fg_color="transparent")
        name_col.pack(side="left", padx=(12, 0))

        ctk.CTkLabel(
            name_col, text="SECTOR",
            font=("Segoe UI", 18, "bold"),
            text_color=_BRANCO,
        ).pack(anchor="w")

        ctk.CTkLabel(
            name_col, text="Automation Platform",
            font=("Segoe UI", 10),
            text_color=_TEXT_SECTION,
        ).pack(anchor="w")

        self._divider(self.sidebar)

        scroll = ctk.CTkScrollableFrame(
            self.sidebar, fg_color="transparent",
            scrollbar_button_color=_AZUL_PRIMARY,
            scrollbar_button_hover_color=_AZUL_ACCENT,
        )
        scroll.pack(fill="both", expand=True, pady=(8, 0))

        for grupo, itens in _GRUPOS:
            ctk.CTkLabel(
                scroll, text=grupo,
                font=("Segoe UI", 10, "bold"),
                text_color=_TEXT_SECTION,
                anchor="w",
            ).pack(anchor="w", padx=20, pady=(20, 8))

            for icon, label, tela, _ in itens:
                item = NavItem(
                    scroll, icon, label,
                    command=lambda t=tela, l=label: self._abrir(t, l),
                )
                self.nav_items.append((label, item))

            ctk.CTkFrame(scroll, height=1, fg_color=_SIDEBAR_ITEM).pack(
                fill="x", padx=18, pady=(12, 0)
            )

        self._build_sidebar_footer()

    def _divider(self, parent, padx=20, pady=12):
        ctk.CTkFrame(
            parent, height=1,
            fg_color=_SIDEBAR_ITEM, corner_radius=0,
        ).pack(fill="x", padx=padx, pady=pady)

    def _build_sidebar_footer(self):
        footer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        footer.pack(fill="x", side="bottom", pady=(0, 20))

        self._divider(footer, padx=18, pady=(0, 16))

        card = ctk.CTkFrame(footer, fg_color=_SIDEBAR_ITEM, corner_radius=12)
        card.pack(fill="x", padx=16)

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=12)

        # Avatar com iniciais
        initials = self.usuario[0].upper()
        av = ctk.CTkFrame(row, width=40, height=40, corner_radius=10,
                          fg_color=_AZUL_PRIMARY)
        av.pack(side="left")
        av.pack_propagate(False)
        ctk.CTkLabel(
            av, text=initials,
            font=("Segoe UI", 16, "bold"),
            text_color=_BRANCO,
        ).place(relx=0.5, rely=0.5, anchor="center")

        info = ctk.CTkFrame(row, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True, padx=(12, 0))

        ctk.CTkLabel(
            info, text=self.usuario,
            font=("Segoe UI", 12, "bold"),
            text_color=_BRANCO, anchor="w",
        ).pack(fill="x")

        ctk.CTkLabel(
            info, text=self.perfil.upper(),
            font=("Segoe UI", 9),
            text_color=_TEXT_SIDEBAR, anchor="w",
        ).pack(fill="x", pady=(2, 0))

        ctk.CTkButton(
            row, text="Sair", width=56, height=32, corner_radius=8,
            font=("Segoe UI", 11, "bold"),
            fg_color=_DANGER, hover_color=_DANGER_DK,
            text_color=_BRANCO,
            command=self.sair,
        ).pack(side="right")

    # ── Topbar ───────────────────────────────────────────────────────────────
    def _build_topbar(self):
        bar = ctk.CTkFrame(
            self.right, height=70,
            fg_color=_HEADER_BG, corner_radius=0,
        )
        bar.grid(row=0, column=0, sticky="ew")
        bar.grid_propagate(False)

        # Linha separadora sutil
        ctk.CTkFrame(bar, height=1, fg_color=_CARD_BORDER, corner_radius=0).place(
            relx=0, rely=1.0, relwidth=1, anchor="sw"
        )

        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=32)

        # Esquerda
        left = ctk.CTkFrame(inner, fg_color="transparent")
        left.pack(side="left", fill="y")

        self.lbl_titulo = ctk.CTkLabel(
            left, text="Consulta",
            font=("Segoe UI", 22, "bold"),
            text_color=_CINZA_TEXTO,
        )
        self.lbl_titulo.pack(anchor="w")

        self.lbl_bread = ctk.CTkLabel(
            left, text="Sistema / Consulta",
            font=("Segoe UI", 12),
            text_color=_CINZA_MEDIO,
        )
        self.lbl_bread.pack(anchor="w", pady=(2, 0))

        # Direita
        right = ctk.CTkFrame(inner, fg_color="transparent")
        right.pack(side="right", fill="y")

        self.lbl_clock = ctk.CTkLabel(
            right, text="",
            font=("Segoe UI", 12),
            text_color=_CINZA_MEDIO,
        )
        self.lbl_clock.pack(side="left", padx=(0, 20))

        # Badge Online com design moderno
        status_pill = ctk.CTkFrame(right, fg_color=_AZUL_LIGHT, corner_radius=20)
        status_pill.pack(side="left")

        ctk.CTkFrame(
            status_pill, width=8, height=8, corner_radius=4,
            fg_color=_VERDE_STATUS,
        ).pack(side="left", padx=(10, 6), pady=6)

        ctk.CTkLabel(
            status_pill, text="Online",
            font=("Segoe UI", 11, "bold"),
            text_color=_AZUL_PRIMARY,
        ).pack(side="left", padx=(0, 12), pady=6)

        self._tick()

    def _tick(self):
        self.lbl_clock.configure(text=datetime.now().strftime("%d/%m/%Y • %H:%M"))
        self.after(1000, self._tick)

    # ── Navegação ────────────────────────────────────────────────────────────
    def _abrir(self, tela_class, titulo: str):
        if self.carregando:
            return
        self.carregando = True

        for label, item in self.nav_items:
            item.set_active(label == titulo)

        self.lbl_titulo.configure(text=titulo)
        self.lbl_bread.configure(text=f"Sistema  /  {titulo}")

        for w in self.main.winfo_children():
            w.destroy()
        self.tela_atual = None

        threading.Thread(
            target=self._load, args=(tela_class, titulo), daemon=True
        ).start()

    def _load(self, tela_class, titulo: str):
        try:
            params = list(inspect.signature(tela_class.__init__).parameters)
            if "conectar_bd" in params:
                self.tela_atual = tela_class(
                    self.main, self.usuario, conectar_bd=self.conectar_bd)
            else:
                self.tela_atual = tela_class(self.main, self.usuario)
            self.after(0, self._show)
        except Exception as exc:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro ao carregar", f"{titulo}:\n{exc}")
            self.carregando = False

    def _show(self):
        try:
            if self.tela_atual:
                self.tela_atual.pack(fill="both", expand=True, padx=8, pady=8)
        finally:
            self.carregando = False

    # ── Sair ─────────────────────────────────────────────────────────────────
    def sair(self):
        if messagebox.askyesno("Sair", "Deseja encerrar a sessão?"):
            self.destroy()