# -*- coding: utf-8 -*-
"""
ui_layout.py — Construção de widgets e estrutura visual.

Melhorias de design v2:
  • Stat cards com borda colorida sutil (accent left-border)
  • Linhas da tabela com altura generosa e separador hover
  • Badge URGENTE repaginado (pill arredondado)
  • Seções da consulta CPF com ícone pill colorido
  • Histórico com Treeview mais legível
  • Cores padronizadas e modo escuro consistente
"""
from tkinter import ttk

import customtkinter as ctk

from app.theme import AppTheme

# ── Paleta ────────────────────────────────────────────────────────────────────
_VERDE   = "#22c55e"
_VERDE_H = "#16a34a"
_VERDE_BG = "#0d2818"
_AZUL    = "#3b82f6"
_AZUL_H  = "#2563eb"
_AZUL_BG = "#0d1f3c"
_AMBER   = "#f59e0b"
_AMBER_H = "#d97706"
_AMBER_BG = "#2d1f06"
_VERM    = "#ef4444"
_VERM_H  = "#dc2626"
_VERM_BG = "#2e0f0f"
_MUTED   = "#64748b"
_MUTED_L = "#94a3b8"

_STATUS_COR = {
    "RENOVACAO": _VERDE,
    "INSCRICAO": _AZUL,
    "LANCADO":   _MUTED,
}

_FONT_TITLE  = ("Segoe UI", 11, "bold")
_FONT_BODY   = ("Segoe UI", 11)
_FONT_SMALL  = ("Segoe UI", 10)
_FONT_TINY   = ("Segoe UI", 9, "bold")


# ── Helpers de widget ─────────────────────────────────────────────────────────

def _pill(parent, text: str, fg: str, bg: str, **kw) -> ctk.CTkLabel:
    """Label pill com fundo colorido."""
    return ctk.CTkLabel(
        parent, text=text,
        font=_FONT_TINY, text_color=fg,
        fg_color=bg, corner_radius=6,
        padx=8, pady=2, **kw
    )


def stat_card(parent, titulo: str, valor: str = "0",
              cor: str = _AZUL, cor_bg: str = _AZUL_BG) -> tuple:
    """
    Card de estatística com accent colorido no topo.
    Retorna (frame, label_valor).
    """
    f = ctk.CTkFrame(parent, fg_color=AppTheme.BG_CARD, corner_radius=16)

    # Barra de accent no topo
    accent = ctk.CTkFrame(f, fg_color=cor, height=3, corner_radius=2)
    accent.pack(fill="x", padx=0, pady=(0, 0))

    ctk.CTkLabel(f, text=titulo,
                 font=("Segoe UI", 10, "bold"),
                 text_color=_MUTED).pack(anchor="w", padx=18, pady=(14, 2))

    lbl = ctk.CTkLabel(f, text=valor,
                       font=("Segoe UI", 28, "bold"),
                       text_color=cor)
    lbl.pack(anchor="w", padx=18, pady=(0, 14))
    return f, lbl


def _secao_titulo(parent, texto: str, cor_pill: str,
                  bg_pill: str, subtexto: str = "") -> ctk.CTkFrame:
    """
    Cabeçalho de seção com pill colorido à esquerda.
    Retorna o frame do cabeçalho.
    """
    hdr = ctk.CTkFrame(parent, fg_color="transparent")
    hdr.pack(fill="x", padx=20, pady=(16, 8))

    pill = ctk.CTkFrame(hdr, fg_color=bg_pill,
                        width=4, height=28, corner_radius=2)
    pill.pack(side="left", padx=(0, 12))
    pill.pack_propagate(False)

    ctk.CTkLabel(hdr, text=texto,
                 font=("Segoe UI", 13, "bold"),
                 text_color=AppTheme.TXT_MAIN).pack(side="left")

    if subtexto:
        ctk.CTkLabel(hdr, text=subtexto,
                     font=_FONT_SMALL,
                     text_color=_MUTED).pack(side="left", padx=(10, 0))
    return hdr


# ── Mixin principal ───────────────────────────────────────────────────────────

class LancamentoLayout:
    """
    Mixin de layout — herdado por LancamentoUI.
    Apenas constrói a interface; lógica vive nos outros mixins.
    """

    # =========================================================================
    # Raiz
    # =========================================================================
    def _build(self):
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=32, pady=24)

        # ── Cabeçalho ────────────────────────────────────────────────────────
        hdr = ctk.CTkFrame(wrap, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 20))

        titulo_frame = ctk.CTkFrame(hdr, fg_color="transparent")
        titulo_frame.pack(side="left")
        ctk.CTkLabel(titulo_frame, text="Lançamento de Processo",
                     font=("Segoe UI", 24, "bold"),
                     text_color=AppTheme.TXT_MAIN).pack(anchor="w")
        ctk.CTkLabel(titulo_frame, text="Gestão e registro de processos",
                     font=("Segoe UI", 12),
                     text_color=_MUTED).pack(anchor="w")

        # Separador
        ctk.CTkFrame(wrap, height=1,
                     fg_color=AppTheme.BG_CARD).pack(fill="x", pady=(0, 20))

        # ── Stat cards ───────────────────────────────────────────────────────
        stats = ctk.CTkFrame(wrap, fg_color="transparent")
        stats.pack(fill="x", pady=(0, 20))
        for i in range(5):
            stats.grid_columnconfigure(i, weight=1)

        f0, self._lbl_pendentes  = stat_card(stats, "Falta Revisar", cor=_VERM,  cor_bg=_VERM_BG)
        f1, self._lbl_prontos    = stat_card(stats, "Prontos",        cor=_VERDE, cor_bg=_VERDE_BG)
        f2, self._lbl_lancados   = stat_card(stats, "Lançados",       cor=_AZUL,  cor_bg=_AZUL_BG)
        f3, self._lbl_urgentes   = stat_card(stats, "Urgentes",       cor=_AMBER, cor_bg=_AMBER_BG)
        f4, self._lbl_devolucoes = stat_card(stats, "Devoluções",     cor=_VERM,  cor_bg=_VERM_BG)

        f0.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        f1.grid(row=0, column=1, sticky="nsew", padx=2)
        f2.grid(row=0, column=2, sticky="nsew", padx=2)
        f3.grid(row=0, column=3, sticky="nsew", padx=2)
        f4.grid(row=0, column=4, sticky="nsew", padx=(4, 0))

        # ── Notebook ─────────────────────────────────────────────────────────
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Lanc.TNotebook",
                        background=AppTheme.BG_APP, borderwidth=0)
        style.configure("Lanc.TNotebook.Tab",
                        background=AppTheme.BG_CARD,
                        foreground=_MUTED,
                        font=("Segoe UI", 12),
                        padding=(22, 10))
        style.map("Lanc.TNotebook.Tab",
                  background=[("selected", AppTheme.BG_INPUT)],
                  foreground=[("selected", AppTheme.TXT_MAIN)])

        nb = ttk.Notebook(wrap, style="Lanc.TNotebook")
        nb.pack(fill="both", expand=True)
        self._nb = nb

        for texto, modo_ou_fn in [
            ("  🔴  Falta Revisar  ", "revisar"),
            ("  ✅  Prontos  ",        "prontos"),
            ("  📤  Devoluções  ",     "devolucoes"),
            ("  🔍  Consulta CPF  ",  "consulta"),
            ("  📋  Histórico  ",     "historico"),
        ]:
            aba = ctk.CTkFrame(nb, fg_color="transparent")
            nb.add(aba, text=texto)
            if modo_ou_fn in ("revisar", "prontos", "devolucoes"):
                self._build_aba_lista(aba, modo=modo_ou_fn)
            elif modo_ou_fn == "consulta":
                self._build_aba_consulta(aba)
            else:
                self._build_aba_historico(aba)

        nb.bind("<<NotebookTabChanged>>", lambda _: self._on_tab())

    # =========================================================================
    # Aba Lista — Falta Revisar / Prontos
    # =========================================================================
    def _build_aba_lista(self, parent, modo: str):
        # ── Barra de ferramentas ──────────────────────────────────────────────
        bar = ctk.CTkFrame(parent, fg_color=AppTheme.BG_CARD, corner_radius=14)
        bar.pack(fill="x", padx=2, pady=(14, 10))

        ctk.CTkButton(
            bar, text="📁  Pasta",
            height=34, corner_radius=8, width=100,
            fg_color=AppTheme.BG_INPUT, hover_color=AppTheme.BG_APP,
            font=_FONT_BODY, text_color=AppTheme.TXT_MAIN,
            command=self._selecionar_pasta,
        ).pack(side="left", padx=(14, 0), pady=12)

        lbl = ctk.CTkLabel(bar, text="Nenhuma pasta selecionada",
                           font=_FONT_SMALL, text_color=_MUTED)
        lbl.pack(side="left", padx=10, pady=12)
        setattr(self, f"_lbl_pasta_{modo}", lbl)

        ctk.CTkButton(
            bar, text="↺  Atualizar",
            height=34, corner_radius=8, width=120,
            fg_color=_AZUL, hover_color=_AZUL_H,
            font=_FONT_TITLE, text_color="#fff",
            command=lambda m=modo: self._carregar_modo(m),
        ).pack(side="right", padx=14, pady=12)

        # ── CPF rápido (só revisar) ───────────────────────────────────────────
        if modo == "revisar":
            cpf_bar = ctk.CTkFrame(parent, fg_color=AppTheme.BG_CARD,
                                   corner_radius=14)
            cpf_bar.pack(fill="x", padx=2, pady=(0, 10))

            ctk.CTkLabel(cpf_bar, text="Registrar por CPF:",
                         font=_FONT_TITLE,
                         text_color=_MUTED_L,
                         ).pack(side="left", padx=(18, 10), pady=12)

            self._cpf_var       = ctk.StringVar()
            self._aplicando_cpf = False
            self._cpf_var.trace_add("write", self._mascara_cpf)

            self._entry_cpf = ctk.CTkEntry(
                cpf_bar, textvariable=self._cpf_var,
                placeholder_text="000.000.000-00",
                height=34, corner_radius=8, width=200,
                fg_color=AppTheme.BG_INPUT,
                border_color=AppTheme.BG_INPUT,
                font=("Segoe UI", 13),
                text_color=AppTheme.TXT_MAIN,
            )
            self._entry_cpf.pack(side="left", pady=12)
            self._entry_cpf.bind("<Return>", self._lancar_por_cpf)

            ctk.CTkButton(
                cpf_bar, text="Registrar",
                height=34, corner_radius=8, width=110,
                fg_color=_VERDE, hover_color=_VERDE_H,
                font=_FONT_TITLE, text_color="#fff",
                command=self._lancar_por_cpf,
            ).pack(side="left", padx=(10, 0), pady=12)

            self._lbl_cpf_status = ctk.CTkLabel(
                cpf_bar, text="",
                font=_FONT_SMALL, text_color=_MUTED)
            self._lbl_cpf_status.pack(side="left", padx=14, pady=12)

        # ── Barra de busca (só devoluções) ────────────────────────────────────
        if modo == "devolucoes":
            busca_bar = ctk.CTkFrame(parent, fg_color=AppTheme.BG_CARD,
                                     corner_radius=14)
            busca_bar.pack(fill="x", padx=2, pady=(0, 10))

            ctk.CTkLabel(busca_bar, text="🔍",
                         font=("Segoe UI", 14),
                         text_color=_MUTED).pack(side="left", padx=(16, 6), pady=12)

            self._dev_busca_var = ctk.StringVar()
            self._dev_busca_var.trace_add(
                "write", lambda *_: self._filtrar_devolucoes())

            ctk.CTkEntry(
                busca_bar,
                textvariable=self._dev_busca_var,
                placeholder_text="Buscar por nome, CPF ou motivo...",
                height=34, corner_radius=8,
                fg_color=AppTheme.BG_INPUT,
                border_color=AppTheme.BG_INPUT,
                font=_FONT_BODY,
                text_color=AppTheme.TXT_MAIN,
            ).pack(side="left", fill="x", expand=True, pady=12)

            ctk.CTkButton(
                busca_bar, text="Limpar", width=80, height=34,
                corner_radius=8,
                fg_color=AppTheme.BG_INPUT, hover_color=AppTheme.BG_APP,
                font=_FONT_BODY, text_color=_MUTED,
                command=lambda: self._dev_busca_var.set(""),
            ).pack(side="right", padx=(8, 16), pady=12)

        # ── Cabeçalho da tabela ───────────────────────────────────────────────
        thead = ctk.CTkFrame(parent, fg_color=AppTheme.BG_INPUT,
                             corner_radius=10)
        thead.pack(fill="x", padx=2, pady=(0, 2))
        thead.grid_columnconfigure(0, weight=0, minsize=22)
        thead.grid_columnconfigure(1, weight=1)
        thead.grid_columnconfigure(2, weight=0, minsize=80)
        thead.grid_columnconfigure(3, weight=0, minsize=100)
        thead.grid_columnconfigure(4, weight=0, minsize=110)
        thead.grid_columnconfigure(5, weight=0, minsize=110)
        thead.grid_columnconfigure(6, weight=0, minsize=120)
        thead.grid_columnconfigure(7, weight=0, minsize=90)

        if modo == "devolucoes":
            cabecalhos = [
                (1, "Nome do PDF"),
                (2, ""),
                (3, "Motivo"),
                (4, "Responsável"),
                (5, ""),
                (6, "Data"),
                (7, "Ações"),
            ]
        else:
            cabecalhos = [
                (1, "Nome do PDF"),
                (2, ""),
                (3, "Status"),
                (4, "Responsável"),
                (5, "Lançado por"),
                (6, "Data"),
                (7, "Ações"),
            ]
        for col, txt in cabecalhos:
            ctk.CTkLabel(
                thead, text=txt,
                font=("Segoe UI", 10, "bold"),
                text_color=_MUTED, anchor="w",
            ).grid(row=0, column=col, padx=(12 if col == 1 else 8, 0),
                   pady=8, sticky="w")

        # ── Tabela scrollável ─────────────────────────────────────────────────
        tabela = ctk.CTkScrollableFrame(
            parent, fg_color=AppTheme.BG_CARD, corner_radius=14,
            scrollbar_button_color=AppTheme.BG_INPUT,
            scrollbar_button_hover_color=_MUTED,
        )
        tabela.pack(fill="both", expand=True, padx=2)
        setattr(self, f"_tabela_{modo}", tabela)

        # ── Rodapé ────────────────────────────────────────────────────────────
        rodape = ctk.CTkFrame(parent, fg_color="transparent")
        rodape.pack(fill="x", pady=(10, 2), padx=2)

        if modo == "revisar":
            ctk.CTkButton(
                rodape, text="🖨  Enviar para Impressão",
                height=40, corner_radius=10,
                fg_color=_AMBER, hover_color=_AMBER_H,
                font=("Segoe UI", 12, "bold"), text_color="#fff",
                command=self._enviar_impressao,
            ).pack(side="left")

        ctk.CTkLabel(
            rodape, text="Duplo clique para abrir o PDF",
            font=_FONT_SMALL, text_color=_MUTED,
        ).pack(side="right")

    # =========================================================================
    # Linha da tabela — design v2
    # =========================================================================
    def _criar_linha(self, reg: dict, tabela, modo: str):
        urgente = reg.get("urgencia", False)
        lancado = bool(reg.get("lancado_por"))

        # Fundo base
        if urgente:
            bg = "#1c1007" if modo == "revisar" else "#071c07"
        else:
            bg = AppTheme.BG_CARD

        linha = ctk.CTkFrame(tabela, fg_color=bg, corner_radius=10)
        linha.pack(fill="x", pady=2, padx=4)

        # col 0=accent | 1=nome(expand) | 2=badge | 3=status | 4=resp | 5=lancado | 6=data | 7=btns
        linha.grid_columnconfigure(0, weight=0, minsize=6)
        linha.grid_columnconfigure(1, weight=1)
        linha.grid_columnconfigure(2, weight=0, minsize=80)
        linha.grid_columnconfigure(3, weight=0, minsize=100)
        linha.grid_columnconfigure(4, weight=0, minsize=110)
        linha.grid_columnconfigure(5, weight=0, minsize=110)
        linha.grid_columnconfigure(6, weight=0, minsize=120)
        linha.grid_columnconfigure(7, weight=0, minsize=90)

        cor_accent = _AMBER if urgente else (_AZUL if modo == "revisar" else _VERDE)

        # Accent colorido na lateral esquerda
        accent = ctk.CTkFrame(linha, fg_color=cor_accent, width=4, height=36, corner_radius=2)
        accent.grid(row=0, column=0, padx=(6, 0), pady=6, sticky="ns")
        accent.grid_propagate(False)

        linha.bind("<Button-1>",
                   lambda _, r=reg, f=linha: self._selecionar_linha(r, f))
        linha.bind("<Double-1>",
                   lambda _, rid=reg["id"]: self._abrir_pdf(rid))

        # Nome do PDF — coluna expansível
        lbl = ctk.CTkLabel(
            linha, text=reg.get("nome_pdf", "—"),
            anchor="w", cursor="hand2",
            font=_FONT_BODY, text_color=cor_accent,
        )
        lbl.grid(row=0, column=1, padx=(12, 8), pady=6, sticky="ew")
        lbl.bind("<Button-1>",
                 lambda _, r=reg, f=linha: self._selecionar_linha(r, f))
        lbl.bind("<Double-1>",
                 lambda _, rid=reg["id"]: self._abrir_pdf(rid))

        # Badge URGENTE
        if urgente:
            badge = ctk.CTkFrame(linha, fg_color=_AMBER, corner_radius=8)
            ctk.CTkLabel(badge, text="URGENTE",
                         font=("Segoe UI", 8, "bold"),
                         text_color="#1a0a00",
                         padx=8, pady=2).pack()
            badge.grid(row=0, column=2, padx=(0, 4), pady=6)
        else:
            ctk.CTkLabel(linha, text="").grid(row=0, column=2)

        # Status pill ou Motivo (devoluções)
        if modo == "devolucoes":
            motivo_txt = reg.get("motivo") or "—"
            if len(motivo_txt) > 30:
                motivo_txt = motivo_txt[:30] + "…"
            mot_frame = ctk.CTkFrame(linha, fg_color=_VERM_BG, corner_radius=6)
            ctk.CTkLabel(mot_frame, text=motivo_txt,
                         font=("Segoe UI", 9),
                         text_color=_VERM).pack(padx=10, pady=3)
            mot_frame.grid(row=0, column=3, padx=8, pady=6, sticky="w")
        else:
            cor_st     = _STATUS_COR.get(reg.get("status", ""), _MUTED)
            status_txt = reg.get("status", "")
            st_bg = {
                "RENOVACAO": _VERDE_BG,
                "INSCRICAO": _AZUL_BG,
                "LANCADO":   AppTheme.BG_INPUT,
            }.get(status_txt, AppTheme.BG_INPUT)
            st_frame = ctk.CTkFrame(linha, fg_color=st_bg, corner_radius=6)
            ctk.CTkLabel(st_frame, text=status_txt,
                         font=("Segoe UI", 9, "bold"),
                         text_color=cor_st).pack(padx=10, pady=3)
            st_frame.grid(row=0, column=3, padx=8, pady=6, sticky="w")

        # Responsável
        ctk.CTkLabel(
            linha, text=reg.get("analisado_por", "—") or "—",
            anchor="center", font=_FONT_SMALL, text_color=_MUTED,
        ).grid(row=0, column=4, padx=8, pady=6, sticky="ew")

        # Lançado por (ou memorando para devoluções)
        if modo == "devolucoes":
            memo_txt = reg.get("memorando") or "—"
            ctk.CTkLabel(
                linha, text=memo_txt, anchor="center",
                font=_FONT_SMALL, text_color=_MUTED,
            ).grid(row=0, column=5, padx=8, pady=6, sticky="ew")
        else:
            lancado_txt = reg.get("lancado_por") or "—"
            ctk.CTkLabel(
                linha, text=lancado_txt, anchor="center",
                font=_FONT_TITLE,
                text_color=_VERDE if lancado else _MUTED,
            ).grid(row=0, column=5, padx=8, pady=6, sticky="ew")

        # Data
        criado   = reg.get("criado_em")
        data_txt = (criado.strftime("%d/%m/%Y %H:%M")
                    if criado and hasattr(criado, "strftime")
                    else str(criado or "—"))
        ctk.CTkLabel(
            linha, text=data_txt, anchor="center",
            font=_FONT_SMALL, text_color=_MUTED,
        ).grid(row=0, column=6, padx=8, pady=6, sticky="ew")

        # Botões
        btns = ctk.CTkFrame(linha, fg_color="transparent")
        btns.grid(row=0, column=7, padx=(4, 14), pady=6, sticky="e")

        ctk.CTkButton(
            btns, text="Ver", width=52, height=28,
            corner_radius=7, fg_color=_AZUL, hover_color=_AZUL_H,
            font=("Segoe UI", 10, "bold"), text_color="#fff",
            command=lambda rid=reg["id"]: self._abrir_pdf(rid),
        ).pack(side="left", padx=2)

        if modo == "revisar" and not lancado:
            ctk.CTkButton(
                btns, text="✓", width=36, height=28,
                corner_radius=7, fg_color=_VERDE, hover_color=_VERDE_H,
                font=("Segoe UI", 13), text_color="#fff",
                command=lambda r=reg: self._lancar_linha(r),
            ).pack(side="left", padx=2)

    # =========================================================================
    # Aba Consulta CPF
    # =========================================================================
    def _build_aba_consulta(self, parent):
        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=24, pady=20)

        # ── Título ────────────────────────────────────────────────────────────
        ctk.CTkLabel(
            wrap, text="Consulta de CPF",
            font=("Segoe UI", 18, "bold"),
            text_color=AppTheme.TXT_MAIN,
        ).pack(anchor="w", pady=(0, 14))

        # ── Barra de busca ────────────────────────────────────────────────────
        busca_frame = ctk.CTkFrame(wrap, fg_color=AppTheme.BG_CARD,
                                   corner_radius=14)
        busca_frame.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(busca_frame, text="CPF:",
                     font=_FONT_TITLE,
                     text_color=_MUTED_L,
                     ).pack(side="left", padx=(20, 10), pady=16)

        self._consulta_cpf_var       = ctk.StringVar()
        self._aplicando_consulta_cpf = False
        self._consulta_cpf_var.trace_add("write", self._mascara_consulta_cpf)

        self._entry_consulta = ctk.CTkEntry(
            busca_frame,
            textvariable=self._consulta_cpf_var,
            placeholder_text="000.000.000-00",
            height=38, corner_radius=10, width=220,
            fg_color=AppTheme.BG_INPUT,
            border_color=AppTheme.BG_INPUT,
            font=("Segoe UI", 14),
            text_color=AppTheme.TXT_MAIN,
        )
        self._entry_consulta.pack(side="left", pady=16)
        self._entry_consulta.bind("<Return>", self._executar_consulta_cpf)

        ctk.CTkButton(
            busca_frame, text="🔍  Consultar",
            height=38, corner_radius=10,
            fg_color=_AZUL, hover_color=_AZUL_H,
            font=("Segoe UI", 12, "bold"), text_color="#fff",
            command=self._executar_consulta_cpf,
        ).pack(side="left", padx=(12, 0), pady=16)

        ctk.CTkButton(
            busca_frame, text="Limpar",
            height=38, corner_radius=10, width=80,
            fg_color=AppTheme.BG_INPUT, hover_color=AppTheme.BG_APP,
            font=_FONT_BODY, text_color=_MUTED,
            command=self._limpar_consulta,
        ).pack(side="left", padx=(8, 0), pady=16)

        # Dica
        ctk.CTkLabel(
            busca_frame,
            text="Busca nos dois bancos: PostgreSQL + MySQL CPP",
            font=_FONT_SMALL, text_color=_MUTED,
        ).pack(side="right", padx=20)

        # ── Área de resultado ─────────────────────────────────────────────────
        self._consulta_resultado = ctk.CTkScrollableFrame(
            wrap, fg_color=AppTheme.BG_CARD, corner_radius=14,
            scrollbar_button_color=AppTheme.BG_INPUT,
            scrollbar_button_hover_color=_MUTED,
        )
        self._consulta_resultado.pack(fill="both", expand=True)

        ctk.CTkLabel(
            self._consulta_resultado,
            text="Digite um CPF acima e pressione Enter ou clique em Consultar.",
            text_color=_MUTED,
            font=_FONT_BODY,
        ).pack(pady=50)

    # =========================================================================
    # Aba Histórico
    # =========================================================================
    def _build_aba_historico(self, parent):
        # ── Barra de busca ────────────────────────────────────────────────────
        bar = ctk.CTkFrame(parent, fg_color=AppTheme.BG_CARD, corner_radius=14)
        bar.pack(fill="x", padx=2, pady=(14, 10))

        self._hist_busca = ctk.StringVar()
        self._hist_busca.trace_add("write", lambda *_: self._filtrar_historico())

        ctk.CTkLabel(bar, text="Buscar:",
                     font=_FONT_TITLE, text_color=_MUTED, width=60,
                     ).pack(side="left", padx=(18, 6), pady=14)

        ctk.CTkEntry(
            bar, textvariable=self._hist_busca,
            placeholder_text="Nome do PDF, CPF ou analista...",
            height=34, corner_radius=8,
            fg_color=AppTheme.BG_INPUT,
            border_color=AppTheme.BG_INPUT,
            font=_FONT_BODY, text_color=AppTheme.TXT_MAIN,
        ).pack(side="left", fill="x", expand=True, padx=(0, 8), pady=10)

        ctk.CTkButton(
            bar, text="Limpar", width=80, height=34, corner_radius=8,
            fg_color=AppTheme.BG_INPUT, hover_color=AppTheme.BG_APP,
            font=_FONT_BODY, text_color=_MUTED,
            command=lambda: self._hist_busca.set(""),
        ).pack(side="right", padx=14, pady=10)

        # ── Treeview ──────────────────────────────────────────────────────────
        frame_tb = ctk.CTkFrame(parent, fg_color=AppTheme.BG_CARD,
                                corner_radius=14)
        frame_tb.pack(fill="both", expand=True, padx=2, pady=(0, 8))

        style = ttk.Style()
        style.configure(
            "HistL.Treeview",
            background=AppTheme.BG_CARD,
            fieldbackground=AppTheme.BG_CARD,
            foreground=AppTheme.TXT_MAIN,
            rowheight=36,
            font=("Segoe UI", 11),
            borderwidth=0,
        )
        style.configure(
            "HistL.Treeview.Heading",
            background=AppTheme.BG_INPUT,
            foreground=_MUTED,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
        )
        style.map("HistL.Treeview",
                  background=[("selected", "#1e3a5f")],
                  foreground=[("selected", "#ffffff")])

        cols = ("pdf", "cpf", "analisado", "lancado", "criado")
        self._hist_tree = ttk.Treeview(
            frame_tb, columns=cols, show="headings",
            style="HistL.Treeview", selectmode="browse",
        )

        for col, titulo, w, stretch in [
            ("pdf",       "Nome do PDF",   300, True),
            ("cpf",       "CPF",           130, False),
            ("analisado", "Analisado por", 150, False),
            ("lancado",   "Lançado por",   150, False),
            ("criado",    "Data/Hora",     130, False),
        ]:
            self._hist_tree.heading(col, text=titulo)
            self._hist_tree.column(col, width=w, minwidth=60, stretch=stretch)

        vsb = ttk.Scrollbar(frame_tb, orient="vertical",
                            command=self._hist_tree.yview)
        self._hist_tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y", pady=8, padx=(0, 4))
        self._hist_tree.pack(fill="both", expand=True, padx=8, pady=8)

        self._hist_tree.tag_configure("par",   background=AppTheme.BG_CARD)
        self._hist_tree.tag_configure("impar", background=AppTheme.BG_INPUT)
        self._hist_dados: list = []

    # =========================================================================
    # Exibir resultado consulta CPF — design v2
    # =========================================================================
    def _exibir_consulta(self, r: dict, cpf_txt: str):
        for w in self._consulta_resultado.winfo_children():
            w.destroy()

        cadastrado = r.get("cadastrado", False)

        # ── Banner de status ──────────────────────────────────────────────────
        banner_bg = _VERDE_BG if cadastrado else _VERM_BG
        banner    = ctk.CTkFrame(self._consulta_resultado,
                                 fg_color=banner_bg, corner_radius=14)
        banner.pack(fill="x", padx=8, pady=(10, 6))

        # Borda colorida no topo do banner
        accent_cor = _VERDE if cadastrado else _VERM
        ctk.CTkFrame(banner, fg_color=accent_cor,
                     height=3, corner_radius=2).pack(fill="x")

        msg_row = ctk.CTkFrame(banner, fg_color="transparent")
        msg_row.pack(fill="x", padx=20, pady=14)

        icone_txt = "✅" if cadastrado else "❌"
        ctk.CTkLabel(msg_row, text=icone_txt,
                     font=("Segoe UI", 20)).pack(side="left", padx=(0, 12))
        ctk.CTkLabel(msg_row,
                     text=r.get("mensagem", ""),
                     font=("Segoe UI", 12, "bold"),
                     text_color=accent_cor,
                     anchor="w", justify="left",
                     wraplength=700,
                     ).pack(side="left", fill="x", expand=True)

        if not cadastrado:
            return

        # ── Responsável ───────────────────────────────────────────────────────
        if r.get("responsavel"):
            sec = ctk.CTkFrame(self._consulta_resultado,
                               fg_color=AppTheme.BG_CARD, corner_radius=14)
            sec.pack(fill="x", padx=8, pady=4)
            _secao_titulo(sec, "Responsável", _AZUL, _AZUL_BG,
                          "quem analisou o processo")
            ctk.CTkLabel(sec,
                         text=r["responsavel"],
                         font=("Segoe UI", 18, "bold"),
                         text_color=_AZUL,
                         ).pack(anchor="w", padx=24, pady=(0, 16))

        # ── Status ────────────────────────────────────────────────────────────
        if r.get("status"):
            cor_s  = _STATUS_COR.get(r["status"], _MUTED)
            st_sec = ctk.CTkFrame(self._consulta_resultado,
                                  fg_color=AppTheme.BG_CARD, corner_radius=14)
            st_sec.pack(fill="x", padx=8, pady=4)
            _secao_titulo(st_sec, "Status atual", cor_s,
                          {_VERDE: _VERDE_BG, _AZUL: _AZUL_BG}.get(cor_s, AppTheme.BG_INPUT))
            st_pill = ctk.CTkFrame(st_sec, fg_color=AppTheme.BG_INPUT,
                                   corner_radius=8)
            ctk.CTkLabel(st_pill, text=r["status"],
                         font=("Segoe UI", 13, "bold"),
                         text_color=cor_s).pack(padx=16, pady=6)
            st_pill.pack(anchor="w", padx=24, pady=(0, 16))

        # ── Análises (banco novo) ─────────────────────────────────────────────
        analises = r.get("analises", [])
        if analises:
            sec_a = ctk.CTkFrame(self._consulta_resultado,
                                 fg_color=AppTheme.BG_CARD, corner_radius=14)
            sec_a.pack(fill="x", padx=8, pady=4)
            _secao_titulo(sec_a, f"Análises ({len(analises)})",
                          _AZUL, _AZUL_BG, "banco novo · PostgreSQL")

            for idx, a in enumerate(analises):
                bg    = AppTheme.BG_INPUT if idx % 2 == 0 else AppTheme.BG_APP
                row   = ctk.CTkFrame(sec_a, fg_color=bg, corner_radius=8)
                row.pack(fill="x", padx=16, pady=2)

                ctk.CTkLabel(row, text=a.get("nome_pdf", "—"),
                             anchor="w", font=_FONT_BODY,
                             text_color=_AZUL,
                             ).pack(side="left", padx=14, pady=10)

                cor_a  = _STATUS_COR.get(a.get("status", ""), _MUTED)
                bg_a   = {_VERDE: _VERDE_BG, _AZUL: _AZUL_BG}.get(cor_a, AppTheme.BG_INPUT)
                a_pill = ctk.CTkFrame(row, fg_color=bg_a, corner_radius=6)
                ctk.CTkLabel(a_pill, text=a.get("status", ""),
                             font=("Segoe UI", 9, "bold"),
                             text_color=cor_a).pack(padx=8, pady=3)
                a_pill.pack(side="right", padx=14, pady=10)

            ctk.CTkLabel(sec_a, text="", height=10).pack()

        # ── Lançamentos (banco novo) ───────────────────────────────────────────
        lancamentos = r.get("lancamentos", [])
        if lancamentos:
            sec_l = ctk.CTkFrame(self._consulta_resultado,
                                 fg_color=AppTheme.BG_CARD, corner_radius=14)
            sec_l.pack(fill="x", padx=8, pady=4)
            _secao_titulo(sec_l, f"Lançamentos ({len(lancamentos)})",
                          _VERDE, _VERDE_BG, "banco novo · PostgreSQL")

            for idx, l in enumerate(lancamentos):
                bg  = AppTheme.BG_INPUT if idx % 2 == 0 else AppTheme.BG_APP
                row = ctk.CTkFrame(sec_l, fg_color=bg, corner_radius=8)
                row.pack(fill="x", padx=16, pady=2)

                ctk.CTkLabel(row, text=l.get("nome_pdf", "—"),
                             anchor="w", font=_FONT_BODY,
                             text_color=AppTheme.TXT_MAIN,
                             ).pack(side="left", padx=14, pady=10)

                info = f"por {l.get('lancado_por','—')}  ·  {l.get('criado_em','')}"
                ctk.CTkLabel(row, text=info,
                             font=_FONT_SMALL, text_color=_MUTED,
                             ).pack(side="right", padx=14, pady=10)

            ctk.CTkLabel(sec_l, text="", height=10).pack()

        # ── Banco de Inscrições/Devoluções (analiseap) ───────────────────────
        ap_regs = r.get("ap_registros", [])
        if ap_regs:
            sec_ap = ctk.CTkFrame(self._consulta_resultado,
                                  fg_color=AppTheme.BG_CARD, corner_radius=14)
            sec_ap.pack(fill="x", padx=8, pady=4)
            _secao_titulo(sec_ap, f"Inscrições / Devoluções ({len(ap_regs)} registro(s))",
                          "#8b5cf6", "#1e1040", "banco analiseap · PostgreSQL")

            _CAMPOS_AP = [
                ("nome",      "Nome"),
                ("municipio", "Município"),
                ("memorando", "Memorando"),
                ("tipo",      "Tipo"),
                ("motivo",    "Motivo"),
                ("usuario",   "Registrado por"),
                ("criado_em", "Data"),
            ]

            for idx, reg in enumerate(ap_regs):
                bg   = AppTheme.BG_INPUT if idx % 2 == 0 else AppTheme.BG_APP
                card = ctk.CTkFrame(sec_ap, fg_color=bg, corner_radius=8)
                card.pack(fill="x", padx=16, pady=3)

                # Cabeçalho da linha: nome + pill de tipo/status
                hdr_row = ctk.CTkFrame(card, fg_color="transparent")
                hdr_row.pack(fill="x", padx=14, pady=(10, 4))

                nome_ap = reg.get("nome") or "—"
                ctk.CTkLabel(hdr_row, text=nome_ap,
                             anchor="w", font=_FONT_TITLE,
                             text_color=AppTheme.TXT_MAIN,
                             ).pack(side="left")

                tipo_ap = str(reg.get("tipo") or reg.get("motivo") or "").strip()
                if tipo_ap:
                    # Detecta se é devolução ou inscrição pelo conteúdo
                    if tipo_ap.startswith("["):
                        pill_txt = "DEVOLUÇÃO"
                        pill_cor = _VERM
                        pill_bg  = _VERM_BG
                    else:
                        pill_txt = tipo_ap
                        pill_cor = _AZUL
                        pill_bg  = _AZUL_BG
                    tp = ctk.CTkFrame(hdr_row, fg_color=pill_bg, corner_radius=6)
                    ctk.CTkLabel(tp, text=pill_txt,
                                 font=("Segoe UI", 9, "bold"),
                                 text_color=pill_cor).pack(padx=8, pady=3)
                    tp.pack(side="right")

                # Chips de detalhes
                det = ctk.CTkFrame(card, fg_color="transparent")
                det.pack(fill="x", padx=14, pady=(0, 10))

                for chave, label in _CAMPOS_AP:
                    if chave in ("nome", "tipo"):
                        continue  # já exibidos acima
                    val = reg.get(chave)
                    if val and str(val).strip() not in ("", "None", "0"):
                        val_str = str(val)
                        # Motivo: truncar se longo
                        if chave == "motivo" and len(val_str) > 50:
                            val_str = val_str[:50] + "…"
                        chip = ctk.CTkFrame(det, fg_color=AppTheme.BG_CARD,
                                            corner_radius=6)
                        ctk.CTkLabel(chip,
                                     text=f"{label}: {val_str}",
                                     font=_FONT_SMALL,
                                     text_color=_MUTED_L).pack(padx=8, pady=3)
                        chip.pack(side="left", padx=(0, 6), pady=2)

            ctk.CTkLabel(sec_ap, text="", height=10).pack()

        # ── Banco CPP (MySQL antigo) ───────────────────────────────────────────
        cpp_regs = r.get("cpp_registros", [])
        if cpp_regs:
            sec_c = ctk.CTkFrame(self._consulta_resultado,
                                 fg_color=AppTheme.BG_CARD, corner_radius=14)
            sec_c.pack(fill="x", padx=8, pady=4)
            _secao_titulo(sec_c, f"Banco CPP ({len(cpp_regs)} registro(s))",
                          _AMBER, _AMBER_BG, "MySQL · somente leitura")

            _CAMPOS_CPP = [
                ("unloc",     "Município"),
                ("memorando", "Memorando"),
                ("datas",     "Data"),
                ("analise",   "Análise"),
                ("motivo",    "Motivo"),
                ("envio",     "Envio"),
                ("lancou",    "Lançou"),
            ]

            for idx, reg in enumerate(cpp_regs):
                bg   = AppTheme.BG_INPUT if idx % 2 == 0 else AppTheme.BG_APP
                card = ctk.CTkFrame(sec_c, fg_color=bg, corner_radius=8)
                card.pack(fill="x", padx=16, pady=3)

                ctk.CTkLabel(card,
                             text=reg.get("nome") or "—",
                             anchor="w", font=_FONT_TITLE,
                             text_color=AppTheme.TXT_MAIN,
                             ).pack(anchor="w", padx=14, pady=(10, 4))

                det = ctk.CTkFrame(card, fg_color="transparent")
                det.pack(fill="x", padx=14, pady=(0, 10))

                for chave, label in _CAMPOS_CPP:
                    val = reg.get(chave)
                    if val and str(val).strip() not in ("", "0", "0000-00-00", "None"):
                        chip = ctk.CTkFrame(det, fg_color=AppTheme.BG_CARD,
                                            corner_radius=6)
                        ctk.CTkLabel(chip,
                                     text=f"{label}: {val}",
                                     font=_FONT_SMALL,
                                     text_color=_MUTED_L).pack(padx=8, pady=3)
                        chip.pack(side="left", padx=(0, 6))

            ctk.CTkLabel(sec_c, text="", height=10).pack()

        elif r.get("cadastrado"):
            # Encontrado no banco novo, ausente no CPP
            aviso = ctk.CTkFrame(self._consulta_resultado,
                                 fg_color=AppTheme.BG_CARD, corner_radius=14)
            aviso.pack(fill="x", padx=8, pady=4)
            ctk.CTkLabel(aviso,
                         text="🗄️  Banco CPP — nenhum registro encontrado para este CPF",
                         font=_FONT_BODY, text_color=_MUTED,
                         ).pack(padx=20, pady=14, anchor="w")