# app/ui/abas/Email/views/components.py
# -*- coding: utf-8 -*-
"""
Componentes de UI reutilizáveis para a interface de download de emails
Versão PyQt6
"""

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class AppTheme:
    """Paleta local — espelha app.theme.AppTheme sem depender do caminho absoluto."""
    BG_INPUT = "#ffffff"
    BG_CARD = "#f1f5f9"
    TXT_MAIN = "#0f172a"
    TXT_MUTED = "#64748b"
    BTN_PRIMARY = "#2c6e9e"
    BTN_PRIMARY_HOVER = "#1e4a6e"
    BORDER = "#e2e8f0"


class HeaderCard(QFrame):
    """Card de cabeçalho estilizado"""
    def __init__(self, parent=None, title="", subtitle=""):
        super().__init__(parent)
        self.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 15)
        
        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        lbl_title.setStyleSheet(f"color: {AppTheme.TXT_MAIN};")
        layout.addWidget(lbl_title)
        
        if subtitle:
            lbl_subtitle = QLabel(subtitle)
            lbl_subtitle.setFont(QFont("Segoe UI", 14))
            lbl_subtitle.setStyleSheet(f"color: {AppTheme.TXT_MUTED};")
            layout.addWidget(lbl_subtitle)


class ActionButton(QPushButton):
    """Botão de ação estilizado"""
    def __init__(self, parent=None, text="", command=None):
        super().__init__(text, parent)
        self.setFixedHeight(46)
        self.setMinimumWidth(220)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppTheme.BTN_PRIMARY};
                color: white;
                border: none;
                border-radius: 14px;
                font-family: 'Segoe UI';
                font-size: 15px;
                font-weight: bold;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background-color: {AppTheme.BTN_PRIMARY_HOVER};
            }}
        """)
        if command:
            self.clicked.connect(command)


class LogTableView:
    """Tabela para exibição de logs usando QTableWidget"""

    @staticmethod
    def criar(parent):
        """Cria e configura a tabela de logs"""
        container = QFrame(parent)
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {AppTheme.BG_CARD};
                border-radius: 16px;
            }}
        """)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 15, 30, 30)

        # Título
        lbl_title = QLabel("Log de Processamento")
        lbl_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(lbl_title)

        # Tabela
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Status", "Mensagem"])
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {AppTheme.BG_INPUT};
                border: 1px solid {AppTheme.BORDER};
                border-radius: 12px;
                gridline-color: {AppTheme.BORDER};
            }}
            QTableWidget::item {{
                padding: 8px;
            }}
            QHeaderView::section {{
                background-color: {AppTheme.BG_CARD};
                color: {AppTheme.TXT_MAIN};
                padding: 8px;
                font-weight: bold;
            }}
        """)

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(table)

        return table, container

    @staticmethod
    def adicionar_log(table, status, mensagem):
        """Adiciona uma entrada de log na tabela"""
        row = table.rowCount()
        table.insertRow(row)
        table.setItem(row, 0, QTableWidgetItem(status))
        table.setItem(row, 1, QTableWidgetItem(mensagem))
        table.scrollToBottom()

    @staticmethod
    def limpar_logs(table):
        """Limpa todos os logs da tabela"""
        table.setRowCount(0)