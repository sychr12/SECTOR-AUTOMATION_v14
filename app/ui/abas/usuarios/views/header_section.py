# -*- coding: utf-8 -*-
"""
HeaderSection — cabeçalho com título e subtítulo.
"""

import customtkinter as ctk
from app.theme import AppTheme


class HeaderSection(ctk.CTkFrame):
    """Seção de cabeçalho com título e subtítulo opcionais."""

    def __init__(self, master, title, subtitle="", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._title    = title
        self._subtitle = subtitle
        self._build()

    def _build(self):
        ctk.CTkLabel(
            self,
            text=self._title,
            font=("Segoe UI", 24, "bold"),
            text_color=AppTheme.TXT_MAIN,
        ).pack(anchor="w")

        if self._subtitle:
            ctk.CTkLabel(
                self,
                text=self._subtitle,
                font=("Segoe UI", 13),
                text_color=AppTheme.TXT_MUTED,
            ).pack(anchor="w", pady=(4, 0))