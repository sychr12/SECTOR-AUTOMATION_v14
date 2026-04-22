# -*- coding: utf-8 -*-
"""
UserListCard — container scrollável com cabeçalho de colunas e estados de UI.
Versão PyQt6.
"""

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

_VERM = "#ef4444"
_MUTED = "#64748b"
_BRANCO = "#ffffff"
_CINZA_BORDER = "#e2e8f0"

_COLUNAS = [
    ("👤 Usuário", 130),
    ("🧑🏻 Perfil", 110),
    ("📧 Email", 210),
    ("📅 Último Acesso", 160),
    ("🔄 Status", 110),
    ("⚙️ Ações", 120),
]


class UserListCard(QFrame):
    """Container scrollável para lista de usuários."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._user_actions_disabled = set()
        
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
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # Cabeçalho de colunas
        header = QFrame()
        header.setFixedHeight(50)
        header.setStyleSheet(f"""
            QFrame {{
                background-color: #f1f5f9;
                border-radius: 12px;
            }}
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 0, 16, 0)
        
        for titulo, largura in _COLUNAS:
            col = QFrame()
            col.setFixedWidth(largura)
            lbl = QLabel(titulo)
            lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            lbl.setStyleSheet("color: #1e2f3e;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            col_layout = QVBoxLayout(col)
            col_layout.setContentsMargins(8, 0, 0, 0)
            col_layout.addWidget(lbl)
            header_layout.addWidget(col)
        
        layout.addWidget(header)

        # Área scrollável
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        self._scroll_content = QWidget()
        self._scroll_layout = QVBoxLayout(self._scroll_content)
        self._scroll_layout.setContentsMargins(0, 0, 0, 0)
        self._scroll_layout.setSpacing(4)
        self._scroll_layout.addStretch()
        
        self._scroll_area.setWidget(self._scroll_content)
        layout.addWidget(self._scroll_area)

    def clear_users(self):
        """Remove todos os usuários da lista."""
        while self._scroll_layout.count() > 1:
            item = self._scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def show_loading(self):
        """Mostra indicador de carregamento."""
        self.clear_users()
        lbl = QLabel("⏳ Carregando usuários...")
        lbl.setFont(QFont("Segoe UI", 14))
        lbl.setStyleSheet(f"color: {_MUTED};")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._scroll_layout.insertWidget(0, lbl)

    def show_no_users_message(self, message="Nenhum usuário encontrado."):
        """Mostra mensagem quando não há usuários."""
        self.clear_users()
        lbl = QLabel(f"📭 {message}")
        lbl.setFont(QFont("Segoe UI", 14))
        lbl.setStyleSheet(f"color: {_MUTED};")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._scroll_layout.insertWidget(0, lbl)

    def show_error(self, error_msg: str):
        """Mostra mensagem de erro."""
        self.clear_users()
        lbl_icon = QLabel("❌")
        lbl_icon.setFont(QFont("Segoe UI", 32))
        lbl_icon.setStyleSheet(f"color: {_VERM};")
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._scroll_layout.insertWidget(0, lbl_icon)
        
        lbl_msg = QLabel(f"Erro ao carregar:\n{error_msg}")
        lbl_msg.setFont(QFont("Segoe UI", 12))
        lbl_msg.setStyleSheet(f"color: {_VERM};")
        lbl_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._scroll_layout.insertWidget(1, lbl_msg)

    def add_user_card(self, user_data: dict, on_select, on_delete):
        """Adiciona um card de usuário à lista."""
        from .user_card import UserCard
        card = UserCard(user_data, on_select, on_delete)
        self._scroll_layout.insertWidget(self._scroll_layout.count() - 1, card)
        
        if user_data.get("username") in self._user_actions_disabled:
            card.disable_actions()

    def disable_user_actions(self, username: str):
        """Desabilita ações para um usuário específico."""
        self._user_actions_disabled.add(username)
        for i in range(self._scroll_layout.count()):
            widget = self._scroll_layout.itemAt(i).widget()
            if widget and hasattr(widget, "user_data") and widget.user_data.get("username") == username:
                widget.disable_actions()

    def enable_user_actions(self, username: str):
        """Reabilita ações para um usuário específico."""
        self._user_actions_disabled.discard(username)
        for i in range(self._scroll_layout.count()):
            widget = self._scroll_layout.itemAt(i).widget()
            if widget and hasattr(widget, "user_data") and widget.user_data.get("username") == username:
                widget.enable_actions()