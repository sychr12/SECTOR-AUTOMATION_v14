# -*- coding: utf-8 -*-
"""
AnexarUI — interface do módulo Anexar (PyQt6).
Design corporativo com ícones personalizados.
"""

import threading
import os
import tempfile
import webbrowser

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QLineEdit,
    QPushButton, QRadioButton, QFileDialog, QMessageBox, QTabWidget
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPixmap, QIcon

from .controller import AnexarController
from .repository import AnexarRepository
from .services import AnexarService
from .errors import ErrorsTable

from .views.tabelas import CarteirasTable, EmAnaliseTable, HistoricoTable, LogTable
from .views.prontos_view import ProntosView
from .views.theme import safe_print


# ── Paleta Corporativa ──────────────────────────────────────────────────────────
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
_ICON_COLOR      = "#1e293b"


class IconManager:
    """Gerenciador de ícones para a interface de anexos."""

    def __init__(self):
        self.icons = {}
        self.icons_dir = None
        self._find_icons_path()

    def _find_icons_path(self):
        """Encontra o caminho correto para a pasta de ícones."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        possible_paths = [
            os.path.join(current_dir, "..", "..", "images", "icons", "anexos"),
            os.path.join(current_dir, "..", "images", "icons", "anexos"),
            os.path.join(os.path.dirname(current_dir), "images", "icons", "anexos"),
            r"images\icons\anexos",
            r"Q:\ARQUIVOS CPCPR\SECTOR AUTOMATION\images\icons\anexos",
        ]

        for path in possible_paths:
            if os.path.exists(path):
                self.icons_dir = path
                print(f"[IconManager] ✅ Ícones encontrados em: {self.icons_dir}")
                return

        self.icons_dir = possible_paths[0] if possible_paths else ""
        print(f"[IconManager] ⚠️ Pasta de ícones não encontrada: {self.icons_dir}")

    def load_icon(self, filename, size=(24, 24)):
        """Carrega um ícone da pasta como QPixmap."""
        if not self.icons_dir:
            return None

        try:
            path = os.path.join(self.icons_dir, filename)
            if os.path.exists(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    return pixmap.scaled(
                        size[0],
                        size[1],
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
        except Exception as e:
            print(f"[IconManager] Erro ao carregar {filename}: {e}")
        return None

    def setup_icons(self):
        """Configura todos os ícones."""
        icons_config = {
            "analise":   ("analise.png",   (22, 22)),
            "check":     ("check.png",     (22, 22)),
            "clip":      ("clip.png",      (32, 32)),
            "delete":    ("delete.png",    (20, 20)),
            "error":     ("error.png",     (26, 26)),
            "historico": ("historico.png", (22, 22)),
            "keep":      ("keep.png",      (22, 22)),
            "logs":      ("logs.png",      (22, 22)),
            "pause":     ("pause.png",     (20, 20)),
            "play":      ("play.png",      (20, 20)),
            "reload":    ("reload.png",    (20, 20)),
            "relogio":   ("relogio.png",   (26, 26)),
            "successo":  ("successo.png",  (26, 26)),
            "task":      ("task.png",      (22, 22)),
            "todos":     ("todos.png",     (26, 26)),
            "pendentes": ("relogio.png",   (26, 26)),
            "com_pdf":   ("check.png",     (26, 26)),
            "sucesso":   ("successo.png",  (26, 26)),
            "erros":     ("error.png",     (26, 26)),
        }

        for name, (filename, size) in icons_config.items():
            self.icons[name] = self.load_icon(filename, size)

        return self.icons

    def get(self, name):
        """Retorna um QPixmap pelo nome."""
        return self.icons.get(name)


class AnexarUI(QWidget):

    def __init__(self, parent=None, usuario=None):
        super().__init__(parent)
        self.usuario = usuario
        self.controller = AnexarController(usuario)
        self.repository = AnexarRepository()
        self._sucesso = 0
        self._erro = 0

        self.tree_erros = None

        self.icon_manager = IconManager()
        self.icons = self.icon_manager.setup_icons()

        self.lista_cart = None
        self.tree_log = None
        self.tree_hist = None
        self.tree_analise = None
        self._prontos_view = None

        self.controller.set_callbacks(
            log_callback=self._log,
            status_callback=self._set_status,
            update_buttons_callback=self._set_botoes,
        )

        self.setStyleSheet(f"background-color: {_CINZA_BG};")
        self._build()
        self._recarregar()

    # ── Layout ───────────────────────────────────────────────────────────────

    def _build(self):
        """Monta a interface principal."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 28, 32, 28)
        main_layout.setSpacing(20)

        self._build_header(main_layout)
        self._build_barra_acao(main_layout)
        self._build_info_cards(main_layout)
        self._build_stat_cards(main_layout)

        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet(f"background-color: {_CINZA_BORDER};")
        main_layout.addWidget(separator)

        self._build_notebook(main_layout)

    def _build_header(self, parent_layout):
        hdr_layout = QHBoxLayout()
        hdr_layout.setContentsMargins(0, 0, 0, 20)

        title_frame = QWidget()
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(0, 0, 0, 0)

        if self.icons.get("clip"):
            icon_lbl = QLabel()
            icon_lbl.setPixmap(self.icons["clip"])
            title_layout.addWidget(icon_lbl)

        title_text = QWidget()
        title_text_layout = QVBoxLayout(title_text)
        title_text_layout.setContentsMargins(12, 0, 0, 0)

        lbl_title = QLabel("Anexar Processos")
        lbl_title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        lbl_title.setStyleSheet(f"color: {_CINZA_TEXTO};")
        title_text_layout.addWidget(lbl_title)

        lbl_subtitle = QLabel("SIGED | Carteiras Digitais")
        lbl_subtitle.setFont(QFont("Segoe UI", 11))
        lbl_subtitle.setStyleSheet(f"color: {_MUTED};")
        title_text_layout.addWidget(lbl_subtitle)

        title_layout.addWidget(title_text)
        hdr_layout.addWidget(title_frame)

        self._status_badge = QLabel("● Pronto")
        self._status_badge.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self._status_badge.setStyleSheet(f"""
            color: {_VERDE_STATUS};
            background-color: {_BRANCO};
            border-radius: 20px;
            padding: 6px 14px;
        """)
        hdr_layout.addWidget(self._status_badge, alignment=Qt.AlignmentFlag.AlignRight)

        parent_layout.addLayout(hdr_layout)

    def _build_barra_acao(self, parent_layout):
        bar_layout = QHBoxLayout()
        bar_layout.setSpacing(12)

        self.btn_iniciar = QPushButton(" Iniciar Anexação")
        if self.icons.get("play"):
            self.btn_iniciar.setIcon(QIcon(self.icons.get("play")))
        self.btn_iniciar.clicked.connect(self._iniciar)
        self.btn_iniciar.setFixedHeight(44)
        self.btn_iniciar.setStyleSheet(f"""
            QPushButton {{
                background-color: {_VERDE_STATUS};
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 13px;
                font-weight: bold;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background-color: {_VERDE_DARK};
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
            }}
        """)
        bar_layout.addWidget(self.btn_iniciar)

        self.btn_parar = QPushButton(" Parar")
        if self.icons.get("pause"):
            self.btn_parar.setIcon(QIcon(self.icons.get("pause")))
        self.btn_parar.clicked.connect(self._parar)
        self.btn_parar.setFixedHeight(44)
        self.btn_parar.setEnabled(False)
        self.btn_parar.setStyleSheet(f"""
            QPushButton {{
                background-color: {_VERMELHO};
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 13px;
                font-weight: bold;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background-color: {_VERMELHO_DARK};
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
            }}
        """)
        bar_layout.addWidget(self.btn_parar)

        btn_recarregar = QPushButton(" Recarregar")
        if self.icons.get("reload"):
            btn_recarregar.setIcon(QIcon(self.icons.get("reload")))
        btn_recarregar.clicked.connect(self._recarregar)
        btn_recarregar.setFixedHeight(44)
        btn_recarregar.setStyleSheet(f"""
            QPushButton {{
                background-color: {_CINZA_BG};
                color: {_CINZA_TEXTO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 10px;
                font-size: 13px;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background-color: {_CINZA_BORDER};
            }}
        """)
        bar_layout.addWidget(btn_recarregar)

        btn_limpar_log = QPushButton(" Limpar Log")
        if self.icons.get("delete"):
            btn_limpar_log.setIcon(QIcon(self.icons.get("delete")))
        btn_limpar_log.clicked.connect(self._limpar_log)
        btn_limpar_log.setFixedHeight(44)
        btn_limpar_log.setStyleSheet(f"""
            QPushButton {{
                background-color: {_CINZA_BG};
                color: {_CINZA_TEXTO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 10px;
                font-size: 13px;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background-color: {_CINZA_BORDER};
            }}
        """)
        bar_layout.addWidget(btn_limpar_log)

        sep = QFrame()
        sep.setFixedSize(1, 32)
        sep.setStyleSheet(f"background-color: {_CINZA_BORDER};")
        bar_layout.addWidget(sep)

        lbl_filtro = QLabel("Filtrar:")
        lbl_filtro.setFont(QFont("Segoe UI", 11))
        lbl_filtro.setStyleSheet(f"color: {_MUTED};")
        bar_layout.addWidget(lbl_filtro)

        self._filtro_pendentes = QRadioButton(" Pendentes")
        self._filtro_pendentes.setChecked(True)
        self._filtro_pendentes.toggled.connect(self._recarregar)
        self._filtro_pendentes.setStyleSheet(f"color: {_CINZA_TEXTO};")
        bar_layout.addWidget(self._filtro_pendentes)

        self._filtro_todas = QRadioButton(" Todas")
        self._filtro_todas.toggled.connect(self._recarregar)
        self._filtro_todas.setStyleSheet(f"color: {_CINZA_TEXTO};")
        bar_layout.addWidget(self._filtro_todas)

        bar_layout.addStretch()

        search_frame = QFrame()
        search_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {_BRANCO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 10px;
            }}
        """)
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(12, 0, 12, 0)

        lbl_search = QLabel("🔍")
        lbl_search.setStyleSheet(f"color: {_MUTED};")
        search_layout.addWidget(lbl_search)

        self._search_entry = QLineEdit()
        self._search_entry.setPlaceholderText("Buscar por nome ou CPF...")
        self._search_entry.setStyleSheet("border: none; padding: 8px;")
        self._search_entry.textChanged.connect(self._on_search)
        search_layout.addWidget(self._search_entry)

        bar_layout.addWidget(search_frame)

        parent_layout.addLayout(bar_layout)

    def _build_info_cards(self, parent_layout):
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)

        card_db = self._create_info_card("Banco de Dados", "keep", "Conectando...")
        cards_layout.addWidget(card_db)
        self._lbl_db = card_db.findChild(QLabel, "value")

        card_tabela = self._create_info_card("Tabela", "task", "carteiras_digitais")
        cards_layout.addWidget(card_tabela)

        card_cred = self._create_info_card("Credencial SEFAZ", "check", "...")
        cards_layout.addWidget(card_cred)
        self._lbl_cred = card_cred.findChild(QLabel, "value")

        parent_layout.addLayout(cards_layout)

    def _create_info_card(self, title, icon_key, value):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {_BRANCO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 12px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)

        top_layout = QHBoxLayout()
        if self.icons.get(icon_key):
            icon_lbl = QLabel()
            icon_lbl.setPixmap(self.icons[icon_key])
            top_layout.addWidget(icon_lbl)

        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        lbl_title.setStyleSheet(f"color: {_MUTED};")
        top_layout.addWidget(lbl_title)
        top_layout.addStretch()
        layout.addLayout(top_layout)

        lbl_value = QLabel(value)
        lbl_value.setObjectName("value")
        lbl_value.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        lbl_value.setStyleSheet(f"color: {_CINZA_TEXTO};")
        layout.addWidget(lbl_value)

        return card

    def _build_stat_cards(self, parent_layout):
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(8)

        cards_config = [
            ("total", "Total", _AZUL, "todos"),
            ("pendente", "Pendentes", _AMARELO, "pendentes"),
            ("gerado", "Com PDF", _VERDE_STATUS, "com_pdf"),
            ("sucesso", "Sucesso", _VERDE_STATUS, "sucesso"),
            ("erro", "Erros", _VERMELHO, "erros"),
        ]

        self._stat_cards = {}

        for key, title, color, icon_key in cards_config:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {_BRANCO};
                    border: 1px solid {_CINZA_BORDER};
                    border-radius: 12px;
                }}
            """)
            layout = QVBoxLayout(card)
            layout.setContentsMargins(16, 12, 16, 12)

            top_layout = QHBoxLayout()
            if self.icons.get(icon_key):
                icon_lbl = QLabel()
                icon_lbl.setPixmap(self.icons[icon_key])
                top_layout.addWidget(icon_lbl)

            lbl_valor = QLabel("0")
            lbl_valor.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
            lbl_valor.setStyleSheet(f"color: {color};")
            top_layout.addWidget(lbl_valor, alignment=Qt.AlignmentFlag.AlignRight)
            layout.addLayout(top_layout)

            lbl_title = QLabel(title)
            lbl_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            lbl_title.setStyleSheet(f"color: {_MUTED};")
            layout.addWidget(lbl_title)

            line = QFrame()
            line.setFixedHeight(2)
            line.setStyleSheet(f"background-color: {color}; border-radius: 1px;")
            layout.addWidget(line)

            self._stat_cards[key] = lbl_valor
            stats_layout.addWidget(card)

        parent_layout.addLayout(stats_layout)

    def _build_notebook(self, parent_layout):
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                background-color: {_BRANCO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 8px;
            }}
            QTabBar::tab {{
                background-color: {_CINZA_BG};
                padding: 10px 24px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {_BRANCO};
                border-bottom: 2px solid {_ACCENT};
            }}
        """)

        tab_carteiras = QWidget()
        self.lista_cart, _ = CarteirasTable.criar(
            tab_carteiras,
            self._baixar_pdf,
            self._visualizar_pdf,
            self._excluir_pdf,
        )
        layout_cart = QVBoxLayout(tab_carteiras)
        layout_cart.setContentsMargins(12, 12, 12, 12)
        layout_cart.addWidget(self.lista_cart)
        self.tab_widget.addTab(tab_carteiras, " Carteiras ")

        tab_analise = QWidget()
        self.tree_analise, _ = EmAnaliseTable.criar(tab_analise)
        layout_analise = QVBoxLayout(tab_analise)
        layout_analise.setContentsMargins(12, 12, 12, 12)
        layout_analise.addWidget(self.tree_analise)
        self.tab_widget.addTab(tab_analise, " Em Análise ")

        tab_historico = QWidget()
        self.tree_hist, _ = HistoricoTable.criar(tab_historico)
        layout_hist = QVBoxLayout(tab_historico)
        layout_hist.setContentsMargins(12, 12, 12, 12)
        layout_hist.addWidget(self.tree_hist)
        self.tab_widget.addTab(tab_historico, " Histórico ")

        tab_log = QWidget()
        self.tree_log, _ = LogTable.criar(tab_log)
        layout_log = QVBoxLayout(tab_log)
        layout_log.setContentsMargins(12, 12, 12, 12)
        layout_log.addWidget(self.tree_log)
        self.tab_widget.addTab(tab_log, " Log ")

        tab_erros = QWidget()
        self.tree_erros, _ = ErrorsTable.criar(tab_erros)
        layout_erros = QVBoxLayout(tab_erros)
        layout_erros.setContentsMargins(12, 12, 12, 12)
        layout_erros.addWidget(self.tree_erros)
        self.tab_widget.addTab(tab_erros, " Erros ")

        tab_prontos = QWidget()
        self._prontos_view = ProntosView(tab_prontos, self.repository)
        layout_prontos = QVBoxLayout(tab_prontos)
        layout_prontos.setContentsMargins(12, 12, 12, 12)
        layout_prontos.addWidget(self._prontos_view)
        self.tab_widget.addTab(tab_prontos, " Prontos ")

        parent_layout.addWidget(self.tab_widget)

    # ── Dados ─────────────────────────────────────────────────────────────────

    def _recarregar(self):
        def _worker():
            try:
                cred = self.repository.buscar_credencial_sefaz()
                is_pendentes = self._filtro_pendentes.isChecked()
                rows = (
                    self.repository.buscar_carteiras_pendentes()
                    if is_pendentes else
                    self.repository.buscar_todas_carteiras()
                )
                hist = self.repository.buscar_historico_anexados()
                analise = self.repository.buscar_em_analise()
                stats = self.repository.estatisticas()

                QTimer.singleShot(0, lambda: self._lbl_cred.setText(cred["usuario"] if cred else "NENHUMA ATIVA"))
                QTimer.singleShot(0, lambda: self._lbl_db.setText(f"Conectado · {len(rows)} registro(s)"))
                QTimer.singleShot(0, lambda: CarteirasTable.carregar(
                    self.lista_cart, rows, self._baixar_pdf, self._visualizar_pdf, self._excluir_pdf
                ))
                QTimer.singleShot(0, lambda: HistoricoTable.carregar(self.tree_hist, hist))
                QTimer.singleShot(0, lambda: EmAnaliseTable.carregar(self.tree_analise, analise))
                QTimer.singleShot(0, lambda: self._atualizar_stats(
                    int(stats.get("total") or 0),
                    int(stats.get("pendentes") or 0),
                    int(stats.get("gerados") or 0)
                ))
                if self._prontos_view:
                    QTimer.singleShot(0, self._prontos_view.recarregar)
            except Exception as exc:
                QTimer.singleShot(0, lambda: QMessageBox.critical(self, "Erro de conexão", str(exc)))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_search(self, query):
        if not query.strip():
            self._recarregar()
            return

        def _worker():
            try:
                is_pendentes = self._filtro_pendentes.isChecked()
                rows = (
                    self.repository.buscar_carteiras_pendentes()
                    if is_pendentes else
                    self.repository.buscar_todas_carteiras()
                )
                q = query.lower()
                filtrados = [
                    r for r in rows
                    if q in str(r.get("nome", "")).lower()
                    or q in str(r.get("cpf", ""))
                ]
                QTimer.singleShot(0, lambda: CarteirasTable.carregar(
                    self.lista_cart, filtrados, self._baixar_pdf, self._visualizar_pdf, self._excluir_pdf
                ))
                QTimer.singleShot(0, lambda: self._lbl_db.setText(f"Conectado · {len(filtrados)} resultado(s)"))
            except Exception as exc:
                QTimer.singleShot(0, lambda: QMessageBox.critical(self, "Erro", str(exc)))

        threading.Thread(target=_worker, daemon=True).start()

    def _atualizar_stats(self, total, pendente, gerado):
        self._stat_cards["total"].setText(str(total))
        self._stat_cards["pendente"].setText(str(pendente))
        self._stat_cards["gerado"].setText(str(gerado))
        self._stat_cards["sucesso"].setText(str(self._sucesso))
        self._stat_cards["erro"].setText(str(self._erro))

    # ── PDF ───────────────────────────────────────────────────────────────────

    def _baixar_pdf(self, record_id: int):
        def _worker():
            try:
                res = self.repository.buscar_pdf_por_id(record_id)
                if not res:
                    QTimer.singleShot(0, lambda: QMessageBox.warning(
                        self, "Aviso", "PDF ainda não gerado para este registro."
                    ))
                    return
                nome, dados = res
                QTimer.singleShot(0, lambda: self._salvar_dialog(nome, dados))
            except Exception as exc:
                QTimer.singleShot(0, lambda: QMessageBox.critical(self, "Erro", str(exc)))

        threading.Thread(target=_worker, daemon=True).start()

    def _salvar_dialog(self, nome: str, dados: bytes):
        destino, _ = QFileDialog.getSaveFileName(
            self, "Salvar carteira como...", nome, "PDF Files (*.pdf);;All Files (*.*)"
        )
        if not destino:
            return
        with open(destino, "wb") as f:
            f.write(dados)
        QMessageBox.information(self, "Salvo", f"✅ PDF salvo em:\n{destino}")

    def _visualizar_pdf(self, record_id: int):
        def _worker():
            try:
                res = self.repository.buscar_pdf_por_id(record_id)
                if not res:
                    QTimer.singleShot(0, lambda: QMessageBox.warning(
                        self, "Aviso", "PDF ainda não gerado para este registro."
                    ))
                    return
                _, dados = res

                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(dados)
                    tmp_path = tmp.name

                webbrowser.open(tmp_path)

                QTimer.singleShot(
                    5000,
                    lambda: os.unlink(tmp_path) if os.path.exists(tmp_path) else None
                )
            except Exception as exc:
                QTimer.singleShot(0, lambda: QMessageBox.critical(self, "Erro", str(exc)))

        threading.Thread(target=_worker, daemon=True).start()

    def _excluir_pdf(self, record_id: int, nome: str):
        reply = QMessageBox.question(
            self,
            "Confirmação",
            f"Tem certeza que deseja excluir o PDF '{nome}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        def _worker():
            try:
                sucesso = self.repository.excluir_pdf_por_id(record_id)
                if sucesso:
                    QTimer.singleShot(0, lambda: QMessageBox.information(
                        self, "Excluído", f"✅ PDF '{nome}' excluído com sucesso."
                    ))
                    QTimer.singleShot(0, self._recarregar)
                else:
                    QTimer.singleShot(0, lambda: QMessageBox.warning(
                        self, "Aviso", f"Nenhum PDF encontrado para '{nome}'."
                    ))
            except Exception as exc:
                QTimer.singleShot(0, lambda: QMessageBox.critical(self, "Erro", str(exc)))

        threading.Thread(target=_worker, daemon=True).start()

    # ── Callbacks do controller ───────────────────────────────────────────────

    def _log(self, status, mensagem, tag="info"):
        safe_print(f"[{status}] {mensagem}")
        QTimer.singleShot(0, lambda: LogTable.add(self.tree_log, status, mensagem, tag))

        if tag.lower() == "sucesso":
            self._sucesso += 1
            QTimer.singleShot(0, lambda: self._stat_cards["sucesso"].setText(str(self._sucesso)))
            if self._prontos_view:
                QTimer.singleShot(500, self._prontos_view.recarregar)
        elif tag.lower() == "erro":
            self._erro += 1
            QTimer.singleShot(0, lambda: self._stat_cards["erro"].setText(str(self._erro)))
            if self.tree_erros is not None:
                QTimer.singleShot(0, lambda: ErrorsTable.adicionar(self.tree_erros, status, mensagem, "erro"))

    def _set_status(self, texto, tipo="info"):
        cores = {
            "primary": _ACCENT,
            "success": _VERDE_STATUS,
            "error": _VERMELHO,
            "warning": _AMARELO,
            "info": _MUTED
        }
        QTimer.singleShot(0, lambda: self._status_badge.setText(f"● {texto}"))
        QTimer.singleShot(0, lambda: self._status_badge.setStyleSheet(f"""
            color: {cores.get(tipo, _MUTED)};
            background-color: {_BRANCO};
            border-radius: 20px;
            padding: 6px 14px;
        """))

    def _set_botoes(self, habilitar_iniciar, habilitar_parar):
        QTimer.singleShot(0, lambda: self.btn_iniciar.setEnabled(habilitar_iniciar))
        QTimer.singleShot(0, lambda: self.btn_parar.setEnabled(habilitar_parar))

    # ── Ações ─────────────────────────────────────────────────────────────────

    def _iniciar(self):
        if self.controller.verificar_processando():
            QMessageBox.warning(self, "Aviso", "Processamento já em andamento!")
            return

        faltantes = AnexarService.verificar_dependencias()
        if faltantes:
            QMessageBox.critical(
                self,
                "Dependências faltando",
                "Instale os seguintes pacotes:\n" + "\n".join(faltantes)
            )
            return

        if not self.controller.iniciar_processamento():
            return

        self._sucesso = 0
        self._erro = 0
        self._stat_cards["sucesso"].setText("0")
        self._stat_cards["erro"].setText("0")
        self.tab_widget.setCurrentIndex(3)

        threading.Thread(target=self.controller.executar_processamento, daemon=True).start()

    def _parar(self):
        self.controller.parar_processamento()

    def _limpar_log(self):
        LogTable.limpar(self.tree_log)
        self._set_status("Pronto", "info")