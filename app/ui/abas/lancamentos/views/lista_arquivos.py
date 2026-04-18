# -*- coding: utf-8 -*-
"""Lista de Arquivos — PyQt6."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from app.theme import AppTheme


class ListaArquivosView(QDialog):

    def __init__(self, parent=None, usuario=None, controller=None):
        super().__init__(parent)
        self.usuario = usuario
        self.controller = controller

        self.setWindowTitle("Lista de Arquivos")
        self.setFixedSize(800, 600)
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

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)

        wrap = QFrame()
        wrap.setStyleSheet("background: transparent;")
        wrap_layout = QVBoxLayout(wrap)
        wrap_layout.setContentsMargins(0, 0, 0, 0)
        wrap_layout.setSpacing(0)

        titulo = QLabel("Lista de Arquivos")
        titulo.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        titulo.setStyleSheet(f"color: {AppTheme.TXT_MAIN};")
        titulo.setAlignment(Qt.AlignmentFlag.AlignLeft)
        wrap_layout.addWidget(titulo)
        wrap_layout.addSpacing(16)

        texto = QLabel("Esta funcionalidade está em desenvolvimento.")
        texto.setFont(QFont("Segoe UI", 14))
        texto.setStyleSheet("color: #64748b;")
        texto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        wrap_layout.addWidget(texto)
        wrap_layout.addStretch()

        root.addWidget(wrap)