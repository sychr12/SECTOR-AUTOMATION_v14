# -*- coding: utf-8 -*-
"""Histórico de Lançamentos (PyQt6)."""

import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFrame, QLabel,
    QPushButton, QLineEdit, QScrollArea, QWidget, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from app.theme import AppTheme


class HistoricoView(QDialog):

    def __init__(self, parent, usuario, controller, service):
        super().__init__(parent)

        self.usuario    = usuario
        self.controller = controller
        self.service    = service

        self.setWindowTitle("Histórico de Lançamentos")
        self.setFixedSize(1050, 650)
        self.setModal(True)
        self.setStyleSheet(f"background-color: {AppTheme.BG_APP};")

        self._build()
        self._centralizar()
        self._carregar()

    # ------------------------------------------------------------------
    def _centralizar(self):
        if self.parent():
            geo = self.parent().frameGeometry()
            center = geo.center()
            frame = self.frameGeometry()
            frame.moveCenter(center)
            self.move(frame.topLeft())

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)

        # Título
        titulo = QLabel("Histórico de Lançamentos")
        titulo.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        titulo.setStyleSheet(f"color: {AppTheme.TXT_MAIN};")
        root.addWidget(titulo)
        root.addSpacing(16)

        # Barra de filtro
        bar = QFrame()
        bar.setStyleSheet(f"""
            QFrame {{
                background-color: {AppTheme.BG_CARD};
                border-radius: 14px;
            }}
        """)
        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(16, 10, 16, 10)

        lbl = QLabel("Pesquisar:")
        lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        lbl.setStyleSheet("color: #64748b;")
        bar_layout.addWidget(lbl)

        self._input_busca = QLineEdit()
        self._input_busca.setPlaceholderText("Nome do arquivo, CPF ou analista...")
        self._input_busca.setFixedHeight(36)
        self._input_busca.setStyleSheet(f"""
            QLineEdit {{
                background-color: {AppTheme.BG_INPUT};
                border: none;
                border-radius: 10px;
                padding: 0 10px;
                color: {AppTheme.TXT_MAIN};
            }}
        """)
        self._input_busca.textChanged.connect(self._pesquisar)
        bar_layout.addWidget(self._input_busca)

        btn_limpar = QPushButton("Limpar")
        btn_limpar.setFixedHeight(36)
        btn_limpar.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppTheme.BG_INPUT};
                border-radius: 10px;
                color: #64748b;
            }}
            QPushButton:hover {{
                background-color: {AppTheme.BG_APP};
            }}
        """)
        btn_limpar.clicked.connect(lambda: self._input_busca.clear())
        bar_layout.addWidget(btn_limpar)

        root.addWidget(bar)
        root.addSpacing(12)

        # Área scroll
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("border: none;")

        self._lista_widget = QWidget()
        self._lista_layout = QVBoxLayout(self._lista_widget)
        self._lista_layout.setSpacing(6)

        self._scroll.setWidget(self._lista_widget)
        root.addWidget(self._scroll)

    # ------------------------------------------------------------------
    def _clear_layout(self):
        while self._lista_layout.count():
            item = self._lista_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    # ------------------------------------------------------------------
    def _carregar(self):
        try:
            self.registros = self.service.listar_ultimos(100)
            self._renderizar("")
        except Exception as exc:
            self._clear_layout()
            lbl = QLabel(f"Erro ao carregar: {exc}")
            lbl.setStyleSheet("color: #ef4444;")
            self._lista_layout.addWidget(lbl)

    # ------------------------------------------------------------------
    def _pesquisar(self):
        termo = self._input_busca.text().lower().strip()
        self._renderizar(termo)

    # ------------------------------------------------------------------
    def _renderizar(self, termo: str):
        self._clear_layout()

        registros = self.registros
        if termo:
            registros = [
                r for r in registros
                if termo in (r.get("nome_pdf") or "").lower()
                or termo in (r.get("cpf") or "").lower()
                or termo in (r.get("analisado_por") or "").lower()
                or termo in (r.get("lancado_por") or "").lower()
            ]

        if not registros:
            lbl = QLabel("Nenhum registro encontrado.")
            lbl.setStyleSheet("color: #64748b; padding: 40px;")
            self._lista_layout.addWidget(lbl)
            return

        for idx, r in enumerate(registros):
            bg = AppTheme.BG_APP if idx % 2 == 0 else AppTheme.BG_CARD
            self._card(r, bg)

        self._lista_layout.addStretch()

    # ------------------------------------------------------------------
    def _card(self, r: dict, bg: str):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border-radius: 12px;
            }}
        """)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)

        # Info
        info = QVBoxLayout()

        nome = r.get("nome_pdf", "—")
        ext = os.path.splitext(nome)[1].lower()
        icon = "📄" if ext == ".pdf" else "📝" if ext in (".docx", ".doc") else "📎"

        titulo = QLabel(f"{icon} {nome}")
        titulo.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        titulo.setStyleSheet("color: #3b82f6;")
        titulo.mousePressEvent = lambda e, rid=r.get("id"): self._visualizar(rid)
        info.addWidget(titulo)

        cpf = r.get("cpf", "")
        if cpf and len(cpf) == 11:
            cpf = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

        for txt in filter(None, [
            f"CPF: {cpf}" if cpf else None,
            f"Analisado por: {r.get('analisado_por','')}" if r.get("analisado_por") else None,
            f"Lançado por: {r.get('lancado_por','')}" if r.get("lancado_por") else None,
            r.get("criado_em", "")
        ]):
            lbl = QLabel(txt)
            lbl.setFont(QFont("Segoe UI", 10))
            lbl.setStyleSheet("color: #64748b;")
            info.addWidget(lbl)

        layout.addLayout(info)

        # Botões
        btns = QVBoxLayout()

        btn_ver = QPushButton("Ver")
        btn_ver.setFixedSize(80, 32)
        btn_ver.setStyleSheet("""
            QPushButton { background:#3b82f6; color:white; border-radius:10px; }
            QPushButton:hover { background:#2563eb; }
        """)
        btn_ver.clicked.connect(lambda _, rid=r.get("id"): self._visualizar(rid))
        btns.addWidget(btn_ver)

        btn_down = QPushButton("Baixar")
        btn_down.setFixedSize(80, 32)
        btn_down.setStyleSheet(f"""
            QPushButton {{
                background:{AppTheme.BG_INPUT};
                border-radius:10px;
                color:{AppTheme.TXT_MAIN};
            }}
            QPushButton:hover {{
                background:{AppTheme.BG_APP};
            }}
        """)
        btn_down.clicked.connect(lambda _, rid=r.get("id"), n=nome: self._baixar(rid, n))
        btns.addWidget(btn_down)

        layout.addLayout(btns)
        self._lista_layout.addWidget(card)

    # ------------------------------------------------------------------
    # Ações
    # ------------------------------------------------------------------
    def _visualizar(self, lancamento_id):
        if not lancamento_id:
            QMessageBox.warning(self, "Aviso", "PDF não disponível.")
            return

        ok, msg = self.controller.visualizar_pdf_banco(lancamento_id)
        if not ok:
            QMessageBox.critical(self, "Erro", msg)

    def _baixar(self, lancamento_id, nome_arquivo):
        if not lancamento_id:
            QMessageBox.warning(self, "Aviso", "PDF não disponível.")
            return

        ext = os.path.splitext(nome_arquivo)[1] or ".pdf"

        caminho, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Arquivo",
            nome_arquivo,
            "Arquivos (*.pdf *.docx *.doc);;Todos (*.*)"
        )

        if not caminho:
            return

        ok, msg = self.controller.baixar_pdf_banco(
            lancamento_id, nome_arquivo, caminho
        )

        if ok:
            QMessageBox.information(self, "Salvo", f"Arquivo salvo!\n{msg}")
        else:
            QMessageBox.critical(self, "Erro", msg)