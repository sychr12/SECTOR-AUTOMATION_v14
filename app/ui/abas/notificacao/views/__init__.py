# -*- coding: utf-8 -*-
# Inicialização da pasta views

from .config_view import EmailConfigView
from .components import EmailStatusIndicator

__all__ = [
    'EmailConfigView',
    'EmailStatusIndicator'
]