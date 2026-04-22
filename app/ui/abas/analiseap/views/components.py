# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from app.theme import AppTheme


class FormCard(QFrame):
    """Card de formulário estilizado"""
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {AppTheme.BG_CARD};
                border-radius: 22px;
                border: 1px solid #e2e8f0;
            }}
        """)
        
    def setLayout(self, layout):
        layout.setContentsMargins(25, 22, 25, 22)
        super().setLayout(layout)


class GridLayout(QGridLayout):
    """Layout de grid para formulários"""
    def __init__(self, columns=5, **kwargs):
        super().__init__(**kwargs)
        self.columns = columns
        self.setHorizontalSpacing(10)
        self.setVerticalSpacing(8)
        
    def setup_grid(self, parent):
        parent.setLayout(self)
        for i in range(self.columns):
            self.setColumnStretch(i, 1)


class StyledEntry(QLineEdit):
    """Campo de entrada estilizado"""
    def __init__(self, parent=None, placeholder="", **kwargs):
        super().__init__(parent, **kwargs)
        self.setPlaceholderText(placeholder)
        self.setFixedHeight(40)
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: {AppTheme.BG_INPUT};
                border: 1px solid {AppTheme.BTN_PRIMARY};
                border-radius: 8px;
                padding: 8px 12px;
                color: {AppTheme.TXT_MAIN};
                font-family: 'Segoe UI';
                font-size: 12px;
            }}
            QLineEdit:focus {{
                border: 2px solid {AppTheme.BTN_PRIMARY};
            }}
            QLineEdit::placeholder {{
                color: {AppTheme.TXT_MUTED};
            }}
        """)
    
    def grid(self, row=0, column=0, **kwargs):
        kwargs.setdefault('padx', 10)
        kwargs.setdefault('sticky', 'ew')
        self.parent().layout().addWidget(self, row, column, **kwargs)


class StyledButton(QPushButton):
    """Botão estilizado"""
    def __init__(self, parent=None, text="", command=None, **kwargs):
        super().__init__(text, parent, **kwargs)
        self.setFixedHeight(40)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppTheme.BTN_PRIMARY};
                color: {AppTheme.TXT_MAIN};
                border: none;
                border-radius: 10px;
                font-family: 'Segoe UI';
                font-size: 12px;
                font-weight: bold;
                padding: 8px 20px;
            }}
            QPushButton:hover {{
                background-color: {AppTheme.BTN_PRIMARY_HOVER};
            }}
        """)
        if command:
            self.clicked.connect(command)
    
    def pack(self, **kwargs):
        layout = self.parent().layout()
        if layout:
            layout.addWidget(self, **kwargs)


class StyledComboBox(QComboBox):
    """ComboBox estilizado"""
    def __init__(self, parent=None, values=None, **kwargs):
        super().__init__(parent, **kwargs)
        if values:
            self.addItems(values)
        self.setFixedHeight(40)
        self.setStyleSheet(f"""
            QComboBox {{
                background-color: {AppTheme.BG_INPUT};
                border: 1px solid {AppTheme.BTN_PRIMARY};
                border-radius: 8px;
                padding: 6px 12px;
                color: {AppTheme.TXT_MAIN};
                font-family: 'Segoe UI';
                font-size: 12px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {AppTheme.BTN_PRIMARY};
                margin-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {AppTheme.BG_INPUT};
                color: {AppTheme.TXT_MAIN};
                selection-background-color: {AppTheme.BG_CARD};
            }}
        """)
    
    def grid(self, row=0, column=0, **kwargs):
        kwargs.setdefault('padx', 10)
        kwargs.setdefault('sticky', 'ew')
        self.parent().layout().addWidget(self, row, column, **kwargs)
    
    def pack(self, **kwargs):
        layout = self.parent().layout()
        if layout:
            layout.addWidget(self, **kwargs)


class StyledTextbox(QTextEdit):
    """Caixa de texto estilizada"""
    def __init__(self, parent=None, height=100, **kwargs):
        super().__init__(parent, **kwargs)
        self.setFixedHeight(height)
        self.setStyleSheet(f"""
            QTextEdit {{
                background-color: {AppTheme.BG_INPUT};
                border: 1px solid {AppTheme.BTN_PRIMARY};
                border-radius: 8px;
                padding: 8px;
                color: {AppTheme.TXT_MAIN};
                font-family: 'Segoe UI';
                font-size: 12px;
            }}
            QTextEdit:focus {{
                border: 2px solid {AppTheme.BTN_PRIMARY};
            }}
        """)
    
    def pack(self, **kwargs):
        layout = self.parent().layout()
        if layout:
            layout.addWidget(self, **kwargs)
    
    def clear(self):
        self.setText("")