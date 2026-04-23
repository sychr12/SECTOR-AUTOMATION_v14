# -*- coding: utf-8 -*-
"""Interface para memorando de saída — design corporativo premium (PyQt6)"""

from PyQt6.QtWidgets import (
    QWidget, QMessageBox, QFrame, QLabel, QPushButton,
    QTextEdit, QVBoxLayout, QHBoxLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPixmap, QIcon, QTextCursor, QTextCharFormat, QColor
import os
from PIL import Image
from datetime import datetime

from ui.base_ui import BaseUI
from .controller import MemorandoController
from .views import MemorandoFormView, HistoricoMemorandoView
from .municipios import lista_formatada, dict_reverso
from app.theme import AppTheme

UNLOC_LIST_FORMATADO = lista_formatada()
UNLOC_CODIGOS = dict_reverso()

_ICON_COLOR = "#1e293b"

# ── Paleta de Cores Premium ──────────────────────────────────────────────────────
_PRIMARY_DARK    = "#0a2540"
_PRIMARY         = "#1a4b6e"
_ACCENT          = "#2c6e9e"
_ACCENT_DARK     = "#1e4a6e"
_ACCENT_LIGHT    = "#e8f0f8"
_BRANCO          = "#ffffff"
_CINZA_BG        = "#f8fafc"
_CINZA_BORDER    = "#e2e8f0"
_CINZA_MEDIO     = "#5a6e8a"
_CINZA_TEXTO     = "#1e2f3e"
_VERDE_STATUS    = "#10b981"
_VERDE_DARK      = "#059669"
_VERDE_LIGHT     = "#d1fae5"
_AMARELO         = "#f59e0b"
_VERMELHO        = "#ef4444"
_VERMELHO_DARK   = "#dc2626"
_AZUL            = "#3b82f6"
_AZUL_DARK       = "#2563eb"
_MUTED           = "#5a6e8a"


class IconManager:
    """Gerenciador de ícones para a interface de memorando"""

    def __init__(self):
        self.icons = {}
        self.icons_dir = r"images\icons\memorando"

    def load_icon(self, filename, size=(24, 24), colorize_to=None):
        """Carrega um ícone da pasta e aplica cor se necessário"""
        try:
            path = os.path.join(self.icons_dir, filename)
            if os.path.exists(path):
                img = Image.open(path)
                img = img.resize(size, Image.Resampling.LANCZOS)

                if colorize_to:
                    if img.mode != "RGBA":
                        img = img.convert("RGBA")

                    data = img.getdata()
                    new_data = []

                    if isinstance(colorize_to, tuple):
                        target_r, target_g, target_b = colorize_to
                    else:
                        hex_color = colorize_to.lstrip("#")
                        target_r, target_g, target_b = tuple(
                            int(hex_color[i:i+2], 16) for i in (0, 2, 4)
                        )

                    for item in data:
                        r, g, b, a = item
                        if a > 0:
                            new_data.append((target_r, target_g, target_b, a))
                        else:
                            new_data.append((r, g, b, a))

                    img.putdata(new_data)

                if img.mode != "RGBA":
                    img = img.convert("RGBA")

                data = img.tobytes("raw", "RGBA")
                pixmap = QPixmap()
                pixmap.loadFromData(data, "RGBA")
                if pixmap.isNull():
                    # fallback via temp png in memory-like conversion
                    temp_path = os.path.join(self.icons_dir, "__temp_icon__.png")
                    img.save(temp_path, format="PNG")
                    pixmap = QPixmap(temp_path)
                    try:
                        os.remove(temp_path)
                    except Exception:
                        pass

                return pixmap
        except Exception:
            pass
        return None

    def setup_icons(self):
        """Configura todos os ícones"""
        icons_config = {
            "document": ("file.png", (36, 36), _ICON_COLOR),
            "file_text": ("file-text.png", (22, 22), _ICON_COLOR),
            "history": ("history.png", (26, 26), _ICON_COLOR),
            "save": ("save.png", (22, 22), (255, 255, 255)),
            "search": ("search.png", (18, 18), _ICON_COLOR),
            "delete": ("delete.png", (20, 20), _ICON_COLOR),
            "download": ("download.png", (22, 22), _ICON_COLOR),
            "eye": ("eye.png", (22, 22), (255, 255, 255)),
            "calendar_search": ("calendar-search.png", (18, 18), _ICON_COLOR),
            "calendar_days": ("calendar-days.png", (16, 16), _ICON_COLOR),
            "clock": ("clock.png", (16, 16), _ICON_COLOR),
            "user": ("user.png", (16, 16), _ICON_COLOR),
            "location": ("location.png", (18, 18), _ICON_COLOR),
            "filter": ("filter.png", (18, 18), _ICON_COLOR),
        }

        for name, (filename, size, color) in icons_config.items():
            self.icons[name] = self.load_icon(filename, size, color)

        return self.icons

    def get(self, name):
        """Retorna um ícone pelo nome"""
        return self.icons.get(name)


class MemorandoUI(BaseUI):

    def __init__(self, parent, usuario=None):
        super().__init__(parent)
        self.usuario = usuario or "sistema"
        self.controller = MemorandoController(self.usuario)

        self.icon_manager = IconManager()
        self.icons = self.icon_manager.setup_icons()

        self.setStyleSheet(f"background-color: {_CINZA_BG};")
        self._timer = None
        self._layout()

    def _set_frame_card_style(self, frame, bg, radius=16, border=1, border_color=_CINZA_BORDER):
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border-radius: {radius}px;
                border: {border}px solid {border_color};
            }}
        """)

    def _set_transparent_frame_style(self, frame):
        frame.setStyleSheet("QFrame { background: transparent; border: none; }")

    def _make_icon_label(self, pixmap, width=None, height=None):
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

    def _layout(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(32, 28, 32, 28)
        root_layout.setSpacing(0)

        main_container = QFrame()
        self._set_transparent_frame_style(main_container)

        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._build_header(main_layout)

        form_card = QFrame()
        self._set_frame_card_style(form_card, _BRANCO, radius=16, border=1, border_color=_CINZA_BORDER)

        form_card_layout = QVBoxLayout(form_card)
        form_card_layout.setContentsMargins(24, 24, 24, 24)
        form_card_layout.setSpacing(0)

        self.form_view = MemorandoFormView(
            form_card, self.controller,
            on_gerar=self.gerar_memorando,
            on_historico=self.abrir_historico,
            icons=self.icons,
            unloc_list=UNLOC_LIST_FORMATADO,
            unloc_dict=UNLOC_CODIGOS
        )
        form_card_layout.addWidget(self.form_view)

        main_layout.addWidget(form_card)
        main_layout.addSpacing(24)

        self._build_log(main_layout)

        root_layout.addWidget(main_container)

    def _build_header(self, parent_layout):
        """Cabeçalho com título e ícone"""
        hdr = QFrame()
        self._set_transparent_frame_style(hdr)

        hdr_layout = QHBoxLayout(hdr)
        hdr_layout.setContentsMargins(0, 0, 0, 0)
        hdr_layout.setSpacing(0)

        left = QFrame()
        self._set_transparent_frame_style(left)
        left_layout = QHBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        if self.icons.get("document"):
            icon_label = self._make_icon_label(self.icons["document"], width=40, height=40)
            left_layout.addWidget(icon_label)
            left_layout.addSpacing(16)

        title_frame = QFrame()
        self._set_transparent_frame_style(title_frame)
        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(4)

        titulo = QLabel("Memorando de Saída")
        titulo.setStyleSheet(f"""
            color: {_CINZA_TEXTO};
            font-size: 28px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)
        titulo.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        subtitulo = QLabel("Geração e controle de memorandos")
        subtitulo.setStyleSheet(f"""
            color: {_MUTED};
            font-size: 13px;
            font-weight: 400;
            background: transparent;
            border: none;
        """)
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        title_layout.addWidget(titulo)
        title_layout.addWidget(subtitulo)

        left_layout.addWidget(title_frame)
        hdr_layout.addWidget(left)

        hdr_layout.addStretch()

        right = QFrame()
        self._set_transparent_frame_style(right)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(2)

        self.lbl_data = QLabel(datetime.now().strftime("%d/%m/%Y"))
        self.lbl_data.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_data.setStyleSheet(f"""
            color: {_ACCENT};
            font-size: 13px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)

        self.lbl_hora = QLabel(datetime.now().strftime("%H:%M"))
        self.lbl_hora.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_hora.setStyleSheet(f"""
            color: {_MUTED};
            font-size: 12px;
            font-weight: 400;
            background: transparent;
            border: none;
        """)

        right_layout.addWidget(self.lbl_data)
        right_layout.addWidget(self.lbl_hora)

        hdr_layout.addWidget(right)

        parent_layout.addWidget(hdr)
        parent_layout.addSpacing(24)

        self._atualizar_hora()

    def _atualizar_hora(self):
        try:
            now = datetime.now()
            self.lbl_data.setText(now.strftime("%d/%m/%Y"))
            self.lbl_hora.setText(now.strftime("%H:%M"))

            if self._timer is None:
                self._timer = QTimer(self)
                self._timer.timeout.connect(self._atualizar_hora)
                self._timer.start(1000)
        except Exception:
            pass

    def _build_log(self, parent_layout):
        """Seção de log de atividades"""
        log_card = QFrame()
        self._set_frame_card_style(log_card, _BRANCO, radius=16, border=1, border_color=_CINZA_BORDER)
        log_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        log_layout = QVBoxLayout(log_card)
        log_layout.setContentsMargins(24, 20, 24, 20)
        log_layout.setSpacing(0)

        log_hdr = QFrame()
        self._set_transparent_frame_style(log_hdr)
        log_hdr_layout = QHBoxLayout(log_hdr)
        log_hdr_layout.setContentsMargins(0, 0, 0, 0)
        log_hdr_layout.setSpacing(0)

        if self.icons.get("file_text"):
            icon_label = self._make_icon_label(self.icons["file_text"], width=24, height=24)
            log_hdr_layout.addWidget(icon_label)
            log_hdr_layout.addSpacing(12)

        titulo_log = QLabel("Registro de Atividade")
        titulo_log.setStyleSheet(f"""
            color: {_CINZA_TEXTO};
            font-size: 16px;
            font-weight: 700;
            background: transparent;
            border: none;
        """)
        log_hdr_layout.addWidget(titulo_log)

        log_hdr_layout.addStretch()

        btn_limpar = QPushButton(" Limpar")
        if self.icons.get("delete"):
            btn_limpar.setIcon(QIcon(self.icons["delete"]))
            btn_limpar.setIconSize(QSize(20, 20))
        btn_limpar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_limpar.setFixedSize(100, 34)
        btn_limpar.setStyleSheet(f"""
            QPushButton {{
                background-color: {_CINZA_BG};
                color: {_MUTED};
                border: none;
                border-radius: 8px;
                font-size: 12px;
                font-weight: 400;
                text-align: center;
                padding: 6px 10px;
            }}
            QPushButton:hover {{
                background-color: {_CINZA_BORDER};
            }}
        """)
        btn_limpar.clicked.connect(self._limpar_log)
        log_hdr_layout.addWidget(btn_limpar)

        log_layout.addWidget(log_hdr)
        log_layout.addSpacing(12)

        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet(f"background-color: {_CINZA_BORDER}; border: none;")
        log_layout.addWidget(separator)
        log_layout.addSpacing(16)

        self.confirmacao = QTextEdit()
        self.confirmacao.setReadOnly(True)
        self.confirmacao.setMinimumHeight(180)
        self.confirmacao.setStyleSheet(f"""
            QTextEdit {{
                background-color: {_CINZA_BG};
                color: {_CINZA_TEXTO};
                border: none;
                border-radius: 8px;
                padding: 8px;
                font-family: Consolas;
                font-size: 11px;
            }}
        """)
        log_layout.addWidget(self.confirmacao, 1)

        parent_layout.addWidget(log_card, 1)

    # ── ações ──────────────────────────────────────────────────────
    def gerar_memorando(self, dados_form):
        numero       = dados_form["numero"]
        data         = dados_form["data"]
        unloc_raw    = dados_form["unloc"]
        memo_entrada = dados_form["memo_entrada"]

        # Extrair apenas o código do UNLOC (ex: "MAO - MANAUS" -> "MAO")
        if " - " in unloc_raw:
            unloc = unloc_raw.split(" - ")[0]
        else:
            unloc = unloc_raw

        self._limpar_log()
        self._log("▶  Iniciando geração do memorando...", "muted")
        self._log(f"   Nº: {numero}  |  Município: {unloc_raw}", "muted")

        try:
            sucesso, mensagem, resultado = self.controller.gerar_memorando(
                numero=numero, data_str=data,
                unloc=unloc, memo_entrada=memo_entrada
            )

            if sucesso:
                self._log(f"✓  {mensagem}", "ok")
                self._log("   Memorando gerado com sucesso!", "ok")
                self.form_view.clear_form()

                resposta = QMessageBox.question(
                    self,
                    "Memorando criado",
                    f"{mensagem}\n\nDeseja abrir agora?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                if resposta == QMessageBox.StandardButton.Yes:
                    if resultado:
                        self.visualizar_memorando(resultado["id"])
            else:
                self._log(f"✕  {mensagem}", "err")
                QMessageBox.critical(self, "Erro", mensagem)
        except Exception as e:
            self._log(f"✕  Erro: {str(e)}", "err")
            QMessageBox.critical(self, "Erro", f"Erro ao gerar memorando:\n{str(e)}")

    def abrir_historico(self):
        """Abre a janela de histórico. Os filtros e carregamento são
        gerenciados internamente pelo próprio HistoricoMemorandoView."""
        self.historico_view = HistoricoMemorandoView(
            self, self.controller,
            on_visualizar=self.visualizar_memorando,
            on_baixar=self.baixar_memorando,
            icons=self.icons,
        )
        try:
            self.historico_view.show()
            self.historico_view.raise_()
            self.historico_view.activateWindow()
        except Exception:
            pass

    def visualizar_memorando(self, mid):
        ok, msg = self.controller.visualizar_memorando(mid)
        if ok:
            self._log(f"✓  {msg}", "ok")
        else:
            QMessageBox.critical(self, "Erro", msg)

    def baixar_memorando(self, mid, numero):
        ok, msg = self.controller.baixar_memorando(mid, numero)
        if ok:
            self._log(f"✓  {msg}", "ok")
            if "salvo em:" in msg:
                resposta = QMessageBox.question(
                    self,
                    "Abrir?",
                    "Abrir o arquivo agora?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                if resposta == QMessageBox.StandardButton.Yes:
                    self.controller.visualizar_memorando(mid)
        else:
            if "cancelada" not in msg.lower():
                QMessageBox.critical(self, "Erro", msg)

    # ── log helpers ─────────────────────────────────────────────────
    _CORES = {"ok": _VERDE_STATUS, "err": _VERMELHO, "muted": _MUTED}

    def _log(self, texto, tipo="muted"):
        try:
            cursor = self.confirmacao.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)

            fmt = QTextCharFormat()
            fmt.setForeground(QColor(self._CORES.get(tipo, _CINZA_MEDIO)))

            ts = datetime.now().strftime("%H:%M:%S")
            cursor.insertText(f"[{ts}] {texto}\n", fmt)

            self.confirmacao.setTextCursor(cursor)
            self.confirmacao.ensureCursorVisible()
        except Exception:
            pass

    def _limpar_log(self):
        try:
            self.confirmacao.clear()
        except Exception:
            pass