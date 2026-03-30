import os
import sys
import customtkinter as ctk
from app.theme import AppTheme
from tkinter import messagebox


class BaseUI(ctk.CTkFrame):
    """
    Classe base para TODAS as abas do sistema.

    Responsabilidades:
    - Resolver diretório raiz do projeto
    - Padronizar layout, cores e fontes
    - Fornecer helpers reutilizáveis de UI
    - Centralizar mensagens e alertas

    IMPORTANTE:
    - NÃO faz pack/grid/place
    - Quem controla layout é o AppPrincipal
    """

    def __init__(self, master):
        super().__init__(master)

        self.BASE_DIR = self._resolver_base_dir()

        # Configuração visual padrão da aba
        self.configure(fg_color=AppTheme.BG_APP)

        # Padronização de layout interno
        self._configurar_grid()

        # Definir estilos padrão locais (fonte e espaçamento)
        self._padx = AppTheme.PADDING_MEDIUM
        self._pady = AppTheme.PADDING_MEDIUM

    # ========================= LAYOUT BASE =========================

    def _configurar_grid(self):
        """
        Define um grid padrão para todas as abas.
        Evita uso misto e desorganizado de pack/grid.
        """
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

    # ========================= BASE DIR =========================

    def _resolver_base_dir(self):
        """
        Retorna o diretório raiz do projeto de forma segura.

        Funciona para:
        - Execução normal (python)
        - Execução empacotada (PyInstaller)
        """
        if getattr(sys, "frozen", False):
            return sys._MEIPASS

        return os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..")
        )

    # ========================= UI HELPERS =========================

    def titulo(self, texto, row=0):
        """
        Título padrão da aba.
        """
        label = ctk.CTkLabel(
            self,
            text=texto,
            font=AppTheme.FONT_TITLE,
            text_color=AppTheme.BTN_SUCCESS
        )
        label.grid(row=row, column=0, sticky="w", padx=self._padx, pady=(AppTheme.PADDING_LARGE, AppTheme.PADDING_SMALL))
        return label

    def subtitulo(self, texto, row=1):
        """
        Subtítulo padrão da aba.
        """
        label = ctk.CTkLabel(
            self,
            text=texto,
            font=AppTheme.FONT_SUBTITLE,
            text_color=AppTheme.TXT_DARK
        )
        label.grid(row=row, column=0, sticky="w", padx=self._padx, pady=(0, AppTheme.PADDING_LARGE))
        return label

    def botao(
        self,
        texto,
        comando,
        width=200,
        height=44,
        fg_color=AppTheme.BTN_SUCCESS,
        hover_color=AppTheme.BTN_SUCCESS_HOVER,
        text_color=AppTheme.TXT_MAIN
    ):
        """
        Botão padrão do sistema.
        """
        return ctk.CTkButton(
            self,
            text=texto,
            command=comando,
            width=width,
            height=height,
            fg_color=fg_color,
            hover_color=hover_color,
            text_color=text_color,
            font=(AppTheme.FONT_FAMILY, 15, "bold"),
            corner_radius=AppTheme.RADIUS_MEDIUM
        )

    def card(self, parent=None, width=900, height=500):
        """
        Cria um container/card padrão.
        NÃO faz pack/grid automaticamente.
        """
        container = parent if parent else self

        frame = ctk.CTkFrame(
            container,
            width=width,
            height=height,
            fg_color=AppTheme.BG_CARD,
            corner_radius=AppTheme.RADIUS_LARGE
        )
        frame.grid_propagate(False)
        return frame

    # ========================= UTIL =========================

    def caminho(self, *partes):
        """
        Resolve caminhos sempre relativos ao projeto.
        """
        return os.path.join(self.BASE_DIR, *partes)

    # ========================= MENSAGENS =========================

    def alerta(self, texto, titulo="Atenção"):
        messagebox.showwarning(titulo, texto)

    def erro(self, texto, titulo="Erro"):
        messagebox.showerror(titulo, texto)

    def sucesso(self, texto, titulo="Sucesso"):
        messagebox.showinfo(titulo, texto)

    def confirmar(self, texto, titulo="Confirmação"):
        return messagebox.askyesno(titulo, texto)
# --- END OF FILE ---