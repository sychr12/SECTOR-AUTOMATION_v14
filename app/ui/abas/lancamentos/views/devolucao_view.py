# -*- coding: utf-8 -*-
"""Popup de devolução — design refinado (PyQt6)."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame,
    QLabel, QPushButton, QRadioButton, QTextEdit, QWidget, QButtonGroup
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from app.theme import AppTheme

_VERDE   = "#22c55e"
_VERDE_H = "#16a34a"
_VERM    = "#ef4444"
_VERM_H  = "#dc2626"
_MUTED   = "#64748b"

MOTIVOS = [
    "Endereço", "Documentos", "Cadastro",
    "Pesca", "Simples Nacional", "Animais", "Outros"
]


class DevolucaoPopup(QDialog):
    def __init__(self, parent=None, callback=None):
        super().__init__(parent)
        self.callback = callback

        self.setWindowTitle("Devolução de Processos")
        self.setFixedSize(520, 460)
        self.setModal(True)
        self.setStyleSheet(f"background-color: {AppTheme.BG_APP};")

        self._build()
        self._centralizar()

    def _centralizar(self):
        if self.parent():
            geo = self.parent().frameGeometry()
            center = geo.center()
            frame = self.frameGeometry()
            frame.moveCenter(center)
            self.move(frame.topLeft())
        else:
            screen = self.screen().availableGeometry()
            frame = self.frameGeometry()
            frame.moveCenter(screen.center())
            self.move(frame.topLeft())

    def _make_label(self, text, size=12, bold=False, color=None):
        lbl = QLabel(text)
        font = QFont("Segoe UI", size)
        font.setBold(bold)
        lbl.setFont(font)
        if color:
            lbl.setStyleSheet(f"color: {color}; background: transparent;")
        else:
            lbl.setStyleSheet("background: transparent;")
        return lbl

    def _make_button(self, text, bg, hover, callback, bold=False):
        btn = QPushButton(text)
        btn.setFixedHeight(46)
        font = QFont("Segoe UI", 13)
        font.setBold(bold)
        btn.setFont(font)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {"#fff" if bg == _VERDE else AppTheme.TXT_MAIN};
                border: none;
                border-radius: 12px;
                padding: 0 14px;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
        """)
        btn.clicked.connect(callback)
        return btn

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(0)

        wrap = QFrame()
        wrap.setStyleSheet("background: transparent;")
        wrap_layout = QVBoxLayout(wrap)
        wrap_layout.setContentsMargins(0, 0, 0, 0)
        wrap_layout.setSpacing(0)

        # Título
        titulo = self._make_label("Devolução de Processos", size=20, bold=True, color=AppTheme.TXT_MAIN)
        wrap_layout.addWidget(titulo)
        wrap_layout.addSpacing(20)

        # Card de motivos
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {AppTheme.BG_CARD};
                border-radius: 14px;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 16)
        card_layout.setSpacing(10)

        subtitulo = self._make_label("Motivo da devolução:", size=12, bold=True, color=_MUTED)
        card_layout.addWidget(subtitulo)

        grid_wrap = QWidget()
        grid_layout = QGridLayout(grid_wrap)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setHorizontalSpacing(16)
        grid_layout.setVerticalSpacing(8)

        self._button_group = QButtonGroup(self)
        self._radios = []

        for i, motivo in enumerate(MOTIVOS):
            radio = QRadioButton(motivo)
            radio.setFont(QFont("Segoe UI", 12))
            radio.setStyleSheet(f"""
                QRadioButton {{
                    color: {AppTheme.TXT_MAIN};
                    spacing: 8px;
                    background: transparent;
                }}
                QRadioButton::indicator {{
                    width: 16px;
                    height: 16px;
                    border-radius: 8px;
                    border: 2px solid {_VERDE};
                    background: transparent;
                }}
                QRadioButton::indicator:checked {{
                    background: {_VERDE};
                    border: 2px solid {_VERDE};
                }}
            """)
            self._button_group.addButton(radio, i)
            self._radios.append(radio)
            grid_layout.addWidget(radio, i // 2, i % 2)

        if self._radios:
            self._radios[0].setChecked(True)

        card_layout.addWidget(grid_wrap)
        wrap_layout.addWidget(card)
        wrap_layout.addSpacing(16)

        # Detalhes
        detalhes_lbl = self._make_label("Detalhes adicionais (opcional):", size=11, bold=True, color=_MUTED)
        wrap_layout.addWidget(detalhes_lbl)
        wrap_layout.addSpacing(6)

        self.detalhes = QTextEdit()
        self.detalhes.setFixedHeight(80)
        self.detalhes.setFont(QFont("Segoe UI", 12))
        self.detalhes.setStyleSheet(f"""
            QTextEdit {{
                background-color: {AppTheme.BG_INPUT};
                color: {AppTheme.TXT_MAIN};
                border: none;
                border-radius: 12px;
                padding: 10px;
            }}
        """)
        wrap_layout.addWidget(self.detalhes)
        wrap_layout.addSpacing(20)

        # Botões
        btns = QWidget()
        btns_layout = QHBoxLayout(btns)
        btns_layout.setContentsMargins(0, 0, 0, 0)
        btns_layout.setSpacing(12)

        btn_confirmar = self._make_button(
            "Confirmar Devolução",
            _VERDE,
            _VERDE_H,
            self._confirmar,
            bold=True
        )
        btn_cancelar = self._make_button(
            "Cancelar",
            AppTheme.BG_INPUT,
            AppTheme.BG_APP,
            self.reject,
            bold=False
        )

        btns_layout.addWidget(btn_confirmar)
        btns_layout.addWidget(btn_cancelar)

        wrap_layout.addWidget(btns)

        root.addWidget(wrap)

    def _confirmar(self):
        motivo = "Endereço"
        checked = self._button_group.checkedButton()
        if checked:
            motivo = checked.text()

        detalhes = self.detalhes.toPlainText().strip()
        resultado = f"[{motivo}] {detalhes}" if detalhes else f"[{motivo}]"

        if callable(self.callback):
            self.callback(resultado)

        self.accept()