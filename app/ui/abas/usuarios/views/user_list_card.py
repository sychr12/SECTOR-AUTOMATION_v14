# -*- coding: utf-8 -*-
"""
UserListCard — container scrollável com cabeçalho de colunas e estados de UI.

Métodos públicos:
    clear_users()
    show_loading()
    show_no_users_message(message)
    show_error(error_msg)
    add_user_card(user_data, on_select, on_delete)
    disable_user_actions(username)
    enable_user_actions(username)
    scroll_to_top()
"""
import customtkinter as ctk
from app.theme import AppTheme

_VERM  = "#ef4444"
_MUTED = "#64748b"

_COLUNAS = [
    ("👤 Usuário",       130),
    ("🧑🏻 Perfil",        110),
    ("📧 Email",         210),
    ("📅 Último Acesso", 160),
    ("🔄 Status",        110),
    ("⚙️ Ações",         120),
]


class UserListCard(ctk.CTkFrame):

    def __init__(self, master, **kwargs):
        super().__init__(master,
                         fg_color=AppTheme.BG_CARD,
                         corner_radius=16, **kwargs)
        self._user_actions_disabled: set = set()
        self._build()

    # ── Layout ───────────────────────────────────────────────────────────────

    def _build(self):
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=12, pady=12)

        # Cabeçalho de colunas
        hdr = ctk.CTkFrame(content, fg_color=AppTheme.BG_INPUT,
                           corner_radius=12, height=50)
        hdr.pack(fill="x", pady=(0, 12))
        hdr.pack_propagate(False)

        hdr_inner = ctk.CTkFrame(hdr, fg_color="transparent")
        hdr_inner.pack(fill="both", expand=True, padx=16, pady=8)

        for titulo, largura in _COLUNAS:
            col = ctk.CTkFrame(hdr_inner, fg_color="transparent", width=largura)
            col.pack(side="left", fill="y")
            col.pack_propagate(False)
            ctk.CTkLabel(col, text=titulo,
                         font=("Segoe UI", 11, "bold"),
                         text_color=AppTheme.TXT_MAIN,
                         anchor="w").pack(fill="x", padx=8)

        # Container scrollável
        self._scroll = ctk.CTkScrollableFrame(
            content, fg_color="transparent")
        self._scroll.pack(fill="both", expand=True, padx=(0, 4))

    # ── API pública ───────────────────────────────────────────────────────────

    def clear_users(self):
        for w in self._scroll.winfo_children():
            w.destroy()

    def show_loading(self):
        self.clear_users()
        ctk.CTkLabel(self._scroll,
                     text="⏳ Carregando usuários...",
                     font=("Segoe UI", 14),
                     text_color=_MUTED).pack(pady=50)

    def show_no_users_message(self,
                               message="Nenhum usuário encontrado."):
        self.clear_users()
        ctk.CTkLabel(self._scroll,
                     text=f"📭 {message}",
                     font=("Segoe UI", 14),
                     text_color=_MUTED).pack(pady=50)

    def show_error(self, error_msg: str):
        self.clear_users()
        wrap = ctk.CTkFrame(self._scroll, fg_color="transparent")
        wrap.pack(expand=True, pady=50)
        ctk.CTkLabel(wrap, text="❌",
                     font=("Segoe UI", 32),
                     text_color=_VERM).pack()
        ctk.CTkLabel(wrap, text=f"Erro ao carregar:\n{error_msg}",
                     font=("Segoe UI", 12),
                     text_color=_VERM).pack(pady=(10, 0))

    def add_user_card(self, user_data: dict, on_select, on_delete):
        from .user_card import UserCard
        card = UserCard(self._scroll, user_data, on_select, on_delete)
        card.pack(fill="x", pady=2)
        if user_data["username"] in self._user_actions_disabled:
            card.disable_actions()

    def disable_user_actions(self, username: str):
        self._user_actions_disabled.add(username)
        for child in self._scroll.winfo_children():
            if (hasattr(child, "user_data") and
                    child.user_data["username"] == username):
                child.disable_actions()

    def enable_user_actions(self, username: str):
        self._user_actions_disabled.discard(username)
        for child in self._scroll.winfo_children():
            if (hasattr(child, "user_data") and
                    child.user_data["username"] == username):
                child.enable_actions()

    def scroll_to_top(self):
        try:
            self._scroll._parent_canvas.yview_moveto(0)
        except Exception:
            pass