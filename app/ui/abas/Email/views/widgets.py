# -*- coding: utf-8 -*-
"""
Widgets customizados para a interface de download de emails
"""

import customtkinter as ctk
from app.theme import AppTheme

class ProgressoDownload(ctk.CTkFrame):
    """Barra de progresso para download"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._criar_widgets()
        self.valor_atual = 0
    
    def _criar_widgets(self):
        # Label do progresso
        self.label = ctk.CTkLabel(
            self,
            text="Progresso: 0%",
            font=("Segoe UI", 12),
            text_color=AppTheme.TXT_MUTED
        )
        self.label.pack(anchor="w", pady=(0, 5))
        
        # Barra de progresso
        self.progress_bar = ctk.CTkProgressBar(
            self,
            height=8,
            fg_color=AppTheme.BG_INPUT,
            progress_color=AppTheme.BTN_PRIMARY
        )
        self.progress_bar.pack(fill="x")
        self.progress_bar.set(0)
        
        # Label de status
        self.status_label = ctk.CTkLabel(
            self,
            text="Pronto para iniciar",
            font=("Segoe UI", 11),
            text_color=AppTheme.TXT_MUTED
        )
        self.status_label.pack(anchor="w", pady=(5, 0))
    
    def atualizar(self, valor, status=""):
        """Atualiza a barra de progresso"""
        self.valor_atual = valor
        self.progress_bar.set(valor / 100)
        self.label.configure(text=f"Progresso: {valor}%")
        
        if status:
            self.status_label.configure(text=status)
    
    def reset(self):
        """Reseta a barra de progresso"""
        self.atualizar(0, "Pronto para iniciar")

class EstatisticasDownload(ctk.CTkFrame):
    """Widget para exibir estatísticas do download"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=AppTheme.BG_CARD, corner_radius=12, **kwargs)
        self._criar_widgets()
        self.reset()
    
    def _criar_widgets(self):
        # Layout em grid
        for i in range(4):
            self.columnconfigure(i, weight=1)
        
        # Título
        ctk.CTkLabel(
            self,
            text="📊 Estatísticas",
            font=("Segoe UI", 14, "bold")
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=15, pady=(15, 10))
        
        # E-mails processados
        self.label_emails = ctk.CTkLabel(
            self,
            text="E-mails: 0",
            font=("Segoe UI", 12)
        )
        self.label_emails.grid(row=1, column=0, sticky="w", padx=15, pady=5)
        
        # Arquivos baixados
        self.label_arquivos = ctk.CTkLabel(
            self,
            text="Arquivos: 0",
            font=("Segoe UI", 12)
        )
        self.label_arquivos.grid(row=1, column=1, sticky="w", padx=15, pady=5)
        
        # Sucessos
        self.label_sucessos = ctk.CTkLabel(
            self,
            text="✅ Sucessos: 0",
            font=("Segoe UI", 12),
            text_color="#10B981"
        )
        self.label_sucessos.grid(row=2, column=0, sticky="w", padx=15, pady=5)
        
        # Erros
        self.label_erros = ctk.CTkLabel(
            self,
            text="❌ Erros: 0",
            font=("Segoe UI", 12),
            text_color="#EF4444"
        )
        self.label_erros.grid(row=2, column=1, sticky="w", padx=15, pady=5)
        
        # Última execução
        self.label_ultima = ctk.CTkLabel(
            self,
            text="Última: Nunca",
            font=("Segoe UI", 11),
            text_color=AppTheme.TXT_MUTED
        )
        self.label_ultima.grid(row=1, column=2, columnspan=2, sticky="e", padx=15, pady=5)
    
    def atualizar(self, emails=0, arquivos=0, sucessos=0, erros=0):
        """Atualiza as estatísticas"""
        self.label_emails.configure(text=f"E-mails: {emails}")
        self.label_arquivos.configure(text=f"Arquivos: {arquivos}")
        self.label_sucessos.configure(text=f"✅ Sucessos: {sucessos}")
        self.label_erros.configure(text=f"❌ Erros: {erros}")
    
    def atualizar_ultima_execucao(self, data_hora):
        """Atualiza a data/hora da última execução"""
        self.label_ultima.configure(text=f"Última: {data_hora}")
    
    def reset(self):
        """Reseta todas as estatísticas"""
        self.atualizar(0, 0, 0, 0)
        self.atualizar_ultima_execucao("Nunca")

class CardInfo(ctk.CTkFrame):
    """Card informativo"""
    
    def __init__(self, master, titulo, conteudo, icon="ℹ️", **kwargs):
        super().__init__(
            master, 
            fg_color=AppTheme.BG_CARD, 
            corner_radius=16,
            **kwargs
        )
        self._criar_widgets(titulo, conteudo, icon)
    
    def _criar_widgets(self, titulo, conteudo, icon):
        # Icone e título
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            header,
            text=icon,
            font=("Segoe UI", 20)
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(
            header,
            text=titulo,
            font=("Segoe UI", 14, "bold")
        ).pack(side="left")
        
        # Conteúdo
        ctk.CTkLabel(
            self,
            text=conteudo,
            font=("Segoe UI", 12),
            text_color=AppTheme.TXT_MUTED,
            wraplength=400,
            justify="left"
        ).pack(fill="x", padx=20, pady=(0, 20))