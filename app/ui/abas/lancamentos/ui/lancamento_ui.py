# -*- coding: utf-8 -*-
"""
ui.py — Orquestrador do módulo Lançamento de Processo (PyQt6).

Abas:
  1. Falta Revisar  — processos sem lançado_por
  2. Prontos       — processos com lançado_por
  3. Devoluções    — processos devolvidos pelo módulo Análise
  4. Consulta CPF  — histórico e situação de um CPF
  5. Histórico     — todos os lançamentos registrados
"""

from PyQt6.QtWidgets import QWidget

from app.theme import AppTheme

from ..backend.controller import LancamentoController
from ..backend.services import LancamentoService
from .ui_layout import LancamentoLayout
from .ui_logic import LancamentoLogic
from .ui_events import LancamentoEvents


class LancamentoUI(LancamentoLayout, LancamentoLogic, LancamentoEvents, QWidget):
    """
    View principal do módulo Lançamento.

    A ordem de herança garante que métodos de layout têm prioridade
    sobre lógica e eventos quando há sobreposição de nomes (raro).
    """

    def __init__(self, parent=None, usuario: str = None, usuario_logado=None, conectar_bd=None):
        super().__init__(parent)

        # Compatibilidade com loaders diferentes do menu
        self.usuario = usuario if usuario is not None else usuario_logado

        # Dependências
        self.service = LancamentoService()
        self.controller = LancamentoController(self.usuario)

        # Configuração visual
        self.setStyleSheet(f"background-color: {AppTheme.BG_APP};")

        # Estado da UI
        self._pasta_origem = ""
        self._selecionado = None
        self._linha_sel = None
        self._linha_sel_reg = None
        self._dados_revisar: list = []
        self._dados_renovacao: list = []
        self._dados_inscricao: list = []
        self._dados_prontos: list = []
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
            if hasattr(self, "_nb") and self._nb is not None:
                if hasattr(self._nb, "setCurrentIndex"):
                    self._nb.setCurrentIndex(0)   # índice 0 = Falta Revisar
                elif hasattr(self._nb, "select"):
                    self._nb.select(0)
        except Exception:
            pass

        self._carregar_revisar()
        self._carregar_renovacao()
        self._carregar_inscricao()
        self._atualizar_stats()

    def refresh_devolucao(self):
        """
        Recarrega 'Devoluções' e navega até ela.
        Chamado após processar uma Devolução no módulo Análise.
        """
        try:
            if hasattr(self, "_nb") and self._nb is not None:
                if hasattr(self._nb, "setCurrentIndex"):
                    self._nb.setCurrentIndex(3)   # índice 3 = Devoluções
                elif hasattr(self._nb, "select"):
                    self._nb.select(3)
        except Exception:
            pass

        self._carregar_devolucoes()
        self._atualizar_stats()