# -*- coding: utf-8 -*-
import customtkinter as ctk
from tkinter import messagebox
import inspect
import sys
import os
import threading
from datetime import datetime
from PIL import Image

current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(current_dir)
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from theme import apply_theme, AppTheme
from ui.abas.Consultar   import ConsultarUI
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
_AZUL_PRIMARY   = "#2c5f8a"
_AZUL_DARK      = "#1e3a5f"
_AZUL_LIGHT     = "#e8f0f7"
_AZUL_ACCENT    = "#3b82f6"
_AZUL_HOVER     = "#e0eef9"
_SIDEBAR_BG     = "#1a2c3e"
_SIDEBAR_ITEM   = "#2a3f54"
_SIDEBAR_ATIV   = "#2c5f8a"
_BRANCO         = "#ffffff"
_CINZA_BG       = "#f8fafc"
_CINZA_BORDER   = "#e2e8f0"
_CINZA_MEDIO    = "#64748b"
_CINZA_TEXTO    = "#1e293b"
_VERDE_STATUS   = "#10b981"
_VERDE_HOVER    = "#d1fae5"
_DANGER         = "#ef4444"
_DANGER_DK      = "#dc2626"
_TEXT_SIDEBAR   = "#cbd5e1"
_TEXT_SECTION   = "#60a5fa"
_TEXT_MUTED     = "#64748b"
_CARD_BORDER    = "#e2e8f0"
_HEADER_BG      = "#ffffff"

# Caminho dos ícones
ICONS_DIR = r"images\icons\sidebar"


def carregar_icone(nome_arquivo, size=(20, 20)):
    """Carrega ícone PNG da pasta images/icons/sidebar"""
    try:
        path = os.path.join(ICONS_DIR, nome_arquivo)
        if os.path.exists(path):
            img = Image.open(path)
            img = img.resize(size, Image.Resampling.LANCZOS)
            return ctk.CTkImage(light_image=img, dark_image=img, size=size)
        else:
            print(f"[Menu] Ícone não encontrado: {path}")
    except Exception as e:
        print(f"[Menu] Erro ao carregar ícone {nome_arquivo}: {e}")
    return None


# Ícones para cada menu (nomes dos arquivos que você tem na pasta)
ICONES_MENU = {
    "Consulta": carregar_icone("consulta.png", (20, 20)),
    "Análises": carregar_icone("analise.png", (20, 20)),
    "E-mails": carregar_icone("email.png", (20, 20)),
    "Lançamento": carregar_icone("lancamento.png", (20, 20)),
    "Carteira": carregar_icone("carteira.png", (20, 20)),
    "Memorando": carregar_icone("memorando.png", (20, 20)),
    "Anexar": carregar_icone("anexo.png", (20, 20)),
    "Relatórios": carregar_icone("relatorio.png", (20, 20)),
    "Senha": carregar_icone("senha.png", (20, 20)),
}
# Grupos de navegação com nomes de ícones
_GRUPOS = [
    ("CONSULTAS", [
        ("consulta", "Consulta",      ConsultarUI,      "Consultas avançadas"),
    ]),
    ("OPERAÇÕES", [
        ("email",     "E-mails",       BaixarEmailUI,    "Gerenciar emails"),
        ("lancamento","Lançamento",    LancamentoUI,     "Novos lançamentos"),
        ("carteira",  "Carteira",      CarteiraDigitalUI,"Gestão financeira"),
    ]),
    ("DOCUMENTOS", [
        ("memorando", "Memorando",     MemorandoUI,      "Documentos internos"),
        ("anexo",     "Anexar",        AnexarUI,         "Gerenciar anexos"),
        ("relatorio", "Relatórios",    RelatoriosUI,     "Gerar relatórios"),
    ]),
    ("SISTEMA", [
        ("seguranca", "Senha",         SenhaUI,          "Alterar senha"),
    ]),
]

SIDEBAR_W = 280


# ── Item de navegação com ícone PNG ────────────────────────────────────────────
class NavItem(ctk.CTkFrame):
    def __init__(self, parent, icon_name: str, label: str, command, is_active=False):
        super().__init__(parent, fg_color="transparent", height=44)
        self.pack(fill="x", padx=12, pady=2)
        self.pack_propagate(False)

        self._cmd    = command
        self._active = is_active
        self._icon_img = ICONES_MENU.get(label)

        self._indicator = ctk.CTkFrame(
            self, width=3,
            fg_color=_AZUL_ACCENT if is_active else "transparent",
            corner_radius=2,
        )
        self._indicator.pack(side="left", fill="y")

        self._bg = ctk.CTkFrame(
            self,
            fg_color=_SIDEBAR_ATIV if is_active else "transparent",
            corner_radius=8,
        )
        self._bg.pack(side="left", fill="both", expand=True, padx=(6, 0))

        if self._icon_img:
            self._icon = ctk.CTkLabel(
                self._bg, text="",
                image=self._icon_img,
                width=28,
            )
        else:
            icon_emoji = {
                "Consulta": "🔍", "Banco Antigo": "🗄️", "Análises": "📈",
                "E-mails": "📥", "Lançamento": "📋", "Carteira": "💳",
                "Memorando": "📄", "Anexar": "📎", "Relatórios": "📊",
                "Senha": "🔒",
            }.get(label, "📄")
            self._icon = ctk.CTkLabel(
                self._bg, text=icon_emoji,
                font=("Segoe UI", 15),
                text_color=_BRANCO if is_active else _TEXT_SIDEBAR,
                width=32,
            )
        self._icon.pack(side="left", padx=(12, 8))

        self._text = ctk.CTkLabel(
            self._bg, text=label,
            font=("Segoe UI", 12, "bold" if is_active else "normal"),
            text_color=_BRANCO if is_active else _TEXT_SIDEBAR,
            anchor="w",
        )
        self._text.pack(side="left", fill="x", expand=True)

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
            if self._icon_img:
                self._icon.configure(text="")
            else:
                self._icon.configure(text_color=_BRANCO)
            self._text.configure(text_color=_BRANCO, font=("Segoe UI", 12, "bold"))
            self._dot.configure(fg_color=_AZUL_ACCENT)
        else:
            self._indicator.configure(fg_color="transparent")
            self._bg.configure(fg_color="transparent")
            if self._icon_img:
                self._icon.configure(text="")
            else:
                self._icon.configure(text_color=_TEXT_SIDEBAR)
            self._text.configure(text_color=_TEXT_SIDEBAR,
                                 font=("Segoe UI", 12, "normal"))
            self._dot.configure(fg_color="transparent")

    def _enter(self, _=None):
        if not self._active:
            self._bg.configure(fg_color=_SIDEBAR_ITEM)
            if not self._icon_img:
                self._icon.configure(text_color=_BRANCO)
            self._text.configure(text_color=_BRANCO)

    def _leave(self, _=None):
        if not self._active:
            self._bg.configure(fg_color="transparent")
            if not self._icon_img:
                self._icon.configure(text_color=_TEXT_SIDEBAR)
            self._text.configure(text_color=_TEXT_SIDEBAR)

    def _click(self, _=None):
        if self._cmd:
            self._cmd()


# ── Janela principal ─────────────────────────────────────────────────────────
class AppPrincipal(ctk.CTkToplevel):

    def __init__(self, usuario_dados, master=None, on_logout=None):
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
        self.on_logout = on_logout
        self.tela_atual = None
        self.nav_items: list[tuple[str, NavItem]] = []
        self.carregando = False

        self._build()
        self._abrir(ConsultarUI, "Consulta")

    def conectar_bd(self):
        try:
            return get_connection()
        except Exception as exc:
            messagebox.showerror("Conexão", str(exc))
            return None

    def _build(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

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

        self.main = ctk.CTkFrame(
            wrap,
            fg_color=_BRANCO,
            corner_radius=12,
            border_width=1,
            border_color=_CARD_BORDER,
        )
        self.main.grid(row=0, column=0, sticky="nsew")

    def _build_sidebar(self):
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=80)
        logo_frame.pack(fill="x", padx=20, pady=(24, 0))
        logo_frame.pack_propagate(False)

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

            for icon_name, label, tela, _ in itens:
                item = NavItem(
                    scroll, icon_name, label,
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

    def _build_topbar(self):
        bar = ctk.CTkFrame(
            self.right, height=70,
            fg_color=_HEADER_BG, corner_radius=0,
        )
        bar.grid(row=0, column=0, sticky="ew")
        bar.grid_propagate(False)

        ctk.CTkFrame(bar, height=1, fg_color=_CARD_BORDER, corner_radius=0).place(
            relx=0, rely=1.0, relwidth=1, anchor="sw"
        )

        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=32)

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

        right = ctk.CTkFrame(inner, fg_color="transparent")
        right.pack(side="right", fill="y")

        self.lbl_clock = ctk.CTkLabel(
            right, text="",
            font=("Segoe UI", 12),
            text_color=_CINZA_MEDIO,
        )
        self.lbl_clock.pack(side="left", padx=(0, 20))

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

    def _abrir(self, tela_class, titulo: str):
        if self.carregando:
            return
        self.carregando = True

        for label, item in self.nav_items:
            item.set_active(label == titulo)

        self.lbl_titulo.configure(text=titulo)
        self.lbl_bread.configure(text=f"Sistema  /  {titulo}")

        for w in self.main.winfo_children():
            try:
                w.destroy()
            except Exception:
                pass

        self.tela_atual = None
        self.after(10, lambda: self._load(tela_class, titulo))

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

    def sair(self):
        if messagebox.askyesno("Sair", "Deseja encerrar a sessão?"):
            callback = getattr(self, "on_logout", None)
            self.destroy()
            if callable(callback):
                callback()