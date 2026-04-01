# -*- coding: utf-8 -*-
"""
Widgets customizados para a interface de devolução
"""

import customtkinter as ctk
from app.theme import AppTheme

class StatusBar(ctk.CTkFrame):
    """Barra de status para feedback"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=AppTheme.BG_CARD, height=40, **kwargs)
        self._create_widgets()
        self.hide()
    
    def _create_widgets(self):
        # Label de status
        self.label_status = ctk.CTkLabel(
            self,
            text="",
            font=("Segoe UI", 11),
            text_color=AppTheme.TXT_MAIN
        )
        self.label_status.pack(side="left", padx=15, pady=5)
        
        # Botão para fechar
        self.btn_fechar = ctk.CTkButton(
            self,
            text="✕",
            width=30,
            height=30,
            fg_color="transparent",
            hover_color=AppTheme.BG_INPUT,
            text_color=AppTheme.TXT_MAIN,
            command=self.hide
        )
        self.btn_fechar.pack(side="right", padx=5, pady=5)
    
    def mostrar_info(self, mensagem):
        """Mostra mensagem informativa"""
        self.label_status.configure(text=mensagem, text_color=AppTheme.TXT_INFO)
        self.fg_color = AppTheme.BG_INFO
        self.show()
    
    def mostrar_sucesso(self, mensagem):
        """Mostra mensagem de sucesso"""
        self.label_status.configure(text=mensagem, text_color=AppTheme.TXT_SUCCESS)
        self.fg_color = AppTheme.BG_SUCCESS
        self.show()
    
    def mostrar_erro(self, mensagem):
        """Mostra mensagem de erro"""
        self.label_status.configure(text=mensagem, text_color=AppTheme.TXT_ERROR)
        self.fg_color = AppTheme.BG_ERROR
        self.show()
    
    def mostrar_aviso(self, mensagem):
        """Mostra mensagem de aviso"""
        self.label_status.configure(text=mensagem, text_color=AppTheme.TXT_WARNING)
        self.fg_color = AppTheme.BG_WARNING
        self.show()
    
    def show(self):
        """Mostra a barra de status"""
        self.pack(fill="x", pady=(0, 10))
    
    def hide(self):
        """Esconde a barra de status"""
        self.pack_forget()

class ContadorCaracteres(ctk.CTkFrame):
    """Widget para contagem de caracteres"""
    
    def __init__(self, master, text_widget, max_caracteres=1000, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.text_widget = text_widget
        self.max_caracteres = max_caracteres
        
        self._create_widgets()
        self._bind_events()
        self.atualizar()
    
    def _create_widgets(self):
        # Label de contagem
        self.label_contagem = ctk.CTkLabel(
            self,
            text="0/1000",
            font=("Segoe UI", 10),
            text_color=AppTheme.TXT_MUTED
        )
        self.label_contagem.pack(side="right", padx=5)
    
    def _bind_events(self):
        """Vincula eventos do text widget"""
        self.text_widget.bind("<KeyRelease>", lambda e: self.atualizar())
    
    def atualizar(self):
        """Atualiza a contagem de caracteres"""
        conteudo = self.text_widget.get("1.0", "end-1c")
        contagem = len(conteudo)
        
        # Atualizar texto
        self.label_contagem.configure(text=f"{contagem}/{self.max_caracteres}")
        
        # Mudar cor se passar do limite
        if contagem > self.max_caracteres:
            self.label_contagem.configure(text_color=AppTheme.TXT_ERROR)
        elif contagem > self.max_caracteres * 0.9:  # 90% do limite
            self.label_contagem.configure(text_color=AppTheme.TXT_WARNING)
        else:
            self.label_contagem.configure(text_color=AppTheme.TXT_MUTED)
    
    def obter_contagem(self):
        """Retorna a contagem atual de caracteres"""
        conteudo = self.text_widget.get("1.0", "end-1c")
        return len(conteudo)
    
    def esta_dentro_limite(self):
        """Verifica se está dentro do limite de caracteres"""
        return self.obter_contagem() <= self.max_caracteres