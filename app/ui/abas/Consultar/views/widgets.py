# -*- coding: utf-8 -*-
"""
Widgets customizados para a interface de consulta.
Tabela: inscrenov
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import *
from PyQt6.QtWidgets import ttk, Menu
from app.theme import AppTheme

# Colunas da tabela inscrenov
COLUNAS = [
    ("ID",          0,   False),   # oculto
    ("NOME",        250, True),
    ("CPF",         130, True),
    ("UNLOC",       150, True),    # município
    ("MEMORANDO",   120, True),
    ("DATAS",       100, True),
    ("DESCRIÇÃO",   200, True),
    ("ANÁLISE",     200, True),
    ("GERADO",      100, True),
    ("LANÇOU",      120, True),
    ("DATA LANÇ.",   140, True),
    ("DATA CRIAÇÃO", 140, True),
]


class TabelaConsulta(ctk.CTkFrame):
    """Frame que encapsula um ttk.Treeview estilizado"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=AppTheme.BG_CARD, corner_radius=14, **kwargs)
        self._configurar_estilo()
        self._build()
    
    def _configurar_estilo(self):
        """Configura o estilo do Treeview"""
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
            foreground="#64748b",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
        )
        
        style.map(
            "Consulta.Treeview",
            background=[("selected", "#1e3a5f")],
        )
    
    def _build(self):
        """Constrói a interface da tabela"""
        # Topo com contagem
        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.pack(fill="x", padx=12, pady=(12, 6))
        
        ctk.CTkLabel(topo, text="Resultados",
                     font=("Segoe UI", 13, "bold"),
                     text_color=AppTheme.TXT_MAIN).pack(side="left")
        
        self._lbl_total = ctk.CTkLabel(topo, text="",
                                       font=("Segoe UI", 11),
                                       text_color="#64748b")
        self._lbl_total.pack(side="right")
        
        # Frame do Treeview
        frame_tv = ctk.CTkFrame(self, fg_color="transparent")
        frame_tv.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        
        # Criar Treeview
        cols = [c[0] for c in COLUNAS]
        self._tree = ttk.Treeview(
            frame_tv,
            columns=cols,
            show="headings",
            style="Consulta.Treeview",
            selectmode="browse",
        )
        
        # Configurar colunas
        for col_id, largura, visivel in COLUNAS:
            self._tree.heading(col_id, text=col_id)
            if visivel:
                stretch = col_id in ("NOME", "DESCRIÇÃO", "ANÁLISE")
                self._tree.column(col_id, width=largura,
                                  minwidth=50, stretch=stretch)
            else:
                self._tree.column(col_id, width=0, stretch=False)
        
        # Scrollbars
        vsb = ttk.Scrollbar(frame_tv, orient="vertical",
                            command=self._tree.yview)
        hsb = ttk.Scrollbar(frame_tv, orient="horizontal",
                            command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set,
                             xscrollcommand=hsb.set)
        
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self._tree.pack(fill="both", expand=True)
    
    def adicionar_dados(self, dados: list):
        """Limpa e repopula a tabela"""
        # Limpar itens existentes
        for item in self._tree.get_children():
            self._tree.delete(item)
        
        if not dados:
            self._lbl_total.configure(text="Nenhum registro encontrado.")
            return
        
        # Adicionar novos dados
        for i, linha in enumerate(dados):
            # Cor alternada para linhas
            tag = "even" if i % 2 == 0 else "odd"
            self._tree.insert("", "end", values=linha, tags=(tag,))
        
        # Configurar tags para cores
        self._tree.tag_configure("even", background=AppTheme.BG_CARD)
        self._tree.tag_configure("odd", background=AppTheme.BG_INPUT)
        
        self._lbl_total.configure(
            text=f"{len(dados):,} registro(s) encontrado(s)")
    
    def obter_linha_selecionada(self):
        """Retorna os valores da linha selecionada ou None"""
        sel = self._tree.selection()
        if not sel:
            return None
        return self._tree.item(sel[0], "values")
    
    def obter_id_selecionado(self):
        """Retorna o ID da linha selecionada"""
        sel = self.obter_linha_selecionada()
        return sel[0] if sel else None
    
    def bind_treeview(self, evento, callback):
        """Vincula eventos diretamente ao Treeview interno"""
        self._tree.bind(evento, callback)
    
    @property
    def tree(self):
        """Acesso direto ao Treeview"""
        return self._tree


class MenuContexto(Menu):
    """Menu de contexto para a tabela"""
    
    def __init__(self, parent, on_editar=None, on_excluir=None):
        super().__init__(parent, tearoff=0)
        
        if on_editar:
            self.add_command(label="✏️ Editar registro", command=on_editar)
        if on_excluir:
            if on_editar:
                self.add_separator()
            self.add_command(label="🗑️ Excluir registro", command=on_excluir)
    
    def mostrar(self, event, tabela):
        """Seleciona o item sob o cursor e exibe o menu"""
        item = tabela.tree.identify_row(event.y)
        if item:
            tabela.tree.selection_set(item)
            try:
                self.tk_popup(event.x_root, event.y_root)
            finally:
                self.grab_release()
