# -*- coding: utf-8 -*-
import customtkinter as ctk
from app.theme import AppTheme

class Header(ctk.CTkFrame):
    """Cabeçalho da página"""
    def __init__(self, master, title, subtitle=""):
        super().__init__(master, fg_color="transparent")
        self._create_widgets(title, subtitle)
        
    def _create_widgets(self, title, subtitle):
        ctk.CTkLabel(
            self,
            text=title,
            font=("Segoe UI", 28, "bold"),
            text_color=AppTheme.TXT_MAIN
        ).pack(anchor="w")

        if subtitle:
            ctk.CTkLabel(
                self,
                text=subtitle,
                font=("Segoe UI", 14),
                text_color=AppTheme.TXT_MUTED
            ).pack(anchor="w", pady=(6, 28))
    
    def pack(self, **kwargs):
        kwargs.setdefault('anchor', 'w')
        kwargs.setdefault('pady', (0, 28))
        super().pack(**kwargs)

class RadioSelector(ctk.CTkFrame):
    """Seletor de opções com radio buttons"""
    def __init__(self, master, options, default_value=None, command=None):
        super().__init__(master, fg_color=AppTheme.BG_CARD, corner_radius=22)
        self.options = options
        self.command = command
        self.radio_var = ctk.StringVar(value=default_value or options[0]['value'])
        self._create_widgets()
        
    def _create_widgets(self):
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(padx=25, pady=20)
        
        for option in self.options:
            ctk.CTkRadioButton(
                row, 
                text=option['text'],
                variable=self.radio_var, 
                value=option['value'],
                command=self.command,
                fg_color=AppTheme.BTN_PRIMARY,
                hover_color=AppTheme.BTN_PRIMARY_HOVER,
                border_color=AppTheme.BTN_PRIMARY,
                text_color=AppTheme.TXT_MAIN,
                font=("Segoe UI", 12)
            ).pack(side="left", padx=40)
    
    def pack(self, **kwargs):
        kwargs.setdefault('fill', 'x')
        kwargs.setdefault('pady', (0, 28))
        super().pack(**kwargs)
    
    def get_value(self):
        return self.radio_var.get()