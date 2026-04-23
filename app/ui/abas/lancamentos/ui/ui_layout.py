# -*- coding: utf-8 -*-
"""
ui_layout.py — Construção de widgets e estrutura visual (PyQt6).

Design v2:
  • Stat cards com borda colorida sutil
  • Linhas da tabela com altura generosa
  • Badge customizado
  • Seções com pill colorido
  • Histórico com QTableWidget
"""

from PyQt6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit,
    QTabWidget, QScrollArea, QSizePolicy, QHeaderView
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt

from app.theme import AppTheme

# ── Paleta ────────────────────────────────────────────────────────────────────
_VERDE    = "#22c55e"
_VERDE_H  = "#16a34a"
_VERDE_BG = "#0d2818"

_AZUL     = "#3b82f6"
_AZUL_H   = "#2563eb"
_AZUL_BG  = "#0d1f3c"

_AMBER    = "#f59e0b"
_AMBER_H  = "#d97706"
_AMBER_BG = "#2d1f06"

_VERM     = "#ef4444"
_VERM_H   = "#dc2626"
_VERM_BG  = "#2e0f0f"

_MUTED    = "#64748b"
_MUTED_L  = "#94a3b8"

_STATUS_COR = {
    "RENOVACAO": _VERDE,
    "INSCRICAO": _AZUL,
    "DEVOLUCAO": _VERM,
    "LANCADO":   _MUTED,
}

_STATUS_BG = {
    "RENOVACAO": _VERDE_BG,
    "INSCRICAO": _AZUL_BG,
    "DEVOLUCAO": _VERM_BG,
    "LANCADO":   _AMBER_BG,
}

_STATUS_LABEL = {
    "RENOVACAO": "Renovação",
    "INSCRICAO": "Inscrição",
    "DEVOLUCAO": "Devolução",
    "LANCADO":   "Lançado",
}

_FONT_TITLE = ("Segoe UI", 11, "bold")
_FONT_BODY  = ("Segoe UI", 11)
_FONT_SMALL = ("Segoe UI", 10)
_FONT_TINY  = ("Segoe UI", 9, "bold")


# ── Helpers PyQt ──────────────────────────────────────────────────────────────

def _set_font(widget, family="Segoe UI", size=11, bold=False):
    font = QFont(family, size)
    font.setBold(bold)
    widget.setFont(font)
    return widget


def _clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        child_layout = item.layout()
        if widget is not None:
            widget.deleteLater()
        elif child_layout is not None:
            _clear_layout(child_layout)


def _make_scroll_section():
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

    content = QWidget()
    content.setStyleSheet("background: transparent;")
    layout = QVBoxLayout(content)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(6)
    layout.addStretch()

    scroll.setWidget(content)
    return scroll, content, layout


def _pill(text: str, fg: str, bg: str):
    lbl = QLabel(text)
    _set_font(lbl, "Segoe UI", 9, True)
    lbl.setStyleSheet(f"""
        QLabel {{
            color: {fg};
            background-color: {bg};
            border-radius: 6px;
            padding: 3px 8px;
        }}
    """)
    return lbl


def stat_card(titulo: str, valor: str = "0", cor: str = _AZUL):
    """
    Retorna (frame, label_valor)
    """
    frame = QFrame()
    frame.setStyleSheet(f"""
        QFrame {{
            background-color: {AppTheme.BG_CARD};
            border-radius: 16px;
        }}
    """)

    layout = QVBoxLayout(frame)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    accent = QFrame()
    accent.setFixedHeight(3)
    accent.setStyleSheet(f"background-color: {cor}; border-radius: 2px;")
    layout.addWidget(accent)

    inner = QVBoxLayout()
    inner.setContentsMargins(18, 14, 18, 14)
    inner.setSpacing(2)

    lbl_titulo = QLabel(titulo)
    _set_font(lbl_titulo, "Segoe UI", 10, True)
    lbl_titulo.setStyleSheet(f"color: {_MUTED}; background: transparent;")
    inner.addWidget(lbl_titulo)

    lbl_valor = QLabel(valor)
    _set_font(lbl_valor, "Segoe UI", 28, True)
    lbl_valor.setStyleSheet(f"color: {cor}; background: transparent;")
    inner.addWidget(lbl_valor)

    layout.addLayout(inner)
    return frame, lbl_valor


def _secao_titulo(texto: str, cor_pill: str, bg_pill: str, subtexto: str = ""):
    hdr = QFrame()
    hdr.setStyleSheet("background: transparent;")
    row = QHBoxLayout(hdr)
    row.setContentsMargins(20, 16, 20, 8)
    row.setSpacing(12)

    pill = QFrame()
    pill.setFixedSize(4, 28)
    pill.setStyleSheet(f"background-color: {bg_pill}; border-radius: 2px;")
    row.addWidget(pill)

    lbl = QLabel(texto)
    _set_font(lbl, "Segoe UI", 13, True)
    lbl.setStyleSheet(f"color: {AppTheme.TXT_MAIN}; background: transparent;")
    row.addWidget(lbl)

    if subtexto:
        sub = QLabel(subtexto)
        _set_font(sub, "Segoe UI", 10, False)
        sub.setStyleSheet(f"color: {_MUTED}; background: transparent;")
        row.addWidget(sub)

    row.addStretch()
    return hdr


class LancamentoLayout:
    """
    Mixin de layout — herdado por LancamentoUI.
    Apenas constrói a interface; lógica vive nos outros mixins.
    """

    # =========================================================================
    # Raiz
    # =========================================================================
    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 24)
        root.setSpacing(20)

        # Cabeçalho
        hdr = QFrame()
        hdr.setStyleSheet("background: transparent;")
        hdr_layout = QHBoxLayout(hdr)
        hdr_layout.setContentsMargins(0, 0, 0, 0)

        titulo_frame = QFrame()
        titulo_frame.setStyleSheet("background: transparent;")
        titulo_layout = QVBoxLayout(titulo_frame)
        titulo_layout.setContentsMargins(0, 0, 0, 0)
        titulo_layout.setSpacing(4)

        lbl_titulo = QLabel("Lançamento de Processo")
        _set_font(lbl_titulo, "Segoe UI", 24, True)
        lbl_titulo.setStyleSheet(f"color: {AppTheme.TXT_MAIN};")
        titulo_layout.addWidget(lbl_titulo)

        lbl_subtitulo = QLabel("Gestão e registro de processos")
        _set_font(lbl_subtitulo, "Segoe UI", 12, False)
        lbl_subtitulo.setStyleSheet(f"color: {_MUTED};")
        titulo_layout.addWidget(lbl_subtitulo)

        hdr_layout.addWidget(titulo_frame)
        hdr_layout.addStretch()
        root.addWidget(hdr)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {AppTheme.BG_CARD}; border: none;")
        root.addWidget(sep)

        # Stat cards
        stats_grid = QGridLayout()
        stats_grid.setHorizontalSpacing(6)
        stats_grid.setVerticalSpacing(6)

        f0, self._lbl_pendentes  = stat_card("Falta Revisar", "0", _VERM)
        f1, self._lbl_renovacoes = stat_card("Renovações", "0", _VERDE)
        f2, self._lbl_inscricoes = stat_card("Inscrições", "0", _AZUL)
        f3, self._lbl_lancados   = stat_card("Lançados", "0", _MUTED)
        f4, self._lbl_urgentes   = stat_card("Urgentes", "0", _AMBER)
        f5, self._lbl_devolucoes = stat_card("Devoluções", "0", _VERM)

        self._lbl_prontos = self._lbl_renovacoes

        cards = [f0, f1, f2, f3, f4, f5]
        for i, card in enumerate(cards):
            stats_grid.addWidget(card, 0, i)

        root.addLayout(stats_grid)

        # Notebook / Tabs
        self._nb = QTabWidget()
        self._nb.setDocumentMode(True)
        self._nb.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background: transparent;
            }}
            QTabBar::tab {{
                background: {AppTheme.BG_CARD};
                color: {_MUTED};
                padding: 10px 22px;
                border-radius: 10px;
                margin-right: 6px;
                font: 12pt "Segoe UI";
            }}
            QTabBar::tab:selected {{
                background: {AppTheme.BG_INPUT};
                color: {AppTheme.TXT_MAIN};
            }}
        """)
        self._nb.currentChanged.connect(lambda _: self._on_tab())
        root.addWidget(self._nb, 1)

        self._tabs = {}

        for texto, modo_ou_fn in [
            ("🔴  Falta Revisar", "revisar"),
            ("🔄  Renovação",     "renovacao"),
            ("📝  Inscrição",     "inscricao"),
            ("📤  Devoluções",    "devolucoes"),
            ("🔍  Consulta CPF",  "consulta"),
            ("📋  Histórico",     "historico"),
        ]:
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            tab_layout.setContentsMargins(0, 0, 0, 0)
            tab_layout.setSpacing(0)

            self._nb.addTab(tab, texto)
            self._tabs[modo_ou_fn] = tab

            if modo_ou_fn in ("revisar", "renovacao", "inscricao", "devolucoes"):
                self._build_aba_lista(tab, modo=modo_ou_fn)
            elif modo_ou_fn == "consulta":
                self._build_aba_consulta(tab)
            else:
                self._build_aba_historico(tab)

    # =========================================================================
    # Aba Lista
    # =========================================================================
    def _build_aba_lista(self, parent, modo: str):
        layout = parent.layout()

        # Barra superior
        bar = QFrame()
        bar.setStyleSheet(f"background-color: {AppTheme.BG_CARD}; border-radius: 14px;")
        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(14, 12, 14, 12)
        bar_layout.setSpacing(10)

        btn_pasta = QPushButton("📁  Pasta")
        btn_pasta.setFixedHeight(34)
        btn_pasta.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppTheme.BG_INPUT};
                color: {AppTheme.TXT_MAIN};
                border: none;
                border-radius: 8px;
                padding: 0 12px;
            }}
            QPushButton:hover {{
                background-color: {AppTheme.BG_APP};
            }}
        """)
        btn_pasta.clicked.connect(self._selecionar_pasta)
        bar_layout.addWidget(btn_pasta)

        lbl = QLabel("Nenhuma pasta selecionada")
        _set_font(lbl, "Segoe UI", 10)
        lbl.setStyleSheet(f"color: {_MUTED};")
        bar_layout.addWidget(lbl)
        setattr(self, f"_lbl_pasta_{modo}", lbl)

        bar_layout.addStretch()

        btn_atualizar = QPushButton("↺  Atualizar")
        btn_atualizar.setFixedHeight(34)
        btn_atualizar.setStyleSheet(f"""
            QPushButton {{
                background-color: {_AZUL};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {_AZUL_H};
            }}
        """)
        btn_atualizar.clicked.connect(lambda: self._carregar_modo(modo))
        bar_layout.addWidget(btn_atualizar)

        layout.addWidget(bar)

        # Filtro por tipo
        if modo == "revisar":
            filtro_bar = QFrame()
            filtro_bar.setStyleSheet(f"background-color: {AppTheme.BG_CARD}; border-radius: 14px;")
            filtro_layout = QHBoxLayout(filtro_bar)
            filtro_layout.setContentsMargins(18, 10, 18, 10)
            filtro_layout.setSpacing(6)

            lbl_tipo = QLabel("Tipo:")
            _set_font(lbl_tipo, "Segoe UI", 10)
            lbl_tipo.setStyleSheet(f"color: {_MUTED};")
            filtro_layout.addWidget(lbl_tipo)

            _btns = {}

            def _aplicar_filtro(tipo: str):
                self._filtrar_por_tipo(modo, tipo)
                for t, b in _btns.items():
                    if t == tipo:
                        cor_map = {
                            "TODOS": _AZUL,
                            "RENOVACAO": _VERDE,
                            "INSCRICAO": _AZUL,
                            "DEVOLUCAO": _VERM,
                        }
                        hover_map = {
                            "TODOS": _AZUL_H,
                            "RENOVACAO": _VERDE_H,
                            "INSCRICAO": _AZUL_H,
                            "DEVOLUCAO": _VERM_H,
                        }
                        b.setStyleSheet(f"""
                            QPushButton {{
                                background-color: {cor_map.get(t, _AZUL)};
                                color: white;
                                border: none;
                                border-radius: 8px;
                                padding: 6px 12px;
                            }}
                            QPushButton:hover {{
                                background-color: {hover_map.get(t, _AZUL_H)};
                            }}
                        """)
                    else:
                        b.setStyleSheet(f"""
                            QPushButton {{
                                background-color: {AppTheme.BG_INPUT};
                                color: {_MUTED};
                                border: none;
                                border-radius: 8px;
                                padding: 6px 12px;
                            }}
                            QPushButton:hover {{
                                background-color: {AppTheme.BG_APP};
                            }}
                        """)

            for label, tipo_val in [
                ("Todos", "TODOS"),
                ("Renovação", "RENOVACAO"),
                ("Inscrição", "INSCRICAO"),
            ]:
                btn = QPushButton(label)
                btn.clicked.connect(lambda _, t=tipo_val: _aplicar_filtro(t))
                filtro_layout.addWidget(btn)
                _btns[tipo_val] = btn

            _aplicar_filtro("TODOS")
            setattr(self, f"_filtro_btns_{modo}", _btns)
            filtro_layout.addStretch()
            layout.addWidget(filtro_bar)

        # CPF rápido
        if modo == "revisar":
            cpf_bar = QFrame()
            cpf_bar.setStyleSheet(f"background-color: {AppTheme.BG_CARD}; border-radius: 14px;")
            cpf_layout = QHBoxLayout(cpf_bar)
            cpf_layout.setContentsMargins(18, 12, 18, 12)
            cpf_layout.setSpacing(10)

            lbl_cpf = QLabel("Registrar por CPF:")
            _set_font(lbl_cpf, "Segoe UI", 11, True)
            lbl_cpf.setStyleSheet(f"color: {_MUTED_L};")
            cpf_layout.addWidget(lbl_cpf)

            self._aplicando_cpf = False
            self._entry_cpf = QLineEdit()
            self._entry_cpf.setPlaceholderText("000.000.000-00")
            self._entry_cpf.setFixedSize(200, 34)
            self._entry_cpf.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {AppTheme.BG_INPUT};
                    color: {AppTheme.TXT_MAIN};
                    border: none;
                    border-radius: 8px;
                    padding: 0 10px;
                }}
            """)
            self._entry_cpf.returnPressed.connect(self._lancar_por_cpf)
            cpf_layout.addWidget(self._entry_cpf)

            btn_registrar = QPushButton("Registrar")
            btn_registrar.setFixedSize(110, 34)
            btn_registrar.setStyleSheet(f"""
                QPushButton {{
                    background-color: {_VERDE};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {_VERDE_H};
                }}
            """)
            btn_registrar.clicked.connect(self._lancar_por_cpf)
            cpf_layout.addWidget(btn_registrar)

            self._lbl_cpf_status = QLabel("")
            _set_font(self._lbl_cpf_status, "Segoe UI", 10)
            self._lbl_cpf_status.setStyleSheet(f"color: {_MUTED};")
            cpf_layout.addWidget(self._lbl_cpf_status)
            cpf_layout.addStretch()

            layout.addWidget(cpf_bar)

        # Busca devoluções
        if modo == "devolucoes":
            busca_bar = QFrame()
            busca_bar.setStyleSheet(f"background-color: {AppTheme.BG_CARD}; border-radius: 14px;")
            busca_layout = QHBoxLayout(busca_bar)
            busca_layout.setContentsMargins(16, 12, 16, 12)

            icon = QLabel("🔍")
            _set_font(icon, "Segoe UI", 14)
            icon.setStyleSheet(f"color: {_MUTED};")
            busca_layout.addWidget(icon)

            self._dev_busca = QLineEdit()
            self._dev_busca.setPlaceholderText("Buscar por nome, CPF ou motivo...")
            self._dev_busca.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {AppTheme.BG_INPUT};
                    color: {AppTheme.TXT_MAIN};
                    border: none;
                    border-radius: 8px;
                    padding: 0 10px;
                    min-height: 34px;
                }}
            """)
            self._dev_busca.textChanged.connect(self._filtrar_devolucoes)
            busca_layout.addWidget(self._dev_busca, 1)

            btn_limpar = QPushButton("Limpar")
            btn_limpar.setFixedSize(80, 34)
            btn_limpar.setStyleSheet(f"""
                QPushButton {{
                    background-color: {AppTheme.BG_INPUT};
                    color: {_MUTED};
                    border: none;
                    border-radius: 8px;
                }}
                QPushButton:hover {{
                    background-color: {AppTheme.BG_APP};
                }}
            """)
            btn_limpar.clicked.connect(lambda: self._dev_busca.clear())
            busca_layout.addWidget(btn_limpar)

            layout.addWidget(busca_bar)

        # Cabeçalho tabela
        thead = QFrame()
        thead.setStyleSheet(f"background-color: {AppTheme.BG_INPUT}; border-radius: 10px;")
        head_layout = QGridLayout(thead)
        head_layout.setContentsMargins(12, 8, 12, 8)
        head_layout.setHorizontalSpacing(8)
        head_layout.setVerticalSpacing(0)

        head_layout.setColumnStretch(1, 1)

        if modo == "devolucoes":
            cabecalhos = {
                1: "Nome do PDF",
                3: "Motivo",
                4: "Responsável",
                6: "Data",
                7: "Ações",
            }
        else:
            cabecalhos = {
                1: "Nome do PDF",
                3: "Tipo",
                4: "Responsável",
                5: "Lançado por",
                6: "Data",
                7: "Ações",
            }

        for col, txt in cabecalhos.items():
            lbl_head = QLabel(txt)
            _set_font(lbl_head, "Segoe UI", 10, True)
            lbl_head.setStyleSheet(f"color: {_MUTED};")
            head_layout.addWidget(lbl_head, 0, col)

        layout.addWidget(thead)

        # Tabela scrollável
        scroll, content, content_layout = _make_scroll_section()
        setattr(self, f"_tabela_{modo}", content)
        setattr(self, f"_tabela_{modo}_layout", content_layout)
        layout.addWidget(scroll, 1)

        # Rodapé
        rodape = QFrame()
        rodape.setStyleSheet("background: transparent;")
        rodape_layout = QHBoxLayout(rodape)
        rodape_layout.setContentsMargins(2, 10, 2, 2)

        if modo == "revisar":
            btn_impressao = QPushButton("🖨  Enviar para Impressão")
            btn_impressao.setFixedHeight(40)
            btn_impressao.setStyleSheet(f"""
                QPushButton {{
                    background-color: {_AMBER};
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 0 14px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {_AMBER_H};
                }}
            """)
            btn_impressao.clicked.connect(self._enviar_impressao)
            rodape_layout.addWidget(btn_impressao)

        rodape_layout.addStretch()

        lbl_hint = QLabel("Duplo clique para abrir o PDF")
        _set_font(lbl_hint, "Segoe UI", 10)
        lbl_hint.setStyleSheet(f"color: {_MUTED};")
        rodape_layout.addWidget(lbl_hint)

        layout.addWidget(rodape)

    # =========================================================================
    # Linha tabela
    # =========================================================================
    def _criar_linha(self, reg: dict, tabela, modo: str):
        layout = getattr(self, f"_tabela_{modo}_layout", None)
        if layout is None:
            return

        urgente = reg.get("urgencia", False)
        lancado = bool(reg.get("lancado_por"))

        bg = "#1c1007" if urgente and modo == "revisar" else "#071c07" if urgente else AppTheme.BG_CARD

        linha = QFrame()
        linha.setStyleSheet(f"background-color: {bg}; border-radius: 10px;")
        linha_layout = QGridLayout(linha)
        linha_layout.setContentsMargins(6, 6, 14, 6)
        linha_layout.setHorizontalSpacing(8)
        linha_layout.setVerticalSpacing(0)
        linha_layout.setColumnStretch(1, 1)

        cor_accent = (
            _AMBER if urgente else
            _VERM if modo == "devolucoes" else
            _VERDE if modo == "renovacao" else
            _AZUL
        )

        accent = QFrame()
        accent.setFixedWidth(4)
        accent.setStyleSheet(f"background-color: {cor_accent}; border-radius: 2px;")
        linha_layout.addWidget(accent, 0, 0)

        nome_lbl = QLabel(reg.get("nome_pdf", "—"))
        _set_font(nome_lbl, "Segoe UI", 11)
        nome_lbl.setStyleSheet(f"color: {cor_accent};")
        linha_layout.addWidget(nome_lbl, 0, 1)

        if urgente:
            badge = QLabel("URGENTE")
            _set_font(badge, "Segoe UI", 8, True)
            badge.setStyleSheet("""
                QLabel {
                    background-color: #f59e0b;
                    color: #1a0a00;
                    border-radius: 8px;
                    padding: 3px 8px;
                }
            """)
            linha_layout.addWidget(badge, 0, 2)

        if modo == "devolucoes":
            motivo_txt = reg.get("motivo") or "—"
            if len(motivo_txt) > 30:
                motivo_txt = motivo_txt[:30] + "…"
            mot = QLabel(motivo_txt)
            _set_font(mot, "Segoe UI", 9)
            mot.setStyleSheet(f"""
                QLabel {{
                    background-color: {_VERM_BG};
                    color: {_VERM};
                    border-radius: 6px;
                    padding: 3px 10px;
                }}
            """)
            linha_layout.addWidget(mot, 0, 3)
        else:
            status_raw = reg.get("status", "")
            cor_st = _STATUS_COR.get(status_raw, _MUTED)
            bg_st = _STATUS_BG.get(status_raw, AppTheme.BG_INPUT)
            txt_st = _STATUS_LABEL.get(status_raw, status_raw)
            st = QLabel(txt_st)
            _set_font(st, "Segoe UI", 9, True)
            st.setStyleSheet(f"""
                QLabel {{
                    background-color: {bg_st};
                    color: {cor_st};
                    border-radius: 6px;
                    padding: 3px 10px;
                }}
            """)
            linha_layout.addWidget(st, 0, 3)

        resp_lbl = QLabel(reg.get("analisado_por", "—") or "—")
        _set_font(resp_lbl, "Segoe UI", 10)
        resp_lbl.setStyleSheet(f"color: {_MUTED};")
        linha_layout.addWidget(resp_lbl, 0, 4)

        if modo == "devolucoes":
            memo_lbl = QLabel(reg.get("memorando") or "—")
            _set_font(memo_lbl, "Segoe UI", 10)
            memo_lbl.setStyleSheet(f"color: {_MUTED};")
            linha_layout.addWidget(memo_lbl, 0, 5)
        else:
            lanc_lbl = QLabel(reg.get("lancado_por") or "—")
            _set_font(lanc_lbl, "Segoe UI", 10, True)
            lanc_lbl.setStyleSheet(f"color: {_VERDE if lancado else _MUTED};")
            linha_layout.addWidget(lanc_lbl, 0, 5)

        criado = reg.get("criado_em")
        data_txt = criado.strftime("%d/%m/%Y %H:%M") if hasattr(criado, "strftime") else str(criado or "—")
        data_lbl = QLabel(data_txt)
        _set_font(data_lbl, "Segoe UI", 10)
        data_lbl.setStyleSheet(f"color: {_MUTED};")
        linha_layout.addWidget(data_lbl, 0, 6)

        btns = QFrame()
        btns.setStyleSheet("background: transparent;")
        btns_layout = QHBoxLayout(btns)
        btns_layout.setContentsMargins(0, 0, 0, 0)
        btns_layout.setSpacing(4)

        btn_ver = QPushButton("Ver")
        btn_ver.setFixedSize(52, 28)
        btn_ver.setStyleSheet(f"""
            QPushButton {{
                background-color: {_AZUL};
                color: white;
                border: none;
                border-radius: 7px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {_AZUL_H};
            }}
        """)
        btn_ver.clicked.connect(lambda: self._abrir_pdf(reg["id"]))
        btns_layout.addWidget(btn_ver)

        if modo == "revisar" and not lancado:
            btn_ok = QPushButton("✓")
            btn_ok.setFixedSize(36, 28)
            btn_ok.setStyleSheet(f"""
                QPushButton {{
                    background-color: {_VERDE};
                    color: white;
                    border: none;
                    border-radius: 7px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {_VERDE_H};
                }}
            """)
            btn_ok.clicked.connect(lambda: self._lancar_linha(reg))
            btns_layout.addWidget(btn_ok)

        linha_layout.addWidget(btns, 0, 7)

        # seleção visual simples
        def _selecionar():
            self._selecionar_linha(reg, linha)

        mouse_press = linha.mousePressEvent
        mouse_double = linha.mouseDoubleClickEvent

        linha.mousePressEvent = lambda e: (_selecionar(), mouse_press(e) if mouse_press else None)
        linha.mouseDoubleClickEvent = lambda e: (self._abrir_pdf(reg["id"]), mouse_double(e) if mouse_double else None)
        nome_lbl.mousePressEvent = lambda e: _selecionar()
        nome_lbl.mouseDoubleClickEvent = lambda e: self._abrir_pdf(reg["id"])

        layout.insertWidget(layout.count() - 1, linha)

    # =========================================================================
    # Aba Consulta CPF
    # =========================================================================
    def _build_aba_consulta(self, parent):
        layout = parent.layout()

        wrap = QFrame()
        wrap_layout = QVBoxLayout(wrap)
        wrap_layout.setContentsMargins(24, 20, 24, 20)
        wrap_layout.setSpacing(16)

        titulo = QLabel("Consulta de CPF")
        _set_font(titulo, "Segoe UI", 18, True)
        titulo.setStyleSheet(f"color: {AppTheme.TXT_MAIN};")
        wrap_layout.addWidget(titulo)

        busca_frame = QFrame()
        busca_frame.setStyleSheet(f"background-color: {AppTheme.BG_CARD}; border-radius: 14px;")
        busca_layout = QHBoxLayout(busca_frame)
        busca_layout.setContentsMargins(20, 16, 20, 16)
        busca_layout.setSpacing(10)

        lbl = QLabel("CPF:")
        _set_font(lbl, "Segoe UI", 11, True)
        lbl.setStyleSheet(f"color: {_MUTED_L};")
        busca_layout.addWidget(lbl)

        self._entry_consulta = QLineEdit()
        self._entry_consulta.setPlaceholderText("000.000.000-00")
        self._entry_consulta.setFixedSize(220, 38)
        self._entry_consulta.setStyleSheet(f"""
            QLineEdit {{
                background-color: {AppTheme.BG_INPUT};
                color: {AppTheme.TXT_MAIN};
                border: none;
                border-radius: 10px;
                padding: 0 10px;
            }}
        """)
        self._entry_consulta.returnPressed.connect(self._executar_consulta_cpf)
        busca_layout.addWidget(self._entry_consulta)

        btn_consultar = QPushButton("🔍  Consultar")
        btn_consultar.setFixedHeight(38)
        btn_consultar.setStyleSheet(f"""
            QPushButton {{
                background-color: {_AZUL};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 0 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {_AZUL_H};
            }}
        """)
        btn_consultar.clicked.connect(self._executar_consulta_cpf)
        busca_layout.addWidget(btn_consultar)

        btn_limpar = QPushButton("Limpar")
        btn_limpar.setFixedSize(80, 38)
        btn_limpar.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppTheme.BG_INPUT};
                color: {_MUTED};
                border: none;
                border-radius: 10px;
            }}
            QPushButton:hover {{
                background-color: {AppTheme.BG_APP};
            }}
        """)
        btn_limpar.clicked.connect(self._limpar_consulta)
        busca_layout.addWidget(btn_limpar)

        busca_layout.addStretch()

        dica = QLabel("Busca nos dois bancos: PostgreSQL + MySQL CPP")
        _set_font(dica, "Segoe UI", 10)
        dica.setStyleSheet(f"color: {_MUTED};")
        busca_layout.addWidget(dica)

        wrap_layout.addWidget(busca_frame)

        scroll, content, content_layout = _make_scroll_section()
        self._consulta_resultado = content
        self._consulta_resultado_layout = content_layout

        info = QLabel("Digite um CPF acima e pressione Enter ou clique em Consultar.")
        _set_font(info, "Segoe UI", 11)
        info.setStyleSheet(f"color: {_MUTED};")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.insertWidget(0, info)

        wrap_layout.addWidget(scroll, 1)
        layout.addWidget(wrap)

    # =========================================================================
    # Aba Histórico
    # =========================================================================
    def _build_aba_historico(self, parent):
        layout = parent.layout()

        wrap = QFrame()
        wrap_layout = QVBoxLayout(wrap)
        wrap_layout.setContentsMargins(2, 14, 2, 8)
        wrap_layout.setSpacing(10)

        bar = QFrame()
        bar.setStyleSheet(f"background-color: {AppTheme.BG_CARD}; border-radius: 14px;")
        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(18, 14, 14, 14)

        lbl = QLabel("Buscar:")
        _set_font(lbl, "Segoe UI", 11, True)
        lbl.setStyleSheet(f"color: {_MUTED};")
        bar_layout.addWidget(lbl)

        self._hist_busca = QLineEdit()
        self._hist_busca.setPlaceholderText("Nome do PDF, CPF ou analista...")
        self._hist_busca.setStyleSheet(f"""
            QLineEdit {{
                background-color: {AppTheme.BG_INPUT};
                color: {AppTheme.TXT_MAIN};
                border: none;
                border-radius: 8px;
                padding: 0 10px;
                min-height: 34px;
            }}
        """)
        self._hist_busca.textChanged.connect(self._filtrar_historico)
        bar_layout.addWidget(self._hist_busca, 1)

        btn_limpar = QPushButton("Limpar")
        btn_limpar.setFixedSize(80, 34)
        btn_limpar.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppTheme.BG_INPUT};
                color: {_MUTED};
                border: none;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {AppTheme.BG_APP};
            }}
        """)
        btn_limpar.clicked.connect(lambda: self._hist_busca.clear())
        bar_layout.addWidget(btn_limpar)

        wrap_layout.addWidget(bar)

        frame_tb = QFrame()
        frame_tb.setStyleSheet(f"background-color: {AppTheme.BG_CARD}; border-radius: 14px;")
        frame_tb_layout = QVBoxLayout(frame_tb)
        frame_tb_layout.setContentsMargins(8, 8, 8, 8)

        self._hist_tree = QTableWidget(0, 5)
        self._hist_tree.setHorizontalHeaderLabels(
            ["Nome do PDF", "CPF", "Analisado por", "Lançado por", "Data/Hora"]
        )
        self._hist_tree.setStyleSheet(f"""
            QTableWidget {{
                background-color: {AppTheme.BG_CARD};
                color: {AppTheme.TXT_MAIN};
                gridline-color: {AppTheme.BG_INPUT};
                border: none;
            }}
            QHeaderView::section {{
                background-color: {AppTheme.BG_INPUT};
                color: {_MUTED};
                border: none;
                padding: 8px;
                font-weight: bold;
            }}
        """)
        self._hist_tree.verticalHeader().setVisible(False)
        self._hist_tree.setAlternatingRowColors(True)
        self._hist_tree.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._hist_tree.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        header = self._hist_tree.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        frame_tb_layout.addWidget(self._hist_tree)
        wrap_layout.addWidget(frame_tb, 1)

        self._hist_dados = []
        layout.addWidget(wrap)

    # =========================================================================
    # Exibir resultado consulta CPF
    # =========================================================================
    def _exibir_consulta(self, r: dict, cpf_txt: str):
        layout = getattr(self, "_consulta_resultado_layout", None)
        if layout is None:
            return

        _clear_layout(layout)
        layout.addStretch()

        cadastrado = r.get("cadastrado", False)

        banner_bg = _VERDE_BG if cadastrado else _VERM_BG
        accent_cor = _VERDE if cadastrado else _VERM

        banner = QFrame()
        banner.setStyleSheet(f"background-color: {banner_bg}; border-radius: 14px;")
        banner_layout = QVBoxLayout(banner)
        banner_layout.setContentsMargins(0, 0, 0, 0)
        banner_layout.setSpacing(0)

        accent = QFrame()
        accent.setFixedHeight(3)
        accent.setStyleSheet(f"background-color: {accent_cor}; border-radius: 2px;")
        banner_layout.addWidget(accent)

        msg_row = QHBoxLayout()
        msg_row.setContentsMargins(20, 14, 20, 14)

        icone = QLabel("✅" if cadastrado else "❌")
        _set_font(icone, "Segoe UI", 20)
        msg_row.addWidget(icone)

        msg = QLabel(r.get("mensagem", ""))
        _set_font(msg, "Segoe UI", 12, True)
        msg.setWordWrap(True)
        msg.setStyleSheet(f"color: {accent_cor};")
        msg_row.addWidget(msg, 1)

        banner_layout.addLayout(msg_row)
        layout.insertWidget(layout.count() - 1, banner)

        if not cadastrado:
            return

        if r.get("responsavel"):
            sec = QFrame()
            sec.setStyleSheet(f"background-color: {AppTheme.BG_CARD}; border-radius: 14px;")
            sec_layout = QVBoxLayout(sec)
            sec_layout.setContentsMargins(0, 0, 0, 0)
            sec_layout.addWidget(_secao_titulo("Responsável", _AZUL, _AZUL_BG, "quem analisou o processo"))

            nome = QLabel(r["responsavel"])
            _set_font(nome, "Segoe UI", 18, True)
            nome.setStyleSheet(f"color: {_AZUL}; padding-left: 24px; padding-bottom: 16px;")
            sec_layout.addWidget(nome)
            layout.insertWidget(layout.count() - 1, sec)

        if r.get("status"):
            status_raw = r["status"]
            cor_s = _STATUS_COR.get(status_raw, _MUTED)
            bg_s = _STATUS_BG.get(status_raw, AppTheme.BG_INPUT)
            label_s = _STATUS_LABEL.get(status_raw, status_raw)

            sec = QFrame()
            sec.setStyleSheet(f"background-color: {AppTheme.BG_CARD}; border-radius: 14px;")
            sec_layout = QVBoxLayout(sec)
            sec_layout.setContentsMargins(0, 0, 0, 0)
            sec_layout.addWidget(_secao_titulo("Status atual", cor_s, bg_s))

            st = QLabel(label_s)
            _set_font(st, "Segoe UI", 13, True)
            st.setStyleSheet(f"""
                QLabel {{
                    background-color: {bg_s};
                    color: {cor_s};
                    border-radius: 8px;
                    padding: 6px 16px;
                    margin-left: 24px;
                    margin-bottom: 16px;
                    max-width: 150px;
                }}
            """)
            sec_layout.addWidget(st)
            layout.insertWidget(layout.count() - 1, sec)

        # as listas detalhadas continuam visuais, mas simplificadas aqui
        for key, titulo, cor, bg, subt in [
            ("analises", "Análises", _AZUL, _AZUL_BG, "banco novo · PostgreSQL"),
            ("lancamentos", "Lançamentos", _VERDE, _VERDE_BG, "banco novo · PostgreSQL"),
            ("ap_registros", "Inscrições / Devoluções", "#8b5cf6", "#1e1040", "banco analiseap · PostgreSQL"),
            ("cpp_registros", "Banco CPP", _AMBER, _AMBER_BG, "MySQL · somente leitura"),
        ]:
            itens = r.get(key, [])
            if not itens:
                continue

            sec = QFrame()
            sec.setStyleSheet(f"background-color: {AppTheme.BG_CARD}; border-radius: 14px;")
            sec_layout = QVBoxLayout(sec)
            sec_layout.setContentsMargins(0, 0, 0, 10)
            sec_layout.setSpacing(4)
            sec_layout.addWidget(_secao_titulo(f"{titulo} ({len(itens)})", cor, bg, subt))

            for idx, item in enumerate(itens):
                row = QFrame()
                row_bg = AppTheme.BG_INPUT if idx % 2 == 0 else AppTheme.BG_APP
                row.setStyleSheet(f"background-color: {row_bg}; border-radius: 8px;")
                row_layout = QVBoxLayout(row)
                row_layout.setContentsMargins(14, 10, 14, 10)
                row_layout.setSpacing(4)

                nome = QLabel(str(item.get("nome_pdf") or item.get("nome") or "—"))
                _set_font(nome, "Segoe UI", 11, True)
                nome.setStyleSheet(f"color: {AppTheme.TXT_MAIN};")
                row_layout.addWidget(nome)

                detalhes = []
                for k, label in [
                    ("cpf", "CPF"),
                    ("municipio", "Município"),
                    ("memorando", "Memorando"),
                    ("tipo", "Tipo"),
                    ("motivo", "Motivo"),
                    ("analisado_por", "Analisado por"),
                    ("lancado_por", "Lançado por"),
                    ("usuario", "Registrado por"),
                    ("criado_em", "Data"),
                ]:
                    v = item.get(k)
                    if v:
                        detalhes.append(f"{label}: {v}")

                if detalhes:
                    det = QLabel("  •  ".join(detalhes[:4]))
                    _set_font(det, "Segoe UI", 10)
                    det.setStyleSheet(f"color: {_MUTED};")
                    det.setWordWrap(True)
                    row_layout.addWidget(det)

                sec_layout.addWidget(row)

            layout.insertWidget(layout.count() - 1, sec)

        if r.get("cadastrado") and not r.get("cpp_registros"):
            aviso = QFrame()
            aviso.setStyleSheet(f"background-color: {AppTheme.BG_CARD}; border-radius: 14px;")
            aviso_layout = QVBoxLayout(aviso)
            aviso_layout.setContentsMargins(20, 14, 20, 14)

            txt = QLabel("🗄️  Banco CPP — nenhum registro encontrado para este CPF")
            _set_font(txt, "Segoe UI", 11)
            txt.setStyleSheet(f"color: {_MUTED};")
            aviso_layout.addWidget(txt)

            layout.insertWidget(layout.count() - 1, aviso)