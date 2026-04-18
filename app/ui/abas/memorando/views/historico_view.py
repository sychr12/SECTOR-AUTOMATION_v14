# -*- coding: utf-8 -*-
"""Histórico de memorandos — design corporativo com filtros e cores"""

from PyQt6.QtWidgets import (
    QWidget, QDialog, QFrame, QLabel, QPushButton, QLineEdit, QComboBox,
    QVBoxLayout, QHBoxLayout, QScrollArea, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from app.theme import AppTheme
import hashlib

from app.ui.abas.memorando.views.municipio_selector import MunicipioSelector
from app.ui.abas.memorando.municipios import lista_formatada

from app.ui.abas.memorando.style import (
    FILTER_RADIUS,
    FILTER_BORDER,
    FILTER_HOVER,
    FILTER_INPUT_BG,
    FILTER_DROPDOWN_BG,
)

# Cores vibrantes para cada código de município
UNLOC_CORES = {
    "ALV": "#10b981",
    "AMT": "#3b82f6",
    "ANA": "#8b5cf6",
    "ANO": "#f59e0b",
    "APU": "#ec489a",
    "ATN": "#14b8a6",
    "ATZ": "#ef4444",
    "BAZ": "#84cc16",
    "BAR": "#06b6d4",
    "BJC": "#a855f7",
    "BER": "#d946ef",
    "BVR": "#f43f5e",
    "BOA": "#0ea5e9",
    "BBA": "#eab308",
    "CAP": "#22c55e",
    "CAN": "#6366f1",
    "CAF": "#e11d48",
    "CAR": "#ea580c",
    "CAZ": "#0891b2",
    "CIZ": "#c026d3",
    "COD": "#059669",
    "ERN": "#0284c7",
    "ENV": "#9333ea",
    "FBA": "#d97706",
    "GAJ": "#db2777",
    "HIA": "#0d9488",
    "IPX": "#e11d48",
    "IRB": "#7c3aed",
    "ITA": "#c2410c",
    "ITR": "#16a34a",
    "ITG": "#2563eb",
    "JPR": "#7e22ce",
    "JUR": "#ca8a04",
    "JUT": "#be185d",
    "LBR": "#0e7490",
    "MPU": "#4f46e5",
    "MQR": "#b45309",
    "MAO": "#10b981",
    "MAO-ZL": "#34d399",
    "MNX": "#f97316",
    "MTS-ATZ": "#fbbf24",
    "MRA": "#ef4444",
    "MBZ": "#3b82f6",
    "NMD": "#8b5cf6",
    "ITR-NRO": "#06b6d4",
    "MNX-MTP": "#84cc16",
    "LBR-VE": "#14b8a6",
    "VRC": "#a855f7",
    "PRF-BNA": "#ec489a",
    "VLD": "#f59e0b",
    "RLD": "#d946ef",
    "NON": "#0ea5e9",
    "NAR": "#eab308",
    "NAP": "#22c55e",
    "PAR": "#6366f1",
    "PUI": "#e11d48",
    "PRF": "#ea580c",
    "RPE": "#0891b2",
    "SIR": "#c026d3",
    "SAI": "#059669",
    "SJL": "#0284c7",
    "SPO": "#9333ea",
    "SSU": "#d97706",
    "SUL-CAN": "#db2777",
    "SLV": "#0d9488",
    "TBT": "#7c3aed",
    "TPA": "#c2410c",
    "TFF": "#16a34a",
    "TNT": "#2563eb",
    "UAN": "#7e22ce",
    "URC": "#ca8a04",
    "UCB": "#be185d",
    "FOZ": "#0e7490",
}

# Cores alternativas para UNLOC não listados (usar como fallback)
CORES_ALTERNATIVAS = [
    "#10b981", "#3b82f6", "#8b5cf6", "#f59e0b", "#ec489a",
    "#14b8a6", "#ef4444", "#84cc16", "#06b6d4", "#a855f7",
    "#d946ef", "#f43f5e", "#0ea5e9", "#eab308", "#22c55e",
    "#6366f1", "#e11d48", "#ea580c", "#0891b2", "#c026d3",
    "#059669", "#0284c7", "#9333ea", "#d97706", "#db2777",
    "#0d9488", "#7c3aed", "#c2410c", "#16a34a", "#2563eb",
    "#7e22ce", "#ca8a04", "#be185d", "#0e7490", "#4f46e5",
    "#b45309", "#34d399", "#f97316", "#fbbf24",
]


def get_unloc_color(unloc: str) -> str:
    """Retorna uma cor consistente para cada UNLOC"""
    if not unloc or unloc == "—":
        return "#64748b"

    unloc_upper = unloc.upper()

    if "-" in unloc_upper:
        codigo_principal = unloc_upper.split("-")[0]
    elif "/" in unloc_upper:
        codigo_principal = unloc_upper.split("/")[0]
    else:
        codigo_principal = unloc_upper

    if len(codigo_principal) > 3:
        if codigo_principal in UNLOC_CORES:
            return UNLOC_CORES[codigo_principal]
        codigo_principal = codigo_principal[:3]

    if codigo_principal in UNLOC_CORES:
        return UNLOC_CORES[codigo_principal]

    hash_val = int(hashlib.md5(codigo_principal.encode()).hexdigest()[:8], 16)
    return CORES_ALTERNATIVAS[hash_val % len(CORES_ALTERNATIVAS)]


class HistoricoMemorandoView(QDialog):

    def __init__(self, parent, controller,
                 on_visualizar=None, on_baixar=None, icons=None):
        super().__init__(parent)
        self.controller = controller
        self.on_visualizar = on_visualizar
        self.on_baixar = on_baixar
        self.icons = icons or {}

        self._configure_window()
        self._create_widgets()
        self._carregar_dados()

    def _configure_window(self):
        self.setWindowTitle("Histórico de Memorandos")
        self.resize(1200, 750)
        self.setModal(True)
        self.setStyleSheet(f"background-color: {AppTheme.BG_APP};")

    def _frame_transparent(self):
        frame = QFrame()
        frame.setStyleSheet("background: transparent; border: none;")
        return frame

    def _frame_card(self, bg, radius=12, border=0, border_color="transparent"):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border-radius: {radius}px;
                border: {border}px solid {border_color};
            }}
        """)
        return frame

    def _label_icon(self, pixmap, width=None, height=None):
        lbl = QLabel()
        if pixmap:
            lbl.setPixmap(pixmap)
        if width:
            lbl.setFixedWidth(width)
        if height:
            lbl.setFixedHeight(height)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("background: transparent; border: none;")
        return lbl

    def _button_style(self, fg, hover, text_color, radius=10, border=0, border_color="transparent", bold=False):
        weight = 700 if bold else 400
        return f"""
            QPushButton {{
                background-color: {fg};
                color: {text_color};
                border-radius: {radius}px;
                border: {border}px solid {border_color};
                font-size: 12px;
                font-weight: {weight};
                padding: 0 12px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
        """

    def _lineedit_style(self):
        return f"""
            QLineEdit {{
                background-color: {FILTER_INPUT_BG};
                color: {AppTheme.TXT_MAIN};
                border: 1px solid {FILTER_BORDER};
                border-radius: {FILTER_RADIUS}px;
                padding: 0 12px;
                min-height: 38px;
                font-size: 12px;
            }}
        """

    def _combobox_style(self):
        return f"""
            QComboBox {{
                background-color: {FILTER_INPUT_BG};
                color: {AppTheme.TXT_MAIN};
                border: 1px solid {FILTER_BORDER};
                border-radius: {FILTER_RADIUS}px;
                padding: 0 12px;
                min-height: 38px;
                font-size: 12px;
            }}
            QComboBox:hover {{
                background-color: {FILTER_HOVER};
            }}
            QComboBox QAbstractItemView {{
                background-color: {FILTER_DROPDOWN_BG};
                color: {AppTheme.TXT_MAIN};
                border: 1px solid {FILTER_BORDER};
                selection-background-color: {FILTER_HOVER};
                outline: none;
            }}
        """

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget is not None:
                widget.deleteLater()
            elif child_layout is not None:
                self._clear_layout(child_layout)

    def _create_widgets(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(36, 32, 36, 32)
        root_layout.setSpacing(0)

        self.root = self._frame_transparent()
        self.root_layout = QVBoxLayout(self.root)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        self._build_header(self.root_layout)
        self._build_filters(self.root_layout)

        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet(f"background-color: {AppTheme.BG_CARD}; border: none;")
        self.root_layout.addWidget(separator)
        self.root_layout.addSpacing(20)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent;")
        self.lista_layout = QVBoxLayout(self.scroll_content)
        self.lista_layout.setContentsMargins(0, 0, 0, 0)
        self.lista_layout.setSpacing(10)
        self.lista_layout.addStretch()

        self.scroll_area.setWidget(self.scroll_content)
        self.root_layout.addWidget(self.scroll_area, 1)

        root_layout.addWidget(self.root)

    def _limpar_filtros(self):
        self.pesquisa_input.clear()
        self.municipio_selector.set("Todos")
        self.ano_combo.setCurrentText("Todos")
        self.ordem_combo.setCurrentText("Recentes")
        self._carregar_dados()

    def _build_header(self, parent_layout):
        hdr = self._frame_transparent()
        hdr_layout = QHBoxLayout(hdr)
        hdr_layout.setContentsMargins(0, 0, 0, 0)
        hdr_layout.setSpacing(0)

        left = self._frame_transparent()
        left_layout = QHBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        if self.icons.get("history"):
            icon_label = self._label_icon(self.icons["history"], width=28, height=28)
            left_layout.addWidget(icon_label)
            left_layout.addSpacing(12)
        else:
            fallback = QLabel("📋")
            fallback.setStyleSheet(f"""
                color: {AppTheme.TXT_MAIN};
                font-size: 28px;
                background: transparent;
                border: none;
            """)
            left_layout.addWidget(fallback)
            left_layout.addSpacing(12)

        title_frame = self._frame_transparent()
        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(4)

        titulo = QLabel("Histórico de Memorandos")
        titulo.setStyleSheet(f"""
            color: {AppTheme.TXT_MAIN};
            font-size: 26px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)

        subtitulo = QLabel("Visualize, abra e baixe memorandos gerados")
        subtitulo.setStyleSheet(f"""
            color: {AppTheme.TXT_MUTED};
            font-size: 12px;
            font-weight: 400;
            background: transparent;
            border: none;
        """)

        title_layout.addWidget(titulo)
        title_layout.addWidget(subtitulo)

        left_layout.addWidget(title_frame)
        hdr_layout.addWidget(left)
        hdr_layout.addStretch()

        status_badge = QLabel("Lista de memorandos")
        status_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {AppTheme.BG_CARD};
                color: {AppTheme.TXT_MUTED};
                border-radius: 20px;
                padding: 6px 14px;
                font-size: 14px;
                font-weight: 700;
            }}
        """)
        hdr_layout.addWidget(status_badge)

        parent_layout.addWidget(hdr)
        parent_layout.addSpacing(24)

    def _build_filters(self, parent_layout):
        bar = self._frame_card(AppTheme.BG_CARD, radius=16)
        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(16, 10, 14, 10)
        bar_layout.setSpacing(8)

        def add_icon(name, width=18, height=18):
            if self.icons.get(name):
                bar_layout.addWidget(self._label_icon(self.icons[name], width=width, height=height))

        def add_label(text):
            lbl = QLabel(text)
            lbl.setStyleSheet(f"""
                color: {AppTheme.TXT_MUTED};
                font-size: 11px;
                font-weight: 700;
                background: transparent;
                border: none;
            """)
            bar_layout.addWidget(lbl)

        add_icon("search")
        add_label("Buscar")

        self.pesquisa_input = QLineEdit()
        self.pesquisa_input.setPlaceholderText("Número do memo ou UNLOC...")
        self.pesquisa_input.setStyleSheet(self._lineedit_style())
        self.pesquisa_input.textChanged.connect(self._carregar_dados)
        bar_layout.addWidget(self.pesquisa_input, 1)

        add_icon("location")
        add_label("Município")

        lista_municipios = ["Todos"] + lista_formatada()

        self.municipio_selector = MunicipioSelector(
            bar,
            values=lista_municipios,
            default="Todos",
            width=200,
            height=38,
            corner_radius=FILTER_RADIUS,
            fg_color=FILTER_INPUT_BG,
            text_color=AppTheme.TXT_MAIN,
            button_color=FILTER_INPUT_BG,
            button_hover_color=FILTER_HOVER,
            dropdown_fg_color=FILTER_DROPDOWN_BG,
            border_color=FILTER_BORDER,
            border_width=1,
            font=("Segoe UI", 12),
            placeholder="Município",
            command=lambda _: self._carregar_dados(),
        )
        bar_layout.addWidget(self.municipio_selector)

        add_icon("calendar_search")
        add_label("Ano")

        ok, anos = self.controller.listar_anos() if hasattr(self.controller, "listar_anos") else (False, [])
        lista_anos = ["Todos"] + anos if ok and anos else ["Todos"]

        self.ano_combo = QComboBox()
        self.ano_combo.addItems(lista_anos)
        self.ano_combo.setCurrentText("Todos")
        self.ano_combo.setStyleSheet(self._combobox_style())
        self.ano_combo.currentTextChanged.connect(self._carregar_dados)
        self.ano_combo.setFixedWidth(100)
        bar_layout.addWidget(self.ano_combo)

        add_icon("filter")
        add_label("Ordem")

        self.ordem_combo = QComboBox()
        self.ordem_combo.addItems(["Recentes", "Antigos"])
        self.ordem_combo.setCurrentText("Recentes")
        self.ordem_combo.setStyleSheet(self._combobox_style())
        self.ordem_combo.currentTextChanged.connect(self._carregar_dados)
        self.ordem_combo.setFixedWidth(120)
        bar_layout.addWidget(self.ordem_combo)

        bar_layout.addStretch()

        self.btn_limpar = QPushButton(" Limpar Filtros")
        if self.icons.get("delete"):
            self.btn_limpar.setIcon(QIcon(self.icons["delete"]))
            self.btn_limpar.setIconSize(QSize(20, 20))
        self.btn_limpar.setFixedSize(130, 38)
        self.btn_limpar.setStyleSheet(self._button_style(
            FILTER_INPUT_BG, FILTER_HOVER, AppTheme.TXT_MUTED,
            radius=FILTER_RADIUS, border=1, border_color=FILTER_BORDER
        ))
        self.btn_limpar.clicked.connect(self._limpar_filtros)
        bar_layout.addWidget(self.btn_limpar)

        parent_layout.addWidget(bar)
        parent_layout.addSpacing(20)

    def _carregar_dados(self):
        termo = self.pesquisa_input.text().strip()
        municipio = self.municipio_selector.get()
        ano = self.ano_combo.currentText()
        ordem = self.ordem_combo.currentText()

        codigo_municipio = None
        if municipio != "Todos" and " - " in municipio:
            codigo_municipio = municipio.split(" - ")[0]

        self._clear_layout(self.lista_layout)

        loading = QLabel("⏳ Carregando...")
        loading.setStyleSheet(f"""
            color: {AppTheme.TXT_MUTED};
            font-size: 13px;
            background: transparent;
            border: none;
        """)
        loading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lista_layout.addWidget(loading)
        self.lista_layout.addStretch()

        try:
            ok, msg, registros = self.controller.buscar_historico_com_filtros(
                termo=termo,
                codigo_municipio=codigo_municipio,
                ano=ano if ano != "Todos" else None,
                ordem=ordem
            )

            self._clear_layout(self.lista_layout)

            if ok:
                self.atualizar_lista(registros)
            else:
                self._mostrar_erro(msg)
        except Exception as e:
            self._clear_layout(self.lista_layout)
            self._mostrar_erro(f"Erro ao carregar dados: {str(e)}")

    def _mostrar_erro(self, mensagem: str):
        lbl = QLabel(f"❌ Erro: {mensagem}")
        lbl.setStyleSheet("""
            color: #ef4444;
            font-size: 13px;
            background: transparent;
            border: none;
        """)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lista_layout.addWidget(lbl)
        self.lista_layout.addStretch()

    def atualizar_lista(self, registros):
        self._clear_layout(self.lista_layout)

        if not registros:
            lbl = QLabel("📭 Nenhum memorando encontrado.")
            lbl.setStyleSheet(f"""
                color: {AppTheme.TXT_MUTED};
                font-size: 13px;
                background: transparent;
                border: none;
            """)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.lista_layout.addWidget(lbl)
            self.lista_layout.addStretch()
            return

        for idx, reg in enumerate(registros):
            self._card(idx, reg)

        self.lista_layout.addStretch()

    def _card(self, idx: int, reg: dict):
        bg = AppTheme.BG_CARD if idx % 2 == 0 else AppTheme.BG_INPUT
        hover_baixar = "#f1f5f9" if bg == AppTheme.BG_CARD else "#ffffff"

        card = self._frame_card(bg, radius=12)
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(20, 16, 20, 16)
        card_layout.setSpacing(16)

        info = self._frame_transparent()
        info_layout = QVBoxLayout(info)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(10)

        linha1 = self._frame_transparent()
        linha1_layout = QHBoxLayout(linha1)
        linha1_layout.setContentsMargins(0, 0, 0, 0)
        linha1_layout.setSpacing(0)

        memo_info = self._frame_transparent()
        memo_info_layout = QHBoxLayout(memo_info)
        memo_info_layout.setContentsMargins(0, 0, 0, 0)
        memo_info_layout.setSpacing(0)

        if self.icons.get("file_text"):
            memo_info_layout.addWidget(self._label_icon(self.icons["file_text"], width=20, height=20))
            memo_info_layout.addSpacing(8)

        titulo_memo = QLabel(f"Memo Nº {reg.get('numero', '—')}")
        titulo_memo.setStyleSheet(f"""
            color: {AppTheme.TXT_MAIN};
            font-size: 15px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)
        memo_info_layout.addWidget(titulo_memo)
        linha1_layout.addWidget(memo_info)

        unloc = reg.get("unloc", "—")
        if unloc != "—":
            cor_unloc = get_unloc_color(unloc)
            linha1_layout.addSpacing(12)

            badge = QLabel(unloc)
            badge.setStyleSheet(f"""
                QLabel {{
                    background-color: {cor_unloc};
                    color: #ffffff;
                    border-radius: 6px;
                    padding: 3px 12px;
                    font-size: 11px;
                    font-weight: 700;
                }}
            """)
            linha1_layout.addWidget(badge)

        linha1_layout.addStretch()
        info_layout.addWidget(linha1)

        linha2 = self._frame_transparent()
        linha2_layout = QHBoxLayout(linha2)
        linha2_layout.setContentsMargins(0, 0, 0, 0)
        linha2_layout.setSpacing(32)

        meta = [
            ("calendar_days", "Emissão", reg.get("data_emissao", "—")),
            ("clock", "Criado em", reg.get("criado_em", "—")),
            ("user", "Usuário", reg.get("usuario", "—")),
        ]

        for icon_name, titulo, valor in meta:
            bloco = self._frame_transparent()
            bloco_layout = QVBoxLayout(bloco)
            bloco_layout.setContentsMargins(0, 0, 0, 0)
            bloco_layout.setSpacing(2)

            titulo_row = self._frame_transparent()
            titulo_row_layout = QHBoxLayout(titulo_row)
            titulo_row_layout.setContentsMargins(0, 0, 0, 0)
            titulo_row_layout.setSpacing(5)

            if self.icons.get(icon_name):
                titulo_row_layout.addWidget(self._label_icon(self.icons[icon_name], width=16, height=16))

            titulo_lbl = QLabel(titulo)
            titulo_lbl.setStyleSheet("""
                color: #6b7280;
                font-size: 10px;
                font-weight: 400;
                background: transparent;
                border: none;
            """)
            titulo_row_layout.addWidget(titulo_lbl)
            titulo_row_layout.addStretch()

            valor_lbl = QLabel(str(valor))
            valor_lbl.setStyleSheet(f"""
                color: {AppTheme.TXT_MUTED};
                font-size: 11px;
                font-weight: 400;
                background: transparent;
                border: none;
            """)

            bloco_layout.addWidget(titulo_row)
            bloco_layout.addWidget(valor_lbl)
            linha2_layout.addWidget(bloco)

        linha2_layout.addStretch()
        info_layout.addWidget(linha2)

        card_layout.addWidget(info, 1)

        btns = self._frame_transparent()
        btns_layout = QVBoxLayout(btns)
        btns_layout.setContentsMargins(0, 0, 0, 0)
        btns_layout.setSpacing(8)

        if self.on_visualizar:
            texto_visualizar = " Visualizar" if self.icons.get("eye") else "👁️ Visualizar"
            btn_visualizar = QPushButton(texto_visualizar)
            if self.icons.get("eye"):
                btn_visualizar.setIcon(QIcon(self.icons["eye"]))
                btn_visualizar.setIconSize(QSize(22, 22))
            btn_visualizar.setFixedSize(120, 38)
            btn_visualizar.setStyleSheet(self._button_style(
                AppTheme.BTN_PRIMARY,
                AppTheme.BTN_PRIMARY_HOVER,
                "#ffffff",
                radius=10,
                bold=True
            ))
            btn_visualizar.clicked.connect(
                lambda _, mid=reg.get("id"): self._visualizar_com_tratamento(mid)
            )
            btns_layout.addWidget(btn_visualizar)

        if self.on_baixar:
            texto_baixar = " Baixar" if self.icons.get("download") else "⬇️ Baixar"
            btn_baixar = QPushButton(texto_baixar)
            if self.icons.get("download"):
                btn_baixar.setIcon(QIcon(self.icons["download"]))
                btn_baixar.setIconSize(QSize(22, 22))
            btn_baixar.setFixedSize(120, 38)
            btn_baixar.setStyleSheet(self._button_style(
                bg,
                hover_baixar,
                AppTheme.TXT_MAIN,
                radius=10,
                border=0
            ))
            btn_baixar.clicked.connect(
                lambda _, mid=reg.get("id"), num=reg.get("numero", ""): self._baixar_com_tratamento(mid, num)
            )
            btns_layout.addWidget(btn_baixar)

        btns_layout.addStretch()
        card_layout.addWidget(btns, 0)

        self.lista_layout.addWidget(card)

    def _visualizar_com_tratamento(self, memorando_id):
        if not memorando_id:
            QMessageBox.critical(self, "Erro", "ID do memorando não encontrado.")
            return

        try:
            if self.on_visualizar:
                self.on_visualizar(memorando_id)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao abrir memorando:\n{str(e)}")

    def _baixar_com_tratamento(self, memorando_id, numero):
        if not memorando_id:
            QMessageBox.critical(self, "Erro", "ID do memorando não encontrado.")
            return

        try:
            if self.on_baixar:
                self.on_baixar(memorando_id, numero)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao baixar memorando:\n{str(e)}")