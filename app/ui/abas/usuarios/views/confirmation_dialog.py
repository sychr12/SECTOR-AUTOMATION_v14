# -*- coding: utf-8 -*-
"""
ConfirmationDialog — popup modal de confirmação com suporte a tipos de alerta.

Uso:
    dlg = ConfirmationDialog(master, "Título", "Mensagem", type="warning")
    if dlg.show():
        ...  # confirmado
"""

import customtkinter as ctk
from app.theme import AppTheme

_VERDE   = "#22c55e"
_VERDE_H = "#16a34a"
_VERM    = "#ef4444"
_VERM_H  = "#dc2626"
_MUTED   = "#64748b"


class ConfirmationDialog(ctk.CTkToplevel):

    def __init__(self, master, titulo: str, mensagem: str,
                 type: str = "question", **kwargs):
        super().__init__(master, **kwargs)
        self.title(titulo)
        self.geometry("440x230")
        self.resizable(False, False)
        self.configure(fg_color=AppTheme.BG_APP)
        self.grab_set()
        self._resultado = False
        self._build(titulo, mensagem, type)
        self.after(0, self._centralizar)

    def _centralizar(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = self.winfo_screenwidth()  // 2 - w // 2
        y = self.winfo_screenheight() // 2 - h // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build(self, titulo, mensagem, type):
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=28, pady=24)

        icone = {"question": "❓", "warning": "⚠️",
                 "error": "❌", "info": "ℹ️"}.get(type, "❓")

        ctk.CTkLabel(wrap, text=f"{icone}  {titulo}",
                     font=("Segoe UI", 16, "bold"),
                     text_color=AppTheme.TXT_MAIN,
                     ).pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(wrap, text=mensagem,
                     font=("Segoe UI", 12),
                     text_color=_MUTED,
                     wraplength=380, justify="left",
                     ).pack(anchor="w", pady=(0, 20))

        btns = ctk.CTkFrame(wrap, fg_color="transparent")
        btns.pack(fill="x")
        btns.columnconfigure((0, 1), weight=1)

        cor   = _VERM  if type in ("warning", "error") else _VERDE
        cor_h = _VERM_H if type in ("warning", "error") else _VERDE_H

        ctk.CTkButton(
            btns, text="Confirmar",
            height=42, corner_radius=10,
            fg_color=cor, hover_color=cor_h,
            font=("Segoe UI", 12, "bold"), text_color="#fff",
            command=self._confirmar,
        ).grid(row=0, column=0, padx=(0, 6), sticky="ew")

        ctk.CTkButton(
            btns, text="Cancelar",
            height=42, corner_radius=10,
            fg_color=AppTheme.BG_INPUT, hover_color=AppTheme.BG_APP,
            font=("Segoe UI", 12), text_color=AppTheme.TXT_MAIN,
            command=self.destroy,
        ).grid(row=0, column=1, padx=(6, 0), sticky="ew")

    def _confirmar(self):
        self._resultado = True
        self.destroy()

    def show(self) -> bool:
        self.wait_window()
        return self._resultado