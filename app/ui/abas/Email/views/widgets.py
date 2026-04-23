# -*- coding: utf-8 -*-
"""
Widgets customizados para a interface de download de emails
Versão PyQt6
"""

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class AppTheme:
    """Paleta local — espelha app.theme.AppTheme sem depender do caminho absoluto."""
    BG_INPUT = "#ffffff"
    BG_CARD = "#f1f5f9"
    TXT_MAIN = "#0f172a"
    TXT_MUTED = "#64748b"
    BTN_PRIMARY = "#2c6e9e"
    BTN_PRIMARY_HOVER = "#1e4a6e"
    BORDER = "#e2e8f0"


class ProgressoDownload(QFrame):
    """Barra de progresso para download"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: transparent;")
        self.valor_atual = 0
        self._criar_widgets()

    def _criar_widgets(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Label do progresso
        self.label = QLabel("Progresso: 0%")
        self.label.setFont(QFont("Segoe UI", 12))
        self.label.setStyleSheet(f"color: {AppTheme.TXT_MUTED};")
        layout.addWidget(self.label)

        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 4px;
                background-color: {AppTheme.BG_INPUT};
                height: 8px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {AppTheme.BTN_PRIMARY};
                border-radius: 4px;
            }}
        """)
        layout.addWidget(self.progress_bar)

        # Label de status
        self.status_label = QLabel("Pronto para iniciar")
        self.status_label.setFont(QFont("Segoe UI", 11))
        self.status_label.setStyleSheet(f"color: {AppTheme.TXT_MUTED};")
        layout.addWidget(self.status_label)

    def atualizar(self, valor, status=""):
        """Atualiza a barra de progresso"""
        self.valor_atual = valor
        self.progress_bar.setValue(valor)
        self.label.setText(f"Progresso: {valor}%")

        if status:
            self.status_label.setText(status)

    def reset(self):
        """Reseta a barra de progresso"""
        self.atualizar(0, "Pronto para iniciar")


class EstatisticasDownload(QFrame):
    """Widget para exibir estatísticas do download"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {AppTheme.BG_CARD};
                border-radius: 12px;
            }}
        """)
        self._criar_widgets()
        self.reset()

    def _criar_widgets(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Título
        lbl_title = QLabel("📊 Estatísticas")
        lbl_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(lbl_title)

        # Grid de estatísticas
        grid_layout = QHBoxLayout()
        grid_layout.setSpacing(20)

        # Coluna esquerda
        left_layout = QVBoxLayout()
        self.label_emails = QLabel("E-mails: 0")
        self.label_arquivos = QLabel("Arquivos: 0")
        left_layout.addWidget(self.label_emails)
        left_layout.addWidget(self.label_arquivos)

        # Coluna direita
        right_layout = QVBoxLayout()
        self.label_sucessos = QLabel("✅ Sucessos: 0")
        self.label_erros = QLabel("❌ Erros: 0")
        right_layout.addWidget(self.label_sucessos)
        right_layout.addWidget(self.label_erros)

        for lbl in [self.label_emails, self.label_arquivos, self.label_sucessos, self.label_erros]:
            lbl.setFont(QFont("Segoe UI", 12))

        self.label_sucessos.setStyleSheet("color: #10B981;")
        self.label_erros.setStyleSheet("color: #EF4444;")

        grid_layout.addLayout(left_layout)
        grid_layout.addLayout(right_layout)
        grid_layout.addStretch()
        layout.addLayout(grid_layout)

        # Última execução
        self.label_ultima = QLabel("Última: Nunca")
        self.label_ultima.setFont(QFont("Segoe UI", 11))
        self.label_ultima.setStyleSheet(f"color: {AppTheme.TXT_MUTED};")
        self.label_ultima.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.label_ultima)

    def atualizar(self, emails=0, arquivos=0, sucessos=0, erros=0):
        """Atualiza as estatísticas"""
        self.label_emails.setText(f"E-mails: {emails}")
        self.label_arquivos.setText(f"Arquivos: {arquivos}")
        self.label_sucessos.setText(f"✅ Sucessos: {sucessos}")
        self.label_erros.setText(f"❌ Erros: {erros}")

    def atualizar_ultima_execucao(self, data_hora):
        """Atualiza a data/hora da última execução"""
        self.label_ultima.setText(f"Última: {data_hora}")

    def reset(self):
        """Reseta todas as estatísticas"""
        self.atualizar(0, 0, 0, 0)
        self.atualizar_ultima_execucao("Nunca")


class CardInfo(QFrame):
    """Card informativo"""

    def __init__(self, parent=None, titulo="", conteudo="", icon="ℹ️"):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {AppTheme.BG_CARD};
                border-radius: 16px;
                border: 1px solid {AppTheme.BORDER};
            }}
        """)
        self._criar_widgets(titulo, conteudo, icon)

    def _criar_widgets(self, titulo, conteudo, icon):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Header com ícone e título
        header_layout = QHBoxLayout()
        lbl_icon = QLabel(icon)
        lbl_icon.setFont(QFont("Segoe UI", 20))
        lbl_title = QLabel(titulo)
        lbl_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        header_layout.addWidget(lbl_icon)
        header_layout.addWidget(lbl_title)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Conteúdo
        lbl_conteudo = QLabel(conteudo)
        lbl_conteudo.setFont(QFont("Segoe UI", 12))
        lbl_conteudo.setStyleSheet(f"color: {AppTheme.TXT_MUTED};")
        lbl_conteudo.setWordWrap(True)
        layout.addWidget(lbl_conteudo)