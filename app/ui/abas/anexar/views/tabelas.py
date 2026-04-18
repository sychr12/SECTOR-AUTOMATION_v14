# -*- coding: utf-8 -*-
"""Tabelas/listas do módulo Anexar - Versão PyQt6."""

from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from .theme import (
    VERDE, VERDE_H, AZUL, AZUL_H, VERM, AMBER, INFO, MUTED, SLATE,
    fmt_data, fmt_data_curta,
)

# Constantes de layout
BG_APP = "#f8fafc"
BG_CARD = "#f1f5f9"
BG_INPUT = "#ffffff"
TXT_MAIN = "#0f172a"


def _create_table(parent, columns, style_name=""):
    """Cria uma tabela QTableWidget estilizada."""
    table = QTableWidget(parent)
    table.setColumnCount(len(columns))
    table.setHorizontalHeaderLabels([c[1] for c in columns])
    table.setAlternatingRowColors(True)
    table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

    header = table.horizontalHeader()
    for i, (key, title, width, stretch) in enumerate(columns):
        if stretch:
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        else:
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
            table.setColumnWidth(i, width)

    table.setStyleSheet(f"""
        QTableWidget {{
            background-color: {BG_INPUT};
            color: {TXT_MAIN};
            border: none;
            gridline-color: {BG_CARD};
        }}
        QTableWidget::item {{
            padding: 8px;
            border-bottom: 1px solid {BG_CARD};
        }}
        QTableWidget::item:selected {{
            background-color: #1e3a5f;
            color: white;
        }}
        QHeaderView::section {{
            background-color: {BG_CARD};
            color: {MUTED};
            padding: 8px;
            border: none;
            font-weight: bold;
        }}
    """)
    return table


def _section_header(parent, texto: str):
    """Cria um cabeçalho de seção."""
    label = QLabel(texto)
    label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
    label.setStyleSheet(f"color: {TXT_MAIN};")
    return label


# ── Tabela Carteiras ──────────────────────────────────────────────────────────

class CarteirasTable:
    _COLS = [
        ("id", "ID", 50, False),
        ("nome", "Nome", 210, True),
        ("cpf", "CPF", 130, False),
        ("unloc", "UNLOC", 90, False),
        ("registro", "Registro", 120, False),
        ("validade", "Validade", 95, False),
        ("atividade", "Atividade", 170, True),
        ("criado_em", "Criado em", 140, False),
        ("pdf", "PDF", 55, False),
        ("status", "Status", 125, False),
    ]

    @classmethod
    def criar(cls, parent, on_baixar=None, on_visualizar=None, on_excluir=None):
        """
        Cria a tabela de carteiras.

        Retorna:
            (container, scroll_content)
        """
        container = QFrame(parent)
        container.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header da tabela
        thead = QFrame()
        thead.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border-radius: 12px;
                min-height: 42px;
            }}
        """)
        thead_layout = QHBoxLayout(thead)
        thead_layout.setContentsMargins(16, 0, 16, 0)

        for _, title, width, stretch in cls._COLS:
            label = QLabel(title)
            label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            label.setStyleSheet(f"color: {MUTED};")
            if stretch:
                thead_layout.addWidget(label, 1)
            else:
                label.setFixedWidth(width)
                thead_layout.addWidget(label)

        layout.addWidget(thead)

        # Área de rolagem para a tabela
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: transparent;")

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(2)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        # Armazenar referências no conteúdo interno
        scroll_content._on_baixar = on_baixar
        scroll_content._on_visualizar = on_visualizar
        scroll_content._on_excluir = on_excluir
        scroll_content._scroll_layout = scroll_layout

        # Espelhar referências no container externo
        container._on_baixar = on_baixar
        container._on_visualizar = on_visualizar
        container._on_excluir = on_excluir
        container._scroll_layout = scroll_layout

        return container, scroll_content

    @staticmethod
    def carregar(lista, registros: list, on_baixar=None, on_visualizar=None, on_excluir=None):
        """Carrega os registros na tabela."""
        while lista._scroll_layout.count():
            item = lista._scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for i, r in enumerate(registros):
            tem_pdf = r.get("pdf_gerado", False)
            bg = BG_APP if i % 2 == 0 else BG_INPUT

            row = QFrame()
            row.setStyleSheet(f"""
                QFrame {{
                    background-color: {bg};
                    border-radius: 8px;
                    margin: 2px 4px;
                }}
                QFrame:hover {{
                    background-color: {BG_CARD};
                }}
            """)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(16, 8, 16, 8)
            row_layout.setSpacing(0)

            def _add_cell(text, width, is_main=False):
                label = QLabel(str(text) if text else "—")
                label.setFont(QFont("Segoe UI", 11 if is_main else 10))
                label.setStyleSheet(f"color: {TXT_MAIN if is_main else MUTED};")
                if width:
                    label.setFixedWidth(width)
                row_layout.addWidget(label)

            _add_cell(r.get("id"), 50)
            _add_cell(r.get("nome"), 210, True)
            _add_cell(r.get("cpf"), 130)
            _add_cell(r.get("unloc"), 90)
            _add_cell(r.get("registro"), 120)
            _add_cell(fmt_data_curta(r.get("validade")), 95)
            _add_cell(r.get("atividade1"), 170)
            _add_cell(fmt_data(r.get("criado_em")), 140)

            # PDF status
            pdf_label = QLabel("✓" if tem_pdf else "✗")
            pdf_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            pdf_label.setStyleSheet(f"color: {VERDE if tem_pdf else MUTED};")
            pdf_label.setFixedWidth(55)
            pdf_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            row_layout.addWidget(pdf_label)

            # Botões de ação
            if tem_pdf:
                btn_frame = QFrame()
                btn_frame.setStyleSheet("background-color: transparent;")
                btn_layout = QHBoxLayout(btn_frame)
                btn_layout.setContentsMargins(0, 0, 0, 0)
                btn_layout.setSpacing(4)

                callback_visualizar = on_visualizar or getattr(lista, "_on_visualizar", None)
                callback_baixar = on_baixar or getattr(lista, "_on_baixar", None)
                callback_excluir = on_excluir or getattr(lista, "_on_excluir", None)

                if callback_visualizar:
                    btn_ver = QPushButton("👁️")
                    btn_ver.setFixedSize(40, 30)
                    btn_ver.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {AZUL};
                            color: white;
                            border: none;
                            border-radius: 8px;
                            font-size: 11px;
                            font-weight: bold;
                        }}
                        QPushButton:hover {{
                            background-color: {AZUL_H};
                        }}
                    """)
                    btn_ver.clicked.connect(lambda checked=False, rid=r.get("id"): callback_visualizar(rid))
                    btn_layout.addWidget(btn_ver)

                if callback_baixar:
                    btn_down = QPushButton("📄")
                    btn_down.setFixedSize(40, 30)
                    btn_down.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {VERDE};
                            color: white;
                            border: none;
                            border-radius: 8px;
                            font-size: 11px;
                            font-weight: bold;
                        }}
                        QPushButton:hover {{
                            background-color: {VERDE_H};
                        }}
                    """)
                    btn_down.clicked.connect(lambda checked=False, rid=r.get("id"): callback_baixar(rid))
                    btn_layout.addWidget(btn_down)

                if callback_excluir:
                    btn_del = QPushButton("🗑️")
                    btn_del.setFixedSize(40, 30)
                    btn_del.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {VERM};
                            color: white;
                            border: none;
                            border-radius: 8px;
                            font-size: 11px;
                            font-weight: bold;
                        }}
                        QPushButton:hover {{
                            background-color: #b91c1c;
                        }}
                    """)
                    btn_del.clicked.connect(
                        lambda checked=False, rid=r.get("id"), nome=r.get("nome", ""): callback_excluir(rid, nome)
                    )
                    btn_layout.addWidget(btn_del)

                row_layout.addWidget(btn_frame)
            else:
                status_label = QLabel("⏳ Pendente")
                status_label.setFixedSize(110, 30)
                status_label.setStyleSheet("""
                    background-color: #854d0e;
                    color: #fef08a;
                    border-radius: 8px;
                    font-size: 10px;
                    font-weight: bold;
                    padding: 5px;
                """)
                status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                row_layout.addWidget(status_label)

            lista._scroll_layout.addWidget(row)

    @staticmethod
    def limpar(lista):
        while lista._scroll_layout.count():
            item = lista._scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


# ── Tabela Em Análise ─────────────────────────────────────────────────────────

class EmAnaliseTable:
    _COLS = [
        ("id", "ID", 50, False),
        ("nome_pdf", "Processo", 220, True),
        ("cpf", "CPF", 130, False),
        ("unloc", "UNLOC", 85, False),
        ("memorando", "Memorando", 120, False),
        ("tipo", "Tipo", 85, False),
        ("urgencia", "Urgente", 80, False),
        ("usuario", "Usuário", 120, False),
        ("criado_em", "Entrada", 140, False),
    ]

    @classmethod
    def criar(cls, parent):
        """Cria a tabela de processos em análise."""
        container = QFrame(parent)
        container.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        hdr_layout = QHBoxLayout()
        hdr_layout.setContentsMargins(0, 0, 0, 12)
        lbl = _section_header(container, "📋 Processos em Análise")
        hdr_layout.addWidget(lbl)
        layout.addLayout(hdr_layout)

        table = _create_table(container, cls._COLS)
        layout.addWidget(table)

        return table, container

    @classmethod
    def carregar(cls, table, registros: list):
        """Carrega registros na tabela."""
        cls.limpar(table)
        table.setRowCount(len(registros))

        for row, r in enumerate(registros):
            urgente = r.get("urgencia", False)

            table.setItem(row, 0, QTableWidgetItem(str(r.get("id", ""))))
            table.setItem(row, 1, QTableWidgetItem(r.get("nome_pdf", "")))
            table.setItem(row, 2, QTableWidgetItem(r.get("cpf", "")))
            table.setItem(row, 3, QTableWidgetItem(r.get("unloc", "")))
            table.setItem(row, 4, QTableWidgetItem(r.get("memorando", "")))
            table.setItem(row, 5, QTableWidgetItem(r.get("tipo", "")))
            table.setItem(row, 6, QTableWidgetItem("⚡ Sim" if urgente else "—"))
            table.setItem(row, 7, QTableWidgetItem(r.get("usuario", "—")))
            table.setItem(row, 8, QTableWidgetItem(fmt_data(r.get("criado_em"))))

            if urgente:
                for col in range(table.columnCount()):
                    item = table.item(row, col)
                    if item:
                        item.setBackground(QColor("#4a0e0e"))
                        item.setForeground(QColor("#fecaca"))

    @staticmethod
    def limpar(table):
        table.setRowCount(0)


# ── Tabela Histórico ──────────────────────────────────────────────────────────

class HistoricoTable:
    _COLS = [
        ("id", "ID", 50, False),
        ("nome", "Nome", 220, True),
        ("cpf", "CPF", 130, False),
        ("unloc", "UNLOC", 90, False),
        ("registro", "Registro", 120, False),
        ("validade", "Validade", 95, False),
        ("usuario", "Anexado por", 130, False),
        ("criado_em", "Data", 150, False),
    ]

    @classmethod
    def criar(cls, parent):
        """Cria a tabela de histórico."""
        container = QFrame(parent)
        container.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        hdr_layout = QHBoxLayout()
        hdr_layout.setContentsMargins(0, 0, 0, 12)
        lbl = _section_header(container, "📜 Histórico de Anexações")
        hdr_layout.addWidget(lbl)
        layout.addLayout(hdr_layout)

        table = _create_table(container, cls._COLS)
        layout.addWidget(table)

        return table, container

    @classmethod
    def carregar(cls, table, registros: list):
        """Carrega registros na tabela."""
        cls.limpar(table)
        table.setRowCount(len(registros))

        for row, r in enumerate(registros):
            table.setItem(row, 0, QTableWidgetItem(str(r.get("id", ""))))
            table.setItem(row, 1, QTableWidgetItem(r.get("nome", "")))
            table.setItem(row, 2, QTableWidgetItem(r.get("cpf", "")))
            table.setItem(row, 3, QTableWidgetItem(r.get("unloc", "")))
            table.setItem(row, 4, QTableWidgetItem(r.get("registro", "")))
            table.setItem(row, 5, QTableWidgetItem(fmt_data_curta(r.get("validade"))))
            table.setItem(row, 6, QTableWidgetItem(r.get("usuario", "—")))
            table.setItem(row, 7, QTableWidgetItem(fmt_data(r.get("criado_em"))))

    @staticmethod
    def limpar(table):
        table.setRowCount(0)


# ── Tabela Log ────────────────────────────────────────────────────────────────

class LogTable:
    _ICONS = {"sucesso": "✓", "erro": "✗", "aviso": "⚠", "info": "ℹ"}

    @classmethod
    def criar(cls, parent):
        """Cria a tabela de log."""
        container = QFrame(parent)
        container.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        hdr_layout = QHBoxLayout()
        hdr_layout.setContentsMargins(0, 0, 0, 12)
        lbl = _section_header(container, "📋 Log de Processamento")
        hdr_layout.addWidget(lbl)
        layout.addLayout(hdr_layout)

        columns = [
            ("status", "Status", 140, False),
            ("mensagem", "Mensagem", 580, True),
        ]
        table = _create_table(container, columns)
        layout.addWidget(table)

        return table, container

    @classmethod
    def add(cls, table, status, mensagem, tag="info"):
        """Adiciona uma mensagem ao log."""
        ts = datetime.now().strftime("%H:%M:%S")
        icon = cls._ICONS.get(tag.lower(), "•")

        row = table.rowCount()
        table.insertRow(row)

        table.setItem(row, 0, QTableWidgetItem(status))
        table.setItem(row, 1, QTableWidgetItem(f"[{ts}] {icon} {mensagem}"))

        colors = {
            "sucesso": VERDE,
            "erro": VERM,
            "aviso": "#f59e0b",
            "info": INFO,
        }
        color = colors.get(tag.lower(), MUTED)

        for col in range(2):
            item = table.item(row, col)
            if item:
                item.setForeground(QColor(color))

        table.scrollToBottom()

    @staticmethod
    def limpar(table):
        table.setRowCount(0)