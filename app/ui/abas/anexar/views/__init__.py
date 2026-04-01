# -*- coding: utf-8 -*-
"""
Módulo de views do módulo Anexar.
"""

# Importar componentes para facilitar acesso
from .componentes import StatCard, CardInfo, ActionButton, SearchBar
from .tabelas import CarteirasTable, EmAnaliseTable, HistoricoTable, LogTable
from .prontos_view import ProntosView
from .theme import (
    VERDE, VERDE_H, VERDE_T, AZUL, AZUL_H, VERM, VERM_H,
    AMBER, MUTED, INFO, SLATE,
    fmt_data, fmt_data_curta, safe_print,
)

__all__ = [
    "StatCard", "CardInfo", "ActionButton", "SearchBar",
    "CarteirasTable", "EmAnaliseTable", "HistoricoTable", "LogTable",
    "ProntosView",
    "VERDE", "VERDE_H", "VERDE_T", "AZUL", "AZUL_H",
    "VERM", "VERM_H", "AMBER", "MUTED", "INFO", "SLATE",
    "fmt_data", "fmt_data_curta", "safe_print",
]