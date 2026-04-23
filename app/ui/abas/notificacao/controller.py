# -*- coding: utf-8 -*-
"""
Controller para operações de email
"""

##from tkinter import messagebox
from typing import Tuple, Optional, Dict, Any
from .models import EmailConfigModel
from .services import EmailService

class EmailController:
    """Controller para operações de email"""
    
    def __init__(self, config_caminho="config_email.json"):
        self.config_caminho = config_caminho
        self.config = EmailConfigModel.carregar_do_arquivo(config_caminho)
    
    def salvar_configuracao(
        self, 
        servidor: str, 
        porta: int, 
        email: str, 
        senha: str,
        assunto: str,
        habilitado: bool,
        template: str
    ) -> Tuple[bool, str]:
        """Salva nova configuração de email"""
        try:
            # Atualizar modelo
            self.config.smtp_server = servidor.strip()
            self.config.smtp_port = porta
            self.config.email_remetente = email.strip()
            self.config.senha_remetente = senha
            self.config.assunto_padrao = assunto.strip()
            self.config.habilitado = habilitado
            self.config.template_novo_usuario = template.strip()
            
            # Validar configuração
            valido, mensagem = self.config.validar()
            if not valido:
                return False, mensagem
            
            # Salvar no arquivo
            if self.config.salvar_para_arquivo(self.config_caminho):
                return True, "Configuração salva com sucesso!"
            else:
                return False, "Erro ao salvar configuração no arquivo"
                
        except Exception as e:
            return False, f"Erro ao salvar configuração: {str(e)}"
    
    def testar_conexao(self) -> Tuple[bool, str]:
        """Testa conexão com servidor SMTP"""
        if not self.config.email_remetente or not self.config.senha_remetente:
            return False, "Configure email e senha antes de testar"
        
        return EmailService.testar_conexao_smtp(
            servidor=self.config.smtp_server,
            porta=self.config.smtp_port,
            email=self.config.email_remetente,
            senha=self.config.senha_remetente
        )
    
    def enviar_email_novo_usuario(self, usuario_info: Dict[str, Any]) -> Tuple[bool, str]:
        """Envia email para novo usuário"""
        return EmailService.enviar_email_novo_usuario(self.config, usuario_info)
    
    def carregar_configuracao_atual(self) -> Dict[str, Any]:
        """Retorna configuração atual como dicionário"""
        from dataclasses import asdict
        return asdict(self.config)
    
    def obter_configuracao(self) -> EmailConfigModel:
        """Retorna o modelo de configuração"""
        return self.config
    
    def esta_habilitado(self) -> bool:
        """Verifica se o serviço de email está habilitado"""
        return self.config.habilitado

