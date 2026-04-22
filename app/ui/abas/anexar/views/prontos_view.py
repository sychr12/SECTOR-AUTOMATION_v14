# -*- coding: utf-8 -*-
"""
Aba "Prontos & Histórico" — mostra quem anexou cada carteira e resumo por usuário.
Versão PyQt6.
"""
import threading
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor

from .theme import (
    VERDE, VERDE_H, VERDE_T, AZUL, AZUL_H,
    VERM, AMBER, MUTED, INFO,
    fmt_data, fmt_data_curta,
)

# Cores padrão
BG_APP = "#f8fafc"
BG_CARD = "#f1f5f9"
BG_INPUT = "#ffffff"
TXT_MAIN = "#0f172a"


def _create_table(parent, columns):
    """Cria uma QTableWidget estilizada."""
    table = QTableWidget(parent)
    table.setColumnCount(len(columns))
    table.setHorizontalHeaderLabels([c[1] for c in columns])
    table.setAlternatingRowColors(True)
    table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
    
    # Configurar larguras das colunas
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


def _create_scrolled_table(parent, columns):
    """Cria uma QTableWidget dentro de um QScrollArea."""
    scroll = QScrollArea(parent)
    scroll.setWidgetResizable(True)
    scroll.setStyleSheet("border: none; background-color: transparent;")
    
    container = QFrame()
    container.setStyleSheet("background-color: transparent;")
    container_layout = QVBoxLayout(container)
    container_layout.setContentsMargins(0, 0, 0, 0)
    
    table = _create_table(container, columns)
    container_layout.addWidget(table)
    scroll.setWidget(container)
    
    return scroll, table


class ProntosView(QWidget):
    """
    Aba com duas seções:
      • Ranking — quem anexou mais e quando foi a última anexação
      • Detalhes — todas as carteiras prontas, filtráveis por usuário/CPF/nome
    """

    def __init__(self, parent=None, repository=None):
        super().__init__(parent)
        self.repository = repository

        self._var_usuario = ""
        self._var_cpf = ""
        self._var_nome = ""

        self.setStyleSheet("background-color: transparent;")
        self._build()

    # ── Layout ───────────────────────────────────────────────────────────────

    def _build(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(10)

        # Coluna esquerda (ranking)
        self._build_ranking(layout)
        
        # Coluna direita (detalhes)
        self._build_detalhes(layout)

    def _build_ranking(self, parent_layout):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border-radius: 14px;
                border: 1px solid {BG_INPUT};
            }}
        """)
        
        inner_layout = QVBoxLayout(card)
        inner_layout.setContentsMargins(16, 16, 16, 16)
        inner_layout.setSpacing(12)

        # Título
        lbl_title = QLabel("🏆 Ranking de Anexações")
        lbl_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl_title.setStyleSheet(f"color: {TXT_MAIN};")
        inner_layout.addWidget(lbl_title)

        # Tabela de ranking
        columns = [
            ("pos", "#", 30, False),
            ("usuario", "Usuário", 160, True),
            ("total", "Total", 60, False),
            ("ultima", "Última em", 130, False),
        ]
        self._tree_rank = _create_table(card, columns)
        inner_layout.addWidget(self._tree_rank)

        # Botão recarregar
        btn_reload = QPushButton("↻  Atualizar")
        btn_reload.setFixedHeight(32)
        btn_reload.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_INPUT};
                color: {TXT_MAIN};
                border: 1px solid {BG_CARD};
                border-radius: 8px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {BG_CARD};
            }}
        """)
        btn_reload.clicked.connect(self.recarregar)
        inner_layout.addWidget(btn_reload)

        parent_layout.addWidget(card, 1)

    def _build_detalhes(self, parent_layout):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border-radius: 14px;
                border: 1px solid {BG_INPUT};
            }}
        """)
        
        inner_layout = QVBoxLayout(card)
        inner_layout.setContentsMargins(16, 16, 16, 16)
        inner_layout.setSpacing(12)

        # Título
        lbl_title = QLabel("📋 Carteiras Anexadas")
        lbl_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl_title.setStyleSheet(f"color: {TXT_MAIN};")
        inner_layout.addWidget(lbl_title)

        # Filtros
        filters_layout = QHBoxLayout()
        filters_layout.setSpacing(16)

        # Filtro Usuário
        lbl_usuario = QLabel("Usuário:")
        lbl_usuario.setFont(QFont("Segoe UI", 10))
        lbl_usuario.setStyleSheet(f"color: {MUTED};")
        filters_layout.addWidget(lbl_usuario)
        
        self._entry_usuario = QLineEdit()
        self._entry_usuario.setPlaceholderText("Digite o usuário")
        self._entry_usuario.setFixedWidth(140)
        self._entry_usuario.setFixedHeight(32)
        self._entry_usuario.textChanged.connect(self._on_filtro_changed)
        self._entry_usuario.setStyleSheet(f"""
            QLineEdit {{
                background-color: {BG_INPUT};
                border: 1px solid {BG_CARD};
                border-radius: 8px;
                padding: 4px 8px;
                font-size: 11px;
            }}
        """)
        filters_layout.addWidget(self._entry_usuario)

        # Filtro CPF
        lbl_cpf = QLabel("CPF:")
        lbl_cpf.setFont(QFont("Segoe UI", 10))
        lbl_cpf.setStyleSheet(f"color: {MUTED};")
        filters_layout.addWidget(lbl_cpf)
        
        self._entry_cpf = QLineEdit()
        self._entry_cpf.setPlaceholderText("Digite o CPF")
        self._entry_cpf.setFixedWidth(130)
        self._entry_cpf.setFixedHeight(32)
        self._entry_cpf.textChanged.connect(self._on_filtro_changed)
        self._entry_cpf.setStyleSheet(f"""
            QLineEdit {{
                background-color: {BG_INPUT};
                border: 1px solid {BG_CARD};
                border-radius: 8px;
                padding: 4px 8px;
                font-size: 11px;
            }}
        """)
        filters_layout.addWidget(self._entry_cpf)

        # Filtro Nome
        lbl_nome = QLabel("Nome:")
        lbl_nome.setFont(QFont("Segoe UI", 10))
        lbl_nome.setStyleSheet(f"color: {MUTED};")
        filters_layout.addWidget(lbl_nome)
        
        self._entry_nome = QLineEdit()
        self._entry_nome.setPlaceholderText("Digite o nome")
        self._entry_nome.setFixedWidth(160)
        self._entry_nome.setFixedHeight(32)
        self._entry_nome.textChanged.connect(self._on_filtro_changed)
        self._entry_nome.setStyleSheet(f"""
            QLineEdit {{
                background-color: {BG_INPUT};
                border: 1px solid {BG_CARD};
                border-radius: 8px;
                padding: 4px 8px;
                font-size: 11px;
            }}
        """)
        filters_layout.addWidget(self._entry_nome)

        # Botão Limpar
        btn_limpar = QPushButton("✕ Limpar")
        btn_limpar.setFixedSize(80, 32)
        btn_limpar.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_INPUT};
                color: {MUTED};
                border: 1px solid {BG_CARD};
                border-radius: 8px;
                font-size: 10px;
            }}
            QPushButton:hover {{
                background-color: {BG_CARD};
            }}
        """)
        btn_limpar.clicked.connect(self._limpar_filtros)
        filters_layout.addWidget(btn_limpar)

        filters_layout.addStretch()

        # Contador
        self._lbl_count = QLabel("")
        self._lbl_count.setFont(QFont("Segoe UI", 10))
        self._lbl_count.setStyleSheet(f"color: {MUTED};")
        filters_layout.addWidget(self._lbl_count)

        inner_layout.addLayout(filters_layout)

        # Tabela de detalhes
        columns = [
            ("id", "ID", 50, False),
            ("nome", "Nome", 200, True),
            ("cpf", "CPF", 120, False),
            ("unloc", "UNLOC", 80, False),
            ("registro", "Registro", 110, False),
            ("validade", "Validade", 88, False),
            ("anexado_por", "Anexado por", 130, False),
            ("anexado_em", "Anexado em", 140, False),
            ("cadastrado", "Cadastrado", 130, False),
        ]
        self._tree_det = _create_table(card, columns)
        self._tree_det.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._tree_det.itemDoubleClicked.connect(self._on_double_click)
        inner_layout.addWidget(self._tree_det)

        parent_layout.addWidget(card, 3)

    # ── Carregar dados ────────────────────────────────────────────────────────

    def recarregar(self):
        """Recarrega ranking e detalhes (chame de fora após cada anexação)."""
        self._carregar_ranking()
        self._carregar_detalhes()

    def _on_filtro_changed(self):
        """Disparado quando os filtros são alterados."""
        QTimer.singleShot(300, self._carregar_detalhes)

    def _carregar_ranking(self):
        def _worker():
            try:
                rows = self.repository.resumo_por_usuario()
                QTimer.singleShot(0, lambda: self._preencher_ranking(rows))
            except Exception as exc:
                print(f"[ProntosView] ERRO ranking: {exc}")

        threading.Thread(target=_worker, daemon=True).start()

    def _carregar_detalhes(self):
        usuario = self._entry_usuario.text().strip()
        cpf = self._entry_cpf.text().strip()
        nome = self._entry_nome.text().strip()

        def _worker():
            try:
                rows = self.repository.buscar_prontos_filtrado(
                    usuario=usuario, cpf=cpf, nome=nome)
                QTimer.singleShot(0, lambda: self._preencher_detalhes(rows))
            except Exception as exc:
                print(f"[ProntosView] ERRO detalhes: {exc}")

        threading.Thread(target=_worker, daemon=True).start()

    # ── Preencher tabelas ─────────────────────────────────────────────────────

    def _preencher_ranking(self, rows: list):
        self._tree_rank.setRowCount(len(rows))
        
        medalhas = {1: "#f59e0b", 2: "#94a3b8", 3: "#b45309"}
        
        for i, r in enumerate(rows):
            ultima = r.get("ultima_em")
            ultima_str = fmt_data(ultima) if ultima else "—"
            pos_txt = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i + 1, str(i + 1))
            
            self._tree_rank.setItem(i, 0, QTableWidgetItem(pos_txt))
            self._tree_rank.setItem(i, 1, QTableWidgetItem(r.get("usuario", "—")))
            self._tree_rank.setItem(i, 2, QTableWidgetItem(str(r.get("total", 0))))
            self._tree_rank.setItem(i, 3, QTableWidgetItem(ultima_str))
            
            # Aplicar cor para medalhas
            if i + 1 in medalhas:
                color = medalhas[i + 1]
                for col in range(4):
                    item = self._tree_rank.item(i, col)
                    if item:
                        item.setForeground(QColor(color))
                        if i + 1 <= 2:
                            font = item.font()
                            font.setBold(True)
                            item.setFont(font)

    def _preencher_detalhes(self, rows: list):
        self._tree_det.setRowCount(len(rows))
        
        self._lbl_count.setText(f"{len(rows)} registro(s)")
        self._lbl_count.setStyleSheet(f"color: {VERDE if rows else MUTED};")
        
        for i, r in enumerate(rows):
            self._tree_det.setItem(i, 0, QTableWidgetItem(str(r.get("id", ""))))
            self._tree_det.setItem(i, 1, QTableWidgetItem(r.get("nome", "—")))
            self._tree_det.setItem(i, 2, QTableWidgetItem(r.get("cpf", "—")))
            self._tree_det.setItem(i, 3, QTableWidgetItem(r.get("unloc", "—")))
            self._tree_det.setItem(i, 4, QTableWidgetItem(r.get("registro", "—")))
            self._tree_det.setItem(i, 5, QTableWidgetItem(fmt_data_curta(r.get("validade"))))
            self._tree_det.setItem(i, 6, QTableWidgetItem(r.get("anexado_por", "—")))
            self._tree_det.setItem(i, 7, QTableWidgetItem(fmt_data(r.get("anexado_em"))))
            self._tree_det.setItem(i, 8, QTableWidgetItem(fmt_data(r.get("criado_em"))))

    # ── Interações ────────────────────────────────────────────────────────────

    def _on_double_click(self, item):
        """Ao dar duplo clique em uma linha, filtra pelo usuário."""
        row = item.row()
        usuario_item = self._tree_det.item(row, 6)
        if usuario_item:
            usuario = usuario_item.text()
            if usuario and usuario != "—":
                self._entry_usuario.setText(usuario)

    def _limpar_filtros(self):
        self._entry_usuario.clear()
        self._entry_cpf.clear()
        self._entry_nome.clear()
        self._carregar_detalhes()