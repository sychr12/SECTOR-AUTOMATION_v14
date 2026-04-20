# -*- coding: utf-8 -*-
"""Componentes reutilizáveis do módulo Anexar - Versão PyQt6."""
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from .theme import VERM, VERM_H, AZUL, AZUL_H, MUTED, SLATE

# Cores padrão do tema (fallback)
BG_INPUT = "#ffffff"
BG_CARD = "#f1f5f9"
BG_APP = "#f8fafc"
TXT_MAIN = "#0f172a"
BTN_PRIMARY = "#2c6e9e"
BTN_PRIMARY_HOVER = "#1e4a6e"


class StatCard(QFrame):
    """Card de estatística com ícone e valor grande."""

    _ICONS = {
        "total": "📊",
        "pendente": "⏳",
        "gerado": "✅",
        "sucesso": "✨",
        "erro": "⚠️",
    }

    def __init__(self, parent=None, titulo="", valor="0", cor=None, icon_key=None):
        super().__init__(parent)
        self._cor = cor or TXT_MAIN

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_INPUT};
                border-radius: 16px;
                border: 1px solid {BG_CARD};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        # Topo com ícone e título
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)

        if icon_key and icon_key in self._ICONS:
            icon_lbl = QLabel(self._ICONS[icon_key])
            icon_lbl.setFont(QFont("Segoe UI", 14))
            icon_lbl.setStyleSheet(f"color: {MUTED};")
            top_layout.addWidget(icon_lbl)

        title_lbl = QLabel(titulo)
        title_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        title_lbl.setStyleSheet(f"color: {MUTED};")
        top_layout.addWidget(title_lbl)
        top_layout.addStretch()

        layout.addLayout(top_layout)

        # Valor
        self._val = QLabel(str(valor))
        self._val.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        self._val.setStyleSheet(f"color: {self._cor};")
        layout.addWidget(self._val)

    def set(self, valor):
        self._val.setText(str(valor))


class CardInfo(QFrame):
    """Card de informação com borda suave e ícone."""

    def __init__(self, parent=None, titulo="", conteudo="", icon="ℹ️"):
        super().__init__(parent)

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_INPUT};
                border-radius: 16px;
                border: 1px solid {BG_CARD};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        # Header com ícone e título
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        icon_lbl = QLabel(icon)
        icon_lbl.setFont(QFont("Segoe UI", 12))
        icon_lbl.setStyleSheet(f"color: {MUTED};")
        header_layout.addWidget(icon_lbl)

        title_lbl = QLabel(titulo)
        title_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        title_lbl.setStyleSheet(f"color: {MUTED};")
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Conteúdo
        self._lbl = QLabel(conteudo)
        self._lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self._lbl.setStyleSheet(f"color: {TXT_MAIN};")
        self._lbl.setWordWrap(True)
        layout.addWidget(self._lbl)

    def set(self, texto: str):
        self._lbl.setText(texto)


class ActionButton(QPushButton):
    """Botão de ação com estilo consistente."""

    def __init__(self, parent=None, text="", command=None, primary=False, danger=False, **kwargs):
        super().__init__(text, parent, **kwargs)

        if primary:
            bg, hover, text_color = BTN_PRIMARY, BTN_PRIMARY_HOVER, "#ffffff"
            font_weight = "bold"
        elif danger:
            bg, hover, text_color = VERM, VERM_H, "#ffffff"
            font_weight = "bold"
        else:
            bg, hover, text_color = BG_INPUT, BG_CARD, TXT_MAIN
            font_weight = "normal"

        self.setFixedHeight(40)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {text_color};
                border: none;
                border-radius: 12px;
                font-family: 'Segoe UI';
                font-size: 12px;
                font-weight: {font_weight};
                padding: 0 16px;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
        """)

        if command:
            self.clicked.connect(command)


class SearchBar(QFrame):
    """Barra de busca estilizada com callback on_search."""

    def __init__(self, parent=None, placeholder="Buscar...", on_search=None):
        super().__init__(parent)
        self._on_search = on_search

        self.setStyleSheet("background-color: transparent;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Container da busca
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_INPUT};
                border-radius: 12px;
                border: 1px solid {BG_CARD};
            }}
        """)

        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(12, 8, 12, 8)
        container_layout.setSpacing(8)

        # Ícone de busca
        icon_lbl = QLabel("🔍")
        icon_lbl.setFont(QFont("Segoe UI", 12))
        icon_lbl.setStyleSheet(f"color: {MUTED};")
        container_layout.addWidget(icon_lbl)

        # Campo de entrada
        self._entry = QLineEdit()
        self._entry.setPlaceholderText(placeholder)
        self._entry.setStyleSheet(f"""
            QLineEdit {{
                background-color: transparent;
                border: none;
                font-family: 'Segoe UI';
                font-size: 11px;
                padding: 4px;
            }}
            QLineEdit:focus {{
                outline: none;
            }}
        """)
        self._entry.returnPressed.connect(self._fire)
        container_layout.addWidget(self._entry, 1)

        # Botão de busca
        if on_search:
            btn_buscar = QPushButton("Buscar")
            btn_buscar.setFixedSize(60, 28)
            btn_buscar.setStyleSheet(f"""
                QPushButton {{
                    background-color: {AZUL};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-family: 'Segoe UI';
                    font-size: 10px;
                }}
                QPushButton:hover {{
                    background-color: {AZUL_H};
                }}
            """)
            btn_buscar.clicked.connect(self._fire)
            container_layout.addWidget(btn_buscar)

        layout.addWidget(container)

    def _fire(self):
        if self._on_search:
            self._on_search(self._entry.text())

    def get(self) -> str:
        return self._entry.text()

    def clear(self):
        self._entry.clear()