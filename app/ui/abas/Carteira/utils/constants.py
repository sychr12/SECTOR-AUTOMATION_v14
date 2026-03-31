# app/ui/abas/Carteira/utils/constants.py
# -*- coding: utf-8 -*-
"""
Constantes e configurações do módulo Carteira Digital
"""

# UI Constants
MAX_FILENAME_DISPLAY = 30
DEBOUNCE_DELAY = 120

# Cores
VERDE = "#22c55e"
VERDE_HOVER = "#16a34a"
AZUL = "#3b82f6"
AZUL_HOVER = "#2563eb"
MUTED = "#64748b"
VERMELHO = "#ef4444"
AMBER = "#f59e0b"

# URLs
SEFAZ_URL = "http://sistemas.sefaz.am.gov.br/gcc/entrada.do"

# Formatos suportados
SUPPORTED_IMAGE_FORMATS = [
    ("Imagens", "*.png *.jpg *.jpeg *.bmp *.webp"),
    ("Todos", "*.*"),
]

# Mapeamento UNLOC
UNLOC_MAP = {
    "BAE": "BAR",
    "MTS-ATZ": "ATZ-MTS", "MTS": "ATZ-MTS",
    "NRO-ITR": "ITR-NRO", "NRO": "ITR-NRO",
    "MTP-MNX": "MNX-MTP", "MTP": "MNX-MTP",
    "VE-LBR": "LBR-VE", "VE": "LBR-VE",
    "VRC-MPU": "MPU-VRC", "VRC": "MPU-VRC",
    "BNA-PRF": "PRF-BNA", "BNA": "PRF-BNA",
    "VDL-ITR": "ITR-VDL", "VDL": "ITR-VDL",
    "RLD-HIA": "HIA-RLD", "RLD": "HIA-RLD",
    "CAN-SUL": "SUL-CAN",
    "ZL-MAO": "MAO-ZL", "ZL": "MAO-ZL",
}

# Configurações do PDF
PDF_CONFIG = {
    "max_filename_length": 50,
    "max_address_lines": 3,
    "font_sizes": {
        "normal": 41,
        "address": 38,
        "small": 32
    },
    "image_size": {
        "width": 420,
        "height": 240
    }
}