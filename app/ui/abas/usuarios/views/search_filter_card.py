# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QComboBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

_VERDE = "#22c55e"
_VERDE_H = "#16a34a"
_BRANCO = "#ffffff"
_CINZA_BORDER = "#e2e8f0"
_CINZA_TEXTO = "#1e2f3e"
_MUTED = "#64748b"


class SearchFilterCard(QFrame):
    """Card de busca e filtros."""

    def __init__(self, on_search=None, on_new_user=None, parent=None):
        super().__init__(parent)
        self._on_search = on_search
        self._on_new_user = on_new_user
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {_BRANCO};
                border-radius: 16px;
                border: 1px solid {_CINZA_BORDER};
            }}
        """)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # Título
        title = QLabel("🔍 Buscar e Filtrar Usuários")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {_CINZA_TEXTO};")
        layout.addWidget(title)

        # Linha de busca
        search_row = QHBoxLayout()
        search_row.setSpacing(8)

        lbl_busca = QLabel("Buscar:")
        lbl_busca.setFont(QFont("Segoe UI", 12))
        lbl_busca.setStyleSheet(f"color: {_MUTED};")
        search_row.addWidget(lbl_busca)

        self._entry_search = QLineEdit()
        self._entry_search.setPlaceholderText("Digite o nome de usuário...")
        self._entry_search.setFixedHeight(40)
        self._entry_search.setStyleSheet(f"""
            QLineEdit {{
                background-color: {_BRANCO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 10px;
                padding: 8px 12px;
                font-size: 12px;
            }}
            QLineEdit:focus {{
                border: 2px solid #2c6e9e;
            }}
        """)
        self._entry_search.returnPressed.connect(self._on_search_callback)
        search_row.addWidget(self._entry_search, 1)

        if self._on_search:
            btn_buscar = QPushButton("🔍 Buscar")
            btn_buscar.setFixedSize(100, 40)
            btn_buscar.setStyleSheet(f"""
                QPushButton {{
                    background-color: #2c6e9e;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #1e4a6e;
                }}
            """)
            btn_buscar.clicked.connect(self._on_search)
            search_row.addWidget(btn_buscar)

        layout.addLayout(search_row)

        # Filtros
        filters_row = QHBoxLayout()
        filters_row.setSpacing(16)

        # Perfil
        lbl_perfil = QLabel("Perfil:")
        lbl_perfil.setFont(QFont("Segoe UI", 12))
        lbl_perfil.setStyleSheet(f"color: {_MUTED};")
        filters_row.addWidget(lbl_perfil)

        self._combo_profile = QComboBox()
        self._combo_profile.addItems(["Todos", "administrador", "chefe", "usuario"])
        self._combo_profile.setFixedSize(150, 40)
        self._combo_profile.setStyleSheet(f"""
            QComboBox {{
                background-color: {_BRANCO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 10px;
                padding: 5px 10px;
            }}
        """)
        self._combo_profile.currentTextChanged.connect(self._on_search_callback)
        filters_row.addWidget(self._combo_profile)

        # Status
        lbl_status = QLabel("Status:")
        lbl_status.setFont(QFont("Segoe UI", 12))
        lbl_status.setStyleSheet(f"color: {_MUTED};")
        filters_row.addWidget(lbl_status)

        self._combo_status = QComboBox()
        self._combo_status.addItems(["Todos", "Ativo", "Inativo"])
        self._combo_status.setFixedSize(120, 40)
        self._combo_status.setStyleSheet(f"""
            QComboBox {{
                background-color: {_BRANCO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 10px;
                padding: 5px 10px;
            }}
        """)
        self._combo_status.currentTextChanged.connect(self._on_search_callback)
        filters_row.addWidget(self._combo_status)

        filters_row.addStretch()

        if self._on_new_user:
            btn_novo = QPushButton("➕ Novo Usuário")
            btn_novo.setFixedHeight(40)
            btn_novo.setStyleSheet(f"""
                QPushButton {{
                    background-color: {_VERDE};
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-weight: bold;
                    padding: 8px 20px;
                }}
                QPushButton:hover {{
                    background-color: {_VERDE_H};
                }}
            """)
            btn_novo.clicked.connect(self._on_new_user)
            filters_row.addWidget(btn_novo)

        layout.addLayout(filters_row)

    def _on_search_callback(self):
        if self._on_search:
            self._on_search()

    def get_search_text(self) -> str:
        return self._entry_search.text().strip()

    def get_selected_profile(self) -> str:
        return self._combo_profile.currentText()

    def get_selected_status(self) -> str:
        return self._combo_status.currentText()