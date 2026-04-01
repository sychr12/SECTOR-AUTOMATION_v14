# -*- coding: utf-8 -*-
import customtkinter as ctk
from app.theme import AppTheme

_VERDE  = "#22c55e"
_AZUL   = "#3b82f6"
_AZUL_H = "#2563eb"
_VERM   = "#ef4444"
_VERM_H = "#b91c1c"
_AMBER  = "#f59e0b"
_CYAN   = "#06b6d4"
_PURPLE = "#8b5cf6"
_MUTED  = "#64748b"

# Perfis atualizados
_PERFIL_CORES = {
    "administrador": _PURPLE,
    "chefe":         _AMBER,
    "usuario":       _CYAN,
}
_PERFIL_ICONS = {
    "administrador": "👑",
    "chefe":         "⭐",
    "usuario":       "👤",
}


class UserCard(ctk.CTkFrame):
    """Linha de usuário compacta — altura fixa 52px."""

    def __init__(self, master, user_data: dict,
                 on_select=None, on_delete=None):
        super().__init__(
            master,
            fg_color=AppTheme.BG_CARD,
            corner_radius=8,
            border_width=1,
            border_color=AppTheme.BORDER,
            height=52,
        )
        self.pack_propagate(False)
        self.user_data = user_data
        self.on_select = on_select
        self.on_delete = on_delete
        self._disabled = False
        self._build()
        self.bind("<Enter>",    self._on_enter)
        self.bind("<Leave>",    self._on_leave)
        self.bind("<Button-1>", lambda e: self._on_select())

    def _build(self):
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="both", expand=True, padx=12)

        # Usuário
        w = ctk.CTkLabel(
            self._col(row, 130),
            text=f"👤 {self.user_data.get('username', '?')}",
            font=("Segoe UI", 12, "bold"),
            text_color=AppTheme.TXT_MAIN, anchor="w")
        w.pack(fill="x", padx=6)
        self._bind_hover(w)

        # Perfil badge
        perfil = self.user_data.get("perfil", "").lower()
        cor    = _PERFIL_CORES.get(perfil, _MUTED)
        icon   = _PERFIL_ICONS.get(perfil, "👤")
        col2   = self._col(row, 110)
        badge  = ctk.CTkFrame(col2, fg_color=cor, corner_radius=6, height=26)
        badge.pack(anchor="w", padx=6)
        badge.pack_propagate(False)
        lb = ctk.CTkLabel(badge,
                          text=f"{icon} {perfil.upper()}" if perfil else "N/A",
                          font=("Segoe UI", 10, "bold"),
                          text_color="#fff")
        lb.pack(fill="both", expand=True, padx=8)
        self._bind_hover(badge)
        self._bind_hover(lb)

        # Email
        w3 = ctk.CTkLabel(
            self._col(row, 210),
            text=self.user_data.get("email") or "—",
            font=("Segoe UI", 11),
            text_color=AppTheme.TXT_MUTED, anchor="w")
        w3.pack(fill="x", padx=6)
        self._bind_hover(w3)

        # Último acesso
        w4 = ctk.CTkLabel(
            self._col(row, 160),
            text=f"🕐 {self.user_data.get('ultimo_acesso_fmt', 'Nunca')}",
            font=("Segoe UI", 10),
            text_color=AppTheme.TXT_MUTED, anchor="w")
        w4.pack(fill="x", padx=6)
        self._bind_hover(w4)

        # Status
        ativo = self.user_data.get("ativo", False)
        w5 = ctk.CTkLabel(
            self._col(row, 110),
            text="🟢 Ativo" if ativo else "🔴 Inativo",
            font=("Segoe UI", 10, "bold"),
            text_color=_VERDE if ativo else _VERM, anchor="w")
        w5.pack(fill="x", padx=6)
        self._bind_hover(w5)

        # Botões
        btn_col = self._col(row, 120)
        btn_row = ctk.CTkFrame(btn_col, fg_color="transparent")
        btn_row.place(relx=0.5, rely=0.5, anchor="center")

        self._btn_edit = ctk.CTkButton(
            btn_row, text="✏️", command=self._on_select,
            width=36, height=30, corner_radius=6,
            fg_color=_AZUL, hover_color=_AZUL_H,
            font=("Segoe UI", 11))
        self._btn_edit.pack(side="left", padx=(0, 4))

        self._btn_del = ctk.CTkButton(
            btn_row, text="🗑️", command=self._on_delete,
            width=36, height=30, corner_radius=6,
            fg_color=_VERM, hover_color=_VERM_H,
            font=("Segoe UI", 11))
        self._btn_del.pack(side="left")

    @staticmethod
    def _col(parent, width):
        f = ctk.CTkFrame(parent, fg_color="transparent", width=width)
        f.pack(side="left", fill="y")
        f.pack_propagate(False)
        return f

    def _bind_hover(self, widget):
        widget.bind("<Enter>",    self._on_enter, add="+")
        widget.bind("<Leave>",    self._on_leave, add="+")
        widget.bind("<Button-1>", lambda e: self._on_select(), add="+")

    def _on_enter(self, _=None):
        if not self._disabled:
            self.configure(border_color=_AZUL, fg_color=AppTheme.BG_INPUT)

    def _on_leave(self, _=None):
        if not self._disabled:
            self.configure(border_color=AppTheme.BORDER, fg_color=AppTheme.BG_CARD)

    def disable_actions(self):
        self._disabled = True
        self._btn_edit.configure(state="disabled")
        self._btn_del.configure(state="disabled")
        self.configure(border_color=_MUTED)

    def enable_actions(self):
        self._disabled = False
        self._btn_edit.configure(state="normal")
        self._btn_del.configure(state="normal")
        self.configure(border_color=AppTheme.BORDER)

    def _on_select(self):
        if not self._disabled and self.on_select:
            self.on_select(self.user_data)

    def _on_delete(self):
        if not self._disabled and self.on_delete:
            self.on_delete(self.user_data)