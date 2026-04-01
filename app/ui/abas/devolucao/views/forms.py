# -*- coding: utf-8 -*-
"""
Formulários para configuração de devolução
"""

import customtkinter as ctk
from tkinter import messagebox
from app.theme import AppTheme

class FormularioDestinatarios(ctk.CTkToplevel):
    """Formulário para gerenciar destinatários de email"""
    
    def __init__(self, parent, destinatarios_iniciais=None, on_salvar=None):
        super().__init__(parent)
        
        self.destinatarios = destinatarios_iniciais or []
        self.on_salvar = on_salvar
        
        self._configurar_janela()
        self._criar_widgets()
    
    def _configurar_janela(self):
        """Configura as propriedades da janela"""
        self.title("Destinatários de Email")
        self.geometry("500x400")
        self.resizable(False, False)
        
        # Centralizar
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        self.grab_set()
        self.focus_set()
    
    def _criar_widgets(self):
        """Cria os widgets do formulário"""
        container = ctk.CTkFrame(self, fg_color=AppTheme.BG_APP)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        ctk.CTkLabel(
            container,
            text="✉️ Destinatários de Email",
            font=("Segoe UI", 18, "bold"),
            text_color=AppTheme.TXT_MAIN
        ).pack(pady=(0, 20))
        
        # Frame para adicionar novo email
        add_frame = ctk.CTkFrame(container, fg_color=AppTheme.BG_CARD, corner_radius=12)
        add_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            add_frame,
            text="Adicionar novo email:",
            font=("Segoe UI", 12),
            text_color=AppTheme.TXT_MAIN
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        input_frame = ctk.CTkFrame(add_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.entry_email = ctk.CTkEntry(
            input_frame,
            placeholder_text="email@exemplo.com",
            fg_color=AppTheme.BG_INPUT,
            border_color=AppTheme.BTN_PRIMARY,
            text_color=AppTheme.TXT_MAIN,
            font=("Segoe UI", 12),
            height=35
        )
        self.entry_email.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(
            input_frame,
            text="+",
            width=40,
            height=35,
            fg_color=AppTheme.BTN_SUCCESS,
            hover_color=AppTheme.BTN_SUCCESS_HOVER,
            command=self._adicionar_email
        ).pack(side="right")
        
        # Lista de destinatários
        lista_frame = ctk.CTkFrame(container, fg_color=AppTheme.BG_CARD, corner_radius=12)
        lista_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        ctk.CTkLabel(
            lista_frame,
            text="Destinatários atuais:",
            font=("Segoe UI", 12, "bold"),
            text_color=AppTheme.TXT_MAIN
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Frame para scroll
        scroll_frame = ctk.CTkFrame(lista_frame, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Canvas para scroll
        self.canvas = ctk.CTkCanvas(scroll_frame, bg=AppTheme.BG_CARD, highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(scroll_frame, orientation="vertical", command=self.canvas.yview)
        self.scrollable_frame = ctk.CTkFrame(self.canvas, fg_color=AppTheme.BG_CARD)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Carregar destinatários
        self._carregar_destinatarios()
        
        # Botões
        botoes_frame = ctk.CTkFrame(container, fg_color="transparent")
        botoes_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkButton(
            botoes_frame,
            text="Cancelar",
            width=100,
            height=35,
            fg_color=AppTheme.BG_INPUT,
            hover_color=AppTheme.TXT_MUTED,
            text_color=AppTheme.TXT_MAIN,
            command=self.destroy
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            botoes_frame,
            text="Salvar",
            width=100,
            height=35,
            fg_color=AppTheme.BTN_SUCCESS,
            hover_color=AppTheme.BTN_SUCCESS_HOVER,
            command=self._salvar
        ).pack(side="right")
    
    def _carregar_destinatarios(self):
        """Carrega os destinatários na lista"""
        # Limpar frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Adicionar cada destinatário
        for i, email in enumerate(self.destinatarios):
            item_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
            item_frame.pack(fill="x", pady=2)
            
            ctk.CTkLabel(
                item_frame,
                text=email,
                font=("Segoe UI", 11),
                text_color=AppTheme.TXT_MAIN
            ).pack(side="left", padx=(10, 0))
            
            ctk.CTkButton(
                item_frame,
                text="🗑️",
                width=30,
                height=25,
                fg_color="transparent",
                hover_color=AppTheme.BG_ERROR,
                text_color=AppTheme.TXT_MAIN,
                command=lambda e=email: self._remover_email(e)
            ).pack(side="right", padx=5)
    
    def _adicionar_email(self):
        """Adiciona um novo email à lista"""
        email = self.entry_email.get().strip()
        
        if not email:
            messagebox.showwarning("Aviso", "Digite um email válido.")
            return
        
        # Validação simples de email
        if "@" not in email or "." not in email:
            messagebox.showwarning("Aviso", "Email inválido.")
            return
        
        if email in self.destinatarios:
            messagebox.showinfo("Info", "Este email já está na lista.")
            return
        
        self.destinatarios.append(email)
        self.entry_email.delete(0, "end")
        self._carregar_destinatarios()
    
    def _remover_email(self, email):
        """Remove um email da lista"""
        if email in self.destinatarios:
            self.destinatarios.remove(email)
            self._carregar_destinatarios()
    
    def _salvar(self):
        """Salva a lista de destinatários"""
        if self.on_salvar:
            self.on_salvar(self.destinatarios)
        
        self.destroy()
    
    def show(self):
        """Mostra o formulário e retorna os destinatários"""
        self.wait_window()
        return self.destinatarios