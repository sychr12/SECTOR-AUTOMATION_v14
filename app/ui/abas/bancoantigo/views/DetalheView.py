# -*- coding: utf-8 -*-
"""
DetalheView — popup somente leitura com todos os campos de um registro.
"""

from datetime import datetime

import customtkinter as ctk
from app.theme import AppTheme

_MUTED = "#64748b"

CAMPOS = [
    ("ID",         "id"),
    ("Nome",       "nome"),
    ("CPF",        "cpf"),
    ("Município",  "unloc"),
    ("Memorando",  "memorando"),
    ("Data",       "datas"),
    ("Análise",    "analise"),
    ("Motivo",     "motivo"),
    ("Envio",      "envio"),
    ("Lançou",     "lancou"),
]


class DetalheView(ctk.CTkToplevel):
    """
    Popup somente leitura que exibe todos os campos de um registro.
    Aceita tanto um dict quanto uma tupla de valores (na ordem de CAMPOS).
    """

    def __init__(self, master, dados):
        super().__init__(master)
        self.title(f"Detalhe — Registro #{self._obter_id(dados)}")
        self.geometry("560x500")
        self.resizable(False, False)
        self.configure(fg_color=AppTheme.BG_APP)
        self.grab_set()
        self.after(0, self._centralizar)
        self._build(dados)

    def _centralizar(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = self.winfo_screenwidth()  // 2 - w // 2
        y = self.winfo_screenheight() // 2 - h // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build(self, dados):
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=28, pady=20)

        ctk.CTkLabel(wrap,
                     text=f"Registro #{self._obter_id(dados)}",
                     font=("Segoe UI", 18, "bold"),
                     text_color=AppTheme.TXT_MAIN).pack(anchor="w",
                                                         pady=(0, 16))

        scroll = ctk.CTkScrollableFrame(
            wrap, fg_color=AppTheme.BG_CARD, corner_radius=14,
            scrollbar_button_color=AppTheme.BG_INPUT)
        scroll.pack(fill="both", expand=True)

        valores = self._normalizar(dados)

        for titulo, valor in valores:
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=5)

            ctk.CTkLabel(row, text=f"{titulo}:",
                         width=110,
                         font=("Segoe UI", 11, "bold"),
                         text_color=_MUTED,
                         anchor="w").pack(side="left")

            ctk.CTkLabel(row,
                         text=self._formatar_valor(valor),
                         font=("Segoe UI", 12),
                         text_color=AppTheme.TXT_MAIN,
                         anchor="w",
                         wraplength=360,
                         justify="left").pack(side="left", fill="x",
                                              expand=True)

        ctk.CTkButton(wrap, text="Fechar",
                      height=40, corner_radius=12,
                      fg_color=AppTheme.BG_INPUT,
                      hover_color=AppTheme.BG_APP,
                      font=("Segoe UI", 12),
                      text_color=AppTheme.TXT_MAIN,
                      command=self.destroy,
                      ).pack(fill="x", pady=(14, 0))

    # ── Helpers ───────────────────────────────────────────────────────────────
    @staticmethod
    def _formatar_valor(valor):
        """Formata valores para exibição, tratando datas e None."""
        if valor is None or valor == "":
            return "—"
        if isinstance(valor, datetime):
            return valor.strftime("%d/%m/%Y %H:%M")
        return str(valor)

    @staticmethod
    def _obter_id(dados) -> str:
        if isinstance(dados, dict):
            return str(dados.get("id", ""))
        if isinstance(dados, (list, tuple)) and dados:
            return str(dados[0])
        return ""

    @staticmethod
    def _normalizar(dados) -> list:
        """Converte dict ou tupla para lista de (titulo, valor)."""
        if isinstance(dados, dict):
            return [(titulo, dados.get(chave, ""))
                    for titulo, chave in CAMPOS]
        # tupla/lista na ordem de CAMPOS
        return [(titulo, dados[i] if i < len(dados) else "")
                for i, (titulo, _) in enumerate(CAMPOS)]