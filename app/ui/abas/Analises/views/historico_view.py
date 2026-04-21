# -*- coding: utf-8 -*-
"""Histórico de Processos — design refinado (PyQt6)."""
import threading
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor

_VERDE = "#22c55e"
_AZUL = "#3b82f6"
_AZUL_H = "#2563eb"
_VERM = "#ef4444"
_AMBER = "#f59e0b"
_MUTED = "#64748b"
_BRANCO = "#ffffff"
_CINZA_BG = "#f8fafc"
_CINZA_BORDER = "#e2e8f0"
_CINZA_TEXTO = "#1e2f3e"

STATUS_COR = {
    "DEVOLUCAO": _VERM,
    "RENOVACAO": _VERDE,
    "INSCRICAO": _AZUL,
    "PENDENTE": _MUTED,
}


class HistoricoView(QDialog):
    """Janela de histórico de movimentações."""

    def __init__(self, parent=None, usuario=None, controller=None):
        super().__init__(parent)
        self.usuario = usuario
        self.controller = controller
        self._dados = []
        self._dados_filtrados = []

        self.setWindowTitle("Histórico de Movimentações")
        self.setModal(True)
        self.resize(1200, 700)
        self.setStyleSheet(f"background-color: {_CINZA_BG};")

        self._build()
        self._carregar()
        self._centralizar()

    def _centralizar(self):
        screen = self.screen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(16)

        # Cabeçalho
        lbl_title = QLabel("Histórico de Movimentações")
        lbl_title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        lbl_title.setStyleSheet(f"color: {_CINZA_TEXTO};")
        layout.addWidget(lbl_title)

        # Painel de filtros
        filtros_card = QFrame()
        filtros_card.setStyleSheet(f"""
            QFrame {{
                background-color: {_BRANCO};
                border-radius: 14px;
                border: 1px solid {_CINZA_BORDER};
            }}
        """)
        filtros_layout = QVBoxLayout(filtros_card)
        filtros_layout.setContentsMargins(20, 14, 20, 14)
        filtros_layout.setSpacing(10)

        # Filtro por status (radio buttons)
        status_layout = QHBoxLayout()
        status_layout.setSpacing(20)

        self.filtro_var = "TODOS"
        self.filtro_buttons = {}

        for txt, val, cor in [
            ("Todos", "TODOS", _MUTED),
            ("Devolução", "DEVOLUCAO", _VERM),
            ("Renovação", "RENOVACAO", _VERDE),
            ("Inscrição", "INSCRICAO", _AZUL),
        ]:
            radio = QPushButton(txt)
            radio.setCheckable(True)
            radio.setFixedHeight(36)
            radio.setStyleSheet(f"""
                QPushButton {{
                    background-color: {_BRANCO};
                    color: {_CINZA_TEXTO};
                    border: 1px solid {_CINZA_BORDER};
                    border-radius: 10px;
                    padding: 0 16px;
                    font-size: 12px;
                }}
                QPushButton:checked {{
                    background-color: {cor};
                    color: white;
                    border: none;
                }}
                QPushButton:hover {{
                    background-color: {_CINZA_BORDER};
                }}
            """)
            radio.clicked.connect(lambda checked, v=val: self._set_filtro(v))
            if val == "TODOS":
                radio.setChecked(True)
            status_layout.addWidget(radio)
            self.filtro_buttons[val] = radio

        status_layout.addStretch()
        filtros_layout.addLayout(status_layout)

        # Barra de pesquisa
        search_layout = QHBoxLayout()
        self.pesquisa_entry = QLineEdit()
        self.pesquisa_entry.setPlaceholderText("Buscar por nome do arquivo ou usuário...")
        self.pesquisa_entry.setFixedHeight(36)
        self.pesquisa_entry.textChanged.connect(self._on_search_changed)
        self.pesquisa_entry.setStyleSheet(f"""
            QLineEdit {{
                background-color: {_BRANCO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 10px;
                padding: 8px 12px;
                font-size: 12px;
            }}
            QLineEdit:focus {{
                border: 2px solid {_AZUL};
            }}
        """)
        search_layout.addWidget(self.pesquisa_entry)

        btn_limpar = QPushButton("Limpar")
        btn_limpar.setFixedSize(80, 36)
        btn_limpar.setStyleSheet(f"""
            QPushButton {{
                background-color: {_BRANCO};
                color: {_MUTED};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 10px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {_CINZA_BORDER};
            }}
        """)
        btn_limpar.clicked.connect(self._limpar_filtros)
        search_layout.addWidget(btn_limpar)

        filtros_layout.addLayout(search_layout)
        layout.addWidget(filtros_card)

        # Tabela
        self._table = QTableWidget()
        self._table.setColumnCount(6)
        self._table.setHorizontalHeaderLabels(["Arquivo PDF", "Status Anterior", "Status Atual", "Usuário", "Data/Hora", "Motivo"])
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
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
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)

        self._table.itemDoubleClicked.connect(self._visualizar_selecionado)
        layout.addWidget(self._table)

        # Rodapé
        rodape_layout = QHBoxLayout()

        lbl_info = QLabel("Duplo clique para visualizar o PDF")
        lbl_info.setFont(QFont("Segoe UI", 11))
        lbl_info.setStyleSheet(f"color: {_MUTED};")
        rodape_layout.addWidget(lbl_info)

        btn_baixar = QPushButton("Baixar PDF selecionado")
        btn_baixar.setFixedSize(180, 38)
        btn_baixar.setStyleSheet(f"""
            QPushButton {{
                background-color: {_AZUL};
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {_AZUL_H};
            }}
        """)
        btn_baixar.clicked.connect(self._baixar_selecionado)
        rodape_layout.addWidget(btn_baixar, alignment=Qt.AlignmentFlag.AlignRight)

        layout.addLayout(rodape_layout)

    def _set_filtro(self, valor):
        self.filtro_var = valor
        self._atualizar_tabela()

    def _on_search_changed(self):
        QTimer.singleShot(300, self._atualizar_tabela)

    def _limpar_filtros(self):
        self.pesquisa_entry.clear()
        for val, btn in self.filtro_buttons.items():
            btn.setChecked(val == "TODOS")
        self.filtro_var = "TODOS"
        self._atualizar_tabela()

    # ── Dados ────────────────────────────────────────────────────────────────
    def _carregar(self):
        threading.Thread(target=self._worker_carregar, daemon=True).start()

    def _worker_carregar(self):
        try:
            dados = self.controller.carregar_historico()
            self._dados = dados or []
            QTimer.singleShot(0, self._atualizar_tabela)
        except Exception as exc:
            QTimer.singleShot(0, lambda: QMessageBox.critical(
                self, "Erro", f"Erro ao carregar histórico:\n{exc}"))

    def _filtrar_dados(self):
        filtro = self.filtro_var
        pesquisa = self.pesquisa_entry.text().lower().strip()

        dados = self._dados
        if filtro != "TODOS":
            dados = [d for d in dados if d.get("novo_status") == filtro]
        if pesquisa:
            dados = [
                d for d in dados
                if pesquisa in d.get("nome_pdf", "").lower()
                or pesquisa in d.get("usuario", "").lower()
            ]
        return dados

    def _atualizar_tabela(self):
        self._dados_filtrados = self._filtrar_dados()
        dados = self._dados_filtrados

        self._table.setRowCount(len(dados))

        for i, h in enumerate(dados):
            data = h.get("data_acao")
            if isinstance(data, str):
                try:
                    data = datetime.fromisoformat(data)
                except ValueError:
                    data = None
            data_txt = data.strftime("%d/%m/%Y %H:%M") if data else "—"

            item_nome = QTableWidgetItem(h.get("nome_pdf", "—"))
            item_nome.setData(Qt.ItemDataRole.UserRole, h)
            self._table.setItem(i, 0, item_nome)

            self._table.setItem(i, 1, QTableWidgetItem(h.get("status_anterior", "—")))

            status_atual = h.get("novo_status", "—")
            item_status = QTableWidgetItem(status_atual)
            cor = STATUS_COR.get(status_atual, _MUTED)
            item_status.setForeground(QColor(cor))
            self._table.setItem(i, 2, item_status)

            self._table.setItem(i, 3, QTableWidgetItem(h.get("usuario", "—")))
            self._table.setItem(i, 4, QTableWidgetItem(data_txt))
            self._table.setItem(i, 5, QTableWidgetItem(h.get("motivo", "")))

    def _get_registro_selecionado(self):
        current_row = self._table.currentRow()
        if current_row < 0:
            return None
        if current_row >= len(self._dados_filtrados):
            return None
        return self._dados_filtrados[current_row]

    def _visualizar_selecionado(self):
        reg = self._get_registro_selecionado()
        if not reg:
            QMessageBox.warning(self, "Aviso", "Selecione um registro com PDF.")
            return

        aid = reg.get("analise_id")
        if aid:
            ok, msg = self.controller.visualizar_pdf(aid)
            if not ok:
                QMessageBox.critical(self, "Erro", msg)

    def _baixar_selecionado(self):
        reg = self._get_registro_selecionado()
        if not reg:
            QMessageBox.warning(self, "Aviso", "Selecione um registro com PDF.")
            return

        aid = reg.get("analise_id")
        nome = reg.get("nome_pdf", "documento")
        if not aid:
            QMessageBox.warning(self, "Aviso", "Selecione um registro com PDF.")
            return

        resultado = self.controller.baixar_pdf(aid, nome)

        if isinstance(resultado, tuple) and len(resultado) == 3 and resultado[0]:
            caminho, _ = QFileDialog.getSaveFileName(
                self,
                "Salvar PDF",
                nome.replace("/", "_").replace("\\", "_"),
                "PDF Files (*.pdf)"
            )
            if not caminho:
                return

            try:
                with open(caminho, "wb") as f:
                    f.write(resultado[1])
                QMessageBox.information(self, "Salvo", f"PDF salvo em:\n{caminho}")
            except Exception as exc:
                QMessageBox.critical(self, "Erro", f"Erro ao salvar PDF:\n{exc}")

        elif isinstance(resultado, tuple) and len(resultado) >= 2 and resultado[0] is False:
            if resultado[1] != "Operação cancelada":
                QMessageBox.critical(self, "Erro", resultado[1])