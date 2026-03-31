# app/ui/abas/Carteira/utils/validators.py
# -*- coding: utf-8 -*-
"""
Validações de dados
"""

import re
from typing import Tuple, List


def validate_cpf(cpf: str) -> Tuple[bool, str]:
    """Valida CPF"""
    digits = re.sub(r"\D", "", cpf)

    if len(digits) != 11:
        return False, "CPF deve ter 11 dígitos"

    # Verifica dígitos repetidos
    if digits == digits[0] * 11:
        return False, "CPF inválido"

    # Valida dígitos verificadores
    def calculate_digit(digits, factor):
        # BUG CORRIGIDO: era "int(d) * factor - i" (sem parênteses), fórmula errada.
        # A fórmula correta multiplica cada dígito por (factor - posição).
        total = sum(int(d) * (factor - i) for i, d in enumerate(digits))
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder

    # Primeiro dígito verificador
    digit1 = calculate_digit(digits[:9], 10)
    if digit1 != int(digits[9]):
        return False, "CPF inválido"

    # Segundo dígito verificador
    digit2 = calculate_digit(digits[:10], 11)
    if digit2 != int(digits[10]):
        return False, "CPF inválido"

    return True, ""


def validate_date(date_str: str) -> Tuple[bool, str]:
    """Valida data no formato dd/mm/aaaa"""
    if not date_str:
        return True, ""

    if not re.match(r"^\d{2}/\d{2}/\d{4}$", date_str):
        return False, "Use formato dd/mm/aaaa"

    try:
        day, month, year = map(int, date_str.split("/"))

        if not (1 <= day <= 31):
            return False, "Dia inválido"
        if not (1 <= month <= 12):
            return False, "Mês inválido"
        if not (1900 <= year <= 2100):
            return False, "Ano inválido"

        days_in_month = [31, 29 if year % 4 == 0 else 28, 31, 30, 31, 30,
                         31, 31, 30, 31, 30, 31]
        if day > days_in_month[month - 1]:
            return False, f"Mês {month} não tem {day} dias"

        return True, ""
    except ValueError:
        return False, "Data inválida"


def validate_required_fields(data: dict, fields: List[str]) -> Tuple[bool, List[str]]:
    """Valida campos obrigatórios"""
    missing = [field for field in fields if not data.get(field, "").strip()]
    return len(missing) == 0, missing


def validate_image_size(filepath: str, max_mb: float = 10) -> Tuple[bool, str]:
    """Valida tamanho da imagem"""
    import os
    try:
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        if size_mb > max_mb:
            return False, f"Arquivo muito grande ({size_mb:.1f} MB). Máximo: {max_mb} MB"
        return True, ""
    except Exception as e:
        return False, f"Erro ao verificar arquivo: {e}"