# -*- coding: utf-8 -*-
"""Tabelas/listas do módulo Anexar."""
from datetime import datetime
from tkinter import ttk

import customtkinter as ctk

from .theme import (
    VERDE, VERDE_H, VERDE_T, AMBER_B, AMBER_T,
    VERM, AMBER, INFO, MUTED, SLATE,
    fmt_data, fmt_data_curta,
)

# Constantes de layout (equivalentes ao AppTheme global)
class AppTheme:
    BG_APP   = "#f8fafc"
    BG_CARD  = "#f1f5f9"
    BG_INPUT = "#ffffff"
    TXT_MAIN = "#0f172a"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _thead(parent, colunas: list):
    thead = ctk.CTkFrame(parent, fg_color=AppTheme.BG_CARD,
                         corner_radius=12, height=42)
    thead.pack(fill="x", pady=(0, 8))
    for i, (txt, w) in enumerate(colunas):
        ctk.CTkLabel(thead, text=txt, width=w, anchor="w",
                     font=("Segoe UI", 11, "bold"),
                     text_color=MUTED,
                     ).pack(side="left", padx=(16 if i == 0 else 8, 0), pady=12)


def _scroll(parent):
    return ctk.CTkScrollableFrame(
        parent, fg_color="transparent", corner_radius=12,
        scrollbar_button_color=AppTheme.BG_CARD,
        scrollbar_button_hover_color=SLATE,
    )


def _style_tree(name):
    s = ttk.Style()
    s.configure(f"{name}.Treeview",
                background=AppTheme.BG_INPUT,
                fieldbackground=AppTheme.BG_INPUT,
                foreground=AppTheme.TXT_MAIN,
                rowheight=36, font=("Segoe UI", 10), borderwidth=0)
    s.configure(f"{name}.Treeview.Heading",
                background=AppTheme.BG_CARD, foreground=MUTED,
                font=("Segoe UI", 10, "bold"), relief="flat")
    s.map(f"{name}.Treeview",
          background=[("selected", "#1e3a5f")])


def _tree_frame(parent):
    frame = ctk.CTkFrame(parent, fg_color=AppTheme.BG_INPUT,
                         corner_radius=12, border_width=1,
                         border_color=AppTheme.BG_CARD)
    frame.pack(fill="both", expand=True)
    return frame


def _section_header(parent, texto: str):
    ctk.CTkLabel(parent, text=texto,
                 font=("Segoe UI", 13, "bold"),
                 text_color=AppTheme.TXT_MAIN).pack(side="left")


# ── Tabela Carteiras ──────────────────────────────────────────────────────────

class CarteirasTable:
    _COLS = [
        ("ID", 50), ("Nome", 210), ("CPF", 130), ("UNLOC", 90),
        ("Registro", 120), ("Validade", 95), ("Atividade", 170),
        ("Criado em", 140), ("PDF", 55), ("Status", 125),
    ]

    @classmethod
    def criar(cls, parent, on_baixar):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        _thead(container, cls._COLS)
        lista = _scroll(container)
        lista.pack(fill="both", expand=True)
        return lista, container

    @staticmethod
    def carregar(lista, registros: list, on_baixar=None):
        for w in lista.winfo_children():
            w.destroy()

        for i, r in enumerate(registros):
            tem_pdf = r.get("pdf_gerado", False)
            bg = AppTheme.BG_APP if i % 2 == 0 else AppTheme.BG_INPUT

            row = ctk.CTkFrame(lista, fg_color=bg, corner_radius=8)
            row.pack(fill="x", pady=2, padx=4)

            row.bind("<Enter>", lambda e, f=row: f.configure(fg_color=AppTheme.BG_CARD))
            row.bind("<Leave>", lambda e, f=row, c=bg: f.configure(fg_color=c))

            def _lbl(text, width, main=False, first=False):
                ctk.CTkLabel(row, text=str(text) if text else "—",
                             width=width, anchor="w",
                             font=("Segoe UI", 11 if main else 10),
                             text_color=AppTheme.TXT_MAIN if main else MUTED,
                             ).pack(side="left", padx=(16 if first else 8, 0), pady=8)

            _lbl(r.get("id"),                         50, first=True)
            _lbl(r.get("nome"),                      210, main=True)
            _lbl(r.get("cpf"),                       130)
            _lbl(r.get("unloc"),                      90)
            _lbl(r.get("registro"),                  120)
            _lbl(fmt_data_curta(r.get("validade")),   95)
            _lbl(r.get("atividade1"),                170)
            _lbl(fmt_data(r.get("criado_em")),       140)

            ctk.CTkLabel(row, text="✓" if tem_pdf else "✗",
                         width=55, anchor="center",
                         font=("Segoe UI", 12, "bold"),
                         text_color=VERDE if tem_pdf else MUTED,
                         ).pack(side="left", padx=(8, 0))

            if tem_pdf:
                ctk.CTkButton(
                    row, text="📄 Baixar", width=110, height=30,
                    corner_radius=8, fg_color=VERDE, hover_color=VERDE_H,
                    text_color=VERDE_T, font=("Segoe UI", 10, "bold"),
                    command=lambda rid=r.get("id"): on_baixar(rid) if on_baixar else None,
                ).pack(side="left", padx=(8, 12), pady=5)
            else:
                ctk.CTkLabel(
                    row, text="⏳ Pendente", width=110, height=30,
                    corner_radius=8, fg_color=AMBER_B, text_color=AMBER_T,
                    font=("Segoe UI", 10, "bold"),
                ).pack(side="left", padx=(8, 12), pady=5)

    @staticmethod
    def limpar(lista):
        for w in lista.winfo_children():
            w.destroy()


# ── Tabela Em Análise ─────────────────────────────────────────────────────────

class EmAnaliseTable:
    _COLS = [
        ("id",        "ID",         50), ("nome_pdf",  "Processo",  220),
        ("cpf",       "CPF",       130), ("unloc",     "UNLOC",      85),
        ("memorando", "Memorando", 120), ("tipo",      "Tipo",       85),
        ("urgencia",  "Urgente",    80), ("usuario",   "Usuário",   120),
        ("criado_em", "Entrada",   140),
    ]

    @classmethod
    def criar(cls, parent):
        _style_tree("Anal")
        container = ctk.CTkFrame(parent, fg_color="transparent")

        hdr = ctk.CTkFrame(container, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 12))
        _section_header(hdr, "📋 Processos em Análise")

        frame = _tree_frame(container)
        cols  = tuple(c[0] for c in cls._COLS)
        tree  = ttk.Treeview(frame, columns=cols, show="headings",
                             style="Anal.Treeview", selectmode="browse")

        for key, titulo, w in cls._COLS:
            tree.heading(key, text=titulo)
            tree.column(key, width=w, minwidth=40, stretch=(key == "nome_pdf"))

        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True, padx=4, pady=4)

        tree.tag_configure("urgente", background="#4a0e0e", foreground="#fecaca")
        tree.tag_configure("normal",  foreground=AppTheme.TXT_MAIN)

        return tree, container

    @classmethod
    def carregar(cls, tree, registros: list):
        cls.limpar(tree)
        for r in registros:
            urgente = r.get("urgencia", False)
            tree.insert("", "end",
                        tags=("urgente" if urgente else "normal",),
                        values=(
                            r.get("id",        ""),
                            r.get("nome_pdf",  ""),
                            r.get("cpf",       ""),
                            r.get("unloc",     ""),
                            r.get("memorando", ""),
                            r.get("tipo",      ""),
                            "⚡ Sim" if urgente else "—",
                            r.get("usuario",   "—"),
                            fmt_data(r.get("criado_em")),
                        ))

    @staticmethod
    def limpar(tree):
        for item in tree.get_children():
            tree.delete(item)


# ── Tabela Histórico ──────────────────────────────────────────────────────────

class HistoricoTable:
    _COLS = [
        ("id",       "ID",           50), ("nome",     "Nome",       220),
        ("cpf",      "CPF",         130), ("unloc",    "UNLOC",       90),
        ("registro", "Registro",    120), ("validade", "Validade",    95),
        ("usuario",  "Anexado por", 130), ("criado_em","Data",       150),
    ]

    @classmethod
    def criar(cls, parent):
        _style_tree("Hist")
        container = ctk.CTkFrame(parent, fg_color="transparent")

        hdr = ctk.CTkFrame(container, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 12))
        _section_header(hdr, "📜 Histórico de Anexações")

        frame = _tree_frame(container)
        cols  = tuple(c[0] for c in cls._COLS)
        tree  = ttk.Treeview(frame, columns=cols, show="headings",
                             style="Hist.Treeview", selectmode="browse")

        for key, titulo, w in cls._COLS:
            tree.heading(key, text=titulo)
            tree.column(key, width=w, minwidth=40, stretch=(key == "nome"))

        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True, padx=4, pady=4)

        tree.tag_configure("par",   background=AppTheme.BG_INPUT)
        tree.tag_configure("impar", background=AppTheme.BG_CARD)

        return tree, container

    @classmethod
    def carregar(cls, tree, registros: list):
        cls.limpar(tree)
        for i, r in enumerate(registros):
            tree.insert("", "end",
                        tags=("par" if i % 2 == 0 else "impar",),
                        values=(
                            r.get("id",       ""),
                            r.get("nome",     ""),
                            r.get("cpf",      ""),
                            r.get("unloc",    ""),
                            r.get("registro", ""),
                            fmt_data_curta(r.get("validade")),
                            r.get("usuario",  "—"),
                            fmt_data(r.get("criado_em")),
                        ))

    @staticmethod
    def limpar(tree):
        for item in tree.get_children():
            tree.delete(item)


# ── Tabela Log ────────────────────────────────────────────────────────────────

class LogTable:
    _TAGS  = {
        "sucesso": (VERDE, "#0a2f1a"),
        "erro":    (VERM,  "#3f0a0a"),
        "aviso":   (AMBER, "#2d2a0a"),
        "info":    (INFO,  "#0a2a3f"),
    }
    _ICONS = {"sucesso": "✓", "erro": "✗", "aviso": "⚠", "info": "ℹ"}

    @classmethod
    def criar(cls, parent):
        _style_tree("Log2")
        container = ctk.CTkFrame(parent, fg_color="transparent")

        hdr = ctk.CTkFrame(container, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 12))
        _section_header(hdr, "📋 Log de Processamento")

        frame = _tree_frame(container)
        tree  = ttk.Treeview(frame, columns=("status", "mensagem"),
                             show="headings", style="Log2.Treeview")
        tree.heading("status",   text="Status")
        tree.heading("mensagem", text="Mensagem")
        tree.column("status",   width=140, minwidth=100)
        tree.column("mensagem", width=580, stretch=True)

        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True, padx=4, pady=4)

        for tag, (bg, fg) in cls._TAGS.items():
            tree.tag_configure(tag, background=bg, foreground=fg)

        return tree, container

    @staticmethod
    def add(tree, status, mensagem, tag="info"):
        ts   = datetime.now().strftime("%H:%M:%S")
        icon = LogTable._ICONS.get(tag.lower(), "•")
        tree.insert("", "end",
                    values=(status, f"[{ts}] {icon} {mensagem}"),
                    tags=(tag.lower(),))
        kids = tree.get_children()
        if kids:
            tree.see(kids[-1])

    @staticmethod
    def limpar(tree):
        for item in tree.get_children():
            tree.delete(item)