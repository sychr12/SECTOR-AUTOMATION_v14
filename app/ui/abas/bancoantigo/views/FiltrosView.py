# -*- coding: utf-8 -*-
"""
FiltrosView — barra de filtros da aba de consulta.

Filtros disponíveis:
  Linha 1: Busca livre | CPF | Análise | Município | Lançou | [Limpar] [Recarregar]
  Linha 2: Período | Data início | Data fim | Envio | Lançado (sim/não)
"""

from datetime import date

import customtkinter as ctk
from app.theme import AppTheme

_VERDE   = "#22c55e"
_VERDE_H = "#16a34a"
_AZUL    = "#3b82f6"
_AZUL_H  = "#2563eb"
_AMBER   = "#f59e0b"
_MUTED   = "#64748b"


class FiltrosView(ctk.CTkFrame):

    PERIODOS = [
        "TODOS",
        "Hoje",
        "Esta semana",
        "Este mês",
        "Este ano",
        "Personalizado",
    ]

    def __init__(self, master, on_filtrar, on_limpar, on_recarregar, **kwargs):
        super().__init__(master, fg_color=AppTheme.BG_CARD,
                         corner_radius=14, **kwargs)
        self._on_filtrar    = on_filtrar
        self._on_limpar     = on_limpar
        self._on_recarregar = on_recarregar
        self._aplicando_cpf = False
        self._build()

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build(self):
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="x", padx=20, pady=(14, 10))
        self._build_linha1(wrap)
        self._build_linha2(wrap)

    # ── Linha 1 ───────────────────────────────────────────────────────────────
    def _build_linha1(self, parent):
        l1 = ctk.CTkFrame(parent, fg_color="transparent")
        l1.pack(fill="x", pady=(0, 8))

        # Busca livre
        ctk.CTkLabel(l1, text="Buscar:",
                     font=("Segoe UI", 11, "bold"),
                     text_color=_MUTED).pack(side="left", padx=(0, 6))

        self._var_busca = ctk.StringVar()
        self._var_busca.trace_add("write", lambda *_: self._disparar())
        ctk.CTkEntry(
            l1, textvariable=self._var_busca,
            placeholder_text="Nome, memorando, motivo...",
            height=36, corner_radius=10, width=220,
            fg_color=AppTheme.BG_INPUT, border_color=AppTheme.BG_INPUT,
            font=("Segoe UI", 12), text_color=AppTheme.TXT_MAIN,
        ).pack(side="left", padx=(0, 14))

        # CPF (com máscara automática)
        ctk.CTkLabel(l1, text="CPF:",
                     font=("Segoe UI", 11, "bold"),
                     text_color=_MUTED).pack(side="left", padx=(0, 6))

        self._var_cpf = ctk.StringVar()
        self._var_cpf.trace_add("write", self._on_cpf_write)
        self._entry_cpf = ctk.CTkEntry(
            l1, textvariable=self._var_cpf,
            placeholder_text="000.000.000-00",
            height=36, corner_radius=10, width=140,
            fg_color=AppTheme.BG_INPUT, border_color=AppTheme.BG_INPUT,
            font=("Segoe UI", 12), text_color=AppTheme.TXT_MAIN,
        )
        self._entry_cpf.pack(side="left", padx=(0, 14))

        # Análise
        ctk.CTkLabel(l1, text="Análise:",
                     font=("Segoe UI", 11, "bold"),
                     text_color=_MUTED).pack(side="left", padx=(0, 6))

        self._var_analise = ctk.StringVar(value="TODOS")
        ctk.CTkComboBox(
            l1,
            values=["TODOS", "INSC", "RENOV", "DEV"],
            variable=self._var_analise,
            width=120, height=36, corner_radius=10,
            font=("Segoe UI", 12),
            fg_color=AppTheme.BG_INPUT, border_color=AppTheme.BG_INPUT,
            button_color=_VERDE, button_hover_color=_VERDE_H,
            text_color=AppTheme.TXT_MAIN,
            dropdown_fg_color=AppTheme.BG_CARD,
            dropdown_text_color=AppTheme.TXT_MAIN,
            command=lambda _: self._disparar(),
        ).pack(side="left", padx=(0, 14))

        # Município
        ctk.CTkLabel(l1, text="Município:",
                     font=("Segoe UI", 11, "bold"),
                     text_color=_MUTED).pack(side="left", padx=(0, 6))

        self._var_municipio = ctk.StringVar(value="TODOS")
        self._combo_municipio = ctk.CTkComboBox(
            l1,
            values=["TODOS"],
            variable=self._var_municipio,
            width=180, height=36, corner_radius=10,
            font=("Segoe UI", 12),
            fg_color=AppTheme.BG_INPUT, border_color=AppTheme.BG_INPUT,
            button_color=_VERDE, button_hover_color=_VERDE_H,
            text_color=AppTheme.TXT_MAIN,
            dropdown_fg_color=AppTheme.BG_CARD,
            dropdown_text_color=AppTheme.TXT_MAIN,
            command=lambda _: self._disparar(),
        )
        self._combo_municipio.pack(side="left", padx=(0, 14))

        # Lançou
        ctk.CTkLabel(l1, text="Lançou:",
                     font=("Segoe UI", 11, "bold"),
                     text_color=_MUTED).pack(side="left", padx=(0, 6))

        self._var_lancou = ctk.StringVar()
        self._var_lancou.trace_add("write", lambda *_: self._disparar())
        ctk.CTkEntry(
            l1, textvariable=self._var_lancou,
            placeholder_text="Nome do analista...",
            height=36, corner_radius=10, width=150,
            fg_color=AppTheme.BG_INPUT, border_color=AppTheme.BG_INPUT,
            font=("Segoe UI", 12), text_color=AppTheme.TXT_MAIN,
        ).pack(side="left")

        # Botões à direita
        ctk.CTkButton(
            l1, text="↺  Recarregar",
            width=130, height=36, corner_radius=10,
            fg_color=_AZUL, hover_color=_AZUL_H,
            font=("Segoe UI", 11), text_color="#fff",
            command=self._on_recarregar,
        ).pack(side="right")

        ctk.CTkButton(
            l1, text="Limpar",
            width=90, height=36, corner_radius=10,
            fg_color=AppTheme.BG_INPUT, hover_color=AppTheme.BG_APP,
            font=("Segoe UI", 11), text_color=_MUTED,
            command=self._limpar,
        ).pack(side="right", padx=(0, 8))

    # ── Linha 2 ───────────────────────────────────────────────────────────────
    def _build_linha2(self, parent):
        l2 = ctk.CTkFrame(parent, fg_color="transparent")
        l2.pack(fill="x")

        # Período
        ctk.CTkLabel(l2, text="Período:",
                     font=("Segoe UI", 11, "bold"),
                     text_color=_MUTED).pack(side="left", padx=(0, 6))

        self._var_periodo = ctk.StringVar(value="TODOS")
        ctk.CTkComboBox(
            l2,
            values=self.PERIODOS,
            variable=self._var_periodo,
            width=160, height=36, corner_radius=10,
            font=("Segoe UI", 12),
            fg_color=AppTheme.BG_INPUT, border_color=AppTheme.BG_INPUT,
            button_color=_AMBER, button_hover_color="#d97706",
            text_color=AppTheme.TXT_MAIN,
            dropdown_fg_color=AppTheme.BG_CARD,
            dropdown_text_color=AppTheme.TXT_MAIN,
            command=self._on_periodo_change,
        ).pack(side="left", padx=(0, 12))

        # Data início
        ctk.CTkLabel(l2, text="De:",
                     font=("Segoe UI", 11, "bold"),
                     text_color=_MUTED).pack(side="left", padx=(0, 4))

        self._var_data_ini = ctk.StringVar()
        self._var_data_ini.trace_add("write", lambda *_: self._disparar())
        self._entry_data_ini = ctk.CTkEntry(
            l2, textvariable=self._var_data_ini,
            placeholder_text="dd/mm/aaaa",
            height=36, corner_radius=10, width=110,
            fg_color=AppTheme.BG_INPUT, border_color=AppTheme.BG_INPUT,
            font=("Segoe UI", 12), text_color=AppTheme.TXT_MAIN,
            state="disabled",
        )
        self._entry_data_ini.pack(side="left", padx=(0, 8))
        self._entry_data_ini.bind(
            "<KeyRelease>",
            lambda _: self._fmt_data(self._entry_data_ini, self._var_data_ini))

        # Data fim
        ctk.CTkLabel(l2, text="Até:",
                     font=("Segoe UI", 11, "bold"),
                     text_color=_MUTED).pack(side="left", padx=(0, 4))

        self._var_data_fim = ctk.StringVar()
        self._var_data_fim.trace_add("write", lambda *_: self._disparar())
        self._entry_data_fim = ctk.CTkEntry(
            l2, textvariable=self._var_data_fim,
            placeholder_text="dd/mm/aaaa",
            height=36, corner_radius=10, width=110,
            fg_color=AppTheme.BG_INPUT, border_color=AppTheme.BG_INPUT,
            font=("Segoe UI", 12), text_color=AppTheme.TXT_MAIN,
            state="disabled",
        )
        self._entry_data_fim.pack(side="left", padx=(0, 20))
        self._entry_data_fim.bind(
            "<KeyRelease>",
            lambda _: self._fmt_data(self._entry_data_fim, self._var_data_fim))

        # Envio
        ctk.CTkLabel(l2, text="Envio:",
                     font=("Segoe UI", 11, "bold"),
                     text_color=_MUTED).pack(side="left", padx=(0, 6))

        self._var_envio = ctk.StringVar(value="TODOS")
        ctk.CTkComboBox(
            l2,
            values=["TODOS", "Com envio", "Sem envio"],
            variable=self._var_envio,
            width=140, height=36, corner_radius=10,
            font=("Segoe UI", 12),
            fg_color=AppTheme.BG_INPUT, border_color=AppTheme.BG_INPUT,
            button_color=_VERDE, button_hover_color=_VERDE_H,
            text_color=AppTheme.TXT_MAIN,
            dropdown_fg_color=AppTheme.BG_CARD,
            dropdown_text_color=AppTheme.TXT_MAIN,
            command=lambda _: self._disparar(),
        ).pack(side="left", padx=(0, 16))

        # Lançado
        ctk.CTkLabel(l2, text="Lançado:",
                     font=("Segoe UI", 11, "bold"),
                     text_color=_MUTED).pack(side="left", padx=(0, 6))

        self._var_lancado = ctk.StringVar(value="TODOS")
        ctk.CTkComboBox(
            l2,
            values=["TODOS", "Sim", "Não"],
            variable=self._var_lancado,
            width=110, height=36, corner_radius=10,
            font=("Segoe UI", 12),
            fg_color=AppTheme.BG_INPUT, border_color=AppTheme.BG_INPUT,
            button_color=_VERDE, button_hover_color=_VERDE_H,
            text_color=AppTheme.TXT_MAIN,
            dropdown_fg_color=AppTheme.BG_CARD,
            dropdown_text_color=AppTheme.TXT_MAIN,
            command=lambda _: self._disparar(),
        ).pack(side="left")

    # ── Máscara CPF ───────────────────────────────────────────────────────────
    def _on_cpf_write(self, *_):
        if self._aplicando_cpf:
            return
        self._aplicando_cpf = True
        try:
            t = self._var_cpf.get()
            d = "".join(c for c in t if c.isdigit())[:11]
            if   len(d) <= 3: r = d
            elif len(d) <= 6: r = f"{d[:3]}.{d[3:]}"
            elif len(d) <= 9: r = f"{d[:3]}.{d[3:6]}.{d[6:]}"
            else:             r = f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"
            if r != t:
                self._var_cpf.set(r)
                self._entry_cpf.after(0,
                    lambda: self._entry_cpf.icursor("end"))
        finally:
            self._aplicando_cpf = False
        self._disparar()

    # ── Período ───────────────────────────────────────────────────────────────
    def _on_periodo_change(self, valor):
        personalizado = (valor == "Personalizado")
        estado = "normal" if personalizado else "disabled"
        self._entry_data_ini.configure(state=estado)
        self._entry_data_fim.configure(state=estado)
        if not personalizado:
            self._var_data_ini.set("")
            self._var_data_fim.set("")
        self._disparar()

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _disparar(self):
        self._on_filtrar(self.obter_valores())

    def _limpar(self):
        self._var_busca.set("")
        self._var_cpf.set("")
        self._var_analise.set("TODOS")
        self._var_municipio.set("TODOS")
        self._var_lancou.set("")
        self._var_periodo.set("TODOS")
        self._var_data_ini.set("")
        self._var_data_fim.set("")
        self._var_envio.set("TODOS")
        self._var_lancado.set("TODOS")
        self._entry_data_ini.configure(state="disabled")
        self._entry_data_fim.configure(state="disabled")
        self._on_limpar()

    @staticmethod
    def _fmt_data(entry, var):
        try:
            t = var.get()
            d = "".join(c for c in t if c.isdigit())[:8]
            if   len(d) <= 2: r = d
            elif len(d) <= 4: r = f"{d[:2]}/{d[2:]}"
            else:             r = f"{d[:2]}/{d[2:4]}/{d[4:]}"
            if r != t:
                var.set(r)
                entry.after(0, lambda: entry.icursor("end"))
        except Exception:
            pass

    # ── API pública ───────────────────────────────────────────────────────────
    def popular_municipios(self, municipios: list):
        self._combo_municipio.configure(values=["TODOS"] + municipios)

    def obter_valores(self) -> dict:
        return {
            "busca":     self._var_busca.get().strip(),
            "cpf":       self._var_cpf.get().strip(),
            "analise":   self._var_analise.get(),
            "municipio": self._var_municipio.get(),
            "lancou":    self._var_lancou.get().strip(),
            "periodo":   self._var_periodo.get(),
            "data_ini":  self._var_data_ini.get().strip(),
            "data_fim":  self._var_data_fim.get().strip(),
            "envio":     self._var_envio.get(),
            "lancado":   self._var_lancado.get(),
        }