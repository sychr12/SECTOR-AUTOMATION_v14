# -*- coding: utf-8 -*-
"""
ConsultarUI — interface de consulta de registros na tabela analise_ap.
Versão PyQt6.
"""

import threading
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QProgressBar, QComboBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

# Remover import do AppTheme problemático
# from app.theme import AppTheme

# Definir cores localmente
BG_APP = "#f5f7fc"
BG_CARD = "#ffffff"
BG_INPUT = "#ffffff"
TXT_MAIN = "#1e2f3e"
TXT_MUTED = "#5a6e8a"
BTN_PRIMARY = "#2c6e9e"
BTN_PRIMARY_HOVER = "#1e4a6e"
BORDER_COLOR = "#e2e8f0"

from .controller import ConsultaController
from .services import FiltroService


class ConsultarUI(QWidget):
    """Interface de consulta de registros."""

    def __init__(self, parent=None, usuario=None, conectar_bd=None):
        super().__init__(parent)
        self.usuario = usuario
        self.conectar_bd = conectar_bd

        self.setStyleSheet(f"background-color: {BG_APP};")

        try:
            self.controller = ConsultaController(conectar_bd, usuario)
        except ValueError as e:
            QMessageBox.critical(self, "Erro", str(e))
            return

        self.filtro_service = FiltroService()

        self._criar_interface()
        self._configurar_menu_contexto()
        QTimer.singleShot(200, self.pesquisar)

    # ── Layout ────────────────────────────────────────────────────────────────
    def _criar_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 24, 30, 24)
        layout.setSpacing(16)

        # Header
        header = self._criar_header()
        layout.addWidget(header)

        # Filtros
        self.filtros_card = self._criar_filtros()
        layout.addWidget(self.filtros_card)

        # Tabela
        self.tabela = self._criar_tabela()
        layout.addWidget(self.tabela)

    def _criar_header(self):
        header_widget = QWidget()
        layout = QVBoxLayout(header_widget)
        layout.setContentsMargins(0, 0, 0, 16)

        title = QLabel("Consulta de Dados")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TXT_MAIN};")
        layout.addWidget(title)

        subtitle = QLabel("Pesquise registros da tabela analise_ap")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setStyleSheet(f"color: {TXT_MUTED};")
        layout.addWidget(subtitle)

        return header_widget

    def _criar_filtros(self):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border-radius: 12px;
                border: 1px solid {BORDER_COLOR};
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        filtro_title = QLabel("Filtros de Pesquisa")
        filtro_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(filtro_title)

        grid_layout = QHBoxLayout()
        grid_layout.setSpacing(10)

        nome_label = QLabel("Nome:")
        nome_label.setFont(QFont("Segoe UI", 10))
        grid_layout.addWidget(nome_label)

        self.filtro_nome = QLineEdit()
        self.filtro_nome.setPlaceholderText("Digite o nome")
        self.filtro_nome.setFixedHeight(35)
        self.filtro_nome.setStyleSheet(f"""
            QLineEdit {{
                background-color: {BG_INPUT};
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
                padding: 6px 10px;
            }}
        """)
        grid_layout.addWidget(self.filtro_nome)

        cpf_label = QLabel("CPF:")
        cpf_label.setFont(QFont("Segoe UI", 10))
        grid_layout.addWidget(cpf_label)

        self.filtro_cpf = QLineEdit()
        self.filtro_cpf.setPlaceholderText("Digite o CPF")
        self.filtro_cpf.setFixedHeight(35)
        self.filtro_cpf.setStyleSheet(f"""
            QLineEdit {{
                background-color: {BG_INPUT};
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
                padding: 6px 10px;
            }}
        """)
        grid_layout.addWidget(self.filtro_cpf)

        tipo_label = QLabel("Tipo:")
        tipo_label.setFont(QFont("Segoe UI", 10))
        grid_layout.addWidget(tipo_label)

        self.filtro_tipo = QComboBox()
        self.filtro_tipo.addItems(["Todos", "INSC", "RENOV", "DEVOLUCAO"])
        self.filtro_tipo.setFixedHeight(35)
        self.filtro_tipo.setStyleSheet(f"""
            QComboBox {{
                background-color: {BG_INPUT};
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
                padding: 5px;
            }}
        """)
        grid_layout.addWidget(self.filtro_tipo)

        layout.addLayout(grid_layout)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_pesquisar = QPushButton("Pesquisar")
        self.btn_pesquisar.setFixedHeight(38)
        self.btn_pesquisar.setStyleSheet(f"""
            QPushButton {{
                background-color: {BTN_PRIMARY};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {BTN_PRIMARY_HOVER};
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
            }}
        """)
        self.btn_pesquisar.clicked.connect(self.pesquisar)
        btn_layout.addWidget(self.btn_pesquisar)

        self.btn_limpar = QPushButton("Limpar")
        self.btn_limpar.setFixedHeight(38)
        self.btn_limpar.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_INPUT};
                color: {TXT_MAIN};
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
                padding: 8px 20px;
            }}
            QPushButton:hover {{
                background-color: {BG_CARD};
            }}
        """)
        self.btn_limpar.clicked.connect(self._limpar_filtros)
        btn_layout.addWidget(self.btn_limpar)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        return card

    def _criar_tabela(self):
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels(["ID", "Nome", "CPF", "Município", "Memorando", "Tipo", "Data"])
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
                gridline-color: {BORDER_COLOR};
            }}
            QTableWidget::item {{
                padding: 8px;
            }}
            QHeaderView::section {{
                background-color: {BG_INPUT};
                padding: 8px;
                border: none;
                font-weight: bold;
            }}
        """)

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)

        return table

    def _configurar_menu_contexto(self):
        pass

    def pesquisar(self):
        filtros = {
            'nome': self.filtro_nome.text().strip(),
            'cpf': self.filtro_cpf.text().strip(),
            'tipo': self.filtro_tipo.currentText() if self.filtro_tipo.currentText() != "Todos" else ""
        }

        self.tabela.setRowCount(0)
        self.btn_pesquisar.setEnabled(False)

        threading.Thread(
            target=self._worker_pesquisa,
            args=(filtros,),
            daemon=True,
        ).start()

    def _worker_pesquisa(self, filtros):
        try:
            sql, params = self.controller.construir_query(filtros)
            dados = self.controller.executar_consulta(sql, params)
            dados_fmt = self.controller.formatar_data_resultados(dados)
            QTimer.singleShot(0, lambda: self._finalizar_pesquisa(dados_fmt))
        except Exception as e:
            QTimer.singleShot(0, lambda: QMessageBox.critical(self, "Erro", f"Erro ao pesquisar:\n{e}"))
            QTimer.singleShot(0, lambda: self._finalizar_pesquisa([]))

    def _finalizar_pesquisa(self, dados):
        self.btn_pesquisar.setEnabled(True)
        self.tabela.setRowCount(len(dados))

        for row, registro in enumerate(dados):
            for col, valor in enumerate(registro):
                self.tabela.setItem(row, col, QTableWidgetItem(str(valor)))

    def _limpar_filtros(self):
        self.filtro_nome.clear()
        self.filtro_cpf.clear()
        self.filtro_tipo.setCurrentIndex(0)
        self.pesquisar()