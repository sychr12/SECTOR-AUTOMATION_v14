# -*- coding: utf-8 -*-
"""
Widgets customizados para a interface de consulta.
"""

import customtkinter as ctk
from tkinter import ttk, Menu
from app.theme import AppTheme

_VERDE  = "#22c55e"
_AZUL   = "#3b82f6"
_VERM   = "#ef4444"
_AMBER  = "#f59e0b"
_MUTED  = "#64748b"

COLUNAS = [
    ("ID",        0,    False),   # oculto
    ("NOME",      220,  True),
    ("CPF",       120,  True),
    ("MUNICÍPIO", 140,  True),
    ("MEMORANDO", 100,  True),
    ("TIPO",       70,  True),
    ("MOTIVO",    200,  True),
    ("USUÁRIO",   110,  True),
    ("DATA",       90,  True),
]


class TabelaConsulta(ctk.CTkFrame):
    """
    Frame que encapsula um ttk.Treeview estilizado com scrollbars.
    Corrigido: _configurar_estilo() agora é chamado APÓS super().__init__().
    """

    def __init__(self, master, **kwargs):
        super().__init__(master,
                         fg_color=AppTheme.BG_CARD,
                         corner_radius=14, **kwargs)
        # Estilo configurado DEPOIS do super().__init__() — BUG 4 corrigido
        self._configurar_estilo()
        self._build()

    # ── Estilo ────────────────────────────────────────────────────────────────
    def _configurar_estilo(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Consulta.Treeview",
            background=AppTheme.BG_CARD,
            foreground=AppTheme.TXT_MAIN,
            fieldbackground=AppTheme.BG_CARD,
            rowheight=34,
            borderwidth=0,
            font=("Segoe UI", 11),
        )
        style.configure(
            "Consulta.Treeview.Heading",
            background=AppTheme.BG_INPUT,
            foreground=_MUTED,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
        )
        style.map(
            "Consulta.Treeview",
            background=[("selected", "#1e3a5f")],
        )

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build(self):
        # Cabeçalho interno com contagem
        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.pack(fill="x", padx=12, pady=(12, 6))

        ctk.CTkLabel(topo, text="Resultados",
                     font=("Segoe UI", 13, "bold"),
                     text_color=AppTheme.TXT_MAIN).pack(side="left")

        self._lbl_total = ctk.CTkLabel(topo, text="",
                                       font=("Segoe UI", 11),
                                       text_color=_MUTED)
        self._lbl_total.pack(side="right")

        # Frame do Treeview
        frame_tv = ctk.CTkFrame(self, fg_color="transparent")
        frame_tv.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        cols = [c[0] for c in COLUNAS]
        self._tree = ttk.Treeview(
            frame_tv,
            columns=cols,
            show="headings",
            style="Consulta.Treeview",
            selectmode="browse",
        )

        for col_id, largura, visivel in COLUNAS:
            self._tree.heading(col_id, text=col_id)
            if visivel:
                stretch = col_id in ("NOME", "MOTIVO")
                self._tree.column(col_id, width=largura,
                                  minwidth=50, stretch=stretch)
            else:
                self._tree.column(col_id, width=0, stretch=False)

        # Tags de cor por tipo
        self._tree.tag_configure("INSC",  foreground=_AZUL)
        self._tree.tag_configure("RENOV", foreground=_VERDE)
        self._tree.tag_configure("DEV",   foreground=_VERM)
        self._tree.tag_configure("par",   background=AppTheme.BG_CARD)
        self._tree.tag_configure("impar", background=AppTheme.BG_INPUT)

        vsb = ttk.Scrollbar(frame_tv, orient="vertical",
                            command=self._tree.yview)
        hsb = ttk.Scrollbar(frame_tv, orient="horizontal",
                            command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set,
                             xscrollcommand=hsb.set)

        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self._tree.pack(fill="both", expand=True)

    # ── API pública ───────────────────────────────────────────────────────────
    def adicionar_dados(self, dados: list):
        """Limpa e repopula a tabela."""
        for item in self._tree.get_children():
            self._tree.delete(item)

        if not dados:
            self._lbl_total.configure(text="Nenhum registro encontrado.")
            self._tree.insert("", "end",
                              values=("", "Nenhum registro encontrado",
                                      *[""] * 7))
            return

        for i, linha in enumerate(dados):
            tipo = str(linha[5]).upper() if len(linha) > 5 else ""
            tag_cor   = tipo if tipo in ("INSC", "RENOV", "DEV") else ""
            tag_linha = "par" if i % 2 == 0 else "impar"
            self._tree.insert("", "end", values=linha,
                              tags=(tag_linha, tag_cor))

        self._lbl_total.configure(
            text=f"{len(dados):,} registro(s) encontrado(s)")

    def obter_linha_selecionada(self):
        """Retorna os valores da linha selecionada ou None."""
        sel = self._tree.selection()
        if not sel:
            return None
        return self._tree.item(sel[0], "values")

    def obter_id_selecionado(self):
        sel = self.obter_linha_selecionada()
        return sel[0] if sel else None

    def bind_treeview(self, evento, callback):
        """Vincula eventos diretamente ao Treeview interno."""
        self._tree.bind(evento, callback)

    @property
    def tree(self):
        """Acesso direto ao Treeview para bind de eventos externos."""
        return self._tree


class MenuContexto(Menu):
    """
    Menu de contexto para a tabela.
    Corrigido: bind deve ser feito no Treeview, não no frame container.
    Use tabela.bind_treeview("<Button-3>", ...) ao configurar.
    """

    def __init__(self, parent, on_editar=None, on_excluir=None):
        super().__init__(parent, tearoff=0)

        if on_editar:
            self.add_command(label="✏️  Editar registro",  command=on_editar)
        if on_excluir:
            self.add_separator()
            self.add_command(label="🗑️  Excluir registro", command=on_excluir)

    def mostrar(self, event, tabela):
        """
        Seleciona o item sob o cursor e exibe o menu.
        Deve ser chamado com event vindo do Treeview interno.
        """
        item = tabela.tree.identify_row(event.y)
        if item:
            tabela.tree.selection_set(item)
            try:
                self.tk_popup(event.x_root, event.y_root)
            finally:
                self.grab_release()