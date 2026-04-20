# views/batch_view.py
# -*- coding: utf-8 -*-
"""
batch_view.py — Aba de geração em LOTE de carteiras digitais.
Versão PyQt6.
"""
import os
import re
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog,
    QMessageBox, QProgressBar, QTextEdit
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor

from .batch_controller import BatchCarteiraController

# ── Cores ─────────────────────────────────────────────────────────────────────
_VERDE = "#22c55e"
_VERDE_H = "#16a34a"
_AZUL = "#3b82f6"
_AZUL_H = "#2563eb"
_AMBER = "#f59e0b"
_AMBER_H = "#d97706"
_VERM = "#ef4444"
_MUTED = "#64748b"
_BRANCO = "#ffffff"
_CINZA_BG = "#f8fafc"
_CINZA_BORDER = "#e2e8f0"
_CINZA_TEXTO = "#1e2f3e"

_LOG_CORES = {
    "sucesso": _VERDE,
    "erro": _VERM,
    "aviso": _AMBER,
    "info": _MUTED,
}


class BatchCarteiraView(QWidget):
    """Aba de geração em lote."""

    def __init__(self, parent=None, usuario: str = None, repo=None, sefaz_repo=None):
        super().__init__(parent)
        self.usuario = usuario
        self._ctrl = BatchCarteiraController(usuario, repo, sefaz_repo)
        self._arquivos: list = []

        self.setStyleSheet(f"background-color: {_CINZA_BG};")
        self._build()

    # ── Layout principal ──────────────────────────────────────────────────────
    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(20)

        # Cabeçalho
        hdr_layout = QHBoxLayout()
        lbl_title = QLabel("Gerar Carteiras em Lote")
        lbl_title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        lbl_title.setStyleSheet(f"color: {_CINZA_TEXTO};")
        hdr_layout.addWidget(lbl_title)

        lbl_info = QLabel("Nome do PDF deve ser o CPF (ex: 01234567890.pdf)")
        lbl_info.setFont(QFont("Segoe UI", 11))
        lbl_info.setStyleSheet(f"color: {_MUTED};")
        hdr_layout.addWidget(lbl_info, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addLayout(hdr_layout)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {_CINZA_BORDER};")
        layout.addWidget(sep)

        # Duas colunas
        cols_layout = QHBoxLayout()
        cols_layout.setSpacing(12)

        self._build_esquerda(cols_layout)
        self._build_direita(cols_layout)
        layout.addLayout(cols_layout)

    # ── Coluna esquerda: seleção + lista + controles ──────────────────────────
    def _build_esquerda(self, parent_layout):
        col = QFrame()
        col.setStyleSheet(f"""
            QFrame {{
                background-color: {_BRANCO};
                border-radius: 16px;
                border: 1px solid {_CINZA_BORDER};
            }}
        """)
        col_layout = QVBoxLayout(col)
        col_layout.setContentsMargins(20, 20, 20, 20)
        col_layout.setSpacing(12)

        lbl_title = QLabel("Arquivos Selecionados")
        lbl_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        col_layout.addWidget(lbl_title)

        # Botões de seleção
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        btn_selecionar = QPushButton("📄 Selecionar PDFs")
        btn_selecionar.setFixedHeight(38)
        btn_selecionar.setStyleSheet(f"""
            QPushButton {{
                background-color: {_AZUL};
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 12px;
                font-weight: bold;
                padding: 0 16px;
            }}
            QPushButton:hover {{ background-color: {_AZUL_H}; }}
        """)
        btn_selecionar.clicked.connect(self._selecionar_pdfs)
        btn_layout.addWidget(btn_selecionar)

        btn_pasta = QPushButton("📁 Selecionar Pasta")
        btn_pasta.setFixedHeight(38)
        btn_pasta.setStyleSheet(f"""
            QPushButton {{
                background-color: {_BRANCO};
                color: {_CINZA_TEXTO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 10px;
                font-size: 12px;
                padding: 0 16px;
            }}
            QPushButton:hover {{ background-color: {_CINZA_BORDER}; }}
        """)
        btn_pasta.clicked.connect(self._selecionar_pasta)
        btn_layout.addWidget(btn_pasta)

        btn_layout.addStretch()

        btn_limpar = QPushButton("✕ Limpar")
        btn_limpar.setFixedSize(80, 38)
        btn_limpar.setStyleSheet(f"""
            QPushButton {{
                background-color: {_BRANCO};
                color: {_MUTED};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 10px;
                font-size: 11px;
            }}
            QPushButton:hover {{ background-color: {_CINZA_BORDER}; }}
        """)
        btn_limpar.clicked.connect(self._limpar_lista)
        btn_layout.addWidget(btn_limpar)

        col_layout.addLayout(btn_layout)

        # Contador
        self._lbl_count = QLabel("0 arquivo(s)")
        self._lbl_count.setFont(QFont("Segoe UI", 11))
        self._lbl_count.setStyleSheet(f"color: {_MUTED};")
        col_layout.addWidget(self._lbl_count)

        # Tabela
        self._table = QTableWidget()
        self._table.setColumnCount(3)
        self._table.setHorizontalHeaderLabels(["CPF", "Arquivo", "Status"])
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
        col_layout.addWidget(self._table)

        # Progresso
        self._lbl_prog = QLabel("")
        self._lbl_prog.setFont(QFont("Segoe UI", 11))
        self._lbl_prog.setStyleSheet(f"color: {_MUTED};")
        col_layout.addWidget(self._lbl_prog)

        self._progress = QProgressBar()
        self._progress.setFixedHeight(8)
        self._progress.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 4px;
                background-color: {_CINZA_BORDER};
            }}
            QProgressBar::chunk {{
                background-color: {_VERDE};
                border-radius: 4px;
            }}
        """)
        col_layout.addWidget(self._progress)

        # Botões ação
        self._btn_gerar = QPushButton("🚀 Gerar Carteiras")
        self._btn_gerar.setFixedHeight(46)
        self._btn_gerar.setStyleSheet(f"""
            QPushButton {{
                background-color: {_VERDE};
                color: white;
                border: none;
                border-radius: 14px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {_VERDE_H}; }}
        """)
        self._btn_gerar.clicked.connect(self._iniciar)
        col_layout.addWidget(self._btn_gerar)

        self._btn_parar = QPushButton("⛔ Parar")
        self._btn_parar.setFixedHeight(40)
        self._btn_parar.setEnabled(False)
        self._btn_parar.setStyleSheet(f"""
            QPushButton {{
                background-color: {_VERM};
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 12px;
            }}
            QPushButton:hover {{ background-color: #dc2626; }}
        """)
        self._btn_parar.clicked.connect(self._parar)
        col_layout.addWidget(self._btn_parar)

        parent_layout.addWidget(col, 2)

    # ── Coluna direita: log ───────────────────────────────────────────────────
    def _build_direita(self, parent_layout):
        col = QFrame()
        col.setStyleSheet(f"""
            QFrame {{
                background-color: {_BRANCO};
                border-radius: 16px;
                border: 1px solid {_CINZA_BORDER};
            }}
        """)
        col_layout = QVBoxLayout(col)
        col_layout.setContentsMargins(20, 20, 20, 20)
        col_layout.setSpacing(12)

        # Header do log
        hdr_layout = QHBoxLayout()
        lbl_title = QLabel("Log de Processamento")
        lbl_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        hdr_layout.addWidget(lbl_title)

        btn_limpar_log = QPushButton("Limpar Log")
        btn_limpar_log.setFixedSize(90, 28)
        btn_limpar_log.setStyleSheet(f"""
            QPushButton {{
                background-color: {_BRANCO};
                color: {_MUTED};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 8px;
                font-size: 10px;
            }}
            QPushButton:hover {{ background-color: {_CINZA_BORDER}; }}
        """)
        btn_limpar_log.clicked.connect(self._limpar_log)
        hdr_layout.addWidget(btn_limpar_log, alignment=Qt.AlignmentFlag.AlignRight)
        col_layout.addLayout(hdr_layout)

        # Resumo (3 mini-stats)
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(8)

        self._sc_sucesso = self._create_stat_card("✓ Sucesso", "0", _VERDE)
        stats_layout.addWidget(self._sc_sucesso)

        self._sc_erro = self._create_stat_card("✕ Erros", "0", _VERM)
        stats_layout.addWidget(self._sc_erro)

        self._sc_ignorado = self._create_stat_card("⊘ Ignorados", "0", _AMBER)
        stats_layout.addWidget(self._sc_ignorado)

        col_layout.addLayout(stats_layout)

        # Log text box
        self._log_box = QTextEdit()
        self._log_box.setReadOnly(True)
        self._log_box.setFont(QFont("Consolas", 11))
        self._log_box.setStyleSheet(f"""
            QTextEdit {{
                background-color: {_CINZA_BG};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 12px;
                padding: 8px;
            }}
        """)
        col_layout.addWidget(self._log_box)

        parent_layout.addWidget(col, 3)

    def _create_stat_card(self, titulo, valor, cor):
        """Cria um card de estatística pequeno."""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {_CINZA_BG};
                border-radius: 10px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 8, 12, 8)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setFont(QFont("Segoe UI", 9))
        lbl_titulo.setStyleSheet(f"color: {_MUTED};")
        layout.addWidget(lbl_titulo)

        lbl_valor = QLabel(valor)
        lbl_valor.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        lbl_valor.setStyleSheet(f"color: {cor};")
        layout.addWidget(lbl_valor, alignment=Qt.AlignmentFlag.AlignCenter)

        return card

    # ── Seleção de arquivos ───────────────────────────────────────────────────
    def _selecionar_pdfs(self):
        caminhos, _ = QFileDialog.getOpenFileNames(
            self, "Selecionar PDFs", "", "PDF Files (*.pdf)"
        )
        if caminhos:
            self._adicionar_arquivos(caminhos)

    def _selecionar_pasta(self):
        pasta = QFileDialog.getExistingDirectory(self, "Selecionar pasta com PDFs")
        if not pasta:
            return
        caminhos = [
            os.path.join(pasta, f)
            for f in os.listdir(pasta)
            if f.lower().endswith(".pdf")
        ]
        if not caminhos:
            QMessageBox.warning(self, "Aviso", "Nenhum PDF encontrado na pasta.")
            return
        self._adicionar_arquivos(caminhos)

    def _adicionar_arquivos(self, caminhos: list):
        existentes = {a["caminho"] for a in self._arquivos}
        invalidos = []

        for caminho in caminhos:
            if caminho in existentes:
                continue
            nome = os.path.basename(caminho)
            cpf = BatchCarteiraController.cpf_do_arquivo(nome)
            if not cpf:
                invalidos.append(nome)
                continue
            self._arquivos.append({
                "caminho": caminho,
                "nome": nome,
                "cpf": BatchCarteiraController.formatar_cpf(cpf),
                "status": "pendente",
            })

        self._renderizar_lista()

        if invalidos:
            QMessageBox.warning(
                self,
                "Arquivos ignorados",
                f"{len(invalidos)} arquivo(s) ignorado(s) (o nome deve ser exatamente 11 dígitos numéricos):\n\n" +
                "\n".join(invalidos[:10]) +
                (f"\n... e mais {len(invalidos) - 10}" if len(invalidos) > 10 else ""),
            )

    def _limpar_lista(self):
        if self._ctrl.esta_rodando():
            QMessageBox.warning(self, "Aviso", "Aguarde o processamento terminar.")
            return
        self._arquivos.clear()
        self._renderizar_lista()

    def _renderizar_lista(self):
        self._table.setRowCount(len(self._arquivos))
        for i, a in enumerate(self._arquivos):
            self._table.setItem(i, 0, QTableWidgetItem(a["cpf"]))
            self._table.setItem(i, 1, QTableWidgetItem(a["nome"]))
            self._table.setItem(i, 2, QTableWidgetItem(a["status"].upper()))
            
            # Aplicar cor do status
            status_colors = {
                "pendente": _MUTED,
                "ok": _VERDE,
                "erro": _VERM,
                "aviso": _AMBER,
                "sucesso": _VERDE,
            }
            color = status_colors.get(a["status"], _MUTED)
            self._table.item(i, 2).setForeground(QColor(color))

        n = len(self._arquivos)
        self._lbl_count.setText(f"{n} arquivo(s)")

    def _atualizar_status_arquivo(self, nome: str, status: str):
        for i, a in enumerate(self._arquivos):
            if a["nome"] == nome:
                a["status"] = status
                if i < self._table.rowCount():
                    self._table.setItem(i, 2, QTableWidgetItem(status.upper()))
                    status_colors = {
                        "pendente": _MUTED,
                        "ok": _VERDE,
                        "erro": _VERM,
                        "aviso": _AMBER,
                        "sucesso": _VERDE,
                    }
                    color = status_colors.get(status, _MUTED)
                    self._table.item(i, 2).setForeground(QColor(color))
                break

    # ── Iniciar / Parar ───────────────────────────────────────────────────────
    def _iniciar(self):
        if not self._arquivos:
            QMessageBox.warning(self, "Aviso", "Adicione PDFs antes de gerar.")
            return
        if self._ctrl.esta_rodando():
            QMessageBox.warning(self, "Aviso", "Processamento já em andamento.")
            return

        # Reset visual
        self._progress.setValue(0)
        self._limpar_log()
        self._atualizar_stats(0, 0, 0)
        self._btn_gerar.setEnabled(False)
        self._btn_gerar.setText("Gerando...")
        self._btn_parar.setEnabled(True)

        # Resetar status na lista
        for a in self._arquivos:
            a["status"] = "pendente"
        self._renderizar_lista()

        caminhos = [a["caminho"] for a in self._arquivos]
        self._ctrl.executar_lote(
            caminhos_pdf=caminhos,
            log_cb=self._on_log,
            progress_cb=self._on_progress,
            concluido_cb=self._on_concluido,
        )

    def _parar(self):
        self._ctrl.parar()
        self._btn_parar.setEnabled(False)
        self._log("Parando após o arquivo atual...", "aviso")

    # ── Callbacks do controller ───────────────────────────────────────────────
    def _on_log(self, msg: str, tipo: str = "info"):
        QTimer.singleShot(0, lambda: self._log(msg, tipo))

        # Atualizar status na árvore
        m = re.match(r"\[\d+/\d+\] (.+?) — (.+)", msg)
        if m:
            cpf_txt = m.group(1)
            status = "ok" if tipo == "sucesso" else tipo
            for a in self._arquivos:
                if a["cpf"] == cpf_txt or cpf_txt in a["nome"]:
                    QTimer.singleShot(0, lambda n=a["nome"], s=status: self._atualizar_status_arquivo(n, s))
                    break

    def _on_progress(self, atual: int, total: int, nome: str):
        pct = int(atual / total * 100) if total else 0
        QTimer.singleShot(0, lambda: self._progress.setValue(pct))
        QTimer.singleShot(0, lambda: self._lbl_prog.setText(f"{atual}/{total} — {nome}"))

    def _on_concluido(self, sucesso: int, erro: int, ignorado: int):
        QTimer.singleShot(0, lambda: self._atualizar_stats(sucesso, erro, ignorado))
        QTimer.singleShot(0, lambda: self._progress.setValue(100))
        QTimer.singleShot(0, lambda: self._lbl_prog.setText(f"Concluído — {sucesso} salvo(s)"))
        QTimer.singleShot(0, lambda: self._btn_gerar.setEnabled(True))
        QTimer.singleShot(0, lambda: self._btn_gerar.setText("🚀 Gerar Carteiras"))
        QTimer.singleShot(0, lambda: self._btn_parar.setEnabled(False))

        if erro == 0:
            QTimer.singleShot(0, lambda: QMessageBox.information(
                self, "Concluído",
                f"Lote finalizado!\n\n✓ Sucesso: {sucesso}\n⊘ Ignorados: {ignorado}\n✕ Erros: {erro}"
            ))
        else:
            QTimer.singleShot(0, lambda: QMessageBox.warning(
                self, "Concluído com erros",
                f"Lote finalizado com erros.\n\n✓ Sucesso: {sucesso}\n⊘ Ignorados: {ignorado}\n✕ Erros: {erro}\n\nVerifique o log."
            ))

    def _atualizar_stats(self, sucesso, erro, ignorado):
        """Atualiza os valores dos cards de estatística."""
        # Atualizar labels dentro dos cards
        for widget in self._sc_sucesso.findChildren(QLabel):
            if widget.font().pointSize() == 18:
                widget.setText(str(sucesso))
        for widget in self._sc_erro.findChildren(QLabel):
            if widget.font().pointSize() == 18:
                widget.setText(str(erro))
        for widget in self._sc_ignorado.findChildren(QLabel):
            if widget.font().pointSize() == 18:
                widget.setText(str(ignorado))

    # ── Log ───────────────────────────────────────────────────────────────────
    def _log(self, msg: str, tipo: str = "info"):
        ts = datetime.now().strftime("%H:%M:%S")
        color = _LOG_CORES.get(tipo, _MUTED)
        self._log_box.setTextColor(QColor(color))
        self._log_box.append(f"[{ts}] {msg}")
        # Scroll para o final
        cursor = self._log_box.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self._log_box.setTextCursor(cursor)

    def _limpar_log(self):
        self._log_box.clear()