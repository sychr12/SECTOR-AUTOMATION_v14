# -*- coding: utf-8 -*-
"""Popup de devolução — design refinado (PyQt6)."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFrame, QLabel, 
    QRadioButton, QButtonGroup, QTextEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

_VERDE = "#22c55e"
_VERDE_H = "#16a34a"
_VERM = "#ef4444"
_VERM_H = "#dc2626"
_MUTED = "#64748b"
_BRANCO = "#ffffff"
_CINZA_BORDER = "#e2e8f0"
_CINZA_BG = "#f5f7fc"
_CINZA_TEXTO = "#1e2f3e"

MOTIVOS = ["Endereço", "Documentos", "Cadastro",
           "Pesca", "Simples Nacional", "Animais", "Outros"]


class DevolucaoPopup(QDialog):
    """Popup de devolução de processos."""

    def __init__(self, parent=None, callback=None):
        super().__init__(parent)
        self.callback = callback

        self.setWindowTitle("Devolução de Processos")
        self.setModal(True)
        self.setFixedSize(520, 460)
        self.setStyleSheet(f"background-color: {_CINZA_BG};")

        self._build()
        self._centralizar()

    def _centralizar(self):
        screen = self.screen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        # Título
        lbl_title = QLabel("Devolução de Processos")
        lbl_title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        lbl_title.setStyleSheet(f"color: {_CINZA_TEXTO};")
        layout.addWidget(lbl_title)

        # Card de motivos
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {_BRANCO};
                border-radius: 14px;
                border: 1px solid {_CINZA_BORDER};
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(10)

        lbl_motivo = QLabel("Motivo da devolução:")
        lbl_motivo.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        lbl_motivo.setStyleSheet(f"color: {_MUTED};")
        card_layout.addWidget(lbl_motivo)

        # Grid de radio buttons
        self.motivo_group = QButtonGroup(self)
        grid_layout = QHBoxLayout()
        grid_layout.setSpacing(20)

        left_col = QVBoxLayout()
        right_col = QVBoxLayout()
        
        for i, m in enumerate(MOTIVOS):
            radio = QRadioButton(m)
            radio.setFont(QFont("Segoe UI", 12))
            radio.setStyleSheet(f"""
                QRadioButton {{
                    color: {_CINZA_TEXTO};
                    spacing: 8px;
                }}
                QRadioButton::indicator {{
                    width: 16px;
                    height: 16px;
                    border: 2px solid {_VERDE};
                    border-radius: 8px;
                    background-color: white;
                }}
                QRadioButton::indicator:checked {{
                    background-color: {_VERDE};
                }}
            """)
            if i == 0:
                radio.setChecked(True)
            self.motivo_group.addButton(radio, i)
            
            if i < 4:
                left_col.addWidget(radio)
            else:
                right_col.addWidget(radio)
        
        grid_layout.addLayout(left_col)
        grid_layout.addLayout(right_col)
        card_layout.addLayout(grid_layout)

        layout.addWidget(card)

        # Detalhes adicionais
        lbl_detalhes = QLabel("Detalhes adicionais (opcional):")
        lbl_detalhes.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        lbl_detalhes.setStyleSheet(f"color: {_MUTED};")
        layout.addWidget(lbl_detalhes)

        self.detalhes = QTextEdit()
        self.detalhes.setPlaceholderText("Digite detalhes adicionais sobre a devolução...")
        self.detalhes.setFixedHeight(80)
        self.detalhes.setStyleSheet(f"""
            QTextEdit {{
                background-color: {_BRANCO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 12px;
                padding: 8px;
                font-family: 'Segoe UI';
                font-size: 12px;
            }}
            QTextEdit:focus {{
                border: 2px solid {_VERDE};
            }}
        """)
        layout.addWidget(self.detalhes)

        # Botões
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        btn_confirmar = QPushButton("Confirmar Devolução")
        btn_confirmar.setFixedHeight(46)
        btn_confirmar.setStyleSheet(f"""
            QPushButton {{
                background-color: {_VERDE};
                color: white;
                border: none;
                border-radius: 12px;
                font-family: 'Segoe UI';
                font-size: 13px;
                font-weight: bold;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background-color: {_VERDE_H};
            }}
        """)
        btn_confirmar.clicked.connect(self._confirmar)
        btn_layout.addWidget(btn_confirmar)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setFixedHeight(46)
        btn_cancelar.setStyleSheet(f"""
            QPushButton {{
                background-color: {_BRANCO};
                color: {_CINZA_TEXTO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 12px;
                font-family: 'Segoe UI';
                font-size: 13px;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background-color: {_CINZA_BORDER};
            }}
        """)
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancelar)

        layout.addLayout(btn_layout)

    def _confirmar(self):
        """Confirma a devolução e chama o callback."""
        selected_button = self.motivo_group.checkedButton()
        if selected_button:
            motivo = selected_button.text()
        else:
            motivo = MOTIVOS[0]
        
        detalhes = self.detalhes.toPlainText().strip()
        resultado = f"[{motivo}] {detalhes}" if detalhes else f"[{motivo}]"
        
        if self.callback:
            self.callback(resultado)
        self.accept()