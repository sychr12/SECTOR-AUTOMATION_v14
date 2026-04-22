# -*- coding: utf-8 -*-
"""
Modelos de dados para configuração de email
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any

@dataclass
class EmailConfigModel:
    """Modelo de configuração de email"""
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    email_remetente: str = ""
    senha_remetente: str = ""
    assunto_padrao: str = "Sector Automation - Novo Acesso"
    assinatura: str = "\n\nAtenciosamente,\nEquipe Sector Automation"
    habilitado: bool = False
    template_novo_usuario: str = """Olá {nome},

Seu acesso ao Sistema Sector Automation foi criado com sucesso!

Detalhes da sua conta:
• Usuário: {username}
• Perfil: {perfil}
• Email: {email}
• Status: {status}

Para acessar o sistema, utilize o link: {url_sistema}

Sua senha inicial foi definida pelo administrador. 
Recomendamos que altere sua senha no primeiro acesso.

{assinatura}"""
    url_sistema: str = "http://localhost:5000"
    
    @classmethod
    def carregar_do_arquivo(cls, caminho_arquivo="config_email.json") -> 'EmailConfigModel':
        """Carrega configuração do arquivo JSON"""
        config_padrao = asdict(cls())
        
        if os.path.exists(caminho_arquivo):
            try:
                with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                    # Mescla dados do arquivo com padrões
                    for key in config_padrao:
                        if key in dados:
                            config_padrao[key] = dados[key]
            except Exception as e:
                # print(f"Erro ao carregar configuração: {e}")
        
        return cls(**config_padrao)
    
    def salvar_para_arquivo(self, caminho_arquivo="config_email.json") -> bool:
        """Salva configuração no arquivo JSON"""
        try:
            dados = asdict(self)
            # Remove senha do dicionário para salvar (se não quiser salvar a senha)
            # dados.pop('senha_remetente', None)
            
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            # print(f"Erro ao salvar configuração: {e}")
            return False
    
    def validar(self) -> tuple[bool, str]:
        """Valida os dados da configuração"""
        if not self.smtp_server:
            return False, "Servidor SMTP é obrigatório"
        
        if not 1 <= self.smtp_port <= 65535:
            return False, "Porta SMTP inválida"
        
        if self.email_remetente:
            from .services import EmailService
            if not EmailService.validar_email(self.email_remetente):
                return False, "Email do remetente inválido"
        
        return True, "Configuração válida"

@dataclass
class EmailLogModel:
    """Modelo de log de email"""
    data_hora: str
    username: str
    acao: str
    destinatario: str
    status: str
    detalhes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return asdict(self)
    
    def to_log_string(self) -> str:
        """Converte para string de log"""
        return f"[{self.data_hora}] Usuário: {self.username} | Ação: {self.acao} | Destinatário: {self.destinatario} | Status: {self.status} | Detalhes: {self.detalhes}"