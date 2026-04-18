import os
import sys

from PyQt6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QMessageBox,
)
from PyQt6.QtCore import Qt

from app.theme import AppTheme


class BaseUI(QFrame):
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

    def __init__(self, master=None):
        super().__init__(master)

        self.BASE_DIR = self._resolver_base_dir()

        # Configuração visual padrão da aba
        self.setStyleSheet(f"background-color: {AppTheme.BG_APP}; border: none;")

        # Definir estilos padrão locais (fonte e espaçamento)
        self._padx = AppTheme.PADDING_MEDIUM
        self._pady = AppTheme.PADDING_MEDIUM

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
        label = QLabel(texto, self)
        font_family = getattr(AppTheme, "FONT_FAMILY", "Segoe UI")

        label.setStyleSheet(f"""
            QLabel {{
                color: {AppTheme.BTN_SUCCESS};
                font-family: {font_family};
                font-size: 24px;
                font-weight: 700;
                background: transparent;
                border: none;
            }}
        """)
        return label

    def subtitulo(self, texto, row=1):
        """
        Subtítulo padrão da aba.
        """
        label = QLabel(texto, self)
        font_family = getattr(AppTheme, "FONT_FAMILY", "Segoe UI")

        label.setStyleSheet(f"""
            QLabel {{
                color: {AppTheme.TXT_DARK};
                font-family: {font_family};
                font-size: 16px;
                font-weight: 500;
                background: transparent;
                border: none;
            }}
        """)
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
        btn = QPushButton(texto, self)
        font_family = getattr(AppTheme, "FONT_FAMILY", "Segoe UI")

        btn.setMinimumSize(width, height)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {fg_color};
                color: {text_color};
                border: none;
                border-radius: {AppTheme.RADIUS_MEDIUM}px;
                font-family: {font_family};
                font-size: 15px;
                font-weight: 700;
                padding: 0 14px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """)
        btn.clicked.connect(comando)
        return btn

    def card(self, parent=None, width=900, height=500):
        """
        Cria um container/card padrão.
        NÃO faz pack/grid automaticamente.
        """
        container = parent if parent else self

        frame = QFrame(container)
        frame.setMinimumSize(width, height)
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {AppTheme.BG_CARD};
                border: none;
                border-radius: {AppTheme.RADIUS_LARGE}px;
            }}
        """)
        return frame

    # ========================= UTIL =========================

    def caminho(self, *partes):
        """
        Resolve caminhos sempre relativos ao projeto.
        """
        return os.path.join(self.BASE_DIR, *partes)

    # ========================= MENSAGENS =========================

    def alerta(self, texto, titulo="Atenção"):
        QMessageBox.warning(self, titulo, texto)

    def erro(self, texto, titulo="Erro"):
        QMessageBox.critical(self, titulo, texto)

    def sucesso(self, texto, titulo="Sucesso"):
        QMessageBox.information(self, titulo, texto)

    def confirmar(self, texto, titulo="Confirmação"):
        resposta = QMessageBox.question(
            self,
            titulo,
            texto,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        return resposta == QMessageBox.StandardButton.Yes