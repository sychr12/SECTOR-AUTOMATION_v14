# app/ui/abas/Email/views/components.py
# -*- coding: utf-8 -*-
"""
Componentes de UI reutilizáveis para a interface de download de emails
"""

import customtkinter as ctk
from tkinter import ttk
from app.theme import AppTheme

class HeaderCard(ctk.CTkFrame):
    """Card de cabeçalho estilizado"""
    def __init__(self, master, title, subtitle="", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._create_widgets(title, subtitle)
    
    def _create_widgets(self, title, subtitle):
        ctk.CTkLabel(
            self,
            text=title,
            font=("Segoe UI", 26, "bold"),
            anchor="w"
        ).pack(anchor="w")
        
        if subtitle:
            ctk.CTkLabel(
                self,
                text=subtitle,
                font=("Segoe UI", 14),
                text_color=AppTheme.TXT_MUTED
            ).pack(anchor="w", pady=(6, 0))
    
    def pack(self, **kwargs):
        kwargs.setdefault('fill', 'x')
        kwargs.setdefault('padx', 30)
        kwargs.setdefault('pady', (30, 15))
        super().pack(**kwargs)

class ActionButton(ctk.CTkButton):
    """Botão de ação estilizado"""
    def __init__(self, master, text="", command=None, **kwargs):
        super().__init__(
            master,
            text=text,
            command=command,
            height=46,
            width=220,
            font=("Segoe UI", 15, "bold"),
            corner_radius=14,
            fg_color=AppTheme.BTN_PRIMARY,
            hover_color=AppTheme.BTN_PRIMARY_HOVER,
            **kwargs
        )
    
    def pack(self, **kwargs):
        kwargs.setdefault('anchor', 'w')
        super().pack(**kwargs)

class LogTableView:
    """Tabela para exibição de logs"""
    
    @staticmethod
    def criar(parent):
        """Cria e configura a tabela de logs"""
        container = ctk.CTkFrame(parent, corner_radius=16, fg_color=AppTheme.BG_CARD)
        container.pack(fill="both", expand=True, padx=30, pady=(10, 30))
        
        # Criar estilo para a tabela
        LogTableView._aplicar_estilo()
        
        # Criar Treeview
        treeview = ttk.Treeview(
            container,
            columns=("Status", "Mensagem"),
            show="headings",
            height=12
        )
        
        # Configurar colunas
        treeview.heading("Status", text="Status")
        treeview.heading("Mensagem", text="Mensagem")
        
        treeview.column("Status", width=140, anchor="center")
        treeview.column("Mensagem", width=900, anchor="w")
        
        treeview.pack(fill="both", expand=True, padx=12, pady=12)
        
        return treeview, container
    
    @staticmethod
    def _aplicar_estilo():
        """Aplica estilo na tabela"""
        style = ttk.Style()
        style.theme_use("default")
        
        style.configure(
            "Treeview",
            background=AppTheme.BG_CARD,
            foreground=AppTheme.TXT_MAIN,
            fieldbackground=AppTheme.BG_CARD,
            rowheight=34,
            font=("Segoe UI", 12)
        )
        
        style.configure(
            "Treeview.Heading",
            background=AppTheme.BG_CARD,
            foreground=AppTheme.TXT_MAIN,
            font=("Segoe UI", 12, "bold")
        )
        
        style.map(
            "Treeview",
            background=[("selected", AppTheme.BTN_PRIMARY)],
            foreground=[("selected", AppTheme.TXT_MAIN)]
        )
    
    @staticmethod
    def adicionar_log(treeview, status, mensagem):
        """Adiciona uma entrada de log na tabela"""
        treeview.insert("", "end", values=(status, mensagem))
    
    @staticmethod
    def limpar_logs(treeview):
        """Limpa todos os logs da tabela"""
        for item in treeview.get_children():
            treeview.delete(item)