# -*- coding: utf-8 -*-
"""Card de estatísticas com ícone"""
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import *


class StatCard(ctk.CTkFrame):
    """Card para exibir estatísticas com ícone"""
    
    def __init__(self, master, icon_name: str, titulo: str, valor="—", cor="#3b82f6", icons=None):
        super().__init__(
            master, fg_color="#ffffff", corner_radius=12,
            border_width=1, border_color="#e2e8f0",
        )
        self.icons = icons
        self.cor = cor
        
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=16)

        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x")
        
        # Ícone
        if icons and icons.get(icon_name):
            ctk.CTkLabel(
                top, text="", image=icons[icon_name],
                width=32, height=32
            ).pack(side="left", padx=(0, 12))
        
        # Título
        title_frame = ctk.CTkFrame(top, fg_color="transparent")
        title_frame.pack(side="left")
        
        ctk.CTkLabel(
            title_frame, text=titulo, font=("Segoe UI", 11, "bold"),
            text_color="#64748b"
        ).pack(anchor="w")
        
        # Valor
        self._lbl = ctk.CTkLabel(
            inner, text=str(valor),
            font=("Segoe UI", 28, "bold"),
            text_color=cor,
        )
        self._lbl.pack(anchor="w", pady=(8, 0))

    def set(self, valor):
        self._lbl.configure(text=str(valor))
