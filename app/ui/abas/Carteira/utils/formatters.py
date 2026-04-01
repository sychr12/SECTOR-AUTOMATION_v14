# app/ui/abas/Carteira/utils/formatters.py
# -*- coding: utf-8 -*-
"""
Funções de formatação de dados (CPF, datas, textos)
"""

import re
from typing import Optional


def format_cpf(cpf: str) -> str:
    """Formata CPF para exibição: 123.456.789-01"""
    try:
        digits = re.sub(r"\D", "", cpf)[:11]
        if len(digits) <= 3:
            return digits
        elif len(digits) <= 6:
            return f"{digits[:3]}.{digits[3:]}"
        elif len(digits) <= 9:
            return f"{digits[:3]}.{digits[3:6]}.{digits[6:]}"
        else:
            return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
    except Exception:
        return cpf


def format_date(date_str: str) -> str:
    """Formata data para dd/mm/aaaa"""
    try:
        digits = re.sub(r"\D", "", date_str)[:8]
        if len(digits) <= 2:
            return digits
        elif len(digits) <= 4:
            return f"{digits[:2]}/{digits[2:]}"
        else:
            return f"{digits[:2]}/{digits[2:4]}/{digits[4:]}"
    except Exception:
        return date_str


def format_unloc(unloc: str) -> str:
    """Formata UNLOC com mapeamento"""
    from .constants import UNLOC_MAP
    return UNLOC_MAP.get(unloc, unloc)


def limit_text(text: str, max_length: int) -> str:
    """Limita texto com reticências"""
    if not text:
        return ""
    return text[:max_length - 3] + "..." if len(text) > max_length else text


def extract_cpf_digits(cpf: str) -> str:
    """Extrai apenas dígitos do CPF"""
    return re.sub(r"\D", "", cpf)


def normalize_text(text: str) -> str:
    """Normaliza texto para busca"""
    if not text:
        return ""
    return text.strip().upper()