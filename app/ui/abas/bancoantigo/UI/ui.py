# -*- coding: utf-8 -*-
"""
ConsultaBancoUI — frame principal de consulta ao banco CPP (somente leitura).
Pertence ao módulo bancoantigo (app/ui/abas/bancoantigo/ui.py).
"""

import threading

import customtkinter as ctk
from tkinter import messagebox

from app.theme import AppTheme
from ..backend.controller import ConsultaBancoController
from ..views import FiltrosView, TabelaView, DetalheView

_MUTED  = "#64748b"
_AZUL   = "#3b82f6"
_AZUL_H = "#2563eb"


class ConsultaBancoUI(ctk.CTkFrame):

    def __init__(self, master, usuario=None, **kwargs):
        super().__init__(master, fg_color=AppTheme.BG_APP, **kwargs)
        self.usuario     = usuario
        self.controller  = ConsultaBancoController()
        self._carregando = False
        self._build()
        self._carregar()

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build(self):
        # ── Cabeçalho ─────────────────────────────────────────────────────────
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=32, pady=(24, 0))

        col_esq = ctk.CTkFrame(hdr, fg_color="transparent")
        col_esq.pack(side="left", fill="y")

        ctk.CTkLabel(
            col_esq,
            text="Consulta ao Banco CPP",
            font=("Segoe UI", 24, "bold"),
            text_color=AppTheme.TXT_MAIN,
        ).pack(anchor="w")

        ctk.CTkLabel(
            col_esq,
            text="Visualização somente leitura · MySQL legado",
            font=("Segoe UI", 11),
            text_color=_MUTED,
        ).pack(anchor="w", pady=(2, 0))

        col_dir = ctk.CTkFrame(hdr, fg_color="transparent")
        col_dir.pack(side="right", fill="y")

        # Badge "somente leitura" visível
        badge = ctk.CTkFrame(col_dir, fg_color="#1e293b", corner_radius=8)
        badge.pack(anchor="e")
        ctk.CTkLabel(
            badge,
            text="🔒  Somente leitura",
            font=("Segoe UI", 10, "bold"),
            text_color=_MUTED,
        ).pack(padx=12, pady=6)

        self._lbl_total = ctk.CTkLabel(
            col_dir,
            text="",
            font=("Segoe UI", 12),
            text_color=_MUTED,
        )
        self._lbl_total.pack(anchor="e", pady=(6, 0))

        # ── Divisor ───────────────────────────────────────────────────────────
        ctk.CTkFrame(self, height=1, fg_color=AppTheme.BG_CARD).pack(
            fill="x", padx=32, pady=(16, 0)
        )

        # ── Filtros ───────────────────────────────────────────────────────────
        self._filtros = FiltrosView(
            self,
            on_filtrar    = self._on_filtrar,
            on_limpar     = self._on_limpar,
            on_recarregar = self._carregar,
        )
        self._filtros.pack(fill="x", padx=32, pady=(16, 0))

        # ── Tabela ────────────────────────────────────────────────────────────
        self._tabela = TabelaView(
            self,
            on_ordenar      = self._on_ordenar,
            on_duplo_clique = self._on_duplo_clique,
            on_primeira     = self._on_primeira,
            on_anterior     = self._on_anterior,
            on_proxima      = self._on_proxima,
            on_ultima       = self._on_ultima,
        )
        self._tabela.pack(fill="both", expand=True, padx=32, pady=(16, 20))

    # ── Carregamento ──────────────────────────────────────────────────────────
    def _carregar(self):
        if self._carregando:
            return
        self._carregando = True
        self._lbl_total.configure(text="Conectando ao banco...")
        threading.Thread(target=self._worker_carregar, daemon=True).start()

    def _worker_carregar(self):
        try:
            dados      = self.controller.carregar()
            municipios = self.controller.carregar_municipios()
            self.after(0, self._on_carregado, dados, municipios)
        except Exception as exc:
            self.after(0, self._on_erro, str(exc))
        finally:
            self._carregando = False

    def _on_carregado(self, dados: list, municipios: list):
        self._filtros.popular_municipios(municipios)
        info = self.controller.filtrar(self._filtros.obter_valores())
        self._tabela.renderizar(info)
        self._atualizar_lbl_total(info)

    def _on_erro(self, msg: str):
        self._lbl_total.configure(text="Erro ao conectar")
        messagebox.showerror(
            "Erro de Conexão",
            f"Não foi possível conectar ao banco:\n\n{msg}",
        )

    # ── Callbacks de filtros ──────────────────────────────────────────────────
    def _on_filtrar(self, filtros: dict):
        info = self.controller.filtrar(filtros)
        self._tabela.renderizar(info)
        self._atualizar_lbl_total(info)

    def _on_limpar(self):
        info = self.controller.filtrar({})
        self._tabela.renderizar(info)
        self._atualizar_lbl_total(info)

    # ── Callbacks de tabela ───────────────────────────────────────────────────
    def _on_ordenar(self, coluna: str):
        info = self.controller.ordenar(coluna)
        self._tabela.renderizar(info)

    def _on_duplo_clique(self, valores: tuple):
        DetalheView(self, valores)

    # ── Callbacks de paginação ────────────────────────────────────────────────
    def _on_primeira(self):
        self._tabela.renderizar(self.controller.primeira_pagina())

    def _on_anterior(self):
        self._tabela.renderizar(self.controller.pagina_anterior())

    def _on_proxima(self):
        self._tabela.renderizar(self.controller.proxima_pagina())

    def _on_ultima(self):
        self._tabela.renderizar(self.controller.ultima_pagina())

    # ── Label total ───────────────────────────────────────────────────────────
    def _atualizar_lbl_total(self, info: dict):
        total    = self.controller.total_banco()
        filtrado = info["total_filtrado"]
        self._lbl_total.configure(
            text=f"Total no banco: {total:,}  |  Exibindo: {filtrado:,}"
        )