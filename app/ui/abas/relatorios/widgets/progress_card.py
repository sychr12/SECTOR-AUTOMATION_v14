# -*- coding: utf-8 -*-
"""Card de progresso"""
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import *


class ProgressCard(ctk.CTkFrame):
    """Card para exibir progresso de execução"""
    
    def __init__(self, master, icons=None):
        super().__init__(
            master, fg_color="#f5f7fc", corner_radius=12,
            border_width=1, border_color="#e2e8f0",
        )
        self.icons = icons
        
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(12, 4))
        
        # Ícone
        if icons and icons.get("settings"):
            ctk.CTkLabel(
                row, text="", image=icons["settings"],
                width=20, height=20
            ).pack(side="left", padx=(0, 8))
        
        self._lbl_nome = ctk.CTkLabel(
            row, text="Aguardando início...",
            font=("Segoe UI", 12, "bold"),
            text_color="#64748b", anchor="w",
        )
        self._lbl_nome.pack(side="left", fill="x", expand=True)

        self._lbl_pct = ctk.CTkLabel(
            row, text="", font=("Segoe UI", 11),
            text_color="#64748b", width=50, anchor="e",
        )
        self._lbl_pct.pack(side="right")

        self._bar = ctk.CTkProgressBar(
            self, height=8, corner_radius=4,
            fg_color="#e2e8f0", progress_color="#10b981",
        )
        self._bar.set(0)
        self._bar.pack(fill="x", padx=16, pady=(0, 12))

    def update(self, atual: int, total: int, nome: str):
        pct = atual / total if total else 0
        self._bar.set(pct)
        self._lbl_nome.configure(text=f"Processando: {nome}",
                                 text_color="#1e2f3e")
        self._lbl_pct.configure(text=f"{atual}/{total}",
                                text_color="#10b981")

    def reset(self):
        self._bar.set(0)
        self._lbl_nome.configure(text="Aguardando início...", text_color="#64748b")
        self._lbl_pct.configure(text="")

    def concluido(self):
        self._bar.set(1)
        self._lbl_nome.configure(text="✓  Concluído com sucesso!",
                                 text_color="#10b981")
        self._lbl_pct.configure(text="100%", text_color="#10b981")

    def erro(self):
        self._bar.configure(progress_color="#ef4444")
        self._lbl_nome.configure(text="✕  Erro durante a geração",
                                 text_color="#ef4444")
