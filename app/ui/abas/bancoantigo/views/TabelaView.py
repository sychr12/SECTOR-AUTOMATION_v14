# -*- coding: utf-8 -*-
"""
TabelaView — tabela principal de registros + rodapé de paginação.
"""

from datetime import datetime
from tkinter import ttk

import customtkinter as ctk
from app.theme import AppTheme

_VERDE  = "#22c55e"
_AZUL   = "#3b82f6"
_VERM   = "#ef4444"
_MUTED  = "#64748b"

COLUNAS = [
    ("id",        "ID",         55),
    ("nome",      "Nome",       260),
    ("cpf",       "CPF",        120),
    ("unloc",     "Município",  150),
    ("memorando", "Memorando",  100),
    ("datas",     "Data",        90),
    ("analise",   "Análise",     80),
    ("motivo",    "Motivo",     200),
    ("envio",     "Envio",       90),
    ("lancou",    "Lançou",     110),
]


class TabelaView(ctk.CTkFrame):
    """
    Treeview estilizada com scroll vertical/horizontal e rodapé de paginação.
    Emite callbacks para ordenação por coluna e duplo clique.
    """

    def __init__(self, master,
                 on_ordenar,
                 on_duplo_clique,
                 on_primeira, on_anterior,
                 on_proxima,  on_ultima,
                 **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self._on_ordenar       = on_ordenar
        self._on_duplo_clique  = on_duplo_clique
        self._on_primeira      = on_primeira
        self._on_anterior      = on_anterior
        self._on_proxima       = on_proxima
        self._on_ultima        = on_ultima

        self._build_tabela()
        self._build_rodape()

    # ── Tabela ────────────────────────────────────────────────────────────────
    def _build_tabela(self):
        frame_tb = ctk.CTkFrame(self, fg_color=AppTheme.BG_CARD,
                                corner_radius=14)
        frame_tb.pack(fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("CPP.Treeview",
                        background=AppTheme.BG_CARD,
                        fieldbackground=AppTheme.BG_CARD,
                        foreground=AppTheme.TXT_MAIN,
                        rowheight=32,
                        font=("Segoe UI", 11),
                        borderwidth=0)
        style.configure("CPP.Treeview.Heading",
                        background=AppTheme.BG_INPUT,
                        foreground=_MUTED,
                        font=("Segoe UI", 10, "bold"),
                        relief="flat")
        style.map("CPP.Treeview",
                  background=[("selected", "#1e3a5f")])

        cols = [c[0] for c in COLUNAS]
        self._tree = ttk.Treeview(
            frame_tb, columns=cols,
            show="headings",
            style="CPP.Treeview",
            selectmode="browse",
        )

        for col_id, titulo, largura in COLUNAS:
            self._tree.heading(
                col_id, text=titulo,
                command=lambda c=col_id: self._on_ordenar(c),
            )
            self._tree.column(col_id, width=largura, minwidth=40,
                              stretch=(col_id in ("nome", "motivo")))

        vsb = ttk.Scrollbar(frame_tb, orient="vertical",
                            command=self._tree.yview)
        hsb = ttk.Scrollbar(frame_tb, orient="horizontal",
                            command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set,
                             xscrollcommand=hsb.set)

        vsb.pack(side="right", fill="y", pady=8)
        hsb.pack(side="bottom", fill="x", padx=8)
        self._tree.pack(fill="both", expand=True, padx=8, pady=(8, 0))

        # Tags de cor
        self._tree.tag_configure("INSC",  foreground=_AZUL)
        self._tree.tag_configure("RENOV", foreground=_VERDE)
        self._tree.tag_configure("DEV",   foreground=_VERM)
        self._tree.tag_configure("par",   background=AppTheme.BG_CARD)
        self._tree.tag_configure("impar", background=AppTheme.BG_INPUT)

        self._tree.bind("<Double-1>", self._duplo_clique)

    # ── Rodapé paginação ──────────────────────────────────────────────────────
    def _build_rodape(self):
        rodape = ctk.CTkFrame(self, fg_color="transparent")
        rodape.pack(fill="x", pady=(10, 0))

        self._lbl_status = ctk.CTkLabel(rodape, text="",
                                        font=("Segoe UI", 11),
                                        text_color=_MUTED)
        self._lbl_status.pack(side="left")

        pag = ctk.CTkFrame(rodape, fg_color="transparent")
        pag.pack(side="right")

        def _btn(txt, cmd):
            return ctk.CTkButton(pag, text=txt, width=40, height=32,
                                 corner_radius=8,
                                 fg_color=AppTheme.BG_INPUT,
                                 hover_color=AppTheme.BG_CARD,
                                 font=("Segoe UI", 12),
                                 text_color=AppTheme.TXT_MAIN,
                                 command=cmd)

        _btn("◀◀", self._on_primeira).pack(side="left", padx=2)
        _btn("◀",  self._on_anterior).pack(side="left", padx=2)

        self._lbl_pagina = ctk.CTkLabel(pag, text="1 / 1", width=80,
                                        font=("Segoe UI", 12, "bold"),
                                        text_color=AppTheme.TXT_MAIN)
        self._lbl_pagina.pack(side="left", padx=8)

        _btn("▶",  self._on_proxima).pack(side="left", padx=2)
        _btn("▶▶", self._on_ultima).pack(side="left", padx=2)

    # ── API pública ───────────────────────────────────────────────────────────
    def renderizar(self, info: dict):
        """
        Recebe o dict retornado pelo controller e atualiza a tabela.
        info = {pagina, pagina_atual, total_paginas,
                total_filtrado, inicio, fim}
        """
        for item in self._tree.get_children():
            self._tree.delete(item)

        for i, r in enumerate(info["pagina"]):
            datas = self._fmt_data(r.get("datas"))
            envio = self._fmt_data(r.get("envio"), zero_vazio=True)
            analise = str(r.get("analise") or "").upper()

            tag_cor   = analise if analise in ("INSC", "RENOV", "DEV") else ""
            tag_linha = "par" if i % 2 == 0 else "impar"

            self._tree.insert(
                "", "end",
                iid=str(r.get("id", i)),
                values=(
                    r.get("id",        "") or "",
                    r.get("nome",      "") or "",
                    r.get("cpf",       "") or "",
                    r.get("unloc",     "") or "",
                    r.get("memorando", "") or "",
                    datas,
                    r.get("analise",   "") or "",
                    r.get("motivo",    "") or "",
                    envio,
                    r.get("lancou",    "") or "",
                ),
                tags=(tag_linha, tag_cor),
            )

        total = info["total_filtrado"]
        ini   = info["inicio"] + 1 if total else 0
        fim   = info["fim"]

        self._lbl_status.configure(
            text=(f"Exibindo {ini}–{fim} de {total:,} registro(s)"
                  if total else "Nenhum registro encontrado."))
        self._lbl_pagina.configure(
            text=f"{info['pagina_atual'] + 1} / {info['total_paginas']}")

    def item_selecionado(self):
        """Retorna os valores da linha selecionada ou None."""
        sel = self._tree.selection()
        if not sel:
            return None
        return self._tree.item(sel[0], "values")

    # ── Helpers ───────────────────────────────────────────────────────────────
    @staticmethod
    def _fmt_data(val, zero_vazio=False) -> str:
        if not val:
            return ""
        if zero_vazio and str(val) == "0000-00-00":
            return ""
        if isinstance(val, datetime):
            return val.strftime("%d/%m/%Y")
        s = str(val)
        return "" if (zero_vazio and s == "0000-00-00") else s

    def _duplo_clique(self, event):
        item = self._tree.identify_row(event.y)
        if not item:
            return
        valores = self._tree.item(item, "values")
        if valores:
            self._on_duplo_clique(valores)