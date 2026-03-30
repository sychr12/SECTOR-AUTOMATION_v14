# -*- coding: utf-8 -*-
"""Paleta de cores e helpers de formatação do módulo Anexar."""

# ── Paleta ────────────────────────────────────────────────────────────────────
VERDE   = "#22c55e"
VERDE_H = "#16a34a"
VERDE_T = "#052e16"
AZUL    = "#3b82f6"
AZUL_H  = "#2563eb"
VERM    = "#ef4444"
VERM_H  = "#b91c1c"
AMBER   = "#f59e0b"
AMBER_B = "#854d0e"
AMBER_T = "#fef08a"
MUTED   = "#64748b"
INFO    = "#60a5fa"
SLATE   = "#334155"


def fmt_data(val) -> str:
    if not val:
        return "—"
    try:
        return val.strftime("%d/%m/%Y %H:%M") if hasattr(val, "strftime") else str(val)
    except Exception:
        return str(val)


def fmt_data_curta(val) -> str:
    if not val:
        return "—"
    try:
        return val.strftime("%d/%m/%Y") if hasattr(val, "strftime") else str(val)
    except Exception:
        return str(val)


def safe_print(msg: str) -> None:
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", errors="replace").decode("ascii"))