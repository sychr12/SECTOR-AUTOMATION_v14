# -*- coding: utf-8 -*-
"""
Formulários para configuração de devolução
Versão PyQt6.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QLineEdit,
    QPushButton, QScrollArea, QWidget, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from app.theme import AppTheme


class FormularioDestinatarios(QDialog):
    """Formulário para gerenciar destinatários de email"""
    
    def __init__(self, parent=None, destinatarios_iniciais=None, on_salvar=None):
        super().__init__(parent)
        
        self.destinatarios = destinatarios_iniciais or []
        self.on_salvar = on_salvar
        
        self.setWindowTitle("Destinatários de Email")
        self.setModal(True)
        self.setFixedSize(500, 400)
        self.setStyleSheet(f"background-color: {AppTheme.BG_APP};")
        
        self._criar_widgets()
        self._centralizar()
    
    def _centralizar(self):
        screen = self.screen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def _criar_widgets(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Título
        lbl_title = QLabel("✉️ Destinatários de Email")
        lbl_title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        lbl_title.setStyleSheet(f"color: {AppTheme.TXT_MAIN};")
        layout.addWidget(lbl_title)
        
        # Frame para adicionar novo email
        add_frame = QFrame()
        add_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {AppTheme.BG_CARD};
                border-radius: 12px;
            }}
        """)
        add_layout = QVBoxLayout(add_frame)
        add_layout.setContentsMargins(15, 15, 15, 15)
        
        lbl_add = QLabel("Adicionar novo email:")
        lbl_add.setFont(QFont("Segoe UI", 12))
        lbl_add.setStyleSheet(f"color: {AppTheme.TXT_MAIN};")
        add_layout.addWidget(lbl_add)
        
        input_layout = QHBoxLayout()
        self.entry_email = QLineEdit()
        self.entry_email.setPlaceholderText("email@exemplo.com")
        self.entry_email.setStyleSheet(f"""
            QLineEdit {{
                background-color: {AppTheme.BG_INPUT};
                border: 1px solid {AppTheme.BTN_PRIMARY};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12px;
            }}
        """)
        input_layout.addWidget(self.entry_email, 1)
        
        btn_add = QPushButton("+")
        btn_add.setFixedSize(40, 35)
        btn_add.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppTheme.BTN_SUCCESS};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {AppTheme.BTN_SUCCESS_HOVER};
            }}
        """)
        btn_add.clicked.connect(self._adicionar_email)
        input_layout.addWidget(btn_add)
        
        add_layout.addLayout(input_layout)
        layout.addWidget(add_frame)
        
        # Lista de destinatários
        lista_frame = QFrame()
        lista_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {AppTheme.BG_CARD};
                border-radius: 12px;
            }}
        """)
        lista_layout = QVBoxLayout(lista_frame)
        lista_layout.setContentsMargins(15, 15, 15, 15)
        
        lbl_lista = QLabel("Destinatários atuais:")
        lbl_lista.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        lbl_lista.setStyleSheet(f"color: {AppTheme.TXT_MAIN};")
        lista_layout.addWidget(lbl_lista)
        
        # Scroll area para a lista
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: transparent;")
        
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(5)
        self.scroll_layout.addStretch()
        
        scroll.setWidget(self.scroll_content)
        lista_layout.addWidget(scroll)
        
        layout.addWidget(lista_frame, 1)
        
        # Botões
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setFixedSize(100, 35)
        btn_cancelar.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppTheme.BG_INPUT};
                color: {AppTheme.TXT_MAIN};
                border: 1px solid {AppTheme.BORDER};
                border-radius: 8px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {AppTheme.TXT_MUTED};
            }}
        """)
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancelar)
        
        btn_salvar = QPushButton("Salvar")
        btn_salvar.setFixedSize(100, 35)
        btn_salvar.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppTheme.BTN_SUCCESS};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {AppTheme.BTN_SUCCESS_HOVER};
            }}
        """)
        btn_salvar.clicked.connect(self._salvar)
        btn_layout.addWidget(btn_salvar, alignment=Qt.AlignmentFlag.AlignRight)
        
        layout.addLayout(btn_layout)
        
        self._carregar_destinatarios()
    
    def _carregar_destinatarios(self):
        """Carrega os destinatários na lista"""
        # Limpar frame (manter apenas o stretch)
        while self.scroll_layout.count() > 1:
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Adicionar cada destinatário
        for email in self.destinatarios:
            item_frame = QFrame()
            item_layout = QHBoxLayout(item_frame)
            item_layout.setContentsMargins(5, 5, 5, 5)
            
            lbl_email = QLabel(email)
            lbl_email.setFont(QFont("Segoe UI", 11))
            lbl_email.setStyleSheet(f"color: {AppTheme.TXT_MAIN};")
            item_layout.addWidget(lbl_email, 1)
            
            btn_remover = QPushButton("🗑️")
            btn_remover.setFixedSize(30, 25)
            btn_remover.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {AppTheme.TXT_MAIN};
                    border: none;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background-color: {AppTheme.BG_ERROR};
                    border-radius: 4px;
                }}
            """)
            btn_remover.clicked.connect(lambda checked, e=email: self._remover_email(e))
            item_layout.addWidget(btn_remover)
            
            self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, item_frame)
    
    def _adicionar_email(self):
        """Adiciona um novo email à lista"""
        email = self.entry_email.text().strip()
        
        if not email:
            QMessageBox.warning(self, "Aviso", "Digite um email válido.")
            return
        
        if "@" not in email or "." not in email:
            QMessageBox.warning(self, "Aviso", "Email inválido.")
            return
        
        if email in self.destinatarios:
            QMessageBox.information(self, "Info", "Este email já está na lista.")
            return
        
        self.destinatarios.append(email)
        self.entry_email.clear()
        self._carregar_destinatarios()
    
    def _remover_email(self, email):
        """Remove um email da lista"""
        if email in self.destinatarios:
            self.destinatarios.remove(email)
            self._carregar_destinatarios()
    
    def _salvar(self):
        """Salva a lista de destinatários"""
        if self.on_salvar:
            self.on_salvar(self.destinatarios)
        self.accept()