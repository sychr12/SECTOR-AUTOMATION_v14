from PyQt6.QtWidgets import (
    QWidget, QFrame, QLabel, QLineEdit, QComboBox, QTextEdit, QRadioButton,
    QButtonGroup, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from .controller import AdicionarController
from .services import AdicionarService


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
_VERDE_HOVER     = "#d1fae5"
_DANGER          = "#dc2626"
_DANGER_DK       = "#b91c1c"
_SUCESSO         = "#10b981"
_SUCESSO_DARK    = "#059669"


class AdicionarUI(QWidget):
    def __init__(self, parent=None, usuario=None):
        super().__init__(parent)
        self.usuario = usuario
        self.service = AdicionarService()
        self.controller = AdicionarController(usuario, self.service.repo)

        self.radio_value = "insc"

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {_CINZA_BG};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        self._criar_topo(layout)
        self._criar_tabela(layout)
        self._criar_formulario(layout)

    def _criar_topo(self, parent_layout):
        """Cabeçalho com radio buttons e título"""
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {_BRANCO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 12px;
            }}
        """)
        parent_layout.addWidget(header)

        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(24, 20, 24, 20)
        header_layout.setSpacing(16)

        # Título e ícone
        title_layout = QHBoxLayout()
        title_layout.setSpacing(12)

        icon_label = QLabel("📝")
        icon_label.setFont(QFont("Segoe UI", 24))
        icon_label.setStyleSheet(f"color: {_ACCENT};")
        title_layout.addWidget(icon_label)

        title_label = QLabel("Registro de Operações")
        title_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {_CINZA_TEXTO};")
        title_layout.addWidget(title_label)

        title_layout.addStretch()
        header_layout.addLayout(title_layout)

        # Subtítulo
        subtitle_label = QLabel("Selecione o tipo de operação e preencha os dados do produtor rural")
        subtitle_label.setFont(QFont("Segoe UI", 12))
        subtitle_label.setStyleSheet(f"color: {_CINZA_MEDIO};")
        header_layout.addWidget(subtitle_label)

        # Radio buttons container
        radio_container = QFrame()
        radio_container.setStyleSheet(f"""
            QFrame {{
                background-color: {_ACCENT_LIGHT};
                border-radius: 8px;
            }}
        """)
        header_layout.addWidget(radio_container)

        radio_layout = QHBoxLayout(radio_container)
        radio_layout.setContentsMargins(20, 16, 20, 16)
        radio_layout.setSpacing(32)

        self.radio_group = QButtonGroup(self)

        # Inscrição Radio
        self.radio_insc = QRadioButton("📋 Inscrição / Renovação")
        self.radio_insc.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.radio_insc.setStyleSheet(f"""
            QRadioButton {{
                color: {_CINZA_TEXTO};
                spacing: 8px;
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
        self.radio_insc.toggled.connect(self._alternar_formulario)
        self.radio_group.addButton(self.radio_insc)
        radio_layout.addWidget(self.radio_insc)

        # Devolução Radio
        self.radio_dev = QRadioButton("🔄 Devolução / Cancelamento")
        self.radio_dev.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.radio_dev.setStyleSheet(f"""
            QRadioButton {{
                color: {_CINZA_TEXTO};
                spacing: 8px;
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
        self.radio_dev.toggled.connect(self._alternar_formulario)
        self.radio_group.addButton(self.radio_dev)
        radio_layout.addWidget(self.radio_dev)

        radio_layout.addStretch()

    def _criar_tabela(self, parent_layout):
        """Tabela de registros com design moderno"""
        table_container = QFrame()
        table_container.setStyleSheet(f"""
            QFrame {{
                background-color: {_BRANCO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 12px;
            }}
        """)
        parent_layout.addWidget(table_container, stretch=1)

        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(24, 20, 24, 20)
        table_layout.setSpacing(12)

        # Header da tabela com ícone
        table_header_layout = QHBoxLayout()
        table_header_layout.setSpacing(8)

        icon_label = QLabel("📊")
        icon_label.setFont(QFont("Segoe UI", 18))
        icon_label.setStyleSheet(f"color: {_ACCENT};")
        table_header_layout.addWidget(icon_label)

        title_label = QLabel("Registros Recentes")
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {_CINZA_TEXTO};")
        table_header_layout.addWidget(title_label)

        table_header_layout.addStretch()
        table_layout.addLayout(table_header_layout)

        # Tabela
        self.tree = QTableWidget()
        self.tree.setColumnCount(5)
        self.tree.setHorizontalHeaderLabels(["👤 NOME", "🆔 CPF", "📍 MUNICÍPIO", "📄 MEMORANDO", "📅 DATA"])
        self.tree.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tree.setAlternatingRowColors(True)
        self.tree.setStyleSheet(f"""
            QTableWidget {{
                background-color: {_BRANCO};
                color: {_CINZA_TEXTO};
                border: none;
                gridline-color: {_CINZA_BORDER};
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {_CINZA_BORDER};
            }}
            QTableWidget::item:selected {{
                background-color: {_ACCENT_LIGHT};
                color: {_ACCENT};
            }}
            QHeaderView::section {{
                background-color: {_ACCENT_LIGHT};
                color: {_ACCENT};
                padding: 8px;
                border: none;
                font-weight: bold;
            }}
        """)
        table_layout.addWidget(self.tree)

    def _criar_formulario(self, parent_layout):
        """Formulário de entrada com design moderno"""
        form_container = QFrame()
        form_container.setStyleSheet(f"""
            QFrame {{
                background-color: {_BRANCO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 12px;
            }}
        """)
        parent_layout.addWidget(form_container)

        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(24, 20, 24, 24)
        form_layout.setSpacing(16)

        # Header do formulário
        form_header_layout = QHBoxLayout()
        form_header_layout.setSpacing(8)

        icon_label = QLabel("✏️")
        icon_label.setFont(QFont("Segoe UI", 18))
        icon_label.setStyleSheet(f"color: {_ACCENT};")
        form_header_layout.addWidget(icon_label)

        title_label = QLabel("Dados do Registro")
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {_CINZA_TEXTO};")
        form_header_layout.addWidget(title_label)

        form_header_layout.addStretch()
        form_layout.addLayout(form_header_layout)

        # Container do formulário com grid
        self.form_frame = QFrame()
        form_layout.addWidget(self.form_frame)

        form_grid = QGridLayout(self.form_frame)
        form_grid.setContentsMargins(0, 0, 0, 0)
        form_grid.setHorizontalSpacing(16)
        form_grid.setVerticalSpacing(12)

        # Linha 0: Nome e CPF
        # Nome
        nome_label = QLabel("👤 Nome Completo")
        nome_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        nome_label.setStyleSheet(f"color: {_CINZA_TEXTO};")
        form_grid.addWidget(nome_label, 0, 0)
        
        self.nome_entry = QLineEdit()
        self.nome_entry.setPlaceholderText("Digite o nome completo do produtor")
        self.nome_entry.setFixedHeight(44)
        self.nome_entry.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {_CINZA_BORDER};
                border-radius: 8px;
                padding: 8px 12px;
                background-color: {_BRANCO};
                color: {_CINZA_TEXTO};
                font-family: 'Segoe UI';
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 2px solid {_ACCENT};
            }}
        """)
        form_grid.addWidget(self.nome_entry, 1, 0)

        # CPF
        cpf_label = QLabel("🆔 CPF")
        cpf_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        cpf_label.setStyleSheet(f"color: {_CINZA_TEXTO};")
        form_grid.addWidget(cpf_label, 0, 1)
        
        self.cpf_entry = QLineEdit()
        self.cpf_entry.setPlaceholderText("000.000.000-00")
        self.cpf_entry.setFixedHeight(44)
        self.cpf_entry.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {_CINZA_BORDER};
                border-radius: 8px;
                padding: 8px 12px;
                background-color: {_BRANCO};
                color: {_CINZA_TEXTO};
                font-family: 'Segoe UI';
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 2px solid {_ACCENT};
            }}
        """)
        self.cpf_entry.textChanged.connect(self._formatar_cpf)
        form_grid.addWidget(self.cpf_entry, 1, 1)

        # Linha 1: Município e Memorando
        # Município
        municipio_label = QLabel("📍 Município")
        municipio_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        municipio_label.setStyleSheet(f"color: {_CINZA_TEXTO};")
        form_grid.addWidget(municipio_label, 2, 0)
        
        self.municipio_entry = QLineEdit()
        self.municipio_entry.setPlaceholderText("Digite o município de origem")
        self.municipio_entry.setFixedHeight(44)
        self.municipio_entry.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {_CINZA_BORDER};
                border-radius: 8px;
                padding: 8px 12px;
                background-color: {_BRANCO};
                color: {_CINZA_TEXTO};
                font-family: 'Segoe UI';
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 2px solid {_ACCENT};
            }}
        """)
        form_grid.addWidget(self.municipio_entry, 3, 0)

        # Memorando
        memo_label = QLabel("📄 Nº Memorando")
        memo_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        memo_label.setStyleSheet(f"color: {_CINZA_TEXTO};")
        form_grid.addWidget(memo_label, 2, 1)
        
        self.memo_entry = QLineEdit()
        self.memo_entry.setPlaceholderText("Número do documento")
        self.memo_entry.setFixedHeight(44)
        self.memo_entry.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {_CINZA_BORDER};
                border-radius: 8px;
                padding: 8px 12px;
                background-color: {_BRANCO};
                color: {_CINZA_TEXTO};
                font-family: 'Segoe UI';
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 2px solid {_ACCENT};
            }}
        """)
        form_grid.addWidget(self.memo_entry, 3, 1)

        # Linha 2: Tipo (apenas para inscrição)
        tipo_label = QLabel("🏷️ Tipo")
        tipo_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        tipo_label.setStyleSheet(f"color: {_CINZA_TEXTO};")
        form_grid.addWidget(tipo_label, 4, 0)
        
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["INSC - Inscrição", "RENOV - Renovação"])
        self.tipo_combo.setCurrentText("INSC - Inscrição")
        self.tipo_combo.setFixedHeight(44)
        self.tipo_combo.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid {_CINZA_BORDER};
                border-radius: 8px;
                padding: 8px 12px;
                background-color: {_BRANCO};
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
            QComboBox:focus {{
                border: 2px solid {_ACCENT};
            }}
        """)
        form_grid.addWidget(self.tipo_combo, 5, 0)

        # Motivo (apenas para devolução)
        motivo_label = QLabel("💬 Motivo da Devolução")
        motivo_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        motivo_label.setStyleSheet(f"color: {_CINZA_TEXTO};")
        form_grid.addWidget(motivo_label, 4, 1)
        
        self.motivo_text = QTextEdit()
        self.motivo_text.setPlaceholderText("Descreva o motivo da devolução/cancelamento...")
        self.motivo_text.setFixedHeight(100)
        self.motivo_text.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid {_CINZA_BORDER};
                border-radius: 8px;
                padding: 8px;
                background-color: {_BRANCO};
                color: {_CINZA_TEXTO};
                font-family: 'Segoe UI';
                font-size: 12px;
            }}
            QTextEdit:focus {{
                border: 2px solid {_ACCENT};
            }}
        """)
        form_grid.addWidget(self.motivo_text, 5, 1)
        self.motivo_text.hide()

        # Botão salvar
        btn_container = QFrame()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 20, 0, 0)

        save_btn = QPushButton("💾 Salvar Registro")
        save_btn.setFixedHeight(48)
        save_btn.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {_SUCESSO};
                color: {_BRANCO};
                border: none;
                border-radius: 8px;
                padding: 12px 40px;
            }}
            QPushButton:hover {{
                background-color: {_SUCESSO_DARK};
            }}
            QPushButton:pressed {{
                background-color: {_SUCESSO_DARK};
            }}
        """)
        save_btn.clicked.connect(self._salvar_registro)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addStretch()

        parent_layout.addWidget(btn_container)

    def _alternar_formulario(self):
        """Alterna entre formulário de inscrição e devolução"""
        if self.radio_insc.isChecked():
            self.radio_value = "insc"
            self.tipo_combo.show()
            self.motivo_text.hide()
            # Ajustar o grid para esconder o motivo
            self._ajustar_layout_formulario(show_motivo=False)
        else:
            self.radio_value = "dev"
            self.tipo_combo.hide()
            self.motivo_text.show()
            self._ajustar_layout_formulario(show_motivo=True)

    def _ajustar_layout_formulario(self, show_motivo=False):
        """Ajusta o layout do formulário baseado no tipo selecionado"""
        # Esta função é chamada apenas para garantir que o layout está correto
        pass

    def _formatar_cpf(self, text):
        """Formata CPF automaticamente enquanto digita"""
        cursor_pos = self.cpf_entry.cursorPosition()
        cpf_formatado = self.controller.formatar_cpf(text)
        
        self.cpf_entry.blockSignals(True)
        self.cpf_entry.setText(cpf_formatado)
        
        # Ajustar posição do cursor
        new_pos = min(cursor_pos, len(cpf_formatado))
        self.cpf_entry.setCursorPosition(new_pos)
        self.cpf_entry.blockSignals(False)

    def _salvar_registro(self):
        """Salva o registro no banco"""
        tipo_registro = self.radio_value

        # Coletar dados do formulário
        dados = {
            'nome': self.nome_entry.text().strip(),
            'cpf': self.cpf_entry.text().strip(),
            'municipio': self.municipio_entry.text().strip(),
            'memo': self.memo_entry.text().strip(),
            'tipo': self.tipo_combo.currentText() if tipo_registro == "insc" else "",
            'motivo': self.motivo_text.toPlainText().strip() if tipo_registro == "dev" else ""
        }

        # Salvar usando o controller
        if tipo_registro == "insc":
            success, message = self.controller.salvar_inscricao(dados)
        else:
            success, message = self.controller.salvar_devolucao(dados)

        if not success:
            QMessageBox.warning(self, "Atenção", f"⚠️ {message}")
            return

        # Adicionar na tabela
        valores_tabela = self.controller.obter_registro_tabela(dados, tipo_registro)
        row_count = self.tree.rowCount()
        self.tree.insertRow(row_count)
        for col, value in enumerate(valores_tabela):
            self.tree.setItem(row_count, col, QTableWidgetItem(value))
        
        # Scroll para a nova linha
        self.tree.scrollToBottom()

        # Limpar formulário
        self._limpar_formulario()

        # Mostrar mensagem de sucesso
        QMessageBox.information(self, "Sucesso", f"✅ {message}")

    def _limpar_formulario(self):
        """Limpa todos os campos do formulário"""
        self.nome_entry.clear()
        self.cpf_entry.clear()
        self.municipio_entry.clear()
        self.memo_entry.clear()
        self.motivo_text.clear()
        self.tipo_combo.setCurrentIndex(0)

    def obter_dados_formulario(self):
        """Obtém dados atuais do formulário"""
        return {
            'nome': self.nome_entry.text().strip(),
            'cpf': self.cpf_entry.text().strip(),
            'municipio': self.municipio_entry.text().strip(),
            'memo': self.memo_entry.text().strip(),
            'tipo': self.tipo_combo.currentText() if self.radio_value == "insc" else "",
            'motivo': self.motivo_text.toPlainText().strip() if self.radio_value == "dev" else ""
        }