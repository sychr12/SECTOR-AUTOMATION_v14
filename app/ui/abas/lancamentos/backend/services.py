# -*- coding: utf-8 -*-
"""
Camada de serviço do módulo Lançamento de Processo.

Centraliza a lógica de negócio que não pertence ao controller
(ex: listagem para histórico, acesso ao binário do PDF).
"""
from typing import Optional

from .LancamentoRepository import LancamentoRepository


class LancamentoService:
    """Serviço de lançamentos — usa o repositório unificado."""

    def __init__(self):
        self.repo = LancamentoRepository()

    def listar_ultimos(self, limite: int = 50) -> list:
        """
        Lista os últimos lançamentos para exibição no histórico.

        Args:
            limite: Quantidade máxima de registros.

        Returns:
            Lista de dicionários com os dados (sem conteúdo binário).
        """
        return self.repo.historico(limit=limite)

    def buscar_pdf_binario(self, lancamento_id: int) -> Optional[dict]:
        """
        Busca o PDF armazenado no banco pelo id do lançamento.

        Args:
            lancamento_id: ID do registro na tabela lancamentos.

        Returns:
            Dicionário com 'pdf_conteudo' (bytes), ou None se não encontrado.
        """
        conteudo = self.repo.buscar_pdf_bytes_por_id(lancamento_id)
        if conteudo:
            return {"pdf_conteudo": conteudo}
        return None