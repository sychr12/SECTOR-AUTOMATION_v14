# -*- coding: utf-8 -*-
"""
Componentes de UI reutilizáveis para a interface de consulta.
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import *
from app.theme import AppTheme

_VERDE   = "#22c55e"
_VERDE_H = "#16a34a"
_AZUL    = "#3b82f6"
_AZUL_H  = "#2563eb"
_MUTED   = "#64748b"
_AMBER   = "#f59e0b"


class HeaderCard(ctk.CTkFrame):
    """Cabeçalho com título e subtítulo opcionais."""

    def __init__(self, master, title, subtitle="", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        ctk.CTkLabel(self, text=title,
                     font=("Segoe UI", 26, "bold"),
                     text_color=AppTheme.TXT_MAIN).pack(anchor="w")
        if subtitle:
            ctk.CTkLabel(self, text=subtitle,
                         font=("Segoe UI", 13),
                         text_color=_MUTED).pack(anchor="w", pady=(4, 0))

    def pack(self, **kwargs):
        kwargs.setdefault("anchor", "w")
        super().pack(**kwargs)


class FiltrosCard(ctk.CTkFrame):
    """
    Barra de filtros de pesquisa.
    Corrigido: usa pack() internamente em vez de mix pack+grid.
    """

    def __init__(self, master, on_pesquisar=None, **kwargs):
        super().__init__(master,
                         corner_radius=16,
                         fg_color=AppTheme.BG_CARD, **kwargs)
        self._on_pesquisar = on_pesquisar
        self._build()

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build(self):
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="x", padx=20, pady=16)

        ctk.CTkLabel(wrap, text="Filtros de Pesquisa",
                     font=("Segoe UI", 13, "bold"),
                     text_color=AppTheme.TXT_MAIN).pack(anchor="w",
                                                         pady=(0, 12))

        # ── Linha de entradas ─────────────────────────────────────────────────
        linha = ctk.CTkFrame(wrap, fg_color="transparent")
        linha.pack(fill="x")

        def _entry(placeholder, width=170):
            return ctk.CTkEntry(
                linha,
                placeholder_text=placeholder,
                height=38, corner_radius=10, width=width,
                font=("Segoe UI", 12),
                fg_color=AppTheme.BG_INPUT,
                border_color=AppTheme.BG_INPUT,
                text_color=AppTheme.TXT_MAIN,
            )

        self.nome_entry      = _entry("Nome",      190)
        self.cpf_entry       = _entry("CPF",       150)
        self.unloc_entry     = _entry("Município", 170)
        self.memorando_entry = _entry("Memorando", 140)

        for w in (self.nome_entry, self.cpf_entry,
                  self.unloc_entry, self.memorando_entry):
            w.pack(side="left", padx=(0, 8))

        # Período
        self._var_periodo = ctk.StringVar(value="Últimos 30 dias")
        ctk.CTkComboBox(
            linha,
            values=["Todos", "Últimos 30 dias",
                    "2025", "2024", "2023", "2022"],
            variable=self._var_periodo,
            width=160, height=38, corner_radius=10,
            font=("Segoe UI", 12),
            fg_color=AppTheme.BG_INPUT,
            border_color=AppTheme.BG_INPUT,
            button_color=_VERDE,
            button_hover_color=_VERDE_H,
            text_color=AppTheme.TXT_MAIN,
            dropdown_fg_color=AppTheme.BG_CARD,
            dropdown_text_color=AppTheme.TXT_MAIN,
        ).pack(side="left", padx=(0, 8))

        # Botão pesquisar
        self._btn = ctk.CTkButton(
            linha, text="🔍  Pesquisar",
            height=38, corner_radius=10,
            font=("Segoe UI", 12, "bold"),
            fg_color=_AZUL, hover_color=_AZUL_H,
            text_color="#fff",
            command=self._on_pesquisar,
        )
        self._btn.pack(side="left", padx=(0, 8))

        # Botão limpar
        ctk.CTkButton(
            linha, text="Limpar",
            height=38, corner_radius=10,
            font=("Segoe UI", 11),
            fg_color=AppTheme.BG_INPUT,
            hover_color=AppTheme.BG_APP,
            text_color=_MUTED,
            command=self.limpar_filtros,
        ).pack(side="left")

        # ── Barra de progresso ────────────────────────────────────────────────
        self._progress = ctk.CTkProgressBar(
            wrap, mode="indeterminate", height=4,
            fg_color=AppTheme.BG_INPUT,
            progress_color=_AZUL,
        )
        # Não exibida por padrão

    # ── API pública ───────────────────────────────────────────────────────────
    def obter_filtros(self) -> dict:
        return {
            "nome":      self.nome_entry.get(),
            "cpf":       self.cpf_entry.get(),
            "municipio": self.unloc_entry.get(),
            "memorando": self.memorando_entry.get(),
            "periodo":   self._var_periodo.get(),
        }

    def limpar_filtros(self):
        for e in (self.nome_entry, self.cpf_entry,
                  self.unloc_entry, self.memorando_entry):
            e.delete(0, "end")
        self._var_periodo.set("Últimos 30 dias")

    def mostrar_progresso(self):
        self._progress.pack(fill="x", pady=(10, 0))
        self._progress.start()

    def esconder_progresso(self):
        self._progress.stop()
        self._progress.pack_forget()

    def desabilitar_botao(self):
        self._btn.configure(state="disabled")

    def habilitar_botao(self):
        self._btn.configure(state="normal")
