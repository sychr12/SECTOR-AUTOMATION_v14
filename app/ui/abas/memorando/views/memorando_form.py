# -*- coding: utf-8 -*-
"""Views para Memorando de Saída — formulário e histórico"""

from PyQt6.QtWidgets import (
    QWidget, QFrame, QLabel, QPushButton, QLineEdit,
    QGridLayout, QHBoxLayout, QVBoxLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from app.theme import AppTheme
from .municipio_selector import MunicipioSelector
from app.ui.abas.memorando.style import (
    FILTER_RADIUS,
    FILTER_BORDER,
    FILTER_HOVER,
    FILTER_INPUT_BG,
    FILTER_DROPDOWN_BG,
)


class MemorandoFormView(QFrame):

    def __init__(self, parent, controller, on_gerar=None, on_historico=None,
                 icons=None, unloc_list=None, unloc_dict=None):
        super().__init__(parent)
        self.controller = controller
        self.on_gerar = on_gerar
        self.on_historico = on_historico
        self.icons = icons or {}
        self.unloc_list = unloc_list or []
        self.unloc_dict = unloc_dict or {}
        self._aplicando_mascara = False

        self.setObjectName("memorandoFormRoot")
        self.setStyleSheet("""
            QFrame#memorandoFormRoot {
                background: transparent;
                border: none;
            }
        """)

        self._create_widgets()

    def _entry_style(self):
        return f"""
            QLineEdit {{
                background-color: {FILTER_INPUT_BG};
                color: {AppTheme.TXT_MAIN};
                border: 1px solid {FILTER_BORDER};
                border-radius: {FILTER_RADIUS}px;
                padding: 0 12px;
                font-size: 13px;
            }}
        """

    def _button_primary_style(self):
        return f"""
            QPushButton {{
                background-color: #2563eb;
                color: #ffffff;
                border: none;
                border-radius: {FILTER_RADIUS}px;
                font-size: 13px;
                font-weight: 700;
                padding: 0 16px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: #1d4ed8;
            }}
        """

    def _button_secondary_style(self):
        return f"""
            QPushButton {{
                background-color: {FILTER_INPUT_BG};
                color: {AppTheme.TXT_MAIN};
                border: none;
                border-radius: {FILTER_RADIUS}px;
                font-size: 13px;
                font-weight: 400;
                padding: 0 16px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {FILTER_HOVER};
            }}
        """

    def _separator_style(self):
        return f"background-color: {AppTheme.BG_INPUT}; border: none;"

    def _create_widgets(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        card = QFrame()
        card.setObjectName("memorandoFormCard")
        card.setStyleSheet(f"""
            QFrame#memorandoFormCard {{
                background-color: {AppTheme.BG_CARD};
                border: none;
                border-radius: 16px;
            }}
        """)
        root_layout.addWidget(card)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        form_grid = QGridLayout()
        form_grid.setContentsMargins(0, 0, 0, 0)
        form_grid.setHorizontalSpacing(8)
        form_grid.setVerticalSpacing(0)
        card_layout.addLayout(form_grid)

        campos = [
            (0, "Nº Memo Saída", "Ex: 001", "entry"),
            (1, "Data", "DD/MM/AAAA", "entry"),
            (2, "Município", "Selecione o município", "combo"),
            (3, "Nº Memo Entrada", "Ex: 045", "entry"),
        ]

        self._entries = {}

        for col, label, placeholder, tipo in campos:
            label_frame = QFrame()
            label_frame.setStyleSheet("background: transparent; border: none;")
            label_layout = QHBoxLayout(label_frame)
            label_layout.setContentsMargins(0, 0, 0, 0)
            label_layout.setSpacing(0)

            label_widget = QLabel(label)
            label_widget.setStyleSheet(f"""
                color: {AppTheme.TXT_MUTED};
                font-size: 11px;
                font-weight: 700;
                background: transparent;
                border: none;
            """)
            label_layout.addWidget(label_widget, alignment=Qt.AlignmentFlag.AlignLeft)

            form_grid.addWidget(label_frame, 0, col)

            if tipo == "combo":
                entry = MunicipioSelector(
                    card,
                    values=self.unloc_list,
                    default="MAO - MANAUS" if "MAO - MANAUS" in self.unloc_list else (self.unloc_list[0] if self.unloc_list else ""),
                    width=220,
                    height=44,
                    corner_radius=FILTER_RADIUS,
                    fg_color=FILTER_INPUT_BG,
                    text_color=AppTheme.TXT_MAIN,
                    button_color=FILTER_INPUT_BG,
                    button_hover_color=FILTER_HOVER,
                    dropdown_fg_color=FILTER_DROPDOWN_BG,
                    border_color=FILTER_BORDER,
                    border_width=1,
                    font=("Segoe UI", 13),
                    placeholder="Selecione o município",
                )
            else:
                entry = QLineEdit()
                entry.setPlaceholderText(placeholder)
                entry.setMinimumHeight(44)
                entry.setStyleSheet(self._entry_style())

                if label == "Data":
                    self._data_var = entry
                    entry.textChanged.connect(self._mascara_data)

            if col == 0:
                form_grid.setColumnStretch(col, 1)
            elif col == 1:
                form_grid.setColumnStretch(col, 1)
            elif col == 2:
                form_grid.setColumnStretch(col, 1)
            elif col == 3:
                form_grid.setColumnStretch(col, 1)

            form_grid.addWidget(entry, 1, col)
            self._entries[col] = entry

        form_grid.setContentsMargins(20, 24, 20, 24)

        self.nmemosaidaentry = self._entries[0]
        self.dataemissaoentry = self._entries[1]
        self.unlocentry = self._entries[2]
        self.nmemoentradaentry = self._entries[3]

        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet(self._separator_style())
        card_layout.addWidget(separator)
        card_layout.setStretchFactor(separator, 0)

        btn_frame = QFrame()
        btn_frame.setStyleSheet("background: transparent; border: none;")
        btn_layout = QHBoxLayout(btn_frame)
        btn_layout.setContentsMargins(20, 20, 20, 24)
        btn_layout.setSpacing(16)
        card_layout.addWidget(btn_frame)

        if self.on_gerar:
            self.btn_gerar = QPushButton(" Gerar e Salvar")
            if self.icons.get("save"):
                self.btn_gerar.setIcon(QIcon(self.icons["save"]))
                self.btn_gerar.setIconSize(QSize(22, 22))
            self.btn_gerar.setMinimumHeight(48)
            self.btn_gerar.setStyleSheet(self._button_primary_style())
            self.btn_gerar.clicked.connect(self._on_gerar)
            btn_layout.addWidget(self.btn_gerar)

        if self.on_historico:
            self.btn_historico = QPushButton(" Histórico")
            if self.icons.get("history"):
                self.btn_historico.setIcon(QIcon(self.icons["history"]))
                self.btn_historico.setIconSize(QSize(26, 26))
            self.btn_historico.setMinimumHeight(48)
            self.btn_historico.setStyleSheet(self._button_secondary_style())
            self.btn_historico.clicked.connect(self.on_historico)
            btn_layout.addWidget(self.btn_historico)

    def _mascara_data(self, texto):
        if self._aplicando_mascara:
            return

        self._aplicando_mascara = True
        try:
            digitos = "".join(c for c in texto if c.isdigit())[:8]

            if len(digitos) <= 2:
                fmt = digitos
            elif len(digitos) <= 4:
                fmt = digitos[:2] + "/" + digitos[2:]
            else:
                fmt = digitos[:2] + "/" + digitos[2:4] + "/" + digitos[4:]

            if fmt != texto:
                cursor_pos = self.dataemissaoentry.cursorPosition()
                self.dataemissaoentry.blockSignals(True)
                self.dataemissaoentry.setText(fmt)
                self.dataemissaoentry.blockSignals(False)
                self.dataemissaoentry.setCursorPosition(min(len(fmt), cursor_pos + 1))
        finally:
            self._aplicando_mascara = False

    def _on_gerar(self):
        if self.on_gerar:
            self.on_gerar(self.get_form_data())

    def get_form_data(self):
        return {
            "numero": self.nmemosaidaentry.text().strip(),
            "data": self.dataemissaoentry.text().strip(),
            "unloc": self.unlocentry.get().strip(),
            "memo_entrada": self.nmemoentradaentry.text().strip(),
        }

    def get_unloc_codigo(self):
        valor = self.unlocentry.get().strip()
        if " - " in valor:
            return valor.split(" - ")[0]
        return valor

    def clear_form(self):
        self.nmemosaidaentry.clear()
        self.dataemissaoentry.clear()

        if "MAO - MANAUS" in self.unloc_list:
            self.unlocentry.set("MAO - MANAUS")
        elif self.unloc_list:
            self.unlocentry.set(self.unloc_list[0])

        self.nmemoentradaentry.clear()
        self.nmemosaidaentry.setFocus()