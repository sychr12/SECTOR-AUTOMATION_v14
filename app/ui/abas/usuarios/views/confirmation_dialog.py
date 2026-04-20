# -*- coding: utf-8 -*-
"""
ConfirmationDialog — popup modal de confirmação com suporte a tipos de alerta.
Versão PyQt6.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

_VERDE   = "#22c55e"
_VERDE_H = "#16a34a"
_VERM    = "#ef4444"
_VERM_H  = "#dc2626"
_MUTED   = "#64748b"
_BRANCO  = "#ffffff"
_CINZA_BG = "#f5f7fc"
_CINZA_BORDER = "#e2e8f0"


class ConfirmationDialog(QDialog):
    """Popup modal de confirmação."""

    def __init__(self, parent=None, titulo: str = "", mensagem: str = "",
                 type: str = "question", **kwargs):
        super().__init__(parent, **kwargs)
        self.setWindowTitle(titulo)
        self.setModal(True)
        self.setFixedSize(440, 230)
        self.setStyleSheet(f"background-color: {_CINZA_BG};")
        
        self._resultado = False
        self._build(titulo, mensagem, type)
        self._centralizar()

    def _centralizar(self):
        screen = self.screen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def _build(self, titulo, mensagem, type):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        icone = {"question": "❓", "warning": "⚠️",
                 "error": "❌", "info": "ℹ️"}.get(type, "❓")

        titulo_label = QLabel(f"{icone}  {titulo}")
        titulo_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        titulo_label.setStyleSheet("color: #1e2f3e;")
        layout.addWidget(titulo_label)

        msg_label = QLabel(mensagem)
        msg_label.setFont(QFont("Segoe UI", 12))
        msg_label.setStyleSheet(f"color: {_MUTED};")
        msg_label.setWordWrap(True)
        layout.addWidget(msg_label)

        layout.addStretch()

        # Botões
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        cor = _VERM if type in ("warning", "error") else _VERDE
        cor_h = _VERM_H if type in ("warning", "error") else _VERDE_H

        btn_confirmar = QPushButton("Confirmar")
        btn_confirmar.setFixedHeight(42)
        btn_confirmar.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        btn_confirmar.setStyleSheet(f"""
            QPushButton {{
                background-color: {cor};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: {cor_h};
            }}
        """)
        btn_confirmar.clicked.connect(self._confirmar)
        btn_layout.addWidget(btn_confirmar)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setFixedHeight(42)
        btn_cancelar.setFont(QFont("Segoe UI", 12))
        btn_cancelar.setStyleSheet(f"""
            QPushButton {{
                background-color: {_BRANCO};
                color: #1e2f3e;
                border: 1px solid {_CINZA_BORDER};
                border-radius: 10px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: {_CINZA_BORDER};
            }}
        """)
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancelar)

        layout.addLayout(btn_layout)

    def _confirmar(self):
        self._resultado = True
        self.accept()

    def show(self) -> bool:
        return self.exec() == QDialog.DialogCode.Accepted and self._resultado