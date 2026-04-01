# -*- coding: utf-8 -*-
# Inicialização do módulo email
from .ui import EmailConfigUI
from .services import EmailService
from .controller import EmailController

# Adicionar alias para compatibilidade
EmailNotificacaoUI = EmailConfigUI

__all__ = [
    'EmailConfigUI',
    'EmailNotificacaoUI',  # ← Alias para o nome antigo
    'EmailService', 
    'EmailController'
]