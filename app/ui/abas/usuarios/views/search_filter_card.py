# -*- coding: utf-8 -*-
import customtkinter as ctk
from app.theme import AppTheme

_VERDE  = "#22c55e"
_VERDE_H = "#16a34a"


class SearchFilterCard(ctk.CTkFrame):

    def __init__(self, master, on_search=None, on_new_user=None, **kwargs):
        super().__init__(master,
                         fg_color=AppTheme.BG_CARD,
                         corner_radius=16, **kwargs)
        self._on_search   = on_search
        self._on_new_user = on_new_user
        self._build()

    def _build(self):
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="x", padx=16, pady=14)

        ctk.CTkLabel(content,
                     text="🔍 Buscar e Filtrar Usuários",
                     font=("Segoe UI", 14, "bold"),
                     text_color=AppTheme.TXT_MAIN,
                     ).pack(anchor="w", pady=(0, 10))

        row = ctk.CTkFrame(content, fg_color="transparent")
        row.pack(fill="x")

        ctk.CTkLabel(row, text="Buscar:",
                     font=("Segoe UI", 12),
                     text_color=AppTheme.TXT_MUTED,
                     ).pack(side="left", padx=(0, 8))

        self._entry_search = ctk.CTkEntry(
            row,
            placeholder_text="Digite o nome de usuário...",
            height=40, corner_radius=10,
            font=("Segoe UI", 12),
            fg_color=AppTheme.BG_INPUT,
            border_color=AppTheme.BG_INPUT,
            text_color=AppTheme.TXT_MAIN,
        )
        self._entry_search.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._entry_search.bind("<Return>",
                                lambda _: self._on_search and self._on_search())

        if self._on_search:
            ctk.CTkButton(
                row, text="🔍 Buscar",
                command=self._on_search,
                height=40, width=100, corner_radius=10,
                font=("Segoe UI", 12),
                fg_color=AppTheme.BTN_PRIMARY,
                hover_color=AppTheme.BTN_PRIMARY_HOVER,
            ).pack(side="left", padx=(0, 16))

        ctk.CTkLabel(row, text="Perfil:",
                     font=("Segoe UI", 12),
                     text_color=AppTheme.TXT_MUTED,
                     ).pack(side="left", padx=(0, 8))

        # Perfis atualizados: "usuario" no lugar de "analista"
        self._combo_profile = ctk.CTkComboBox(
            row,
            values=["Todos", "administrador", "chefe", "usuario"],
            width=150, height=40, corner_radius=10,
            font=("Segoe UI", 12),
            fg_color=AppTheme.BG_INPUT,
            border_color=AppTheme.BG_INPUT,
            button_color=_VERDE,
            button_hover_color=_VERDE_H,
            text_color=AppTheme.TXT_MAIN,
            dropdown_fg_color=AppTheme.BG_CARD,
            dropdown_text_color=AppTheme.TXT_MAIN,
        )
        self._combo_profile.set("Todos")
        self._combo_profile.pack(side="left", padx=(0, 16))

        ctk.CTkLabel(row, text="Status:",
                     font=("Segoe UI", 12),
                     text_color=AppTheme.TXT_MUTED,
                     ).pack(side="left", padx=(0, 8))

        self._combo_status = ctk.CTkComboBox(
            row,
            values=["Todos", "Ativo", "Inativo"],
            width=120, height=40, corner_radius=10,
            font=("Segoe UI", 12),
            fg_color=AppTheme.BG_INPUT,
            border_color=AppTheme.BG_INPUT,
            button_color=_VERDE,
            button_hover_color=_VERDE_H,
            text_color=AppTheme.TXT_MAIN,
            dropdown_fg_color=AppTheme.BG_CARD,
            dropdown_text_color=AppTheme.TXT_MAIN,
        )
        self._combo_status.set("Todos")
        self._combo_status.pack(side="left")

        if self._on_new_user:
            ctk.CTkButton(
                row, text="➕ Novo Usuário",
                command=self._on_new_user,
                height=40, corner_radius=10,
                font=("Segoe UI", 12, "bold"),
                fg_color=AppTheme.BTN_SUCCESS,
                hover_color=AppTheme.BTN_SUCCESS_HOVER,
            ).pack(side="right", padx=(16, 0))

    def get_search_text(self) -> str:
        return self._entry_search.get().strip()

    def get_selected_profile(self) -> str:
        return self._combo_profile.get()

    def get_selected_status(self) -> str:
        return self._combo_status.get()