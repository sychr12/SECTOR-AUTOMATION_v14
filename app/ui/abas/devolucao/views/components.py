# -*- coding: utf-8 -*-
"""
Componentes de UI reutilizáveis para a interface de devolução
"""

import customtkinter as ctk
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
            font=("Segoe UI", 28, "bold"),
            text_color=AppTheme.TXT_MAIN
        ).pack(anchor="w", pady=(0, 10))
        
        if subtitle:
            ctk.CTkLabel(
                self,
                text=subtitle,
                font=("Segoe UI", 14),
                text_color=AppTheme.TXT_MUTED
            ).pack(anchor="w", pady=(0, 30))
    
    def pack(self, **kwargs):
        kwargs.setdefault('anchor', 'w')
        super().pack(**kwargs)

class ConteudoCard(ctk.CTkFrame):
    """Card para conteúdo da devolução"""
    def __init__(self, master, on_content_change=None, **kwargs):
        super().__init__(master, fg_color=AppTheme.BG_CARD, corner_radius=18, **kwargs)
        self.on_content_change = on_content_change
        self._create_widgets()
    
    def _create_widgets(self):
        # Título do card
        ctk.CTkLabel(
            self,
            text="Conteúdo da Devolução",
            font=("Segoe UI", 16, "bold"),
            text_color=AppTheme.TXT_MAIN
        ).pack(anchor="w", padx=20, pady=(20, 10))
        
        # Área de texto
        self.text_widget = ctk.CTkTextbox(
            self,
            height=300,
            corner_radius=12,
            fg_color=AppTheme.BG_INPUT,
            text_color=AppTheme.TXT_MAIN,
            border_color=AppTheme.BORDER,
            font=("Segoe UI", 12)
        )
        self.text_widget.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Bind para evento de mudança de conteúdo
        if self.on_content_change:
            self.text_widget.bind("<KeyRelease>", lambda e: self.on_content_change())
    
    def obter_conteudo(self):
        """Retorna o conteúdo do textbox"""
        return self.text_widget.get("1.0", "end").strip()
    
    def definir_conteudo(self, conteudo):
        """Define o conteúdo do textbox"""
        self.text_widget.delete("1.0", "end")
        self.text_widget.insert("1.0", conteudo)
    
    def limpar_conteudo(self):
        """Limpa o conteúdo do textbox"""
        self.text_widget.delete("1.0", "end")

class BotoesAcao(ctk.CTkFrame):
    """Frame com botões de ação"""
    def __init__(self, master, on_gerar_pdf=None, on_enviar_email=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_gerar_pdf = on_gerar_pdf
        self.on_enviar_email = on_enviar_email
        self._create_widgets()
    
    def _create_widgets(self):
        # Botão Gerar PDF
        if self.on_gerar_pdf:
            self.btn_pdf = ctk.CTkButton(
                self,
                text="📄 Gerar PDF",
                width=180,
                height=45,
                font=("Segoe UI", 13, "bold"),
                fg_color=AppTheme.BTN_PRIMARY,
                hover_color=AppTheme.BTN_PRIMARY_HOVER,
                corner_radius=10,
                command=self.on_gerar_pdf
            )
            self.btn_pdf.grid(row=0, column=0, padx=10)
        
        # Botão Enviar Email
        if self.on_enviar_email:
            self.btn_email = ctk.CTkButton(
                self,
                text="✉️ Enviar Email",
                width=180,
                height=45,
                font=("Segoe UI", 13, "bold"),
                fg_color=AppTheme.BTN_SUCCESS,
                hover_color=AppTheme.BTN_SUCCESS_HOVER,
                corner_radius=10,
                command=self.on_enviar_email
            )
            self.btn_email.grid(row=0, column=1, padx=10)
        
        # Botão Ambos (opcional)
        if self.on_gerar_pdf and self.on_enviar_email:
            self.btn_ambos = ctk.CTkButton(
                self,
                text="📧 Gerar e Enviar",
                width=180,
                height=45,
                font=("Segoe UI", 13, "bold"),
                fg_color=AppTheme.BTN_WARNING,
                hover_color=AppTheme.BTN_WARNING_HOVER,
                corner_radius=10,
                command=self._executar_ambos
            )
            self.btn_ambos.grid(row=0, column=2, padx=10)
    
    def _executar_ambos(self):
        """Executa ambas as ações"""
        if self.on_gerar_pdf:
            self.on_gerar_pdf()
        if self.on_enviar_email:
            self.on_enviar_email()
    
    def desabilitar_botoes(self):
        """Desabilita todos os botões"""
        if hasattr(self, 'btn_pdf'):
            self.btn_pdf.configure(state="disabled")
        if hasattr(self, 'btn_email'):
            self.btn_email.configure(state="disabled")
        if hasattr(self, 'btn_ambos'):
            self.btn_ambos.configure(state="disabled")
    
    def habilitar_botoes(self):
        """Habilita todos os botões"""
        if hasattr(self, 'btn_pdf'):
            self.btn_pdf.configure(state="normal")
        if hasattr(self, 'btn_email'):
            self.btn_email.configure(state="normal")
        if hasattr(self, 'btn_ambos'):
            self.btn_ambos.configure(state="normal")