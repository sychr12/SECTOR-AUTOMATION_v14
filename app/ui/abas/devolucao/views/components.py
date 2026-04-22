# -*- coding: utf-8 -*-
"""
Componentes de UI reutilizáveis para a interface de devolução
Versão PyQt6.
"""

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from app.theme import AppTheme


class HeaderCard(QFrame):
    """Card de cabeçalho estilizado"""
    def __init__(self, title="", subtitle="", parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        lbl_title.setStyleSheet(f"color: {AppTheme.TXT_MAIN};")
        layout.addWidget(lbl_title)
        
        if subtitle:
            lbl_subtitle = QLabel(subtitle)
            lbl_subtitle.setFont(QFont("Segoe UI", 14))
            lbl_subtitle.setStyleSheet(f"color: {AppTheme.TXT_MUTED};")
            layout.addWidget(lbl_subtitle)
        
        # Espaçamento inferior
        spacer = QFrame()
        spacer.setFixedHeight(30)
        layout.addWidget(spacer)


class ConteudoCard(QFrame):
    """Card para conteúdo da devolução"""
    def __init__(self, on_content_change=None, parent=None):
        super().__init__(parent)
        self.on_content_change = on_content_change
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {AppTheme.BG_CARD};
                border-radius: 18px;
                border: 1px solid {AppTheme.BORDER};
            }}
        """)
        
        self._create_widgets()
    
    def _create_widgets(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        lbl_title = QLabel("Conteúdo da Devolução")
        lbl_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        lbl_title.setStyleSheet(f"color: {AppTheme.TXT_MAIN};")
        layout.addWidget(lbl_title)
        
        self.text_widget = QTextEdit()
        self.text_widget.setPlaceholderText("Digite o conteúdo da devolução...")
        self.text_widget.setStyleSheet(f"""
            QTextEdit {{
                background-color: {AppTheme.BG_INPUT};
                color: {AppTheme.TXT_MAIN};
                border: 1px solid {AppTheme.BORDER};
                border-radius: 12px;
                padding: 12px;
                font-family: 'Segoe UI';
                font-size: 12px;
            }}
            QTextEdit:focus {{
                border: 2px solid {AppTheme.BTN_PRIMARY};
            }}
        """)
        
        if self.on_content_change:
            self.text_widget.textChanged.connect(self.on_content_change)
        
        layout.addWidget(self.text_widget)
    
    def obter_conteudo(self):
        """Retorna o conteúdo do textbox"""
        return self.text_widget.toPlainText().strip()
    
    def definir_conteudo(self, conteudo):
        """Define o conteúdo do textbox"""
        self.text_widget.setPlainText(conteudo)
    
    def limpar_conteudo(self):
        """Limpa o conteúdo do textbox"""
        self.text_widget.clear()


class BotoesAcao(QFrame):
    """Frame com botões de ação"""
    def __init__(self, on_gerar_pdf=None, on_enviar_email=None, parent=None):
        super().__init__(parent)
        self.on_gerar_pdf = on_gerar_pdf
        self.on_enviar_email = on_enviar_email
        self.setStyleSheet("background-color: transparent;")
        self._create_widgets()
    
    def _create_widgets(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 10)
        layout.setSpacing(10)
        
        # Botão Gerar PDF
        if self.on_gerar_pdf:
            self.btn_pdf = QPushButton("📄 Gerar PDF")
            self.btn_pdf.setFixedSize(180, 45)
            self.btn_pdf.setStyleSheet(f"""
                QPushButton {{
                    background-color: {AppTheme.BTN_PRIMARY};
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-size: 13px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {AppTheme.BTN_PRIMARY_HOVER};
                }}
                QPushButton:disabled {{
                    background-color: #cccccc;
                }}
            """)
            self.btn_pdf.clicked.connect(self.on_gerar_pdf)
            layout.addWidget(self.btn_pdf)
        
        # Botão Enviar Email
        if self.on_enviar_email:
            self.btn_email = QPushButton("✉️ Enviar Email")
            self.btn_email.setFixedSize(180, 45)
            self.btn_email.setStyleSheet(f"""
                QPushButton {{
                    background-color: {AppTheme.BTN_SUCCESS};
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-size: 13px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {AppTheme.BTN_SUCCESS_HOVER};
                }}
                QPushButton:disabled {{
                    background-color: #cccccc;
                }}
            """)
            self.btn_email.clicked.connect(self.on_enviar_email)
            layout.addWidget(self.btn_email)
        
        # Botão Ambos
        if self.on_gerar_pdf and self.on_enviar_email:
            self.btn_ambos = QPushButton("📧 Gerar e Enviar")
            self.btn_ambos.setFixedSize(180, 45)
            self.btn_ambos.setStyleSheet(f"""
                QPushButton {{
                    background-color: {AppTheme.BTN_WARNING};
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-size: 13px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {AppTheme.BTN_WARNING_HOVER};
                }}
                QPushButton:disabled {{
                    background-color: #cccccc;
                }}
            """)
            self.btn_ambos.clicked.connect(self._executar_ambos)
            layout.addWidget(self.btn_ambos)
        
        layout.addStretch()
    
    def _executar_ambos(self):
        """Executa ambas as ações"""
        if self.on_gerar_pdf:
            self.on_gerar_pdf()
        if self.on_enviar_email:
            self.on_enviar_email()
    
    def desabilitar_botoes(self):
        """Desabilita todos os botões"""
        if hasattr(self, 'btn_pdf'):
            self.btn_pdf.setEnabled(False)
        if hasattr(self, 'btn_email'):
            self.btn_email.setEnabled(False)
        if hasattr(self, 'btn_ambos'):
            self.btn_ambos.setEnabled(False)
    
    def habilitar_botoes(self):
        """Habilita todos os botões"""
        if hasattr(self, 'btn_pdf'):
            self.btn_pdf.setEnabled(True)
        if hasattr(self, 'btn_email'):
            self.btn_email.setEnabled(True)
        if hasattr(self, 'btn_ambos'):
            self.btn_ambos.setEnabled(True)