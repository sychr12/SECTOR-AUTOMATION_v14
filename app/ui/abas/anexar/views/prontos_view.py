# -*- coding: utf-8 -*-
"""
Aba "Prontos & Histórico" — mostra quem anexou cada carteira e resumo por usuário.
"""
import threading
from tkinter import ttk

import customtkinter as ctk

from .theme import (
    VERDE, VERDE_H, VERDE_T, AZUL, AZUL_H,
    VERM, AMBER, MUTED, INFO,
    fmt_data, fmt_data_curta,
)

# Cores padrão
BG_APP = "#f8fafc"
BG_CARD = "#f1f5f9"
BG_INPUT = "#ffffff"
TXT_MAIN = "#0f172a"


def _style_tree(name: str):
    s = ttk.Style()
    s.configure(f"{name}.Treeview",
                background=BG_INPUT,
                fieldbackground=BG_INPUT,
                foreground=TXT_MAIN,
                rowheight=34, font=("Segoe UI", 10), borderwidth=0)
    s.configure(f"{name}.Treeview.Heading",
                background=BG_CARD, foreground=MUTED,
                font=("Segoe UI", 10, "bold"), relief="flat")
    s.map(f"{name}.Treeview",
          background=[("selected", "#1e3a5f")])


def _scrolled_tree(parent, style_name: str, columns: list) -> ttk.Treeview:
    """Cria um Treeview com scrollbar vertical dentro de parent."""
    _style_tree(style_name)
    wrap = ctk.CTkFrame(parent, fg_color=BG_INPUT,
                        corner_radius=12, border_width=1,
                        border_color=BG_CARD)
    wrap.pack(fill="both", expand=True)

    tree = ttk.Treeview(wrap,
                        columns=tuple(c[0] for c in columns),
                        show="headings",
                        style=f"{style_name}.Treeview",
                        selectmode="browse")

    for key, titulo, w, stretch in columns:
        tree.heading(key, text=titulo)
        tree.column(key, width=w, minwidth=40, stretch=stretch)

    vsb = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    tree.pack(fill="both", expand=True, padx=4, pady=4)

    tree.tag_configure("par",   background=BG_INPUT)
    tree.tag_configure("impar", background=BG_CARD)

    return tree


def _label_secao(parent, texto: str, pady=(0, 12)):
    ctk.CTkLabel(parent, text=texto,
                 font=("Segoe UI", 13, "bold"),
                 text_color=TXT_MAIN).pack(anchor="w", pady=pady)


def _filtro_entry(parent, label: str, var: ctk.StringVar, width=140) -> ctk.CTkEntry:
    ctk.CTkLabel(parent, text=label,
                 font=("Segoe UI", 10), text_color=MUTED).pack(side="left")
    e = ctk.CTkEntry(parent, textvariable=var,
                     width=width, height=32, corner_radius=8,
                     fg_color=BG_INPUT,
                     border_color=BG_CARD, border_width=1,
                     font=("Segoe UI", 11))
    e.pack(side="left", padx=(4, 16))
    return e


class ProntosView(ctk.CTkFrame):
    """
    Aba com duas seções:
      • Ranking — quem anexou mais e quando foi a última anexação
      • Detalhes — todas as carteiras prontas, filtráveis por usuário/CPF/nome
    """

    def __init__(self, parent, repository):
        super().__init__(parent, fg_color="transparent")
        self.repository = repository

        self._var_usuario = ctk.StringVar()
        self._var_cpf     = ctk.StringVar()
        self._var_nome    = ctk.StringVar()

        # Rastreia e dispara pesquisa ao digitar
        for v in (self._var_usuario, self._var_cpf, self._var_nome):
            v.trace_add("write", lambda *_: self.after(300, self._carregar_detalhes))

        self._build()

    # ── Layout ───────────────────────────────────────────────────────────────

    def _build(self):
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=4, pady=4)

        # divide em coluna esquerda (ranking) e direita (detalhes)
        wrap.columnconfigure(0, weight=1)
        wrap.columnconfigure(1, weight=3)
        wrap.rowconfigure(0, weight=1)

        self._build_ranking(wrap)
        self._build_detalhes(wrap)

    def _build_ranking(self, parent):
        card = ctk.CTkFrame(parent, fg_color=BG_CARD,
                            corner_radius=14, border_width=1,
                            border_color=BG_INPUT)
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=4)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=16, pady=16)

        _label_secao(inner, "🏆 Ranking de Anexações")

        cols = [
            ("pos",      "#",          30, False),
            ("usuario",  "Usuário",   160, True),
            ("total",    "Total",      60, False),
            ("ultima",   "Última em", 130, False),
        ]
        self._tree_rank = _scrolled_tree(inner, "Rank", cols)
        self._tree_rank.tag_configure("ouro",   foreground="#f59e0b", font=("Segoe UI", 10, "bold"))
        self._tree_rank.tag_configure("prata",  foreground="#94a3b8", font=("Segoe UI", 10, "bold"))
        self._tree_rank.tag_configure("bronze", foreground="#b45309")

        # Botão recarregar
        ctk.CTkButton(inner, text="↻  Atualizar",
                      height=32, corner_radius=8,
                      fg_color=BG_INPUT,
                      hover_color=BG_CARD,
                      text_color=TXT_MAIN,
                      font=("Segoe UI", 11),
                      command=self.recarregar).pack(fill="x", pady=(12, 0))

    def _build_detalhes(self, parent):
        card = ctk.CTkFrame(parent, fg_color=BG_CARD,
                            corner_radius=14, border_width=1,
                            border_color=BG_INPUT)
        card.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=4)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=16, pady=16)

        _label_secao(inner, "📋 Carteiras Anexadas")

        # Filtros em linha
        filtros = ctk.CTkFrame(inner, fg_color="transparent")
        filtros.pack(fill="x", pady=(0, 12))

        _filtro_entry(filtros, "Usuário:",  self._var_usuario, width=140)
        _filtro_entry(filtros, "CPF:",      self._var_cpf,     width=130)
        _filtro_entry(filtros, "Nome:",     self._var_nome,    width=160)

        ctk.CTkButton(filtros, text="✕ Limpar", width=80, height=32,
                      corner_radius=8,
                      fg_color=BG_INPUT,
                      hover_color=BG_CARD,
                      text_color=MUTED,
                      font=("Segoe UI", 10),
                      command=self._limpar_filtros).pack(side="left")

        # Contador
        self._lbl_count = ctk.CTkLabel(
            filtros, text="",
            font=("Segoe UI", 10), text_color=MUTED)
        self._lbl_count.pack(side="right")

        # Tabela principal
        cols = [
            ("id",          "ID",           50,  False),
            ("nome",        "Nome",        200,  True),
            ("cpf",         "CPF",         120,  False),
            ("unloc",       "UNLOC",        80,  False),
            ("registro",    "Registro",    110,  False),
            ("validade",    "Validade",     88,  False),
            ("anexado_por", "Anexado por", 130,  False),
            ("anexado_em",  "Anexado em",  140,  False),
            ("cadastrado",  "Cadastrado",  130,  False),
        ]
        self._tree_det = _scrolled_tree(inner, "Pron", cols)

        # Clique duplo → destaque do usuário no ranking
        self._tree_det.bind("<Double-1>", self._on_double_click)

    # ── Carregar dados ────────────────────────────────────────────────────────

    def recarregar(self):
        """Recarrega ranking e detalhes (chame de fora após cada anexação)."""
        self._carregar_ranking()
        self._carregar_detalhes()

    def _carregar_ranking(self):
        def _worker():
            try:
                rows = self.repository.resumo_por_usuario()
                self.after(0, self._preencher_ranking, rows)
            except Exception as exc:
                print(f"[ProntosView] ERRO ranking: {exc}")

        threading.Thread(target=_worker, daemon=True).start()

    def _carregar_detalhes(self):
        usuario = self._var_usuario.get()
        cpf     = self._var_cpf.get()
        nome    = self._var_nome.get()

        def _worker():
            try:
                rows = self.repository.buscar_prontos_filtrado(
                    usuario=usuario, cpf=cpf, nome=nome)
                self.after(0, self._preencher_detalhes, rows)
            except Exception as exc:
                print(f"[ProntosView] ERRO detalhes: {exc}")

        threading.Thread(target=_worker, daemon=True).start()

    # ── Preencher tabelas ─────────────────────────────────────────────────────

    def _preencher_ranking(self, rows: list):
        for item in self._tree_rank.get_children():
            self._tree_rank.delete(item)

        medalhas = {1: "ouro", 2: "prata", 3: "bronze"}

        for i, r in enumerate(rows, 1):
            ultima = r.get("ultima_em")
            ultima_str = fmt_data(ultima) if ultima else "—"
            pos_txt = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, str(i))
            tag = medalhas.get(i, "par" if i % 2 == 0 else "impar")

            self._tree_rank.insert("", "end", tags=(tag,),
                                   values=(
                                       pos_txt,
                                       r.get("usuario", "—"),
                                       r.get("total",    0),
                                       ultima_str,
                                   ))

    def _preencher_detalhes(self, rows: list):
        for item in self._tree_det.get_children():
            self._tree_det.delete(item)

        self._lbl_count.configure(
            text=f"{len(rows)} registro(s)",
            text_color=VERDE if rows else MUTED,
        )

        for i, r in enumerate(rows):
            tag = "par" if i % 2 == 0 else "impar"
            self._tree_det.insert("", "end", tags=(tag,),
                                  values=(
                                      r.get("id",          ""),
                                      r.get("nome",        "—"),
                                      r.get("cpf",         "—"),
                                      r.get("unloc",       "—"),
                                      r.get("registro",    "—"),
                                      fmt_data_curta(r.get("validade")),
                                      r.get("anexado_por", "—"),
                                      fmt_data(r.get("anexado_em")),
                                      fmt_data(r.get("criado_em")),
                                  ))

    # ── Interações ────────────────────────────────────────────────────────────

    def _on_double_click(self, _event):
        """Ao dar duplo clique em uma linha, filtra o ranking pelo usuário."""
        sel = self._tree_det.selection()
        if not sel:
            return
        vals = self._tree_det.item(sel[0], "values")
        if vals and len(vals) > 6:
            usuario = vals[6]  # coluna "Anexado por"
            if usuario and usuario != "—":
                self._var_usuario.set(usuario)

    def _limpar_filtros(self):
        self._var_usuario.set("")
        self._var_cpf.set("")
        self._var_nome.set("")