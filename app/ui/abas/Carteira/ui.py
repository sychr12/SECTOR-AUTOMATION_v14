# ui.py
# -*- coding: utf-8 -*-
"""
ui.py — Ponto de entrada da Carteira Digital do Produtor Rural.
Local: app/ui/abas/Carteira/ui.py

BUG CORRIGIDO: este módulo definia uma classe CarteiraDigitalUI duplicada
em paralelo à versão mais completa e refatorada em views/carteira_view.py.
As duas classes coexistiam com o mesmo nome, causando ambiguidade.
Solução: ui.py importa e re-exporta CarteiraDigitalUI de views/carteira_view.py,
que é a implementação canônica.
"""

from .views.carteira_view import CarteiraDigitalUI  # noqa: F401 — re-exportado

__all__ = ["CarteiraDigitalUI"]