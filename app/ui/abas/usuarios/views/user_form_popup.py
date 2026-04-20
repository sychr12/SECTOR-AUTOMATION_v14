# -*- coding: utf-8 -*-
"""UserFormPopup — popup modal para criar ou editar usuário.
Versão PyQt6.
"""

import re
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QComboBox, QPushButton, QCheckBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

_VERDE = "#22c55e"
_VERDE_H = "#16a34a"
_VERM = "#ef4444"
_VERM_H = "#dc2626"
_MUTED = "#64748b"
_BRANCO = "#ffffff"
_CINZA_BORDER = "#e2e8f0"
_CINZA_BG = "#f5f7fc"

PERFIS = ["administrador", "chefe", "usuario"]


def aplicar_mascara_cpf(entry):
    """Aplica máscara CPF (000.000.000-00) em tempo real ao entry."""
    def on_key():
        texto = entry.text()
        apenas_numeros = re.sub(r"\D", "", texto)[:11]
        mascara = ''
        for i, d in enumerate(apenas_numeros):
            if i == 3 or i == 6:
                mascara += '.'
            elif i == 9:
                mascara += '-'
            mascara += d
        entry.blockSignals(True)
        entry.setText(mascara)
        entry.blockSignals(False)
    
    entry.textChanged.connect(on_key)


class UserFormPopup(QDialog):
    """Popup modal para criar/editar usuário."""

    def __init__(self, parent, on_save, on_delete=None, user_data: dict = None):
        super().__init__(parent)
        self._on_save = on_save
        self._on_delete = on_delete
        self._user_data = user_data
        self._is_new = user_data is None

        titulo = "➕ Novo Usuário" if self._is_new else f"✏️ Editando: {user_data.get('username', '')}"
        self.setWindowTitle(titulo)
        self.setModal(True)
        self.setFixedSize(560, 520)
        self.setStyleSheet(f"background-color: {_CINZA_BG};")

        self._build()
        if not self._is_new:
            self._carregar_dados()

        self._centralizar()

    def _centralizar(self):
        screen = self.screen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def _build(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Card
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {_BRANCO};
                border-radius: 16px;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(16)

        # Título
        titulo = "➕ Novo Usuário" if self._is_new else f"✏️ Editando: {self._user_data.get('username', '') if self._user_data else ''}"
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        lbl_titulo.setStyleSheet("color: #1e2f3e;")
        card_layout.addWidget(lbl_titulo)

        # Grid de campos
        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(12)

        # Linha 0: Usuário e Perfil
        lbl_user = QLabel("Usuário *")
        lbl_user.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        lbl_user.setStyleSheet(f"color: {_MUTED};")
        grid.addWidget(lbl_user, 0, 0)
        
        self._e_user = QLineEdit()
        self._e_user.setPlaceholderText("nome.sobrenome")
        self._e_user.setFixedHeight(40)
        self._e_user.setStyleSheet(f"""
            QLineEdit {{
                background-color: {_BRANCO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 10px;
                padding: 8px 12px;
            }}
        """)
        grid.addWidget(self._e_user, 1, 0)

        lbl_perfil = QLabel("Perfil *")
        lbl_perfil.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        lbl_perfil.setStyleSheet(f"color: {_MUTED};")
        grid.addWidget(lbl_perfil, 0, 1)

        self._combo = QComboBox()
        self._combo.addItems(PERFIS)
        self._combo.setFixedHeight(40)
        self._combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {_BRANCO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 10px;
                padding: 5px 10px;
            }}
        """)
        self._combo.setCurrentText("usuario")
        grid.addWidget(self._combo, 1, 1)

        # Linha 1: CPF e Email
        lbl_cpf = QLabel("CPF")
        lbl_cpf.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        lbl_cpf.setStyleSheet(f"color: {_MUTED};")
        grid.addWidget(lbl_cpf, 2, 0)

        self._e_cpf = QLineEdit()
        self._e_cpf.setPlaceholderText("000.000.000-00")
        self._e_cpf.setFixedHeight(40)
        self._e_cpf.setStyleSheet(f"""
            QLineEdit {{
                background-color: {_BRANCO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 10px;
                padding: 8px 12px;
            }}
        """)
        aplicar_mascara_cpf(self._e_cpf)
        grid.addWidget(self._e_cpf, 3, 0)

        lbl_email = QLabel("E-mail")
        lbl_email.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        lbl_email.setStyleSheet(f"color: {_MUTED};")
        grid.addWidget(lbl_email, 2, 1)

        self._e_email = QLineEdit()
        self._e_email.setPlaceholderText("usuario@dominio.com")
        self._e_email.setFixedHeight(40)
        self._e_email.setStyleSheet(f"""
            QLineEdit {{
                background-color: {_BRANCO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 10px;
                padding: 8px 12px;
            }}
        """)
        grid.addWidget(self._e_email, 3, 1)

        # Linha 2: Senha e Observações
        lbl_senha = QLabel("Senha")
        lbl_senha.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        lbl_senha.setStyleSheet(f"color: {_MUTED};")
        grid.addWidget(lbl_senha, 4, 0)

        placeholder_senha = "Senha obrigatória" if self._is_new else "Deixe em branco p/ manter"
        self._e_senha = QLineEdit()
        self._e_senha.setPlaceholderText(placeholder_senha)
        self._e_senha.setEchoMode(QLineEdit.EchoMode.Password)
        self._e_senha.setFixedHeight(40)
        self._e_senha.setStyleSheet(f"""
            QLineEdit {{
                background-color: {_BRANCO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 10px;
                padding: 8px 12px;
            }}
        """)
        grid.addWidget(self._e_senha, 5, 0)

        lbl_obs = QLabel("Observações")
        lbl_obs.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        lbl_obs.setStyleSheet(f"color: {_MUTED};")
        grid.addWidget(lbl_obs, 4, 1)

        self._e_obs = QLineEdit()
        self._e_obs.setPlaceholderText("Observações opcionais")
        self._e_obs.setFixedHeight(40)
        self._e_obs.setStyleSheet(f"""
            QLineEdit {{
                background-color: {_BRANCO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 10px;
                padding: 8px 12px;
            }}
        """)
        grid.addWidget(self._e_obs, 5, 1)

        card_layout.addLayout(grid)

        # Checkbox Ativo
        self._var_ativo = QCheckBox("Usuário ativo")
        self._var_ativo.setChecked(True)
        self._var_ativo.setFont(QFont("Segoe UI", 12))
        self._var_ativo.setStyleSheet(f"color: {_MUTED};")
        card_layout.addWidget(self._var_ativo)

        # Botões
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self._btn_salvar = QPushButton("💾 Salvar")
        self._btn_salvar.setFixedHeight(42)
        self._btn_salvar.setStyleSheet(f"""
            QPushButton {{
                background-color: {_VERDE};
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 13px;
                padding: 8px 20px;
            }}
            QPushButton:hover {{
                background-color: {_VERDE_H};
            }}
        """)
        self._btn_salvar.clicked.connect(self._salvar)
        btn_layout.addWidget(self._btn_salvar)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setFixedHeight(42)
        btn_cancelar.setStyleSheet(f"""
            QPushButton {{
                background-color: {_BRANCO};
                color: #1e2f3e;
                border: 1px solid {_CINZA_BORDER};
                border-radius: 10px;
                font-size: 13px;
                padding: 8px 20px;
            }}
            QPushButton:hover {{
                background-color: {_CINZA_BORDER};
            }}
        """)
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancelar)

        if not self._is_new and self._on_delete:
            btn_excluir = QPushButton("🗑 Excluir")
            btn_excluir.setFixedHeight(42)
            btn_excluir.setStyleSheet(f"""
                QPushButton {{
                    background-color: {_VERM};
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-size: 13px;
                    padding: 8px 20px;
                }}
                QPushButton:hover {{
                    background-color: {_VERM_H};
                }}
            """)
            btn_excluir.clicked.connect(self._excluir)
            btn_layout.addWidget(btn_excluir)

        card_layout.addLayout(btn_layout)
        main_layout.addWidget(card)

    def _carregar_dados(self):
        """Carrega dados do usuário no formulário."""
        if not self._user_data:
            return
            
        self._e_user.setText(self._user_data.get("username", ""))
        self._e_user.setReadOnly(True)
        self._combo.setCurrentText(self._user_data.get("perfil", "usuario"))
        self._e_cpf.setText(self._user_data.get("cpf", ""))
        self._e_email.setText(self._user_data.get("email", ""))
        self._e_obs.setText(self._user_data.get("observacoes", ""))
        self._var_ativo.setChecked(self._user_data.get("ativo", True))

    def show_saving_state(self):
        """Desabilita botão durante salvamento."""
        self._btn_salvar.setEnabled(False)
        self._btn_salvar.setText("⏳ Salvando...")

    def hide_saving_state(self):
        """Reabilita botão após salvamento."""
        self._btn_salvar.setEnabled(True)
        self._btn_salvar.setText("💾 Salvar")

    def _salvar(self):
        """Coleta dados e chama callback de salvamento."""
        form = {
            "username": self._e_user.text().strip(),
            "perfil": self._combo.currentText().strip(),
            "cpf": self._e_cpf.text().strip(),
            "email": self._e_email.text().strip(),
            "senha": self._e_senha.text().strip(),
            "observacoes": self._e_obs.text().strip(),
            "ativo": self._var_ativo.isChecked(),
        }
        self._on_save(form, self._is_new, self._user_data, self)

    def _excluir(self):
        """Chama callback de exclusão."""
        if self._on_delete:
            self._on_delete(self._user_data, self)