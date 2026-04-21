# -*- coding: utf-8 -*-
"""Interface de Análise de Processos — design refinado (PyQt6)."""
import os
import threading
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QLineEdit,
    QPushButton, QComboBox, QTextEdit, QRadioButton, QButtonGroup,
    QCheckBox, QFileDialog, QMessageBox, QTabWidget, QScrollArea,
    QDialog
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from .controller import AnaliseController
from .services import AnaliseService
from .views.devolucao_view import DevolucaoPopup
from .views.historico_view import HistoricoView

# ── Caminhos dos arquivos OAuth2 ─────────────────────────────────────────────
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_TOKEN_PATH = os.path.join(_BASE_DIR, "token.json")
_CREDENTIALS_PATH = os.path.join(_BASE_DIR, "credentials.json")
_GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# ── Paleta ───────────────────────────────────────────────────────────────
_VERDE = "#22c55e"
_VERDE_H = "#16a34a"
_AZUL = "#3b82f6"
_AZUL_H = "#2563eb"
_VERMELHO = "#ef4444"
_VERM_H = "#dc2626"
_MUTED = "#64748b"
_AMBER = "#f59e0b"
_BRANCO = "#ffffff"
_CINZA_BORDER = "#e2e8f0"
_CINZA_BG = "#f5f7fc"
_CINZA_TEXTO = "#1e2f3e"


def _badge(parent, texto: str, cor: str) -> QFrame:
    """Mini badge colorido."""
    frame = QFrame(parent)
    frame.setStyleSheet(f"""
        QFrame {{
            background-color: {cor};
            border-radius: 6px;
        }}
    """)
    lbl = QLabel(texto, frame)
    lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
    lbl.setStyleSheet("color: white; padding: 2px 8px;")
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout = QHBoxLayout(frame)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(lbl)
    return frame


class AnaliseUI(QWidget):
    """Interface de Análise de Processos."""

    def __init__(self, parent=None, usuario: str = None,
                 on_refresh_lancamento=None,
                 on_refresh_devolucao=None):
        super().__init__(parent)
        self.usuario = usuario
        self.service = AnaliseService()
        self.controller = AnaliseController(
            usuario, self.service.repo,
            self.service.repo_ap,
            self.service.sefaz_repo
        )
        self._on_refresh_lancamento = on_refresh_lancamento
        self._on_refresh_devolucao = on_refresh_devolucao
        self.urgencia = False
        self.registros_vars = {}
        self.registros_checkboxes = {}
        self._popup_motivos = None
        self._historico_dialog = None

        # Carrega motivos de devolução
        self._motivos = self._carregar_motivos()

        self.setStyleSheet(f"background-color: {_CINZA_BG};")
        self._build_interface()

        # Carregar dados em thread
        threading.Thread(target=self._carregar_thread, daemon=True).start()

    def closeEvent(self, event):
        """Fecha recursos abertos ao encerrar a tela."""
        try:
            self._on_close()
        finally:
            super().closeEvent(event)

    def _build_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                background-color: {_BRANCO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 8px;
            }}
            QTabBar::tab {{
                background-color: {_CINZA_BG};
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }}
            QTabBar::tab:selected {{
                background-color: {_BRANCO};
                border-bottom: 2px solid {_VERDE};
            }}
            QTabBar::tab:hover {{
                background-color: {_CINZA_BORDER};
            }}
        """)

        self.tab_analise = QWidget()
        self.tab_adicionar = QWidget()

        self.tab_widget.addTab(self.tab_analise, "  Análise de Processos  ")
        self.tab_widget.addTab(self.tab_adicionar, "  Adicionar Registro  ")

        self._build_analise()
        self._build_adicionar()

        layout.addWidget(self.tab_widget)

    # ────────────────────────────────────────────────────────────────
    # Motivos de devolução
    # ────────────────────────────────────────────────────────────────
    def _carregar_motivos(self) -> dict:
        """Motivos de devolução embutidos no código."""
        return {
            "Endereço": [
                "NOME DA COMUNIDADE ESTÁ DIVERGENTE ENTRE FAC E DECLARAÇÃO;",
                "CORRIGIR A COORDENADAS, NÃO SÃO DO ENDEREÇO DESCRITO;",
                "ENDEREÇO INCOMPLETO, FALTA A COMUNIDADE OU SE É PRODUTOR ISOLADO;",
                "ENVIAR COMO ALTERAÇÃO DE ENDEREÇO;",
                "FALTA O KM DA RODOVIA;",
                "FALTA O KM DA ESTRADA;",
                "FALTA O KM DO RAMAL;",
                "FALTA O KM DA VICINAL;",
                "COORDENADAS E ENDEREÇO ESTÃO DIVERGENTES;",
                "ENDEREÇO ESTÁ DIVERGENTE ENTRE FAC E DECLARAÇÃO;",
                "COORDENADAS INVÁLIDAS, CORRIGIR;",
                "O ENDEREÇO DA ÁREA DA PESCA ESTÁ DIVERGENTE ENTRE FAC E DECLARAÇÃO;",
                "COORDENADAS E ENDEREÇO ESTÃO DIVERGENTES, CORRIGIR;",
                "FALTA A COMUNIDADE NA DECLARAÇÃO;",
                "ENDEREÇO DIVERGENTE DA CPP, CORRIGIR OU ENVIAR COMO ALTERAÇÃO;",
            ],
            "Documentos": [
                "ENVIAR OUTRO DOCUMENTO DE IDENTIFICAÇÃO, RG, OU HABILITAÇÃO, ETC;",
                "FALTA UM DOCUMENTO DE IDENTIFICAÇÃO COM FOTO;",
                "NA RG ELE NÃO ASSINA E ASSINOU NA FAC, ENTÃO APRESENTAR UM DOCUMENTO DE IDENTIDADE COM ASSINATURA;",
                "NÚMERO DO RG DIVERGENTE DO DOCUMENTO;",
                "NOME ESTÁ DIVERGENTE ENTRE RG E CPF, ATUALIZAR DOCUMENTOS;",
                "FRENTE DO RG ESTÁ ILEGÍVEL;",
                "FALTA O RG NA DECLARAÇÃO;",
                "COPIA DO RG ESTÁ ILEGÍVEL;",
                "ASSINATURA NA RG ESTÁ ILEGÍVEL;",
                "FALTA A AUTENTICAÇÃO DO CONTRATO;",
                "CORRIGIR CPF, DIVERGENTE DOS DOCUMENTOS PESSOAIS;",
                "CONTRATO DE COMODATO NÃO PODE SER POR TEMPO INDETERMINADO, PRECISA TER UM PRAZO ESTIPULADO;",
                "COM A NOVA DATA DE VALIDADE DA CPP DE 4 ANOS, OS CONTRATOS DEVEM TER O PRAZO DE NO MÍNIMO 4 ANOS DE VALIDADE;",
                "FALTA O TERMO DE EXTRATIVISMO;",
                "ENVIAR O COMPROVANTE DA SITUAÇÃO CADASTRAL NO CPF (DO SITE DA RECEITA FEDERAL);",
                "A SITUAÇÃO CADASTRAL ESTÁ SUSPENSA, REGULARIZAR O CPF PERANTE A RECEITA FEDERAL;",
                "ENVIAR CÓPIA DE UMA DOCUMENTAÇÃO COM FOTO E ASSINATURA;",
                "NECESSITA DO BOLETIM DE OCORRÊNCIA EMITIDO PELA POLICIA CIVIL;",
                "FALTA A FOLHA DE SOLICITAÇÃO DE BAIXA DE INSCRIÇÃO ESTADUAL;",
                "CARTEIRA DE TRABALHO TRANSCRITA A MÃO, NÃO É VÁLIDA;",
            ],
            "Cadastro": [
                "CORRIGIR O NOME DA PRODUTORA NA DECLARAÇÃO;",
                "JÁ POSSUI CADASTRO, ENVIAR COMO ALTERAÇÃO OU RENOVAÇÃO;",
                "CORRIGIR A DATA NA DECLARAÇÃO;",
                "ENVIAR TAMBÉM A FAC DIGITALIZADA;",
                "ENVIAR COMO ALTERAÇÃO, ENVIAR A CÓPIA DA CPP OU O BO;",
                "ATUALIZAR A FAC E A DECLARAÇÃO, ESTÃO COM DATA SUPERIOR A 6 MESES;",
                "NÚMERO DE CONTROLE DIVERGENTE DA CPP;",
                "NÚMERO DE CONTROLE DIVERGENTE NA DECLARAÇÃO;",
                "NÚMERO DE CONTROLE ESTÁ DIVERGENTE ENTRE DECLARAÇÃO E FAC;",
                "ESTÁ SEM O NÚMERO DE CONTROLE;",
                "NOME DA PROPRIEDADE ESTÁ DIVERGENTE ENTRE FAC E DECLARAÇÃO;",
                "NOME DA PROPRIEDADE ESTÁ DIVERGENTE DA CPP;",
                "ESPECIFICAR A CULTURA SECUNDÁRIA;",
                "AS DUAS ATIVIDADES ESTÃO DIVERGENTES ENTRE FAC E DECLARAÇÃO;",
                "COLOCAR A COMUNIDADE NA DECLARAÇÃO;",
                "COMUNIDADE ESTÁ DIVERGENTE ENTRE FAC E DECLARAÇÃO;",
                "ENVIAR COMO ALTERAÇÃO, HOUVE MUDANÇA NO SOBRENOME;",
                "ENVIAR COMO ALTERAÇÃO DE ATIVIDADE;",
                "FALTA O NOME DA PROPRIEDADE NA DECLARAÇÃO;",
                "FALTA O CARIMBO DO GERENTE;",
                "FALTA A ASSINATURA DO GERENTE;",
                "FALTA A ASSINATURA DO PRODUTOR NA FAC;",
                "NOME INCOMPLETO NA DECLARAÇÃO;",
                "NOME DO PRODUTOR ESTÁ DIVERGENTE ENTRE DECLARAÇÃO E FAC;",
                "CORRIGIR A SIGLA DO MUNICIPIO;",
                "ASSINATURA DO PRODUTOR ESTÁ DIVERGENTE DA RG;",
                "ATUALIZAR A DATA NA DECLARAÇÃO, ESTÁ SUPERIOR A 6 MESES;",
                "SEM ASSINATURA E CARIMBO DO GERENTE E TÉCNICO;",
                "APAGAR O NUMERO DA INSCRIÇÃO ESTADUAL NA FAC, É UMA INSCRIÇÃO;",
            ],
            "Pesca": [
                "REGISTRO DE PESCADOR NÃO ENCONTRADO NO SITE DO MINISTÉRIO DA PESCA E AGRICULTURA, APRESENTAR A CARTEIRA DE PESCADOR ATUAL;",
                "ESPECIFICAR AS ESPÉCIES E AS QUANTIDADES DE PEIXES E A ÁREA DA PISCICULTURA;",
                "FALTA A ÁREA DA PISCICULTURA;",
            ],
            "Simples Nacional": [
                "FALTA DAR A BAIXA;",
                "SIMPLES NACIONAL ATIVO;",
                "SIMPLES NACIONAL SUSPENSO;",
            ],
            "Animais": [
                "FALTA A QUANTIDADE DE FRANGOS;",
                "FALTA A QUANTIDADE E AS ESPÉCIES DE PEIXES;",
                "ENVIAR O COMPROVANTE DE SITUAÇÃO CADASTRAL NO CPF (DO SITE DA RECEITA FEDERAL);",
            ],
            "Outros": [],
        }

    def _abrir_motivos(self, categoria: str):
        """Abre popup com os motivos da categoria selecionada."""
        motivos = self._motivos.get(categoria, [])
        if not motivos:
            return

        popup = QDialog(self)
        popup.setWindowTitle(f"Motivos — {categoria}")
        popup.setModal(True)
        popup.setFixedSize(520, 420)
        popup.setStyleSheet(f"background-color: {_CINZA_BG};")

        layout = QVBoxLayout(popup)
        layout.setContentsMargins(24, 18, 24, 18)
        layout.setSpacing(16)

        lbl_title = QLabel(f"Selecione o motivo — {categoria}")
        lbl_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        layout.addWidget(lbl_title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: transparent;")

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(2)

        for mot in motivos:
            btn = QPushButton(mot)
            btn.setStyleSheet(f"""
                QPushButton {{
                    text-align: left;
                    padding: 8px 12px;
                    border: none;
                    border-radius: 6px;
                    background-color: {_BRANCO};
                    color: {_CINZA_TEXTO};
                    font-family: 'Segoe UI';
                    font-size: 11px;
                }}
                QPushButton:hover {{
                    background-color: {_CINZA_BORDER};
                }}
            """)
            btn.clicked.connect(lambda checked=False, m=mot, p=popup: self._selecionar_motivo(m, p))
            scroll_layout.addWidget(btn)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        self._popup_motivos = popup
        popup.exec()

    def _selecionar_motivo(self, motivo: str, popup):
        """Seleciona um motivo e fecha o popup."""
        self.motivo.setText(motivo)
        popup.accept()

    def _on_close(self):
        self.controller.fechar_driver()

    # ────────────────────────────────────────────────────────────────
    # ABA 1 — ANÁLISE
    # ────────────────────────────────────────────────────────────────
    def _build_analise(self):
        main_layout = QVBoxLayout(self.tab_analise)
        main_layout.setContentsMargins(0, 0, 0, 0)

        wrap = QWidget(self.tab_analise)
        wrap.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(wrap)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(20)

        # cabeçalho
        hdr = QWidget()
        hdr_layout = QHBoxLayout(hdr)
        hdr_layout.setContentsMargins(0, 0, 0, 20)
        lbl_title = QLabel("Análise de Processos")
        lbl_title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        hdr_layout.addWidget(lbl_title)
        layout.addWidget(hdr)

        # barra de ações
        bar = QFrame()
        bar.setStyleSheet(f"""
            QFrame {{
                background-color: {_BRANCO};
                border-radius: 14px;
                border: 1px solid {_CINZA_BORDER};
            }}
        """)
        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(20, 14, 20, 14)
        bar_layout.setSpacing(12)

        self.chk_urgencia = QCheckBox("URGÊNCIA")
        self.chk_urgencia.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.chk_urgencia.setStyleSheet(f"""
            QCheckBox {{
                color: {_CINZA_TEXTO};
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid {_AMBER};
            }}
            QCheckBox::indicator:checked {{
                background-color: {_AMBER};
            }}
        """)
        bar_layout.addWidget(self.chk_urgencia)

        # separador
        sep = QFrame()
        sep.setFixedSize(1, 28)
        sep.setStyleSheet(f"background-color: {_CINZA_BORDER};")
        bar_layout.addWidget(sep)

        for txt, cmd, cor, hov in [
            ("Selecionar PDFs", self.select_pdfs, _VERDE, _VERDE_H),
            ("SEFAZ + Google Maps", self._abrir_sefaz_thread, _AZUL, _AZUL_H),
            ("Atualizar", self.carregar_do_banco, _MUTED, _CINZA_BORDER),
        ]:
            btn = QPushButton(f"  {txt}")
            btn.setFixedHeight(36)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {cor};
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-size: 12px;
                    padding: 0 16px;
                }}
                QPushButton:hover {{
                    background-color: {hov};
                }}
            """)
            btn.clicked.connect(cmd)
            bar_layout.addWidget(btn)

        bar_layout.addStretch()

        btn_historico = QPushButton("  Histórico")
        btn_historico.setFixedHeight(36)
        btn_historico.setStyleSheet(f"""
            QPushButton {{
                background-color: {_CINZA_BG};
                color: {_CINZA_TEXTO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 10px;
                font-size: 12px;
                padding: 0 16px;
            }}
            QPushButton:hover {{
                background-color: {_CINZA_BORDER};
            }}
        """)
        btn_historico.clicked.connect(self.abrir_historico)
        bar_layout.addWidget(btn_historico)

        layout.addWidget(bar)

        # corpo da tabela (scroll area)
        self.tabela_container = QScrollArea()
        self.tabela_container.setWidgetResizable(True)
        self.tabela_container.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: {_BRANCO};
                border-radius: 14px;
            }}
        """)

        self.tabela_content = QWidget()
        self.tabela_layout = QVBoxLayout(self.tabela_content)
        self.tabela_layout.setContentsMargins(0, 0, 0, 0)
        self.tabela_layout.setSpacing(4)
        self.tabela_layout.addStretch()

        self.tabela_container.setWidget(self.tabela_content)
        layout.addWidget(self.tabela_container)

        # rodapé de ações em lote
        rodape = QWidget()
        rodape_layout = QHBoxLayout(rodape)
        rodape_layout.setContentsMargins(0, 12, 0, 0)
        rodape_layout.setSpacing(10)

        btn_selecionar_todos = QPushButton("Selecionar Todos")
        btn_selecionar_todos.setFixedSize(140, 40)
        btn_selecionar_todos.setStyleSheet(f"""
            QPushButton {{
                background-color: {_CINZA_BG};
                color: {_CINZA_TEXTO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 10px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {_CINZA_BORDER};
            }}
        """)
        btn_selecionar_todos.clicked.connect(self._selecionar_todos)
        rodape_layout.addWidget(btn_selecionar_todos)

        for txt, cmd, cor, hov in [
            ("Renovação", lambda: self.processar("RENOVACAO"), _VERDE, _VERDE_H),
            ("Inscrição", lambda: self.processar("INSCRICAO"), _AZUL, _AZUL_H),
            ("Devolução", self.processar_devolucao, _VERMELHO, _VERM_H),
            ("Enviar E-mail", self.abrir_popup_email, _AMBER, "#d97706"),
        ]:
            btn = QPushButton(txt)
            btn.setFixedHeight(40)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {cor};
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 0 20px;
                }}
                QPushButton:hover {{
                    background-color: {hov};
                }}
            """)
            btn.clicked.connect(cmd)
            rodape_layout.addWidget(btn)

        rodape_layout.addStretch()
        layout.addWidget(rodape)

        main_layout.addWidget(wrap)

    # ────────────────────────────────────────────────────────────────
    # ABA 2 — ADICIONAR
    # ────────────────────────────────────────────────────────────────
    def _build_adicionar(self):
        scroll = QScrollArea(self.tab_adicionar)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: transparent;")

        wrap = QWidget()
        wrap.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(wrap)
        layout.setContentsMargins(40, 28, 40, 28)
        layout.setSpacing(20)

        lbl_title = QLabel("Adicionar Registro")
        lbl_title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        layout.addWidget(lbl_title)

        # tipo selector
        tipo_card = QFrame()
        tipo_card.setStyleSheet(f"""
            QFrame {{
                background-color: {_BRANCO};
                border-radius: 14px;
                border: 1px solid {_CINZA_BORDER};
            }}
        """)
        tipo_layout = QVBoxLayout(tipo_card)
        tipo_layout.setContentsMargins(20, 16, 20, 16)

        tipo_inner = QHBoxLayout()
        self.radio_group = QButtonGroup(self)

        self.radio_insc = QRadioButton("Inscrição")
        self.radio_insc.setChecked(True)
        self.radio_insc.toggled.connect(self._reset_form)
        self.radio_group.addButton(self.radio_insc)
        tipo_inner.addWidget(self.radio_insc)

        self.radio_dev = QRadioButton("Devolução")
        self.radio_dev.toggled.connect(self._reset_form)
        self.radio_group.addButton(self.radio_dev)
        tipo_inner.addWidget(self.radio_dev)

        tipo_inner.addStretch()
        tipo_layout.addLayout(tipo_inner)
        layout.addWidget(tipo_card)

        # formulário
        form_card = QFrame()
        form_card.setStyleSheet(f"""
            QFrame {{
                background-color: {_BRANCO};
                border-radius: 14px;
                border: 1px solid {_CINZA_BORDER};
            }}
        """)
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(28, 24, 28, 24)
        form_layout.setSpacing(12)

        def _create_field(label_text, placeholder):
            lbl = QLabel(label_text)
            lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            lbl.setStyleSheet(f"color: {_MUTED};")
            entry = QLineEdit()
            entry.setPlaceholderText(placeholder)
            entry.setFixedHeight(44)
            entry.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {_CINZA_BG};
                    border: 1px solid {_CINZA_BORDER};
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-size: 13px;
                }}
                QLineEdit:focus {{
                    border: 2px solid {_VERDE};
                }}
            """)
            form_layout.addWidget(lbl)
            form_layout.addWidget(entry)
            return entry

        # Campos comuns
        self.nome = _create_field("Nome Completo *", "Ex: João da Silva")
        self.cpf = _create_field("CPF *", "000.000.000-00")
        self.cpf.textChanged.connect(self._formatar_cpf)

        self.municipio = _create_field("Município *", "Ex: Manaus")
        self.memorando = _create_field("Memorando *", "Ex: 001/2025")

        # Campo exclusivo inscrição
        lbl_tipo = QLabel("Tipo")
        lbl_tipo.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        lbl_tipo.setStyleSheet(f"color: {_MUTED};")
        form_layout.addWidget(lbl_tipo)

        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["INSC", "RENOV"])
        self.tipo_combo.setFixedHeight(44)
        self.tipo_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {_CINZA_BG};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
            }}
        """)
        form_layout.addWidget(self.tipo_combo)

        # Campos exclusivos devolução (ocultos inicialmente)
        lbl_categoria = QLabel("Categoria *")
        lbl_categoria.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        lbl_categoria.setStyleSheet(f"color: {_MUTED};")
        form_layout.addWidget(lbl_categoria)

        self.categoria_combo = QComboBox()
        self.categoria_combo.addItems(["Endereço", "Documentos", "Cadastro", "Pesca", "Simples Nacional", "Animais", "Outros"])
        self.categoria_combo.setFixedHeight(44)
        self.categoria_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {_CINZA_BG};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
            }}
        """)
        self.categoria_combo.currentTextChanged.connect(self._abrir_motivos)
        form_layout.addWidget(self.categoria_combo)

        lbl_motivo = QLabel("Motivo da Devolução *")
        lbl_motivo.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        lbl_motivo.setStyleSheet(f"color: {_MUTED};")
        form_layout.addWidget(lbl_motivo)

        self.motivo = QTextEdit()
        self.motivo.setPlaceholderText("Digite o motivo da devolução...")
        self.motivo.setFixedHeight(100)
        self.motivo.setStyleSheet(f"""
            QTextEdit {{
                background-color: {_CINZA_BG};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 8px;
                padding: 8px;
                font-size: 12px;
            }}
            QTextEdit:focus {{
                border: 2px solid {_VERDE};
            }}
        """)
        form_layout.addWidget(self.motivo)

        # Ocultar campos de devolução inicialmente
        lbl_categoria.hide()
        self.categoria_combo.hide()
        lbl_motivo.hide()
        self.motivo.hide()

        self._lbl_categoria = lbl_categoria
        self._lbl_motivo = lbl_motivo
        self._lbl_tipo = lbl_tipo

        # Botões
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        btn_salvar = QPushButton("💾 Salvar Registro")
        btn_salvar.setFixedHeight(50)
        btn_salvar.setStyleSheet(f"""
            QPushButton {{
                background-color: {_VERDE};
                color: white;
                border: none;
                border-radius: 14px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {_VERDE_H};
            }}
        """)
        btn_salvar.clicked.connect(self._salvar_registro)
        btn_row.addWidget(btn_salvar)

        btn_email = QPushButton("📧 Enviar E-mail")
        btn_email.setFixedHeight(50)
        btn_email.setStyleSheet(f"""
            QPushButton {{
                background-color: {_AMBER};
                color: white;
                border: none;
                border-radius: 14px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #d97706;
            }}
        """)
        btn_email.clicked.connect(self._enviar_email_form)
        btn_row.addWidget(btn_email)

        form_layout.addLayout(btn_row)
        layout.addWidget(form_card)

        scroll.setWidget(wrap)
        main_layout = QVBoxLayout(self.tab_adicionar)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    # ────────────────────────────────────────────────────────────────
    # Helpers — reset form
    # ────────────────────────────────────────────────────────────────
    def _reset_form(self):
        """Mostra/oculta campos conforme tipo selecionado."""
        is_dev = self.radio_dev.isChecked()

        if is_dev:
            self._lbl_tipo.hide()
            self.tipo_combo.hide()
            self._lbl_categoria.show()
            self.categoria_combo.show()
            self._lbl_motivo.show()
            self.motivo.show()
        else:
            self._lbl_categoria.hide()
            self.categoria_combo.hide()
            self._lbl_motivo.hide()
            self.motivo.hide()
            self._lbl_tipo.show()
            self.tipo_combo.show()

    # ────────────────────────────────────────────────────────────────
    # Formatação CPF
    # ────────────────────────────────────────────────────────────────
    def _formatar_cpf(self, text):
        """Formata CPF automaticamente."""
        cpf_formatado = self.controller.formatar_cpf(text)
        if cpf_formatado != text:
            self.cpf.blockSignals(True)
            self.cpf.setText(cpf_formatado)
            self.cpf.blockSignals(False)

    # ────────────────────────────────────────────────────────────────
    # Carregar registros — em thread
    # ────────────────────────────────────────────────────────────────
    def _carregar_thread(self):
        try:
            registros = self.controller.carregar_registros_pendentes()
            QTimer.singleShot(0, lambda: self._preencher_tabela(registros))
        except Exception as exc:
            QTimer.singleShot(0, lambda: QMessageBox.critical(
                self, "Erro", f"Erro ao carregar dados:\n{exc}"))

    def carregar_do_banco(self):
        """Limpa tabela e recarrega em thread."""
        self._limpar_tabela()
        self._mostrar_mensagem_carregando()
        threading.Thread(target=self._carregar_thread, daemon=True).start()

    def _limpar_tabela(self):
        """Remove todos os itens da tabela."""
        while self.tabela_layout.count() > 1:
            item = self.tabela_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.registros_vars.clear()
        self.registros_checkboxes.clear()

    def _mostrar_mensagem_carregando(self):
        lbl = QLabel("Carregando...")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(f"color: {_MUTED}; font-size: 12px; padding: 30px;")
        self.tabela_layout.insertWidget(0, lbl)

    def _preencher_tabela(self, registros: list):
        self._limpar_tabela()
        if not registros:
            lbl = QLabel("Nenhum registro pendente.")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(f"color: {_MUTED}; font-size: 13px; padding: 40px;")
            self.tabela_layout.insertWidget(0, lbl)
            return

        for reg in registros:
            self._criar_linha(reg)

    def _criar_linha(self, reg: dict):
        """Cria uma linha na tabela para um registro."""
        linha = QFrame()
        linha.setStyleSheet(f"""
            QFrame {{
                background-color: {_BRANCO};
                border-radius: 10px;
                border: 1px solid {_CINZA_BORDER};
                margin: 2px 6px;
            }}
            QFrame:hover {{
                background-color: {_CINZA_BG};
            }}
        """)

        layout = QHBoxLayout(linha)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        # Checkbox
        chk = QCheckBox()
        chk.setStyleSheet(f"""
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid {_VERDE};
            }}
            QCheckBox::indicator:checked {{
                background-color: {_VERDE};
            }}
        """)
        layout.addWidget(chk)
        self.registros_checkboxes[reg["id"]] = chk

        # Nome do PDF (clicável)
        lbl_nome = QLabel(reg["nome_pdf"])
        lbl_nome.setStyleSheet(f"color: {_AZUL}; text-decoration: underline;")
        lbl_nome.setCursor(Qt.CursorShape.PointingHandCursor)
        lbl_nome.mousePressEvent = lambda e, aid=reg["id"]: self.visualizar_pdf(aid)
        layout.addWidget(lbl_nome, 1)

        # Badge urgência
        if reg.get("urgencia", False):
            badge = _badge(linha, "URGENTE", _AMBER)
            layout.addWidget(badge)
        else:
            lbl_normal = QLabel("Normal")
            lbl_normal.setFixedWidth(90)
            lbl_normal.setStyleSheet(f"color: {_MUTED};")
            layout.addWidget(lbl_normal)

        # Data
        criado = reg.get("criado_em")
        if isinstance(criado, str):
            try:
                criado = datetime.fromisoformat(criado)
            except ValueError:
                criado = datetime.now()
        data_txt = criado.strftime("%d/%m/%Y %H:%M") if criado else "—"
        lbl_data = QLabel(data_txt)
        lbl_data.setFixedWidth(130)
        lbl_data.setStyleSheet(f"color: {_MUTED};")
        layout.addWidget(lbl_data)

        # Botões
        btn_ver = QPushButton("Ver")
        btn_ver.setFixedSize(44, 30)
        btn_ver.setStyleSheet(f"""
            QPushButton {{
                background-color: {_AZUL};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 11px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {_AZUL_H};
            }}
        """)
        btn_ver.clicked.connect(lambda checked=False, aid=reg["id"]: self.visualizar_pdf(aid))
        layout.addWidget(btn_ver)

        btn_download = QPushButton("↓")
        btn_download.setFixedSize(32, 30)
        btn_download.setStyleSheet(f"""
            QPushButton {{
                background-color: {_CINZA_BG};
                color: {_CINZA_TEXTO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 8px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {_CINZA_BORDER};
            }}
        """)
        btn_download.clicked.connect(lambda checked=False, aid=reg["id"], n=reg["nome_pdf"]: self.baixar_pdf(aid, n))
        layout.addWidget(btn_download)

        self.tabela_layout.insertWidget(self.tabela_layout.count() - 1, linha)

    # ────────────────────────────────────────────────────────────────
    # Selecionar todos
    # ────────────────────────────────────────────────────────────────
    def _selecionar_todos(self):
        if not self.registros_checkboxes:
            return
        novo = not all(chk.isChecked() for chk in self.registros_checkboxes.values())
        for chk in self.registros_checkboxes.values():
            chk.setChecked(novo)

    def _get_ids_selecionados(self):
        return [i for i, chk in self.registros_checkboxes.items() if chk.isChecked()]

    # ────────────────────────────────────────────────────────────────
    # Ações
    # ────────────────────────────────────────────────────────────────
    def select_pdfs(self):
        caminhos, _ = QFileDialog.getOpenFileNames(
            self, "Selecionar PDFs", "", "PDF Files (*.pdf)"
        )
        if not caminhos:
            return
        sucesso, erros = self.controller.salvar_pdfs(
            caminhos, self.chk_urgencia.isChecked())
        msg = f"{sucesso} PDF(s) adicionado(s)."
        if erros:
            msg += f"\n\nErros ({len(erros)}):\n" + "\n".join(erros[:5])
            if len(erros) > 5:
                msg += f"\n... e mais {len(erros) - 5}."
        if sucesso:
            QMessageBox.information(self, "Sucesso", msg)
            self.carregar_do_banco()
        else:
            QMessageBox.critical(self, "Erro", msg)

    def visualizar_pdf(self, analise_id):
        ok, msg = self.controller.visualizar_pdf(analise_id)
        if not ok:
            QMessageBox.critical(self, "Erro", msg)

    def baixar_pdf(self, analise_id, nome):
        resultado = self.controller.baixar_pdf(analise_id, nome)
        if isinstance(resultado, tuple) and len(resultado) == 3 and resultado[0]:
            caminho, _ = QFileDialog.getSaveFileName(
                self, "Salvar PDF", nome.replace('/', '_').replace('\\', '_'), "PDF Files (*.pdf)"
            )
            if caminho:
                with open(caminho, 'wb') as f:
                    f.write(resultado[1])
                QMessageBox.information(self, "Salvo", f"PDF salvo em:\n{caminho}")
        elif isinstance(resultado, tuple) and resultado[0] is False and resultado[1] != "Operação cancelada":
            QMessageBox.critical(self, "Erro", resultado[1])

    def processar(self, novo_status: str):
        ids = self._get_ids_selecionados()
        if not ids:
            QMessageBox.warning(self, "Atenção", "Nenhum registro selecionado.")
            return
        ok, msg = self.controller.processar_registros(ids, novo_status)
        if ok:
            QMessageBox.information(self, "Sucesso", msg)
            self.carregar_do_banco()
            if callable(self._on_refresh_lancamento):
                try:
                    self._on_refresh_lancamento()
                except Exception:
                    pass
        else:
            QMessageBox.critical(self, "Erro", msg)

    def processar_devolucao(self):
        ids = self._get_ids_selecionados()
        if not ids:
            QMessageBox.warning(self, "Atenção", "Nenhum registro selecionado.")
            return

        def _confirmar(motivo):
            ok, msg = self.controller.processar_devolucao(ids, motivo)
            if ok:
                QMessageBox.information(self, "Sucesso", msg)
                self.carregar_do_banco()
                if callable(self._on_refresh_devolucao):
                    try:
                        self._on_refresh_devolucao()
                    except Exception:
                        pass
            else:
                QMessageBox.critical(self, "Erro", msg)

        popup = DevolucaoPopup(self, _confirmar)
        popup.exec()

    def _abrir_sefaz_thread(self):
        threading.Thread(target=self._abrir_sefaz, daemon=True).start()

    def _abrir_sefaz(self):
        ok, msg = self.controller.abrir_sefaz()
        if not ok:
            QTimer.singleShot(0, lambda: QMessageBox.critical(self, "Erro", msg))

    def _salvar_registro(self):
        nome = self.nome.text().strip()
        cpf_txt = self.cpf.text().strip()
        muni = self.municipio.text().strip()
        memo_val = self.memorando.text().strip()

        if not nome:
            QMessageBox.warning(self, "Atenção", "Informe o nome completo!")
            self.nome.setFocus()
            return
        if not self.controller.validar_cpf(cpf_txt):
            QMessageBox.warning(self, "Atenção", "CPF deve conter 11 dígitos!")
            self.cpf.setFocus()
            return
        if not muni:
            QMessageBox.warning(self, "Atenção", "Informe o município!")
            self.municipio.setFocus()
            return
        if not memo_val:
            QMessageBox.warning(self, "Atenção", "Informe o memorando!")
            self.memorando.setFocus()
            return

        tipo_reg = "dev" if self.radio_dev.isChecked() else "insc"
        dados = {
            "nome": nome,
            "cpf": self.controller.limpar_cpf(cpf_txt),
            "municipio": muni,
            "memorando": memo_val,
        }

        if tipo_reg == "insc":
            dados["tipo"] = self.tipo_combo.currentText()
        else:
            dados["categoria"] = self.categoria_combo.currentText()
            dados["motivo"] = self.motivo.toPlainText().strip()
            if not dados["motivo"]:
                QMessageBox.warning(self, "Atenção", "Informe o motivo da devolução!")
                self.motivo.setFocus()
                return

        ok, msg = self.controller.salvar_registro(tipo_reg, dados)
        if ok:
            self.nome.clear()
            self.cpf.clear()
            self.municipio.clear()
            self.memorando.clear()
            self.motivo.clear()
            self.tipo_combo.setCurrentIndex(0)
            self.categoria_combo.setCurrentIndex(0)
            QMessageBox.information(self, "Sucesso", msg)
        else:
            QMessageBox.critical(self, "Erro", msg)

    # ────────────────────────────────────────────────────────────────
    # E-mail (métodos simplificados - implementar conforme necessário)
    # ────────────────────────────────────────────────────────────────
    def abrir_popup_email(self):
        QMessageBox.information(self, "E-mail", "Funcionalidade de envio de e-mail em desenvolvimento.")

    def _enviar_email_form(self):
        QMessageBox.information(self, "E-mail", "Funcionalidade de envio de e-mail em desenvolvimento.")

    def abrir_historico(self):
        self._historico_dialog = HistoricoView(self, self.usuario, self.controller)
        self._historico_dialog.exec()