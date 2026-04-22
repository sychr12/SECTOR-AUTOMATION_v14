# -*- coding: utf-8 -*-
"""Interface de Análise AP — gerenciamento de Análise de Pedidos (PyQt6)."""
import os
from PyQt6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QTextEdit, QPushButton, QRadioButton,
    QButtonGroup, QMessageBox, QStackedWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from services.analiseap_repository import AnaliseapRepository
from .controller import AnaliseapController
from .services import AnaliseapServices

# ================== MOTIVOS DE DEVOLUÇÃO ==================
MOTIVOS_DEVOLUCAO = [
    "Endereço", "Documentos", "Cadastro",
    "Pesca", "Simples Nacional", "Animais"
]

# ── Paleta Corporativa ──────────────────────────────────────────────────────────
_PRIMARY_DARK    = "#0a2540"
_PRIMARY         = "#1a4b6e"
_ACCENT          = "#2c6e9e"
_ACCENT_DARK     = "#1e4a6e"
_ACCENT_LIGHT    = "#e8f0f8"
_BRANCO          = "#ffffff"
_CINZA_BG        = "#f5f7fc"
_CINZA_BORDER    = "#e2e8f0"
_CINZA_MEDIO     = "#5a6e8a"
_CINZA_TEXTO     = "#1e2f3e"
_VERDE_STATUS    = "#10b981"
_VERDE_DARK      = "#059669"
_VERDE_LIGHT     = "#d1fae5"
_AMARELO         = "#f59e0b"
_VERMELHO        = "#ef4444"
_VERMELHO_DARK   = "#dc2626"
_AZUL            = "#3b82f6"
_AZUL_DARK       = "#2563eb"
_MUTED           = "#5a6e8a"


class AnaliseapUI(QWidget):
    """Interface PyQt6 para Análise AP."""

    def __init__(self, parent=None, usuario=None):
        super().__init__(parent)

        self.usuario = usuario
        self.repo = AnaliseapRepository()
        self.lista_municipios = {}
        self.BASE_DIR = os.path.dirname(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(os.path.abspath(__file__))
                )
            )
        )

        # Inicializar controller e services
        self.controller = AnaliseapController(usuario, self.repo)
        self.services = AnaliseapServices(self.BASE_DIR)

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {_CINZA_BG};
            }}
        """)

        self.init_ui()

    def init_ui(self):
        """Inicializa a interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 35, 40, 35)
        main_layout.setSpacing(20)

        # Header
        self._create_header(main_layout)

        # Selector (Radio buttons)
        self._create_selector(main_layout)

        # Content
        self._create_content(main_layout)

        main_layout.addStretch()

    def _create_header(self, parent_layout):
        """Cria o header com título e subtítulo."""
        title = QLabel("Adicionar Dados")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {_CINZA_TEXTO};")
        parent_layout.addWidget(title)

        subtitle = QLabel("Gestão de Inscrição, Renovação e Devolução")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setStyleSheet(f"color: {_CINZA_MEDIO};")
        parent_layout.addWidget(subtitle)

    def _create_selector(self, parent_layout):
        """Cria o seletor de tipo de operação (radio buttons)."""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {_BRANCO};
                border-radius: 12px;
                border: 1px solid {_CINZA_BORDER};
            }}
        """)
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(25, 20, 25, 20)
        card_layout.setSpacing(20)

        self.radio_group = QButtonGroup(self)

        self.radio_insc = QRadioButton("Inscrição / Renovação")
        self.radio_insc.setFont(QFont("Segoe UI", 12))
        self.radio_insc.setStyleSheet(f"""
            QRadioButton {{
                color: {_CINZA_TEXTO};
            }}
            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
                border: 2px solid {_ACCENT};
                border-radius: 8px;
                background-color: white;
            }}
            QRadioButton::indicator:checked {{
                background-color: {_ACCENT};
            }}
        """)
        self.radio_insc.setChecked(True)
        self.radio_insc.toggled.connect(self._on_radio_changed)
        self.radio_group.addButton(self.radio_insc, 0)
        card_layout.addWidget(self.radio_insc)

        self.radio_dev = QRadioButton("Devolução")
        self.radio_dev.setFont(QFont("Segoe UI", 12))
        self.radio_dev.setStyleSheet(f"""
            QRadioButton {{
                color: {_CINZA_TEXTO};
            }}
            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
                border: 2px solid {_ACCENT};
                border-radius: 8px;
                background-color: white;
            }}
            QRadioButton::indicator:checked {{
                background-color: {_ACCENT};
            }}
        """)
        self.radio_dev.toggled.connect(self._on_radio_changed)
        self.radio_group.addButton(self.radio_dev, 1)
        card_layout.addWidget(self.radio_dev)

        card_layout.addStretch()
        parent_layout.addWidget(card)

    def _create_content(self, parent_layout):
        """Cria as abas de conteúdo (inscrição e devolução)."""
        self.stacked_widget = QStackedWidget()

        # Frame inscrição
        self.frame_insc = QWidget()
        frame_insc_layout = QVBoxLayout(self.frame_insc)
        frame_insc_layout.setContentsMargins(0, 0, 0, 0)
        self._create_form_inscricao(frame_insc_layout)

        # Frame devolução
        self.frame_dev = QWidget()
        frame_dev_layout = QVBoxLayout(self.frame_dev)
        frame_dev_layout.setContentsMargins(0, 0, 0, 0)
        self._create_form_devolucao(frame_dev_layout)

        self.stacked_widget.addWidget(self.frame_insc)
        self.stacked_widget.addWidget(self.frame_dev)
        self.stacked_widget.setCurrentWidget(self.frame_insc)

        parent_layout.addWidget(self.stacked_widget)

    def _create_form_inscricao(self, parent_layout):
        """Cria o formulário de inscrição/renovação."""
        # Card principal
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {_BRANCO};
                border-radius: 12px;
                border: 1px solid {_CINZA_BORDER};
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(25, 22, 25, 22)
        card_layout.setSpacing(16)

        # Grid de campos
        grid = QGridLayout()
        grid.setSpacing(10)

        self.services.carregar_municipios()

        # Campo Nome
        self.nome = self._create_labeled_field(grid, "Nome", 0, 0)

        # Campo CPF
        self.cpf = self._create_labeled_field(grid, "CPF", 0, 1)
        self.cpf.textChanged.connect(self._format_cpf)

        # Campo Município
        self.unloc = self._create_labeled_field(grid, "Município", 1, 0)
        self.unloc.textChanged.connect(self._filter_city)

        # Campo Memorando
        self.memorando = self._create_labeled_field(grid, "Memorando", 1, 1)

        # ComboBox Descrição (INSC/RENOV)
        desc_label = QLabel("Tipo")
        desc_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        grid.addWidget(desc_label, 2, 0)

        self.descricao = QComboBox()
        self.descricao.addItems(["INSC", "RENOV"])
        self.descricao.setFixedHeight(44)
        self.descricao.setStyleSheet(f"""
            QComboBox {{
                background-color: {_BRANCO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 8px;
                padding: 8px 12px;
                color: {_CINZA_TEXTO};
                font-family: 'Segoe UI';
                font-size: 13px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid {_ACCENT};
                margin-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {_BRANCO};
                color: {_CINZA_TEXTO};
                selection-background-color: {_ACCENT_LIGHT};
            }}
        """)
        grid.addWidget(self.descricao, 2, 1)

        card_layout.addLayout(grid)
        parent_layout.addWidget(card)

        # Botão Salvar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        save_btn = QPushButton("💾 Salvar")
        save_btn.setFixedHeight(44)
        save_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {_VERDE_STATUS};
                color: {_BRANCO};
                border: none;
                border-radius: 8px;
                padding: 10px 30px;
            }}
            QPushButton:hover {{
                background-color: {_VERDE_DARK};
            }}
        """)
        save_btn.clicked.connect(self._add_insc)
        btn_layout.addWidget(save_btn)
        btn_layout.addStretch()

        parent_layout.addLayout(btn_layout)

    def _create_form_devolucao(self, parent_layout):
        """Cria o formulário de devolução."""
        # Card principal
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {_BRANCO};
                border-radius: 12px;
                border: 1px solid {_CINZA_BORDER};
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(25, 22, 25, 22)
        card_layout.setSpacing(16)

        # Grid de campos
        grid = QGridLayout()
        grid.setSpacing(10)

        # Campo Nome
        self.nome_dev = self._create_labeled_field(grid, "Nome", 0, 0)

        # Campo CPF
        self.cpf_dev = self._create_labeled_field(grid, "CPF", 0, 1)
        self.cpf_dev.textChanged.connect(self._format_cpf_dev)

        # Campo Município
        self.unloc_dev = self._create_labeled_field(grid, "Município", 1, 0)
        self.unloc_dev.textChanged.connect(self._filter_city_dev)

        # Campo Memorando
        self.memo_dev = self._create_labeled_field(grid, "Memorando", 1, 1)

        card_layout.addLayout(grid)
        parent_layout.addWidget(card)

        # Card Motivo
        motivo_card = QFrame()
        motivo_card.setStyleSheet(f"""
            QFrame {{
                background-color: {_BRANCO};
                border-radius: 12px;
                border: 1px solid {_CINZA_BORDER};
            }}
        """)
        motivo_layout = QVBoxLayout(motivo_card)
        motivo_layout.setContentsMargins(25, 22, 25, 22)
        motivo_layout.setSpacing(12)

        motivo_label = QLabel("Motivo da Devolução")
        motivo_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        motivo_layout.addWidget(motivo_label)

        self.motivo_combo = QComboBox()
        self.motivo_combo.addItems(MOTIVOS_DEVOLUCAO)
        self.motivo_combo.setFixedHeight(44)
        self.motivo_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {_BRANCO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 8px;
                padding: 8px 12px;
                color: {_CINZA_TEXTO};
                font-family: 'Segoe UI';
                font-size: 13px;
            }}
        """)
        motivo_layout.addWidget(self.motivo_combo)

        self.motivo_texto = QTextEdit()
        self.motivo_texto.setFixedHeight(100)
        self.motivo_texto.setStyleSheet(f"""
            QTextEdit {{
                background-color: {_BRANCO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 8px;
                padding: 8px;
                color: {_CINZA_TEXTO};
                font-family: 'Segoe UI';
                font-size: 12px;
            }}
        """)
        motivo_layout.addWidget(self.motivo_texto)

        parent_layout.addWidget(motivo_card)

        # Botão Salvar
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        save_btn = QPushButton("💾 Salvar")
        save_btn.setFixedHeight(44)
        save_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {_VERDE_STATUS};
                color: {_BRANCO};
                border: none;
                border-radius: 8px;
                padding: 10px 30px;
            }}
            QPushButton:hover {{
                background-color: {_VERDE_DARK};
            }}
        """)
        save_btn.clicked.connect(self._add_dev)
        btn_layout.addWidget(save_btn)
        btn_layout.addStretch()

        parent_layout.addLayout(btn_layout)

    def _create_labeled_field(self, grid, label_text, row, col):
        """Helper para criar um campo com label."""
        label = QLabel(label_text)
        label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        label.setStyleSheet(f"color: {_CINZA_TEXTO};")

        entry = QLineEdit()
        entry.setPlaceholderText(f"Digite {label_text.lower()}")
        entry.setFixedHeight(44)
        entry.setStyleSheet(f"""
            QLineEdit {{
                background-color: {_BRANCO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 8px;
                padding: 8px 12px;
                color: {_CINZA_TEXTO};
                font-family: 'Segoe UI';
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 2px solid {_ACCENT};
            }}
        """)

        grid.addWidget(label, row * 2, col)
        grid.addWidget(entry, row * 2 + 1, col)

        return entry

    def _on_radio_changed(self):
        """Muda entre formulários de inscrição e devolução."""
        if self.radio_insc.isChecked():
            self.stacked_widget.setCurrentWidget(self.frame_insc)
        else:
            self.stacked_widget.setCurrentWidget(self.frame_dev)

    def _format_cpf(self, text):
        """Formata CPF automaticamente."""
        cpf_formatado = self.controller.formatar_cpf(text)
        if cpf_formatado != text:
            self.cpf.blockSignals(True)
            self.cpf.setText(cpf_formatado)
            self.cpf.blockSignals(False)

    def _format_cpf_dev(self, text):
        """Formata CPF automaticamente no formulário de devolução."""
        cpf_formatado = self.controller.formatar_cpf(text)
        if cpf_formatado != text:
            self.cpf_dev.blockSignals(True)
            self.cpf_dev.setText(cpf_formatado)
            self.cpf_dev.blockSignals(False)

    def _filter_city(self):
        """Filtra e autocompleta o município."""
        texto = self.unloc.text()
        if texto:
            cidade = self.services.filtrar_cidade(texto)
            if cidade and cidade != texto:
                self.unloc.blockSignals(True)
                self.unloc.setText(cidade)
                self.unloc.blockSignals(False)

    def _filter_city_dev(self):
        """Filtra e autocompleta o município no formulário de devolução."""
        texto = self.unloc_dev.text()
        if texto:
            cidade = self.services.filtrar_cidade(texto)
            if cidade and cidade != texto:
                self.unloc_dev.blockSignals(True)
                self.unloc_dev.setText(cidade)
                self.unloc_dev.blockSignals(False)

    def _add_insc(self):
        """Salva inscrição/renovação."""
        campos = [
            self.nome.text().strip(),
            self.cpf.text().strip(),
            self.unloc.text().strip(),
            self.memorando.text().strip(),
            self.descricao.currentText()
        ]

        if not all(campos):
            QMessageBox.warning(self, "Aviso", "Preencha todos os campos.")
            return

        sucesso, mensagem = self.controller.salvar_inscricao(
            nome=self.nome.text().strip(),
            cpf=self.cpf.text().strip(),
            municipio=self.unloc.text().strip(),
            memorando=self.memorando.text().strip(),
            tipo=self.descricao.currentText()
        )

        if sucesso:
            QMessageBox.information(self, "Sucesso", mensagem)
            self._limpar_campos_inscricao()
        else:
            QMessageBox.critical(self, "Erro", mensagem)

    def _add_dev(self):
        """Salva devolução."""
        campos = [
            self.nome_dev.text().strip(),
            self.cpf_dev.text().strip(),
            self.unloc_dev.text().strip(),
            self.memo_dev.text().strip(),
            self.motivo_combo.currentText(),
            self.motivo_texto.toPlainText().strip()
        ]

        if not all(campos):
            QMessageBox.warning(self, "Aviso", "Preencha todos os campos.")
            return

        sucesso, mensagem = self.controller.salvar_devolucao(
            nome=self.nome_dev.text().strip(),
            cpf=self.cpf_dev.text().strip(),
            municipio=self.unloc_dev.text().strip(),
            memorando=self.memo_dev.text().strip(),
            motivo_combo=self.motivo_combo.currentText(),
            motivo_texto=self.motivo_texto.toPlainText().strip()
        )

        if sucesso:
            QMessageBox.information(self, "Sucesso", mensagem)
            self._limpar_campos_devolucao()
        else:
            QMessageBox.critical(self, "Erro", mensagem)

    def _limpar_campos_inscricao(self):
        """Limpa campos do formulário de inscrição."""
        self.nome.clear()
        self.cpf.clear()
        self.unloc.clear()
        self.memorando.clear()
        self.descricao.setCurrentIndex(0)

    def _limpar_campos_devolucao(self):
        """Limpa campos do formulário de devolução."""
        self.nome_dev.clear()
        self.cpf_dev.clear()
        self.unloc_dev.clear()
        self.memo_dev.clear()
        self.motivo_combo.setCurrentIndex(0)
        self.motivo_texto.clear()