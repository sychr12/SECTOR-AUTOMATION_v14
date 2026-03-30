# -*- coding: utf-8 -*-
"""
ui_layout.py — Construção de widgets e estrutura visual.

Todos os métodos _build_* e _criar_linha.
Não carrega dados nem responde a eventos diretamente.
"""
from tkinter import ttk

import customtkinter as ctk

from app.theme import AppTheme

_VERDE   = "#22c55e"
_VERDE_H = "#16a34a"
_AZUL    = "#3b82f6"
_AZUL_H  = "#2563eb"
_AMBER   = "#f59e0b"
_AMBER_H = "#d97706"
_VERM    = "#ef4444"
_MUTED   = "#64748b"

_STATUS_COR = {
    "RENOVACAO": _VERDE,
    "INSCRICAO": _AZUL,
    "LANCADO":   _MUTED,
}


def stat_card(parent, titulo, valor="0", cor=_AZUL):
    f = ctk.CTkFrame(parent, fg_color=AppTheme.BG_CARD, corner_radius=14)
    ctk.CTkLabel(f, text=titulo,
                 font=("Segoe UI", 10, "bold"),
                 text_color=_MUTED).pack(anchor="w", padx=16, pady=(12, 2))
    lbl = ctk.CTkLabel(f, text=valor,
                       font=("Segoe UI", 26, "bold"),
                       text_color=cor)
    lbl.pack(anchor="w", padx=16, pady=(0, 12))
    return f, lbl


class LancamentoLayout:

    # =========================================================================
    # Raiz
    # =========================================================================
    def _build(self):
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=36, pady=28)

        hdr = ctk.CTkFrame(wrap, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(hdr, text="Lançamento de Processo",
                     font=("Segoe UI", 26, "bold"),
                     text_color=AppTheme.TXT_MAIN).pack(side="left")
        ctk.CTkLabel(hdr, text="Gestão e registro de lançamentos",
                     font=("Segoe UI", 12),
                     text_color=_MUTED).pack(side="right", pady=(6, 0))

        ctk.CTkFrame(wrap, height=1,
                     fg_color=AppTheme.BG_CARD).pack(fill="x", pady=(0, 20))

        stats = ctk.CTkFrame(wrap, fg_color="transparent")
        stats.pack(fill="x", pady=(0, 20))
        for i in range(4):
            stats.grid_columnconfigure(i, weight=1)

        f0, self._lbl_pendentes = stat_card(stats, "Falta Revisar", cor=_VERM)
        f1, self._lbl_prontos   = stat_card(stats, "Prontos",       cor=_VERDE)
        f2, self._lbl_lancados  = stat_card(stats, "Lançados",      cor=_AZUL)
        f3, self._lbl_urgentes  = stat_card(stats, "Urgentes",      cor=_AMBER)
        f0.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        f1.grid(row=0, column=1, sticky="nsew", padx=4)
        f2.grid(row=0, column=2, sticky="nsew", padx=4)
        f3.grid(row=0, column=3, sticky="nsew", padx=(8, 0))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Lanc.TNotebook",
                        background=AppTheme.BG_APP, borderwidth=0)
        style.configure("Lanc.TNotebook.Tab",
                        background=AppTheme.BG_CARD, foreground=_MUTED,
                        font=("Segoe UI", 12), padding=(20, 10))
        style.map("Lanc.TNotebook.Tab",
                  background=[("selected", AppTheme.BG_INPUT)],
                  foreground=[("selected", AppTheme.TXT_MAIN)])

        nb = ttk.Notebook(wrap, style="Lanc.TNotebook")
        nb.pack(fill="both", expand=True)
        self._nb = nb

        aba1 = ctk.CTkFrame(nb, fg_color="transparent")
        nb.add(aba1, text="  🔴 Falta Revisar  ")
        self._build_aba_lista(aba1, modo="revisar")

        aba2 = ctk.CTkFrame(nb, fg_color="transparent")
        nb.add(aba2, text="  ✅ Prontos  ")
        self._build_aba_lista(aba2, modo="prontos")

        aba3 = ctk.CTkFrame(nb, fg_color="transparent")
        nb.add(aba3, text="  🔍 Consulta CPF  ")
        self._build_aba_consulta(aba3)

        aba4 = ctk.CTkFrame(nb, fg_color="transparent")
        nb.add(aba4, text="  📋 Histórico  ")
        self._build_aba_historico(aba4)

        nb.bind("<<NotebookTabChanged>>", lambda _: self._on_tab())

    # =========================================================================
    # Aba Lista — Falta Revisar / Prontos
    # =========================================================================
    def _build_aba_lista(self, parent, modo: str):
        bar = ctk.CTkFrame(parent, fg_color=AppTheme.BG_CARD, corner_radius=14)
        bar.pack(fill="x", pady=(16, 12))

        ctk.CTkButton(bar, text="📁 Selecionar Pasta",
                      height=36, corner_radius=10, width=160,
                      fg_color=AppTheme.BG_INPUT, hover_color=AppTheme.BG_APP,
                      font=("Segoe UI", 12), text_color=AppTheme.TXT_MAIN,
                      command=self._selecionar_pasta
                      ).pack(side="left", padx=(16, 0), pady=14)

        lbl = ctk.CTkLabel(bar, text="Nenhuma pasta selecionada",
                           font=("Segoe UI", 11), text_color=_MUTED)
        lbl.pack(side="left", padx=10, pady=14)
        setattr(self, f"_lbl_pasta_{modo}", lbl)

        ctk.CTkButton(bar, text="↺ Atualizar",
                      height=36, corner_radius=10, width=110,
                      fg_color=_AZUL, hover_color=_AZUL_H,
                      font=("Segoe UI", 12, "bold"), text_color="#fff",
                      command=lambda m=modo: self._carregar_modo(m)
                      ).pack(side="right", padx=16, pady=14)

        if modo == "revisar":
            cpf_bar = ctk.CTkFrame(parent, fg_color=AppTheme.BG_CARD,
                                   corner_radius=14)
            cpf_bar.pack(fill="x", pady=(0, 12))

            ctk.CTkLabel(cpf_bar, text="Registrar por CPF:",
                         font=("Segoe UI", 12, "bold"),
                         text_color=AppTheme.TXT_MAIN
                         ).pack(side="left", padx=(20, 10), pady=14)

            self._cpf_var       = ctk.StringVar()
            self._aplicando_cpf = False
            self._cpf_var.trace_add("write", self._mascara_cpf)

            self._entry_cpf = ctk.CTkEntry(
                cpf_bar, textvariable=self._cpf_var,
                placeholder_text="000.000.000-00",
                height=36, corner_radius=10, width=200,
                fg_color=AppTheme.BG_INPUT, border_color=AppTheme.BG_INPUT,
                font=("Segoe UI", 13), text_color=AppTheme.TXT_MAIN)
            self._entry_cpf.pack(side="left", pady=14)
            self._entry_cpf.bind("<Return>", self._lancar_por_cpf)

            ctk.CTkButton(cpf_bar, text="Registrar Lançamento",
                          height=36, corner_radius=10,
                          fg_color=_VERDE, hover_color=_VERDE_H,
                          font=("Segoe UI", 12, "bold"), text_color="#fff",
                          command=self._lancar_por_cpf
                          ).pack(side="left", padx=(10, 0), pady=14)

            self._lbl_cpf_status = ctk.CTkLabel(
                cpf_bar, text="", font=("Segoe UI", 11), text_color=_MUTED)
            self._lbl_cpf_status.pack(side="left", padx=12, pady=14)

        thead = ctk.CTkFrame(parent, fg_color=AppTheme.BG_INPUT, corner_radius=10)
        thead.pack(fill="x", pady=(0, 4))
        thead.grid_columnconfigure(0, weight=1)

        for col, txt in [(0, "Nome do PDF"), (1, ""), (2, "Status"),
                         (3, "Responsável"), (4, "Lançado por"),
                         (5, "Data"), (6, "Ações")]:
            ctk.CTkLabel(thead, text=txt,
                         font=("Segoe UI", 11, "bold"),
                         text_color=_MUTED, anchor="w"
                         ).grid(row=0, column=col,
                                padx=(16 if col == 0 else 8),
                                pady=10, sticky="w")

        tabela = ctk.CTkScrollableFrame(
            parent, fg_color=AppTheme.BG_CARD, corner_radius=14,
            scrollbar_button_color=AppTheme.BG_INPUT)
        tabela.pack(fill="both", expand=True)
        setattr(self, f"_tabela_{modo}", tabela)

        rodape = ctk.CTkFrame(parent, fg_color="transparent")
        rodape.pack(fill="x", pady=(10, 0))

        if modo == "revisar":
            ctk.CTkButton(rodape, text="Enviar Selecionado para Impressão",
                          height=44, corner_radius=12,
                          fg_color=_AMBER, hover_color=_AMBER_H,
                          font=("Segoe UI", 13, "bold"), text_color="#fff",
                          command=self._enviar_impressao
                          ).pack(side="left")

        ctk.CTkLabel(rodape, text="Duplo clique para abrir o PDF",
                     font=("Segoe UI", 11), text_color=_MUTED
                     ).pack(side="right")

    # =========================================================================
    # Linha da tabela principal
    # =========================================================================
    def _criar_linha(self, reg: dict, tabela, modo: str):
        urgente = reg.get("urgencia", False)
        lancado = bool(reg.get("lancado_por"))

        bg = ("#1c1007" if urgente else AppTheme.BG_CARD) if modo == "revisar" \
             else ("#071c07" if urgente else AppTheme.BG_CARD)

        linha = ctk.CTkFrame(tabela, fg_color=bg, corner_radius=10)
        linha.pack(fill="x", pady=3, padx=6)
        linha.grid_columnconfigure(0, weight=1)

        linha.bind("<Button-1>",
                   lambda _, r=reg, f=linha: self._selecionar_linha(r, f))
        linha.bind("<Double-1>",
                   lambda _, rid=reg["id"]: self._abrir_pdf(rid))

        cor_nome = _AMBER if urgente else (_AZUL if modo == "revisar" else _VERDE)
        lbl = ctk.CTkLabel(linha, text=reg.get("nome_pdf", "—"),
                           anchor="w", cursor="hand2",
                           font=("Segoe UI", 12), text_color=cor_nome)
        lbl.grid(row=0, column=0, padx=(16, 8), pady=12, sticky="ew")
        lbl.bind("<Button-1>",
                 lambda _, r=reg, f=linha: self._selecionar_linha(r, f))
        lbl.bind("<Double-1>",
                 lambda _, rid=reg["id"]: self._abrir_pdf(rid))

        if urgente:
            badge = ctk.CTkFrame(linha, fg_color=_AMBER, corner_radius=6)
            ctk.CTkLabel(badge, text="URGENTE",
                         font=("Segoe UI", 9, "bold"),
                         text_color="#fff", padx=6, pady=2).pack()
            badge.grid(row=0, column=1, padx=4, pady=12)
        else:
            ctk.CTkLabel(linha, text="", width=10).grid(row=0, column=1)

        cor_st = _STATUS_COR.get(reg.get("status", ""), _MUTED)
        ctk.CTkLabel(linha, text=reg.get("status", ""), width=90,
                     font=("Segoe UI", 11, "bold"), text_color=cor_st,
                     ).grid(row=0, column=2, padx=8, pady=12)

        ctk.CTkLabel(linha,
                     text=reg.get("analisado_por", "—") or "—", width=110,
                     font=("Segoe UI", 11), text_color=_MUTED,
                     ).grid(row=0, column=3, padx=8, pady=12)

        lancado_txt = reg.get("lancado_por") or "—"
        ctk.CTkLabel(linha, text=lancado_txt, width=110,
                     font=("Segoe UI", 11, "bold"),
                     text_color=_VERDE if lancado else _MUTED,
                     ).grid(row=0, column=4, padx=8, pady=12)

        criado   = reg.get("criado_em")
        data_txt = (criado.strftime("%d/%m/%Y %H:%M")
                    if criado and hasattr(criado, "strftime")
                    else str(criado or "—"))
        ctk.CTkLabel(linha, text=data_txt, width=110,
                     font=("Segoe UI", 11), text_color=_MUTED,
                     ).grid(row=0, column=5, padx=8, pady=12)

        btns = ctk.CTkFrame(linha, fg_color="transparent")
        btns.grid(row=0, column=6, padx=(8, 16), pady=12)

        ctk.CTkButton(btns, text="Ver", width=44, height=30,
                      corner_radius=8, fg_color=_AZUL, hover_color=_AZUL_H,
                      font=("Segoe UI", 11, "bold"), text_color="#fff",
                      command=lambda rid=reg["id"]: self._abrir_pdf(rid)
                      ).pack(side="left", padx=2)

        if modo == "revisar" and not lancado:
            ctk.CTkButton(btns, text="✓", width=32, height=30,
                          corner_radius=8, fg_color=_VERDE, hover_color=_VERDE_H,
                          font=("Segoe UI", 13), text_color="#fff",
                          command=lambda r=reg: self._lancar_linha(r)
                          ).pack(side="left", padx=2)

    # =========================================================================
    # Aba Consulta CPF
    # =========================================================================
    def _build_aba_consulta(self, parent):
        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(wrap, text="Consulta de CPF",
                     font=("Segoe UI", 20, "bold"),
                     text_color=AppTheme.TXT_MAIN).pack(anchor="w", pady=(0, 16))

        busca_frame = ctk.CTkFrame(wrap, fg_color=AppTheme.BG_CARD,
                                   corner_radius=14)
        busca_frame.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(busca_frame, text="CPF:",
                     font=("Segoe UI", 12, "bold"),
                     text_color=AppTheme.TXT_MAIN
                     ).pack(side="left", padx=(20, 10), pady=16)

        self._consulta_cpf_var       = ctk.StringVar()
        self._aplicando_consulta_cpf = False
        self._consulta_cpf_var.trace_add("write", self._mascara_consulta_cpf)

        self._entry_consulta = ctk.CTkEntry(
            busca_frame,
            textvariable=self._consulta_cpf_var,
            placeholder_text="000.000.000-00",
            height=40, corner_radius=10, width=220,
            fg_color=AppTheme.BG_INPUT, border_color=AppTheme.BG_INPUT,
            font=("Segoe UI", 14), text_color=AppTheme.TXT_MAIN)
        self._entry_consulta.pack(side="left", pady=16)
        self._entry_consulta.bind("<Return>", self._executar_consulta_cpf)

        ctk.CTkButton(busca_frame, text="🔍 Consultar",
                      height=40, corner_radius=10,
                      fg_color=_AZUL, hover_color=_AZUL_H,
                      font=("Segoe UI", 13, "bold"), text_color="#fff",
                      command=self._executar_consulta_cpf
                      ).pack(side="left", padx=(12, 0), pady=16)

        ctk.CTkButton(busca_frame, text="Limpar",
                      height=40, corner_radius=10, width=80,
                      fg_color=AppTheme.BG_INPUT, hover_color=AppTheme.BG_APP,
                      font=("Segoe UI", 11), text_color=_MUTED,
                      command=self._limpar_consulta
                      ).pack(side="left", padx=(8, 0), pady=16)

        self._consulta_resultado = ctk.CTkScrollableFrame(
            wrap, fg_color=AppTheme.BG_CARD, corner_radius=14,
            scrollbar_button_color=AppTheme.BG_INPUT)
        self._consulta_resultado.pack(fill="both", expand=True)

        ctk.CTkLabel(self._consulta_resultado,
                     text="Digite um CPF acima e clique em Consultar.",
                     text_color=_MUTED,
                     font=("Segoe UI", 13)).pack(pady=40)

    # =========================================================================
    # Aba Histórico
    # =========================================================================
    def _build_aba_historico(self, parent):
        bar = ctk.CTkFrame(parent, fg_color=AppTheme.BG_CARD, corner_radius=14)
        bar.pack(fill="x", pady=(16, 12))

        self._hist_busca = ctk.StringVar()
        self._hist_busca.trace_add("write", lambda *_: self._filtrar_historico())

        ctk.CTkLabel(bar, text="Buscar:",
                     font=("Segoe UI", 11, "bold"),
                     text_color=_MUTED, width=55
                     ).pack(side="left", padx=(18, 6), pady=14)

        ctk.CTkEntry(bar, textvariable=self._hist_busca,
                     placeholder_text="Nome do PDF, CPF ou analista...",
                     height=36, corner_radius=10,
                     fg_color=AppTheme.BG_INPUT, border_color=AppTheme.BG_INPUT,
                     font=("Segoe UI", 12), text_color=AppTheme.TXT_MAIN,
                     ).pack(side="left", fill="x", expand=True,
                            padx=(0, 8), pady=10)

        ctk.CTkButton(bar, text="Limpar", width=80, height=36, corner_radius=10,
                      fg_color=AppTheme.BG_INPUT, hover_color=AppTheme.BG_APP,
                      font=("Segoe UI", 11), text_color=_MUTED,
                      command=lambda: self._hist_busca.set("")
                      ).pack(side="right", padx=14, pady=10)

        frame_tb = ctk.CTkFrame(parent, fg_color=AppTheme.BG_CARD, corner_radius=14)
        frame_tb.pack(fill="both", expand=True, pady=(0, 16))

        style = ttk.Style()
        style.configure("HistL.Treeview",
                        background=AppTheme.BG_CARD,
                        fieldbackground=AppTheme.BG_CARD,
                        foreground=AppTheme.TXT_MAIN,
                        rowheight=34, font=("Segoe UI", 11), borderwidth=0)
        style.configure("HistL.Treeview.Heading",
                        background=AppTheme.BG_INPUT, foreground=_MUTED,
                        font=("Segoe UI", 10, "bold"), relief="flat")
        style.map("HistL.Treeview", background=[("selected", "#1e3a5f")])

        cols = ("pdf", "cpf", "analisado", "lancado", "criado")
        self._hist_tree = ttk.Treeview(
            frame_tb, columns=cols, show="headings",
            style="HistL.Treeview", selectmode="browse")

        for col, titulo, w in [
            ("pdf",       "Nome do PDF",   280),
            ("cpf",       "CPF",           130),
            ("analisado", "Analisado por", 140),
            ("lancado",   "Lançado por",   140),
            ("criado",    "Data/Hora",     130),
        ]:
            self._hist_tree.heading(col, text=titulo)
            self._hist_tree.column(col, width=w, minwidth=60,
                                   stretch=(col == "pdf"))

        vsb = ttk.Scrollbar(frame_tb, orient="vertical",
                            command=self._hist_tree.yview)
        self._hist_tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y", pady=8)
        self._hist_tree.pack(fill="both", expand=True, padx=8, pady=8)

        self._hist_tree.tag_configure("par",   background=AppTheme.BG_CARD)
        self._hist_tree.tag_configure("impar", background=AppTheme.BG_INPUT)
        self._hist_dados: list = []

    # =========================================================================
    # Exibir resultado da consulta CPF
    # =========================================================================
    def _exibir_consulta(self, r: dict, cpf_txt: str):
        for w in self._consulta_resultado.winfo_children():
            w.destroy()

        cadastrado = r.get("cadastrado", False)

        # ── Banner de status ──────────────────────────────────────────────────
        status_frame = ctk.CTkFrame(
            self._consulta_resultado,
            fg_color=("#0f2e0f" if cadastrado else "#2e0f0f"),
            corner_radius=14)
        status_frame.pack(fill="x", padx=10, pady=(10, 6))
        icone = "✅" if cadastrado else "❌"
        cor   = _VERDE if cadastrado else _VERM
        ctk.CTkLabel(status_frame,
                     text=f"{icone}  {r.get('mensagem', '')}",
                     font=("Segoe UI", 13, "bold"),
                     text_color=cor, anchor="w").pack(padx=20, pady=16, anchor="w")

        if not cadastrado:
            return

        # ── Responsável ───────────────────────────────────────────────────────
        if r.get("responsavel"):
            resp_frame = ctk.CTkFrame(self._consulta_resultado,
                                      fg_color=AppTheme.BG_CARD, corner_radius=14)
            resp_frame.pack(fill="x", padx=10, pady=6)
            ctk.CTkLabel(resp_frame, text="👤  Responsável (analisou o processo)",
                         font=("Segoe UI", 11, "bold"),
                         text_color=_MUTED).pack(anchor="w", padx=20, pady=(14, 4))
            ctk.CTkLabel(resp_frame, text=r["responsavel"],
                         font=("Segoe UI", 16, "bold"),
                         text_color=_AZUL).pack(anchor="w", padx=20, pady=(0, 14))

        # ── Status atual ──────────────────────────────────────────────────────
        if r.get("status"):
            cor_s    = _STATUS_COR.get(r["status"], _MUTED)
            st_frame = ctk.CTkFrame(self._consulta_resultado,
                                    fg_color=AppTheme.BG_CARD, corner_radius=14)
            st_frame.pack(fill="x", padx=10, pady=6)
            ctk.CTkLabel(st_frame, text="📋  Status atual do processo",
                         font=("Segoe UI", 11, "bold"),
                         text_color=_MUTED).pack(anchor="w", padx=20, pady=(14, 4))
            ctk.CTkLabel(st_frame, text=r["status"],
                         font=("Segoe UI", 16, "bold"),
                         text_color=cor_s).pack(anchor="w", padx=20, pady=(0, 14))

        # ── Análises (banco novo) ─────────────────────────────────────────────
        analises = r.get("analises", [])
        if analises:
            sec = ctk.CTkFrame(self._consulta_resultado,
                               fg_color=AppTheme.BG_CARD, corner_radius=14)
            sec.pack(fill="x", padx=10, pady=6)
            ctk.CTkLabel(sec, text=f"📁  Análises — banco novo ({len(analises)})",
                         font=("Segoe UI", 12, "bold"),
                         text_color=AppTheme.TXT_MAIN
                         ).pack(anchor="w", padx=20, pady=(14, 6))
            for idx, a in enumerate(analises):
                bg    = AppTheme.BG_INPUT if idx % 2 == 0 else AppTheme.BG_APP
                row   = ctk.CTkFrame(sec, fg_color=bg, corner_radius=8)
                row.pack(fill="x", padx=12, pady=2)
                cor_a = _STATUS_COR.get(a.get("status", ""), _MUTED)
                ctk.CTkLabel(row, text=a.get("nome_pdf", "—"),
                             anchor="w", font=("Segoe UI", 11),
                             text_color=_AZUL).pack(side="left", padx=12, pady=8)
                ctk.CTkLabel(row, text=a.get("status", ""),
                             font=("Segoe UI", 10, "bold"),
                             text_color=cor_a).pack(side="right", padx=12, pady=8)
            ctk.CTkLabel(sec, text="", height=8).pack()

        # ── Lançamentos (banco novo) ───────────────────────────────────────────
        lancamentos = r.get("lancamentos", [])
        if lancamentos:
            sec2 = ctk.CTkFrame(self._consulta_resultado,
                                fg_color=AppTheme.BG_CARD, corner_radius=14)
            sec2.pack(fill="x", padx=10, pady=6)
            ctk.CTkLabel(sec2,
                         text=f"🚀  Lançamentos — banco novo ({len(lancamentos)})",
                         font=("Segoe UI", 12, "bold"),
                         text_color=AppTheme.TXT_MAIN
                         ).pack(anchor="w", padx=20, pady=(14, 6))
            for idx, l in enumerate(lancamentos):
                bg  = AppTheme.BG_INPUT if idx % 2 == 0 else AppTheme.BG_APP
                row = ctk.CTkFrame(sec2, fg_color=bg, corner_radius=8)
                row.pack(fill="x", padx=12, pady=2)
                ctk.CTkLabel(row, text=l.get("nome_pdf", "—"),
                             anchor="w", font=("Segoe UI", 11),
                             text_color=AppTheme.TXT_MAIN
                             ).pack(side="left", padx=12, pady=8)
                ctk.CTkLabel(row,
                             text=f"Lançado por: {l.get('lancado_por','—')}  |  {l.get('criado_em','')}",
                             font=("Segoe UI", 10),
                             text_color=_MUTED).pack(side="right", padx=12, pady=8)
            ctk.CTkLabel(sec2, text="", height=8).pack()

        # ── Banco CPP (MySQL antigo) ───────────────────────────────────────────
        cpp_regs = r.get("cpp_registros", [])
        if cpp_regs:
            sec3 = ctk.CTkFrame(self._consulta_resultado,
                                fg_color=AppTheme.BG_CARD, corner_radius=14)
            sec3.pack(fill="x", padx=10, pady=6)

            hdr3 = ctk.CTkFrame(sec3, fg_color="transparent")
            hdr3.pack(fill="x", padx=20, pady=(14, 6))
            ctk.CTkLabel(hdr3,
                         text=f"🗄️  Banco CPP — registros encontrados ({len(cpp_regs)})",
                         font=("Segoe UI", 12, "bold"),
                         text_color=AppTheme.TXT_MAIN).pack(side="left")
            ctk.CTkLabel(hdr3, text="MySQL · somente leitura",
                         font=("Segoe UI", 10),
                         text_color=_MUTED).pack(side="left", padx=(10, 0))

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
                card = ctk.CTkFrame(sec3, fg_color=bg, corner_radius=8)
                card.pack(fill="x", padx=12, pady=3)

                ctk.CTkLabel(card, text=reg.get("nome") or "—",
                             anchor="w", font=("Segoe UI", 11, "bold"),
                             text_color=AppTheme.TXT_MAIN
                             ).pack(anchor="w", padx=12, pady=(8, 2))

                det = ctk.CTkFrame(card, fg_color="transparent")
                det.pack(fill="x", padx=12, pady=(0, 8))
                for chave, label in _CAMPOS_CPP:
                    val = reg.get(chave)
                    if val and str(val).strip() not in ("", "0", "0000-00-00", "None"):
                        ctk.CTkLabel(det,
                                     text=f"{label}: {val}",
                                     font=("Segoe UI", 10),
                                     text_color=_MUTED
                                     ).pack(side="left", padx=(0, 16))

            ctk.CTkLabel(sec3, text="", height=8).pack()

        elif r.get("cadastrado"):
            # Encontrado no banco novo mas não no CPP
            info_cpp = ctk.CTkFrame(self._consulta_resultado,
                                    fg_color=AppTheme.BG_CARD, corner_radius=14)
            info_cpp.pack(fill="x", padx=10, pady=6)
            ctk.CTkLabel(info_cpp,
                         text="🗄️  Banco CPP — nenhum registro encontrado para este CPF",
                         font=("Segoe UI", 11),
                         text_color=_MUTED).pack(padx=20, pady=14, anchor="w")