# views/historico_view.py
# -*- coding: utf-8 -*-
"""
Histórico de Carteiras Digitais.
Versão PyQt6.
"""
import re
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QLineEdit,
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from ..utils.formatters import format_cpf

# ── Cores ─────────────────────────────────────────────────────────────────────
_VERDE = "#22c55e"
_AZUL = "#3b82f6"
_AZUL_H = "#2563eb"
_MUTED = "#64748b"
_VERMELHO = "#ef4444"
_BRANCO = "#ffffff"
_CINZA_BG = "#f8fafc"
_CINZA_BORDER = "#e2e8f0"
_CINZA_TEXTO = "#1e2f3e"


class HistoricoView(QDialog):
    """Janela de histórico de carteiras digitais."""

    def __init__(self, parent=None, usuario=None, controller=None):
        super().__init__(parent)
        self.usuario = usuario
        self.controller = controller

        self.setWindowTitle("Histórico de Carteiras Digitais")
        self.setModal(True)
        self.resize(1200, 750)
        self.setStyleSheet(f"background-color: {_CINZA_BG};")

        self._build()
        self._atualizar()
        self._centralizar()

    def _centralizar(self):
        screen = self.screen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        # Cabeçalho
        hdr_layout = QHBoxLayout()
        lbl_title = QLabel("Histórico de Carteiras Digitais")
        lbl_title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        lbl_title.setStyleSheet(f"color: {_CINZA_TEXTO};")
        hdr_layout.addWidget(lbl_title)

        btn_fechar = QPushButton("✕ Fechar")
        btn_fechar.setFixedSize(90, 34)
        btn_fechar.setStyleSheet(f"""
            QPushButton {{
                background-color: {_BRANCO};
                color: {_MUTED};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 8px;
                font-size: 11px;
            }}
            QPushButton:hover {{ background-color: {_CINZA_BORDER}; }}
        """)
        btn_fechar.clicked.connect(self.close)
        hdr_layout.addWidget(btn_fechar, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addLayout(hdr_layout)

        # Filtros
        filtros_card = QFrame()
        filtros_card.setStyleSheet(f"""
            QFrame {{
                background-color: {_BRANCO};
                border-radius: 12px;
                border: 1px solid {_CINZA_BORDER};
            }}
        """)
        filtros_layout = QHBoxLayout(filtros_card)
        filtros_layout.setContentsMargins(16, 12, 16, 12)
        filtros_layout.setSpacing(16)

        # Busca
        lbl_busca = QLabel("Pesquisar:")
        lbl_busca.setStyleSheet(f"color: {_MUTED};")
        filtros_layout.addWidget(lbl_busca)

        self._entry_busca = QLineEdit()
        self._entry_busca.setPlaceholderText("Nome, CPF ou UNLOC...")
        self._entry_busca.setFixedWidth(280)
        self._entry_busca.setStyleSheet(self._entry_style())
        self._entry_busca.textChanged.connect(self._on_filtro_changed)
        filtros_layout.addWidget(self._entry_busca)

        # Período
        lbl_periodo = QLabel("Período:")
        lbl_periodo.setStyleSheet(f"color: {_MUTED};")
        filtros_layout.addWidget(lbl_periodo)

        self._periodo = QComboBox()
        self._periodo.addItems(["TODOS", "HOJE", "SEMANA", "MES", "ANO"])
        self._periodo.setFixedWidth(130)
        self._periodo.setStyleSheet(self._combo_style())
        self._periodo.currentTextChanged.connect(self._on_filtro_changed)
        filtros_layout.addWidget(self._periodo)

        # Usuário
        lbl_usuario = QLabel("Usuário:")
        lbl_usuario.setStyleSheet(f"color: {_MUTED};")
        filtros_layout.addWidget(lbl_usuario)

        self._usuario_combo = QComboBox()
        self._usuario_combo.addItems(["TODOS"])
        self._usuario_combo.setFixedWidth(160)
        self._usuario_combo.setStyleSheet(self._combo_style())
        self._usuario_combo.currentTextChanged.connect(self._on_filtro_changed)
        filtros_layout.addWidget(self._usuario_combo)

        # Botão Atualizar
        btn_atualizar = QPushButton("🔄 Atualizar")
        btn_atualizar.setFixedSize(110, 34)
        btn_atualizar.setStyleSheet(f"""
            QPushButton {{
                background-color: {_AZUL};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 11px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {_AZUL_H}; }}
        """)
        btn_atualizar.clicked.connect(self._atualizar)
        filtros_layout.addWidget(btn_atualizar)

        layout.addWidget(filtros_card)

        # Contador
        self._lbl_total = QLabel("")
        self._lbl_total.setFont(QFont("Segoe UI", 11))
        self._lbl_total.setStyleSheet(f"color: {_MUTED};")
        layout.addWidget(self._lbl_total)

        # Tabela
        self._table = QTableWidget()
        self._table.setColumnCount(7)
        self._table.setHorizontalHeaderLabels(["ID", "Nome", "CPF", "UNLOC", "Validade", "Usuário", "Data"])
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {_BRANCO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 12px;
                gridline-color: {_CINZA_BORDER};
            }}
            QTableWidget::item {{
                padding: 8px;
            }}
            QHeaderView::section {{
                background-color: {_CINZA_BORDER};
                color: {_MUTED};
                padding: 8px;
                font-weight: bold;
            }}
        """)
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        
        self._table.itemDoubleClicked.connect(self._visualizar_pdf)
        layout.addWidget(self._table)

        # Botões de ação
        acoes_layout = QHBoxLayout()
        acoes_layout.setSpacing(8)

        btn_visualizar = QPushButton("👁️ Visualizar PDF")
        btn_visualizar.setFixedSize(140, 38)
        btn_visualizar.setStyleSheet(f"""
            QPushButton {{
                background-color: {_AZUL};
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {_AZUL_H}; }}
        """)
        btn_visualizar.clicked.connect(self._visualizar_pdf)
        acoes_layout.addWidget(btn_visualizar)

        btn_baixar = QPushButton("⬇️ Baixar PDF")
        btn_baixar.setFixedSize(140, 38)
        btn_baixar.setStyleSheet(f"""
            QPushButton {{
                background-color: {_BRANCO};
                color: {_CINZA_TEXTO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 10px;
                font-size: 12px;
            }}
            QPushButton:hover {{ background-color: {_CINZA_BORDER}; }}
        """)
        btn_baixar.clicked.connect(self._baixar_pdf)
        acoes_layout.addWidget(btn_baixar)

        acoes_layout.addStretch()
        layout.addLayout(acoes_layout)

    def _entry_style(self):
        return f"""
            QLineEdit {{
                background-color: {_BRANCO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 11px;
            }}
            QLineEdit:focus {{
                border: 2px solid {_AZUL};
            }}
        """

    def _combo_style(self):
        return f"""
            QComboBox {{
                background-color: {_BRANCO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 8px;
                padding: 6px;
                font-size: 11px;
            }}
        """

    def _on_filtro_changed(self):
        QTimer.singleShot(300, self._atualizar)

    # ── Dados ─────────────────────────────────────────────────────────────────
    def _atualizar(self):
        termo = self._entry_busca.text().strip()
        periodo = self._periodo.currentText()
        usuario = self._usuario_combo.currentText()

        # Carregar usuários se necessário
        if self._usuario_combo.count() <= 1:
            try:
                usuarios = self.controller.buscar_usuarios_unicos()
                self._usuario_combo.addItems(usuarios)
            except Exception:
                pass

        try:
            registros = self.controller.carregar_historico(termo, periodo, usuario)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar histórico:\n{e}")
            return

        self._table.setRowCount(len(registros))

        for i, reg in enumerate(registros):
            data_str = ""
            if reg.get("criado_em"):
                try:
                    dt = reg["criado_em"]
                    if isinstance(dt, datetime):
                        data_str = dt.strftime("%d/%m/%Y %H:%M")
                    else:
                        data_str = str(dt)
                except Exception:
                    data_str = str(reg["criado_em"])

            self._table.setItem(i, 0, QTableWidgetItem(str(reg.get("id", ""))))
            self._table.setItem(i, 1, QTableWidgetItem(reg.get("nome", "")))
            self._table.setItem(i, 2, QTableWidgetItem(format_cpf(reg.get("cpf", "") or "")))
            self._table.setItem(i, 3, QTableWidgetItem(reg.get("unloc", "")))
            self._table.setItem(i, 4, QTableWidgetItem(reg.get("validade", "")))
            self._table.setItem(i, 5, QTableWidgetItem(reg.get("usuario", "")))
            self._table.setItem(i, 6, QTableWidgetItem(data_str))

        total = len(registros)
        self._lbl_total.setText(f"{total} registro(s) encontrado(s)")

    def _get_selected(self):
        """Retorna (carteira_id, nome) da linha selecionada."""
        current_row = self._table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Aviso", "Selecione um registro na lista.")
            return None, None
        return self._table.item(current_row, 0).text(), self._table.item(current_row, 1).text()

    def _visualizar_pdf(self):
        carteira_id, nome = self._get_selected()
        if not carteira_id:
            return
        ok, msg = self.controller.visualizar_pdf(int(carteira_id))
        if not ok:
            QMessageBox.critical(self, "Erro", msg)

    def _baixar_pdf(self):
        carteira_id, nome = self._get_selected()
        if not carteira_id:
            return
        ok, msg = self.controller.baixar_pdf(int(carteira_id), nome)
        if ok:
            QMessageBox.information(self, "Sucesso", f"PDF salvo em:\n{msg}")
        elif msg != "Operação cancelada":
            QMessageBox.critical(self, "Erro", msg)