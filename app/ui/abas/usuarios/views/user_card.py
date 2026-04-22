# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

_VERDE = "#22c55e"
_AZUL = "#3b82f6"
_AZUL_H = "#2563eb"
_VERM = "#ef4444"
_VERM_H = "#b91c1c"
_AMBER = "#f59e0b"
_CYAN = "#06b6d4"
_PURPLE = "#8b5cf6"
_MUTED = "#64748b"
_BRANCO = "#ffffff"
_CINZA_BORDER = "#e2e8f0"

_PERFIL_CORES = {
    "administrador": _PURPLE,
    "chefe": _AMBER,
    "usuario": _CYAN,
}
_PERFIL_ICONS = {
    "administrador": "👑",
    "chefe": "⭐",
    "usuario": "👤",
}


class UserCard(QFrame):
    """Card de usuário compacto."""

    def __init__(self, user_data: dict, on_select=None, on_delete=None, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.on_select = on_select
        self.on_delete = on_delete
        self._disabled = False

        self.setFixedHeight(52)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {_BRANCO};
                border-radius: 8px;
                border: 1px solid {_CINZA_BORDER};
            }}
            QFrame:hover {{
                border-color: {_AZUL};
                background-color: #f8fafc;
            }}
        """)

        self._build()

    def _build(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)

        # Usuário
        username = self.user_data.get('username', '?')
        lbl_user = QLabel(f"👤 {username}")
        lbl_user.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        lbl_user.setFixedWidth(130)
        layout.addWidget(lbl_user)

        # Perfil badge
        perfil = self.user_data.get("perfil", "").lower()
        cor = _PERFIL_CORES.get(perfil, _MUTED)
        icon = _PERFIL_ICONS.get(perfil, "👤")
        
        badge = QFrame()
        badge.setFixedSize(110, 26)
        badge.setStyleSheet(f"""
            QFrame {{
                background-color: {cor};
                border-radius: 6px;
            }}
        """)
        badge_layout = QHBoxLayout(badge)
        badge_layout.setContentsMargins(8, 0, 8, 0)
        lbl_badge = QLabel(f"{icon} {perfil.upper()}" if perfil else "N/A")
        lbl_badge.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        lbl_badge.setStyleSheet("color: white;")
        lbl_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge_layout.addWidget(lbl_badge)
        layout.addWidget(badge)

        # Email
        email = self.user_data.get("email") or "—"
        lbl_email = QLabel(email)
        lbl_email.setFont(QFont("Segoe UI", 11))
        lbl_email.setStyleSheet(f"color: {_MUTED};")
        lbl_email.setFixedWidth(210)
        layout.addWidget(lbl_email)

        # Último acesso
        ultimo = self.user_data.get('ultimo_acesso_fmt', 'Nunca')
        lbl_acesso = QLabel(f"🕐 {ultimo}")
        lbl_acesso.setFont(QFont("Segoe UI", 10))
        lbl_acesso.setStyleSheet(f"color: {_MUTED};")
        lbl_acesso.setFixedWidth(160)
        layout.addWidget(lbl_acesso)

        # Status
        ativo = self.user_data.get("ativo", False)
        status_text = "🟢 Ativo" if ativo else "🔴 Inativo"
        status_color = _VERDE if ativo else _VERM
        lbl_status = QLabel(status_text)
        lbl_status.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        lbl_status.setStyleSheet(f"color: {status_color};")
        lbl_status.setFixedWidth(110)
        layout.addWidget(lbl_status)

        # Botões
        btn_edit = QPushButton("✏️")
        btn_edit.setFixedSize(36, 30)
        btn_edit.setStyleSheet(f"""
            QPushButton {{
                background-color: {_AZUL};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {_AZUL_H};
            }}
        """)
        btn_edit.clicked.connect(self._on_select)
        layout.addWidget(btn_edit)

        btn_del = QPushButton("🗑️")
        btn_del.setFixedSize(36, 30)
        btn_del.setStyleSheet(f"""
            QPushButton {{
                background-color: {_VERM};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {_VERM_H};
            }}
        """)
        btn_del.clicked.connect(self._on_delete)
        layout.addWidget(btn_del)

        self._btn_edit = btn_edit
        self._btn_del = btn_del

    def disable_actions(self):
        self._disabled = True
        self._btn_edit.setEnabled(False)
        self._btn_del.setEnabled(False)

    def enable_actions(self):
        self._disabled = False
        self._btn_edit.setEnabled(True)
        self._btn_del.setEnabled(True)

    def _on_select(self):
        if not self._disabled and self.on_select:
            self.on_select(self.user_data)

    def _on_delete(self):
        if not self._disabled and self.on_delete:
            self.on_delete(self.user_data)