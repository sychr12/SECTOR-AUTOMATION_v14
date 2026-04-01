# -*- coding: utf-8 -*-
"""
Modelos de dados para Dashboard
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime

@dataclass
class DashboardStats:
    """Estatísticas gerais do sistema"""
    usuarios_online: int = 0
    usuarios_offline: int = 0
    total_usuarios: int = 0
    relatorios_gerados_hoje: int = 0
    relatorios_gerados_mes: int = 0
    relatorios_gerados_total: int = 0
    total_inscricoes: int = 0
    total_devolucoes: int = 0
    ultimo_acesso: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'usuarios_online': self.usuarios_online,
            'usuarios_offline': self.usuarios_offline,
            'total_usuarios': self.total_usuarios,
            'relatorios_hoje': self.relatorios_gerados_hoje,
            'relatorios_mes': self.relatorios_gerados_mes,
            'relatorios_total': self.relatorios_gerados_total,
            'total_inscricoes': self.total_inscricoes,
            'total_devolucoes': self.total_devolucoes,
            'ultimo_acesso': self.ultimo_acesso
        }

@dataclass
class UsuarioAtivo:
    """Modelo de usuário ativo no sistema"""
    username: str
    nome: str
    perfil: str
    ultimo_acesso: datetime
    tempo_online: str
    ip_address: str = "127.0.0.1"
    
    def tempo_online_formatado(self) -> str:
        """Retorna tempo online formatado"""
        return self.tempo_online

@dataclass
class AtividadeRecente:
    """Modelo de atividade recente no sistema"""
    tipo: str  # RELATORIO, INSCRICAO, DEVOLUCAO, CADASTRO, etc
    usuario: str
    descricao: str
    data_hora: datetime
    icone: str = "📋"
    
    def data_hora_formatada(self) -> str:
        """Retorna data/hora formatada"""
        return self.data_hora.strftime("%d/%m/%Y %H:%M:%S")