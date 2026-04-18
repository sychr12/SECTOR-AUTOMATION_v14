# views/carteira_view.py
# -*- coding: utf-8 -*-
"""
carteira_view.py — Interface principal da Carteira Digital.
Versão PyQt6.
"""
import os
import re
import threading
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QLineEdit,
    QPushButton, QTextEdit, QScrollArea, QFileDialog, QMessageBox,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPixmap

from PIL import Image

from ..controller import CarteiraController
from ..carteira_service import CarteiraService
from .batch_view import BatchCarteiraView
from .historico_view import HistoricoView

# ── Cores ─────────────────────────────────────────────────────────────────────
_VERDE = "#22c55e"
_VERDE_H = "#16a34a"
_AZUL = "#3b82f6"
_AZUL_H = "#2563eb"
_MUTED = "#64748b"
_VERMELHO = "#ef4444"
_BRANCO = "#ffffff"
_CINZA_BG = "#f8fafc"
_CINZA_BORDER = "#e2e8f0"
_CINZA_TEXTO = "#1e2f3e"

MAX_FILENAME_DISPLAY = 30
DEBOUNCE_DELAY = 120


class CarteiraDigitalUI(QWidget):
    """Interface principal da carteira digital"""

    def __init__(self, parent=None, usuario=None):
        super().__init__(parent)
        self.usuario = usuario
        self.service = CarteiraService()
        self.controller = CarteiraController(usuario, self.service)

        self.lado = "frente"
        self._after_id = None
        self._pdf_path = None
        self.fotos = {"foto1": None, "foto2": None, "foto3": None}
        self._lbl_fotos = {}
        self._labels_frente = {}
        self._labels_verso = {}

        self.setStyleSheet(f"background-color: {_CINZA_BG};")
        self._setup_ui()
        self._setup_shortcuts()

    # ── Atalhos ───────────────────────────────────────────────────────────────
    def _setup_shortcuts(self):
        # Atalhos serão implementados via eventFilter se necessário
        pass

    # ── Layout principal ──────────────────────────────────────────────────────
    def _setup_ui(self):
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
                padding: 10px 24px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {_BRANCO};
                border-bottom: 2px solid {_VERDE};
            }}
        """)

        # Aba 1 — Gerar em Lote
        aba_batch = QWidget()
        BatchCarteiraView(
            aba_batch,
            usuario=self.usuario,
            repo=self.service,
            sefaz_repo=self.service.sefaz_repo,
        )
        batch_layout = QVBoxLayout(aba_batch)
        batch_layout.setContentsMargins(0, 0, 0, 0)
        self.tab_widget.addTab(aba_batch, "  Gerar em Lote  ")

        # Aba 2 — Cadastro Individual
        aba_individual = QWidget()
        self.tab_widget.addTab(aba_individual, "  Cadastro Individual  ")
        self._build_individual_tab(aba_individual)

        layout.addWidget(self.tab_widget)

    # ── Aba de Cadastro Individual ────────────────────────────────────────────
    def _build_individual_tab(self, parent):
        layout = QHBoxLayout(parent)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(28)

        self._build_card_preview(layout)
        self._build_form(layout)

    def _build_card_preview(self, parent_layout):
        col = QFrame()
        col.setStyleSheet("background-color: transparent;")
        col_layout = QVBoxLayout(col)
        col_layout.setContentsMargins(0, 0, 0, 0)
        col_layout.setSpacing(8)

        lbl_title = QLabel("PRÉVIA DO CARTÃO")
        lbl_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        lbl_title.setStyleSheet(f"color: {_MUTED};")
        col_layout.addWidget(lbl_title)

        card_container = QFrame()
        card_container.setStyleSheet(f"""
            QFrame {{
                background-color: {_CINZA_BG};
                border-radius: 16px;
                border: 1px solid {_CINZA_BORDER};
            }}
        """)
        card_layout = QVBoxLayout(card_container)
        card_layout.setContentsMargins(12, 12, 12, 12)

        self.card = QFrame()
        self.card.setFixedSize(self.controller.CARD_W, self.controller.CARD_H)
        self.card.setStyleSheet("background-color: transparent;")
        card_layout.addWidget(self.card)
        col_layout.addWidget(card_container)

        # Botões
        btn_virar = QPushButton("🔄  Virar cartão")
        btn_virar.setFixedHeight(40)
        btn_virar.setStyleSheet(f"""
            QPushButton {{
                background-color: {_BRANCO};
                color: {_CINZA_TEXTO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 10px;
                font-size: 11px;
            }}
            QPushButton:hover {{ background-color: {_CINZA_BORDER}; }}
        """)
        btn_virar.clicked.connect(self._virar_cartao)
        col_layout.addWidget(btn_virar)

        btn_salvar = QPushButton("💾  Salvar no Banco")
        btn_salvar.setFixedHeight(40)
        btn_salvar.setStyleSheet(f"""
            QPushButton {{
                background-color: {_VERDE};
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 11px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {_VERDE_H}; }}
        """)
        btn_salvar.clicked.connect(self._salvar_banco)
        col_layout.addWidget(btn_salvar)

        btn_historico = QPushButton("📜  Histórico")
        btn_historico.setFixedHeight(40)
        btn_historico.setStyleSheet(f"""
            QPushButton {{
                background-color: {_AZUL};
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 11px;
            }}
            QPushButton:hover {{ background-color: {_AZUL_H}; }}
        """)
        btn_historico.clicked.connect(self.abrir_historico)
        col_layout.addWidget(btn_historico)

        btn_limpar = QPushButton("🗑️  Limpar Formulário")
        btn_limpar.setFixedHeight(40)
        btn_limpar.setStyleSheet(f"""
            QPushButton {{
                background-color: {_BRANCO};
                color: {_CINZA_TEXTO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 10px;
                font-size: 11px;
            }}
            QPushButton:hover {{ background-color: {_CINZA_BORDER}; }}
        """)
        btn_limpar.clicked.connect(self._confirmar_limpar)
        col_layout.addWidget(btn_limpar)

        col_layout.addStretch()
        parent_layout.addWidget(col)

    def _build_form(self, parent_layout):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: transparent;")
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(16)

        # Dados do Produtor
        scroll_layout.addWidget(self._create_section_title("DADOS DO PRODUTOR"))
        form_panel = self._create_form_panel()
        
        self.registro = self._create_field(form_panel, "Registro estadual")
        
        # CPF com botão de busca
        cpf_row = QHBoxLayout()
        self.cpf = QLineEdit()
        self.cpf.setPlaceholderText("CPF")
        self.cpf.textChanged.connect(self._debounce_preview)
        self.cpf.setStyleSheet(self._entry_style())
        cpf_row.addWidget(self.cpf)
        
        self._btn_buscar_cpf = QPushButton("🔍 Buscar CPF")
        self._btn_buscar_cpf.setFixedSize(130, 36)
        self._btn_buscar_cpf.setStyleSheet(f"""
            QPushButton {{
                background-color: {_AZUL};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {_AZUL_H}; }}
        """)
        self._btn_buscar_cpf.clicked.connect(self._buscar_por_cpf)
        cpf_row.addWidget(self._btn_buscar_cpf)
        
        self._lbl_buscar_status = QLabel("")
        self._lbl_buscar_status.setFont(QFont("Segoe UI", 9))
        self._lbl_buscar_status.setStyleSheet(f"color: {_MUTED};")
        cpf_row.addWidget(self._lbl_buscar_status)
        
        form_panel.layout().addLayout(cpf_row)
        
        self.nome = self._create_field(form_panel, "Nome do produtor")
        self.propriedade = self._create_field(form_panel, "Propriedade")
        
        # Linha com UNLOC, Início, Validade
        row_layout = QHBoxLayout()
        self.unloc = self._create_field_inline(row_layout, "UNLOC")
        self.inicio = self._create_field_inline(row_layout, "Início")
        self.validade = self._create_field_inline(row_layout, "Validade")
        form_panel.layout().addLayout(row_layout)
        
        scroll_layout.addWidget(form_panel)

        # Informações Complementares
        scroll_layout.addWidget(self._create_section_title("INFORMAÇÕES COMPLEMENTARES"))
        form_panel2 = self._create_form_panel()
        self.endereco = self._create_field(form_panel2, "Endereço")
        self.atividade1 = self._create_field(form_panel2, "Atividade primária")
        self.atividade2 = self._create_field(form_panel2, "Atividade secundária")
        self.georef = self._create_field(form_panel2, "Georreferenciamento")
        scroll_layout.addWidget(form_panel2)

        # Importar PDF
        scroll_layout.addWidget(self._create_section_title("IMPORTAR PDF DA CARTEIRA"))
        pdf_panel = self._create_form_panel()
        self._build_import_pdf(pdf_panel)
        scroll_layout.addWidget(pdf_panel)

        # Fotos
        scroll_layout.addWidget(self._create_section_title("FOTOS"))
        fotos_panel = self._create_form_panel()
        self._build_photos_section(fotos_panel)
        scroll_layout.addWidget(fotos_panel)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        parent_layout.addWidget(scroll, 1)

    def _entry_style(self):
        return f"""
            QLineEdit {{
                background-color: {_BRANCO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12px;
            }}
            QLineEdit:focus {{
                border: 2px solid {_AZUL};
            }}
        """

    def _create_section_title(self, text):
        label = QLabel(text)
        label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        label.setStyleSheet(f"color: {_VERDE}; margin-top: 8px;")
        return label

    def _create_form_panel(self):
        panel = QFrame()
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: {_BRANCO};
                border-radius: 12px;
                border: 1px solid {_CINZA_BORDER};
            }}
        """)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        return panel

    def _create_field(self, parent, placeholder):
        entry = QLineEdit()
        entry.setPlaceholderText(placeholder)
        entry.textChanged.connect(self._debounce_preview)
        entry.setStyleSheet(self._entry_style())
        parent.layout().addWidget(entry)
        return entry

    def _create_field_inline(self, parent_layout, placeholder):
        entry = QLineEdit()
        entry.setPlaceholderText(placeholder)
        entry.textChanged.connect(self._debounce_preview)
        entry.setStyleSheet(self._entry_style())
        parent_layout.addWidget(entry)
        return entry

    def _build_import_pdf(self, parent):
        layout = QHBoxLayout()
        
        self._btn_importar_pdf = QPushButton("📄 Selecionar PDF")
        self._btn_importar_pdf.setFixedSize(160, 38)
        self._btn_importar_pdf.setStyleSheet(f"""
            QPushButton {{
                background-color: {_AZUL};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {_AZUL_H}; }}
        """)
        self._btn_importar_pdf.clicked.connect(self._select_pdf)
        layout.addWidget(self._btn_importar_pdf)
        
        self._lbl_pdf = QLabel("Nenhum PDF selecionado")
        self._lbl_pdf.setFont(QFont("Segoe UI", 11))
        self._lbl_pdf.setStyleSheet(f"color: {_MUTED};")
        layout.addWidget(self._lbl_pdf)
        layout.addStretch()
        
        parent.layout().addLayout(layout)
        
        # Linha para extrair
        layout2 = QHBoxLayout()
        self._btn_extrair = QPushButton("🔍 Extrair Informações do PDF")
        self._btn_extrair.setFixedSize(220, 38)
        self._btn_extrair.setEnabled(False)
        self._btn_extrair.setStyleSheet(f"""
            QPushButton {{
                background-color: {_BRANCO};
                color: {_CINZA_TEXTO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 8px;
                font-size: 11px;
            }}
            QPushButton:hover {{ background-color: {_CINZA_BORDER}; }}
        """)
        self._btn_extrair.clicked.connect(self._extract_pdf)
        layout2.addWidget(self._btn_extrair)
        
        self._lbl_extrair_status = QLabel("")
        self._lbl_extrair_status.setFont(QFont("Segoe UI", 11))
        self._lbl_extrair_status.setStyleSheet(f"color: {_MUTED};")
        layout2.addWidget(self._lbl_extrair_status)
        layout2.addStretch()
        
        parent.layout().addLayout(layout2)

    def _build_photos_section(self, parent):
        for i in range(1, 4):
            chave = f"foto{i}"
            row = QHBoxLayout()
            
            btn = QPushButton(f"📷 Foto {i}")
            btn.setFixedSize(120, 36)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {_AZUL};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 11px;
                }}
                QPushButton:hover {{ background-color: {_AZUL_H}; }}
            """)
            btn.clicked.connect(lambda checked, c=chave: self._select_photo(c))
            row.addWidget(btn)
            
            lbl = QLabel("—")
            lbl.setFont(QFont("Segoe UI", 11))
            lbl.setStyleSheet(f"color: {_MUTED};")
            row.addWidget(lbl)
            row.addStretch()
            
            self._lbl_fotos[chave] = lbl
            parent.layout().addLayout(row)

    # ── Preview ───────────────────────────────────────────────────────────────
    def _debounce_preview(self, _=None):
        if self._after_id:
            self._after_id = None
        QTimer.singleShot(DEBOUNCE_DELAY, self._update_preview)

    def _update_preview(self):
        # Implementar atualização da prévia do cartão
        pass

    def _virar_cartao(self):
        self.lado = "verso" if self.lado == "frente" else "frente"
        self._update_preview()

    # ── Busca por CPF ─────────────────────────────────────────────────────────
    def _buscar_por_cpf(self):
        cpf_text = self.cpf.text().strip()
        cpf_limpo = re.sub(r"\D", "", cpf_text)

        if not cpf_limpo:
            QMessageBox.warning(self, "CPF obrigatório", "Digite um CPF antes de pesquisar.")
            return
        if len(cpf_limpo) != 11:
            QMessageBox.warning(self, "CPF inválido", "CPF deve ter 11 dígitos.")
            return

        self._btn_buscar_cpf.setEnabled(False)
        self._lbl_buscar_status.setText("Pesquisando...")
        QTimer.singleShot(100, lambda: self._buscar_por_cpf_exec(cpf_limpo))

    def _buscar_por_cpf_exec(self, cpf_limpo):
        try:
            resultado = self.controller.buscar_por_cpf(cpf_limpo)

            if not resultado:
                QMessageBox.information(self, "Não encontrado", "Nenhum cadastro encontrado para este CPF.")
                return

            fields = [
                ("registro", self.registro),
                ("cpf", self.cpf),
                ("nome", self.nome),
                ("propriedade", self.propriedade),
                ("unloc", self.unloc),
                ("inicio", self.inicio),
                ("validade", self.validade),
                ("endereco", self.endereco),
                ("atividade1", self.atividade1),
                ("atividade2", self.atividade2),
                ("georef", self.georef),
            ]
            for key, entry in fields:
                entry.blockSignals(True)
                entry.setText(str(resultado.get(key, "") or ""))
                entry.blockSignals(False)

            self._update_preview()
            QMessageBox.information(self, "Encontrado", "Dados carregados a partir do CPF encontrado.")

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao buscar CPF:\n{e}")
        finally:
            self._btn_buscar_cpf.setEnabled(True)
            self._lbl_buscar_status.setText("")

    # ── Importar PDF ──────────────────────────────────────────────────────────
    def _select_pdf(self):
        caminho, _ = QFileDialog.getOpenFileName(
            self, "Selecionar PDF da Carteira", "", "PDF Files (*.pdf)"
        )
        if not caminho or not os.path.exists(caminho):
            return
        self._pdf_path = caminho
        nome = os.path.basename(caminho)
        if len(nome) > MAX_FILENAME_DISPLAY:
            nome = nome[:MAX_FILENAME_DISPLAY - 3] + "..."
        self._lbl_pdf.setText(f"✓ {nome}")
        self._lbl_pdf.setStyleSheet(f"color: {_VERDE};")
        self._btn_extrair.setEnabled(True)
        self._lbl_extrair_status.setText("")

    def _extract_pdf(self):
        if not self._pdf_path:
            return
        self._btn_extrair.setEnabled(False)
        self._btn_extrair.setText("⏳ Extraindo...")
        self._lbl_extrair_status.setText("Lendo PDF...")
        threading.Thread(target=self._worker_extract_pdf, daemon=True).start()

    def _worker_extract_pdf(self):
        try:
            from ..utils.pdf_parser import PDFParser
            parser = PDFParser()
            text = parser.extract_text(self._pdf_path)
            if not text.strip():
                QTimer.singleShot(0, lambda: self._show_extraction_result(None, "PDF sem texto legível"))
                return
            dados = parser.parse(text)
            QTimer.singleShot(0, lambda: self._show_extraction_result(dados, None))
        except Exception as e:
            QTimer.singleShot(0, lambda: self._show_extraction_result(None, str(e)))

    def _show_extraction_result(self, dados, erro):
        self._btn_extrair.setEnabled(True)
        self._btn_extrair.setText("🔍 Extrair Informações do PDF")

        if erro:
            self._lbl_extrair_status.setText(f"❌ {erro[:60]}")
            self._lbl_extrair_status.setStyleSheet(f"color: {_VERMELHO};")
            QMessageBox.critical(self, "Erro ao extrair PDF", erro)
            return

        if not dados:
            self._lbl_extrair_status.setText("⚠️ Nenhum campo identificado.")
            self._lbl_extrair_status.setStyleSheet(f"color: {_VERMELHO};")
            return

        mapa = {
            "registro": self.registro, "cpf": self.cpf,
            "nome": self.nome, "propriedade": self.propriedade,
            "unloc": self.unloc, "inicio": self.inicio,
            "validade": self.validade, "endereco": self.endereco,
            "atividade1": self.atividade1, "atividade2": self.atividade2,
            "georef": self.georef,
        }
        preenchidos = 0
        for chave, entry in mapa.items():
            valor = dados.get(chave, "")
            if valor:
                entry.blockSignals(True)
                entry.setText(valor)
                entry.blockSignals(False)
                preenchidos += 1

        self._update_preview()
        total = len(mapa)
        cor = _VERDE if preenchidos >= total // 2 else _MUTED
        self._lbl_extrair_status.setText(f"✅ {preenchidos}/{total} campos preenchidos")
        self._lbl_extrair_status.setStyleSheet(f"color: {cor};")

    # ── Fotos ─────────────────────────────────────────────────────────────────
    def _select_photo(self, chave):
        caminho, _ = QFileDialog.getOpenFileName(
            self, f"Selecionar {chave.replace('foto', 'Foto ')}",
            "", "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if not caminho or not os.path.exists(caminho):
            return

        mb = os.path.getsize(caminho) / (1024 * 1024)
        if mb > 10:
            QMessageBox.critical(self, "Erro", f"Arquivo muito grande ({mb:.1f} MB). Máximo: 10 MB")
            return

        try:
            with Image.open(caminho) as img:
                img.verify()
            with Image.open(caminho) as img:
                w, h = img.size
                fmt = img.format
        except Exception as exc:
            QMessageBox.critical(self, "Erro", f"Imagem inválida:\n{exc}")
            return

        self.fotos[chave] = caminho
        nome = os.path.basename(caminho)
        if len(nome) > MAX_FILENAME_DISPLAY:
            nome = nome[:MAX_FILENAME_DISPLAY - 3] + "..."
        self._lbl_fotos[chave].setText(f"✓ {nome} ({w}×{h}, {fmt})")
        self._lbl_fotos[chave].setStyleSheet(f"color: {_VERDE};")

    # ── Salvar ────────────────────────────────────────────────────────────────
    def _salvar_banco(self):
        dados = {
            "registro": self.registro.text().strip(),
            "cpf": self.cpf.text().strip(),
            "nome": self.nome.text().strip(),
            "propriedade": self.propriedade.text().strip(),
            "unloc": self.unloc.text().strip(),
            "inicio": self.inicio.text().strip(),
            "validade": self.validade.text().strip(),
            "endereco": self.endereco.text().strip(),
            "atividade1": self.atividade1.text().strip(),
            "atividade2": self.atividade2.text().strip(),
            "georef": self.georef.text().strip(),
        }

        required = [("registro", "Registro Estadual"), ("cpf", "CPF"),
                    ("nome", "Nome do Produtor"), ("propriedade", "Propriedade")]
        missing = [name for field, name in required if not dados.get(field)]
        if missing:
            QMessageBox.warning(self, "Validação", "Campos obrigatórios:\n• " + "\n• ".join(missing))
            return

        if len(re.sub(r"\D", "", dados["cpf"])) != 11:
            QMessageBox.warning(self, "Validação", "CPF deve ter 11 dígitos.")
            return

        for campo, nome in [("inicio", "Início"), ("validade", "Validade")]:
            v = dados.get(campo, "")
            if v and not re.match(r"^\d{2}/\d{2}/\d{4}$", v):
                QMessageBox.warning(self, "Validação", f"{nome} inválida. Use dd/mm/aaaa.")
                return

        if not any(self.fotos.values()):
            reply = QMessageBox.question(self, "Aviso", "Nenhuma foto selecionada. Continuar mesmo assim?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return

        ok, msg = self.controller.salvar_carteira(dados, self.fotos, self._pdf_path)
        if ok:
            QMessageBox.information(self, "Sucesso", msg)
            self._clear_form()
        else:
            QMessageBox.critical(self, "Erro", msg)

    # ── Limpar ────────────────────────────────────────────────────────────────
    def _clear_form(self):
        for entry in [self.registro, self.cpf, self.nome, self.propriedade,
                      self.unloc, self.inicio, self.validade, self.endereco,
                      self.atividade1, self.atividade2, self.georef]:
            entry.clear()

        self.fotos = {"foto1": None, "foto2": None, "foto3": None}
        for lbl in self._lbl_fotos.values():
            lbl.setText("—")
            lbl.setStyleSheet(f"color: {_MUTED};")

        if self.lado == "verso":
            self.lado = "frente"
            self._update_preview()

    def _confirmar_limpar(self):
        has_data = any([
            self.registro.text().strip(),
            self.cpf.text().strip(),
            self.nome.text().strip(),
            any(self.fotos.values()),
        ])
        if has_data:
            reply = QMessageBox.question(self, "Confirmação", "Limpar todos os campos?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return
        self._clear_form()

    # ── Histórico ─────────────────────────────────────────────────────────────
    def abrir_historico(self):
        self.historico_window = HistoricoView(self, self.usuario, self.controller)
        self.historico_window.show()