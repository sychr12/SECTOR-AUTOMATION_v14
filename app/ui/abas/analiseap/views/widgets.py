# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton, QButtonGroup
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from app.theme import AppTheme


class Header(QFrame):
    """Cabeçalho da página"""
    def __init__(self, parent=None, title="", subtitle=""):
        super().__init__(parent)
        self.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 28)
        layout.setSpacing(6)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {AppTheme.TXT_MAIN};")
        layout.addWidget(title_label)

        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setFont(QFont("Segoe UI", 14))
            subtitle_label.setStyleSheet(f"color: {AppTheme.TXT_MUTED};")
            layout.addWidget(subtitle_label)


class RadioSelector(QFrame):
    """Seletor de opções com radio buttons"""
    def __init__(self, parent=None, options=None, default_value=None, command=None):
        super().__init__(parent)
        self.options = options or []
        self.command = command
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {AppTheme.BG_CARD};
                border-radius: 22px;
                border: 1px solid #e2e8f0;
            }}
        """)
        
        self._create_widgets(default_value)
        
    def _create_widgets(self, default_value):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(40)
        
        self.radio_group = QButtonGroup(self)
        
        for option in self.options:
            radio = QRadioButton(option['text'])
            radio.setFont(QFont("Segoe UI", 12))
            radio.setStyleSheet(f"""
                QRadioButton {{
                    color: {AppTheme.TXT_MAIN};
                    spacing: 8px;
                }}
                QRadioButton::indicator {{
                    width: 16px;
                    height: 16px;
                    border: 2px solid {AppTheme.BTN_PRIMARY};
                    border-radius: 8px;
                    background-color: white;
                }}
                QRadioButton::indicator:checked {{
                    background-color: {AppTheme.BTN_PRIMARY};
                }}
            """)
            if option['value'] == default_value:
                radio.setChecked(True)
            if self.command:
                radio.toggled.connect(self.command)
            self.radio_group.addButton(radio, self.radio_group.buttons().__len__())
            layout.addWidget(radio)
        
        layout.addStretch()
    
    def get_value(self):
        """Retorna o valor do radio selecionado"""
        button = self.radio_group.checkedButton()
        if button:
            index = self.radio_group.buttons().index(button)
            if index < len(self.options):
                return self.options[index]['value']
        return None