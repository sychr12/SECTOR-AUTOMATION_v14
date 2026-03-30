# -*- coding: utf-8 -*-
"""
Componentes reutilizáveis para interface de email
"""

import customtkinter as ctk
from app.theme import AppTheme

class EmailStatusIndicator(ctk.CTkFrame):
    """Indicador de status do serviço de email"""
    
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.controller = controller
        
        self._create_widgets()
        self.update_status()
    
    def _create_widgets(self):
        """Cria os widgets do indicador"""
        self.status_icon = ctk.CTkLabel(
            self,
            text="🔴",
            font=("Segoe UI", 14),
            text_color=AppTheme.STATUS_ERROR
        )
        self.status_icon.pack(side="left", padx=(0, 8))
        
        self.status_text = ctk.CTkLabel(
            self,
            text="Email Desabilitado",
            font=("Segoe UI", 12),
            text_color=AppTheme.TXT_MUTED
        )
        self.status_text.pack(side="left")
    
    def update_status(self):
        """Atualiza o status baseado na configuração"""
        if self.controller.esta_habilitado():
            self.status_icon.configure(text="🟢", text_color=AppTheme.STATUS_SUCCESS)
            self.status_text.configure(text="Email Habilitado")
        else:
            self.status_icon.configure(text="🔴", text_color=AppTheme.STATUS_ERROR)
            self.status_text.configure(text="Email Desabilitado")