# -*- coding: utf-8 -*-
import customtkinter as ctk
from app.theme import AppTheme

class FormCard(ctk.CTkFrame):
    """Card de formulário estilizado"""
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=AppTheme.BG_CARD,
            corner_radius=22,
            **kwargs
        )
        
    def pack(self, **kwargs):
        kwargs.setdefault('fill', 'x')
        kwargs.setdefault('pady', (0, 24))
        super().pack(**kwargs)

class GridLayout(ctk.CTkFrame):
    """Layout de grid para formulários"""
    def __init__(self, master, columns=5, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.columns = columns
        
    def pack(self, **kwargs):
        kwargs.setdefault('padx', 25)
        kwargs.setdefault('pady', 22)
        kwargs.setdefault('fill', 'x')
        super().pack(**kwargs)
        
        # Configurar colunas
        for i in range(self.columns):
            self.columnconfigure(i, weight=1)

class StyledEntry(ctk.CTkEntry):
    """Campo de entrada estilizado"""
    def __init__(self, master, placeholder="", **kwargs):
        super().__init__(
            master,
            placeholder_text=placeholder,
            fg_color=AppTheme.BG_INPUT,
            border_color=AppTheme.BTN_PRIMARY,
            text_color=AppTheme.TXT_MAIN,
            placeholder_text_color=AppTheme.TXT_MUTED,
            font=("Segoe UI", 12),
            height=40,
            **kwargs
        )
    
    def grid(self, row=0, column=0, **kwargs):
        kwargs.setdefault('padx', 10)
        kwargs.setdefault('sticky', 'ew')
        super().grid(row=row, column=column, **kwargs)

class StyledButton(ctk.CTkButton):
    """Botão estilizado"""
    def __init__(self, master, text="", command=None, **kwargs):
        super().__init__(
            master,
            text=text,
            command=command,
            fg_color=AppTheme.BTN_PRIMARY,
            hover_color=AppTheme.BTN_PRIMARY_HOVER,
            text_color=AppTheme.TXT_MAIN,
            font=("Segoe UI", 12, "bold"),
            height=40,
            corner_radius=10,
            **kwargs
        )
    
    def pack(self, **kwargs):
        kwargs.setdefault('anchor', 'e')
        kwargs.setdefault('padx', 20)
        kwargs.setdefault('pady', 10)
        super().pack(**kwargs)

class StyledComboBox(ctk.CTkComboBox):
    """ComboBox estilizado"""
    def __init__(self, master, values=None, **kwargs):
        super().__init__(
            master,
            values=values or [],
            fg_color=AppTheme.BG_INPUT,
            border_color=AppTheme.BTN_PRIMARY,
            button_color=AppTheme.BTN_PRIMARY,
            button_hover_color=AppTheme.BTN_PRIMARY_HOVER,
            text_color=AppTheme.TXT_MAIN,
            dropdown_fg_color=AppTheme.BG_INPUT,
            dropdown_text_color=AppTheme.TXT_MAIN,
            dropdown_hover_color=AppTheme.BG_CARD,
            font=("Segoe UI", 12),
            height=40,
            **kwargs
        )
    
    def pack(self, **kwargs):
        kwargs.setdefault('fill', 'x')
        kwargs.setdefault('padx', 20)
        kwargs.setdefault('pady', (12, 6))
        super().pack(**kwargs)
    
    def grid(self, row=0, column=0, **kwargs):
        kwargs.setdefault('padx', 10)
        kwargs.setdefault('sticky', 'ew')
        super().grid(row=row, column=column, **kwargs)

class StyledTextbox(ctk.CTkTextbox):
    """Caixa de texto estilizada"""
    def __init__(self, master, height=100, **kwargs):
        super().__init__(
            master,
            height=height,
            fg_color=AppTheme.BG_INPUT,
            text_color=AppTheme.TXT_MAIN,
            border_color=AppTheme.BTN_PRIMARY,
            font=("Segoe UI", 12),
            **kwargs
        )
    
    def pack(self, **kwargs):
        kwargs.setdefault('fill', 'x')
        kwargs.setdefault('padx', 20)
        kwargs.setdefault('pady', (0, 18))
        super().pack(**kwargs)