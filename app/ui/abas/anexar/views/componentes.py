# -*- coding: utf-8 -*-
"""Componentes reutilizáveis do módulo Anexar."""
import customtkinter as ctk

from .theme import VERM, VERM_H, AZUL, AZUL_H, MUTED, SLATE

# Cores padrão do tema (fallback)
BG_INPUT = "#ffffff"
BG_CARD = "#f1f5f9"
BG_APP = "#f8fafc"
TXT_MAIN = "#0f172a"
BTN_PRIMARY = "#2c6e9e"
BTN_PRIMARY_HOVER = "#1e4a6e"


class StatCard(ctk.CTkFrame):
    """Card de estatística com ícone e valor grande."""

    _ICONS = {
        "total":    "📊",
        "pendente": "⏳",
        "gerado":   "✅",
        "sucesso":  "✨",
        "erro":     "⚠️",
    }

    def __init__(self, master, titulo, valor="0", cor=None, icon_key=None):
        super().__init__(master,
                         fg_color=BG_INPUT,
                         corner_radius=16,
                         border_width=1,
                         border_color=BG_CARD)
        self._cor = cor or TXT_MAIN

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=16, pady=12)

        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x")

        if icon_key and icon_key in self._ICONS:
            ctk.CTkLabel(top, text=self._ICONS[icon_key],
                         font=("Segoe UI", 14),
                         text_color=MUTED).pack(side="left")

        ctk.CTkLabel(top, text=titulo,
                     font=("Segoe UI", 11, "bold"),
                     text_color=MUTED).pack(side="left", padx=(4, 0))

        self._val = ctk.CTkLabel(inner, text=str(valor),
                                 font=("Segoe UI", 28, "bold"),
                                 text_color=self._cor)
        self._val.pack(anchor="w", pady=(8, 0))

    def set(self, valor):
        self._val.configure(text=str(valor))


class CardInfo(ctk.CTkFrame):
    """Card de informação com borda suave e ícone."""

    def __init__(self, master, titulo, conteudo, icon="ℹ️"):
        super().__init__(master, corner_radius=16,
                         fg_color=BG_INPUT,
                         border_width=1, border_color=BG_CARD)

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=14, pady=12)

        header = ctk.CTkFrame(inner, fg_color="transparent")
        header.pack(fill="x")

        ctk.CTkLabel(header, text=icon,
                     font=("Segoe UI", 12),
                     text_color=MUTED).pack(side="left")

        ctk.CTkLabel(header, text=titulo,
                     font=("Segoe UI", 10, "bold"),
                     text_color=MUTED).pack(side="left", padx=(6, 0))

        self._lbl = ctk.CTkLabel(inner, text=conteudo,
                                 font=("Segoe UI", 12, "bold"),
                                 text_color=TXT_MAIN,
                                 wraplength=280, justify="left")
        self._lbl.pack(anchor="w", pady=(8, 0))

    def set(self, texto: str):
        self._lbl.configure(text=texto)


class ActionButton(ctk.CTkButton):
    """Botão de ação com estilo consistente."""

    def __init__(self, master, text, command, primary=False, danger=False, **kwargs):
        if primary:
            fg, hov, tc = BTN_PRIMARY, BTN_PRIMARY_HOVER, "#ffffff"
        elif danger:
            fg, hov, tc = VERM, VERM_H, "#ffffff"
        else:
            fg, hov, tc = BG_INPUT, BG_CARD, TXT_MAIN

        super().__init__(
            master, text=text, command=command,
            height=40, corner_radius=12,
            font=("Segoe UI", 12, "bold" if primary else "normal"),
            fg_color=fg, hover_color=hov, text_color=tc,
            **kwargs,
        )


class SearchBar(ctk.CTkFrame):
    """Barra de busca estilizada com callback on_search."""

    def __init__(self, master, placeholder="Buscar...", on_search=None):
        super().__init__(master, fg_color="transparent")
        self._on_search = on_search

        container = ctk.CTkFrame(self, fg_color=BG_INPUT,
                                  corner_radius=12, border_width=1,
                                  border_color=BG_CARD)
        container.pack(fill="x")

        inner = ctk.CTkFrame(container, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=12, pady=8)

        ctk.CTkLabel(inner, text="🔍", font=("Segoe UI", 12),
                     text_color=MUTED).pack(side="left")

        self._entry = ctk.CTkEntry(inner, placeholder_text=placeholder,
                                   fg_color="transparent", border_width=0,
                                   font=("Segoe UI", 11))
        self._entry.pack(side="left", fill="x", expand=True, padx=(8, 0))
        self._entry.bind("<Return>", lambda _e: self._fire())

        if on_search:
            ctk.CTkButton(inner, text="Buscar", width=60, height=28,
                          corner_radius=8, font=("Segoe UI", 10),
                          fg_color=AZUL, hover_color=AZUL_H,
                          command=self._fire).pack(side="right")

    def _fire(self):
        if self._on_search:
            self._on_search(self._entry.get())

    def get(self) -> str:
        return self._entry.get()

    def clear(self):
        self._entry.delete(0, "end")