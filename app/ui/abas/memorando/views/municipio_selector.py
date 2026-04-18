# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import (
    QFrame, QPushButton, QDialog, QVBoxLayout, QLineEdit,
    QListWidget, QListWidgetItem, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPoint
from PyQt6.QtGui import QFont


class MunicipioSelector(QFrame):
    valueChanged = pyqtSignal(str)

    def __init__(
        self,
        parent,
        values,
        default=None,
        width=220,
        height=44,
        corner_radius=12,
        fg_color="#f8fafc",
        text_color="#1f2937",
        button_color="#f8fafc",
        button_hover_color="#eef2f7",
        dropdown_fg_color="#ffffff",
        border_color="#dbe2ea",
        font=("Segoe UI", 13),
        placeholder="Selecione...",
        command=None,
        border_width=1,
    ):
        super().__init__(parent)

        self.values = list(values or [])
        self.filtered_values = self.values[:]
        self.command = command
        self.placeholder = placeholder
        self.selector_width = width
        self.selector_height = height
        self.corner_radius = corner_radius
        self.fg_color = fg_color
        self.text_color = text_color
        self.button_color = button_color
        self.button_hover_color = button_hover_color
        self.dropdown_fg_color = dropdown_fg_color
        self.border_color = border_color
        self.border_width = border_width
        self.font = font

        self._selected = default if default in self.values else (self.values[0] if self.values else "")
        self._popup = None
        self._closing_popup = False

        self.setStyleSheet("background: transparent; border: none;")
        self._build_main()

    def _font_css(self, size=None, bold=False):
        family = self.font[0] if isinstance(self.font, tuple) and len(self.font) > 0 else "Segoe UI"
        size = size if size is not None else (self.font[1] if isinstance(self.font, tuple) and len(self.font) > 1 else 13)
        weight = 700 if bold else 400
        return family, size, weight

    def _build_main(self):
        self._button = QPushButton(self._selected if self._selected else self.placeholder, self)
        self._button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._button.setFixedSize(self.selector_width, self.selector_height)
        self._button.clicked.connect(self._toggle_popup)

        family, size, weight = self._font_css()
        self._button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.fg_color};
                color: {self.text_color};
                border: {self.border_width}px solid {self.border_color};
                border-radius: {self.corner_radius}px;
                text-align: left;
                padding: 0 12px;
                font-family: "{family}";
                font-size: {size}px;
                font-weight: {weight};
            }}
            QPushButton:hover {{
                background-color: {self.button_hover_color};
            }}
        """)

        self.setFixedSize(self.selector_width, self.selector_height)

    def _toggle_popup(self):
        if self._popup and self._popup.isVisible():
            self._close_popup()
        else:
            self._open_popup()

    def _open_popup(self):
        if self._popup and self._popup.isVisible():
            return

        self._closing_popup = False
        self._popup = QDialog(self, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self._popup.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        self._popup.setModal(False)

        popup_width = max(self.selector_width, 280)
        popup_height = 320

        self._popup.setFixedSize(popup_width, popup_height)
        self._popup.setStyleSheet(f"""
            QDialog {{
                background-color: {self.dropdown_fg_color};
                border: 1px solid {self.border_color};
                border-radius: {self.corner_radius}px;
            }}
        """)

        layout = QVBoxLayout(self._popup)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self._search_entry = QLineEdit()
        self._search_entry.setPlaceholderText("Buscar município...")
        family, _, _ = self._font_css()
        self._search_entry.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.fg_color};
                color: #1f2937;
                border: {self.border_width}px solid {self.border_color};
                border-radius: {self.corner_radius}px;
                padding: 0 12px;
                min-height: 38px;
                font-family: "{family}";
                font-size: 12px;
            }}
        """)
        self._search_entry.textChanged.connect(self._on_search)
        layout.addWidget(self._search_entry)

        self._list_widget = QListWidget()
        self._list_widget.setStyleSheet(f"""
            QListWidget {{
                background-color: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                padding: 8px 10px;
                margin: 2px 0;
                border-radius: {max(2, self.corner_radius - 2)}px;
                color: #1f2937;
                font-family: "{family}";
                font-size: 12px;
            }}
            QListWidget::item:hover {{
                background-color: {self.button_hover_color};
            }}
            QListWidget::item:selected {{
                background-color: {self.button_hover_color};
                color: #1f2937;
            }}
        """)
        self._list_widget.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self._list_widget)

        self.filtered_values = self.values[:]
        self._render_options()

        global_pos = self.mapToGlobal(QPoint(0, self.height() + 4))
        self._popup.move(global_pos)
        self._popup.show()
        self._search_entry.setFocus()

    def _on_search(self, texto):
        try:
            if self._closing_popup:
                return

            termo = texto.strip().lower()

            if not termo:
                self.filtered_values = self.values[:]
            else:
                self.filtered_values = [
                    item for item in self.values
                    if termo in item.lower()
                ]

            self._render_options()
        except Exception:
            pass

    def _render_options(self):
        try:
            if not hasattr(self, "_list_widget") or self._list_widget is None:
                return

            self._list_widget.clear()

            if not self.filtered_values:
                item = QListWidgetItem("Nenhum município encontrado")
                item.setFlags(Qt.ItemFlag.NoItemFlags)
                self._list_widget.addItem(item)
                return

            for item_text in self.filtered_values:
                self._list_widget.addItem(QListWidgetItem(item_text))

            self._list_widget.scrollToTop()
        except Exception:
            pass

    def _on_item_clicked(self, item):
        texto = item.text()
        if texto == "Nenhum município encontrado":
            return
        self.set(texto, trigger=True)

    def _close_popup(self):
        if self._closing_popup:
            return

        self._closing_popup = True
        try:
            if self._popup:
                self._popup.close()
        except Exception:
            pass
        finally:
            self._popup = None
            self._search_entry = None
            self._list_widget = None
            self._closing_popup = False

    def get(self):
        return self._selected

    def set(self, value, trigger=False):
        if value not in self.values:
            return

        self._selected = value
        self._button.setText(value if value else self.placeholder)
        self._close_popup()

        if trigger and callable(self.command):
            self.command(value)

        if trigger:
            self.valueChanged.emit(value)

    def configure_values(self, values, default=None):
        self.values = list(values or [])
        self.filtered_values = self.values[:]

        if default in self.values:
            self._selected = default
        elif self._selected not in self.values:
            self._selected = self.values[0] if self.values else ""

        self._button.setText(self._selected if self._selected else self.placeholder)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        try:
            if self._popup and self._popup.isVisible():
                popup_has_focus = self._popup.isActiveWindow()
                if not popup_has_focus:
                    self._close_popup()
        except Exception:
            pass