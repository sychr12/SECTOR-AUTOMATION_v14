# -*- coding: utf-8 -*-
"""Linha de seleção de pasta"""
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import *


class PastaRow(ctk.CTkFrame):
    """Linha compacta para exibir e alterar uma pasta."""

    def __init__(self, parent, label: str, path: str, command, icons=None):
        super().__init__(
            parent, fg_color="#f5f7fc", corner_radius=8,
            border_width=1, border_color="#e2e8f0",
        )
        self.icons = icons
        
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="x", padx=10, pady=8)
        
        # Ícone
        if icons and icons.get("paste"):
            ctk.CTkLabel(
                inner, text="", image=icons["paste"],
                width=20, height=20
            ).pack(side="left", padx=(0, 8))
        
        ctk.CTkLabel(
            inner, text=label, font=("Segoe UI", 11, "bold"),
            text_color="#64748b", width=70, anchor="w",
        ).pack(side="left")
        
        self._lbl = ctk.CTkLabel(
            inner, text=self._trunc(path),
            font=("Segoe UI", 10), text_color="#1e2f3e", anchor="w",
        )
        self._lbl.pack(side="left", fill="x", expand=True, padx=(8, 0))
        
        ctk.CTkButton(
            inner, text="📂", width=30, height=28, corner_radius=6,
            fg_color="#d1fae5", hover_color="#e2e8f0",
            text_color="#10b981", font=("Segoe UI", 12, "bold"),
            command=command,
        ).pack(side="right")

    def set_path(self, path: str):
        self._lbl.configure(text=self._trunc(path))

    @staticmethod
    def _trunc(p: str, n: int = 40) -> str:
        return f"…{p[-(n-1):]}" if len(p) > n else p
