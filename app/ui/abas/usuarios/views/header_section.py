# -*- coding: utf-8 -*-
"""
HeaderSection — cabeçalho com título e subtítulo (PyQt6).
"""

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


class HeaderSection(QFrame):
    """Seção de cabeçalho com título e subtítulo opcionais."""

    def __init__(self, title="", subtitle="", parent=None):
        super().__init__(parent)
        self._title = title
        self._subtitle = subtitle
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        title_label = QLabel(self._title)
        title_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #1e2f3e;")
        layout.addWidget(title_label)

        if self._subtitle:
            subtitle_label = QLabel(self._subtitle)
            subtitle_label.setFont(QFont("Segoe UI", 13))
            subtitle_label.setStyleSheet("color: #64748b;")
            layout.addWidget(subtitle_label)