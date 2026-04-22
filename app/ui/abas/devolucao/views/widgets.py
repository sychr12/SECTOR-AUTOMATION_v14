# -*- coding: utf-8 -*-
"""
Widgets customizados para a interface de devolução
Versão PyQt6.
"""

from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from app.theme import AppTheme


class StatusBar(QFrame):
    """Barra de status para feedback"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self.setStyleSheet(f"border-radius: 8px;")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 5, 5, 5)
        
        self.label_status = QLabel("")
        self.label_status.setFont(QFont("Segoe UI", 11))
        layout.addWidget(self.label_status, 1)
        
        self.btn_fechar = QPushButton("✕")
        self.btn_fechar.setFixedSize(30, 30)
        self.btn_fechar.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
                border-radius: 4px;
            }
        """)
        self.btn_fechar.clicked.connect(self.hide)
        layout.addWidget(self.btn_fechar)
        
        self.hide()
    
    def mostrar_info(self, mensagem):
        """Mostra mensagem informativa"""
        self.label_status.setText(mensagem)
        self.label_status.setStyleSheet(f"color: {AppTheme.TXT_INFO};")
        self.setStyleSheet(f"""
            background-color: {AppTheme.BG_INFO};
            border-radius: 8px;
        """)
        self.show()
    
    def mostrar_sucesso(self, mensagem):
        """Mostra mensagem de sucesso"""
        self.label_status.setText(mensagem)
        self.label_status.setStyleSheet(f"color: {AppTheme.TXT_SUCCESS};")
        self.setStyleSheet(f"""
            background-color: {AppTheme.BG_SUCCESS};
            border-radius: 8px;
        """)
        self.show()
    
    def mostrar_erro(self, mensagem):
        """Mostra mensagem de erro"""
        self.label_status.setText(mensagem)
        self.label_status.setStyleSheet(f"color: {AppTheme.TXT_ERROR};")
        self.setStyleSheet(f"""
            background-color: {AppTheme.BG_ERROR};
            border-radius: 8px;
        """)
        self.show()
    
    def mostrar_aviso(self, mensagem):
        """Mostra mensagem de aviso"""
        self.label_status.setText(mensagem)
        self.label_status.setStyleSheet(f"color: {AppTheme.TXT_WARNING};")
        self.setStyleSheet(f"""
            background-color: {AppTheme.BG_WARNING};
            border-radius: 8px;
        """)
        self.show()


class ContadorCaracteres(QFrame):
    """Widget para contagem de caracteres"""
    
    def __init__(self, text_widget, max_caracteres=1000, parent=None):
        super().__init__(parent)
        self.text_widget = text_widget
        self.max_caracteres = max_caracteres
        
        self.setStyleSheet("background-color: transparent;")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.label_contagem = QLabel("0/1000")
        self.label_contagem.setFont(QFont("Segoe UI", 10))
        self.label_contagem.setStyleSheet(f"color: {AppTheme.TXT_MUTED};")
        layout.addWidget(self.label_contagem)
        
        self.text_widget.textChanged.connect(self.atualizar)
        self.atualizar()
    
    def atualizar(self):
        """Atualiza a contagem de caracteres"""
        conteudo = self.text_widget.toPlainText()
        contagem = len(conteudo)
        
        self.label_contagem.setText(f"{contagem}/{self.max_caracteres}")
        
        if contagem > self.max_caracteres:
            self.label_contagem.setStyleSheet(f"color: {AppTheme.TXT_ERROR};")
        elif contagem > self.max_caracteres * 0.9:
            self.label_contagem.setStyleSheet(f"color: {AppTheme.TXT_WARNING};")
        else:
            self.label_contagem.setStyleSheet(f"color: {AppTheme.TXT_MUTED};")
    
    def obter_contagem(self):
        """Retorna a contagem atual de caracteres"""
        return len(self.text_widget.toPlainText())
    
    def esta_dentro_limite(self):
        """Verifica se está dentro do limite de caracteres"""
        return self.obter_contagem() <= self.max_caracteres