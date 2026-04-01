# -*- coding: utf-8 -*-
"""
ui.py — Orquestrador do módulo Lançamento de Processo.

Abas:
  1. 🔴 Falta Revisar  — processos sem lançado_por
  2. ✅ Prontos         — processos com lançado_por
  3. 📤 Devoluções      — processos devolvidos pelo módulo Análise
  4. 🔍 Consulta CPF   — histórico e situação de um CPF
  5. 📋 Histórico       — todos os lançamentos registrados
"""
import customtkinter as ctk

from app.theme import AppTheme
from ui.base_ui import BaseUI

from ..backend.controller import LancamentoController
from ..backend.services  import LancamentoService
from .ui_layout  import LancamentoLayout
from .ui_logic   import LancamentoLogic
from .ui_events  import LancamentoEvents


class LancamentoUI(LancamentoLayout, LancamentoLogic, LancamentoEvents, BaseUI):
    """
    View principal do módulo Lançamento.

    A ordem de herança garante que métodos de layout têm prioridade
    sobre lógica e eventos quando há sobreposição de nomes (raro).
    """

    def __init__(self, master, usuario: str):
        super().__init__(master)

        # Dependências
        self.usuario    = usuario
        self.service    = LancamentoService()
        self.controller = LancamentoController(usuario)

        # Configuração visual
        self.configure(fg_color=AppTheme.BG_APP)
        self.pack(fill="both", expand=True)

        # Estado da UI
        self._pasta_origem      = ""
        self._selecionado       = None
        self._linha_sel         = None
        self._linha_sel_reg     = None
        self._dados_revisar:    list = []
        self._dados_prontos:    list = []
        self._dados_devolucoes: list = []

        # Construção e carga inicial
        self._build()
        self._atualizar_stats()
        self._carregar_revisar()

    # ------------------------------------------------------------------
    # Callbacks públicos — chamados pelo módulo Análise
    # ------------------------------------------------------------------
    def refresh_lancamento(self):
        """
        Recarrega 'Falta Revisar' e navega até ela.
        Chamado após processar Inscrição ou Renovação no módulo Análise.
        """
        try:
            if hasattr(self, "_nb") and self._nb.winfo_exists():
                self._nb.select(0)   # índice 0 = Falta Revisar
        except Exception:
            pass
        self._carregar_revisar()
        self._atualizar_stats()

    def refresh_devolucao(self):
        """
        Recarrega 'Devoluções' e navega até ela.
        Chamado após processar uma Devolução no módulo Análise.
        """
        try:
            if hasattr(self, "_nb") and self._nb.winfo_exists():
                self._nb.select(2)   # índice 2 = Devoluções
        except Exception:
            pass
        self._carregar_devolucoes()
        self._atualizar_stats()