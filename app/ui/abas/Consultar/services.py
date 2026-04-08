# -*- coding: utf-8 -*-
"""
Services para gerenciamento de conexões e utilidades
"""

import psycopg2
from datetime import datetime, date


class DatabaseService:
    """Service para gerenciamento de conexões com banco"""
    
    @staticmethod
    def testar_conexao(conectar_func):
        """Testa se uma conexão funciona"""
        try:
            conn = conectar_func()
            conn.close()
            return True
        except:
            return False
    
    @staticmethod
    def formatar_cpf(cpf):
        """Formata CPF para exibição"""
        if not cpf:
            return ""
        cpf_str = str(cpf)
        if len(cpf_str) == 11:
            return f"{cpf_str[:3]}.{cpf_str[3:6]}.{cpf_str[6:9]}-{cpf_str[9:]}"
        return cpf_str


class FiltroService:
    """Service para gerenciamento de filtros"""
    
    @staticmethod
    def obter_opcoes_periodo():
        """Retorna opções de período para filtro"""
        ano_atual = datetime.now().year
        anos = ["Todos", "Últimos 30 dias"] + [str(a) for a in range(ano_atual, ano_atual - 6, -1)]
        return anos
    
    @staticmethod
    def validar_filtros(filtros):
        """Valida os filtros de pesquisa"""
        filtros_validos = {}
        
        # CORREÇÃO: Verificar se filtros existe e é um dicionário
        if not filtros or not isinstance(filtros, dict):
            return filtros_validos
        
        # Remove espaços em branco e valida
        if 'nome' in filtros and filtros.get('nome') and filtros['nome'].strip():
            filtros_validos['nome'] = filtros['nome'].strip()
        
        if 'cpf' in filtros and filtros.get('cpf') and filtros['cpf'].strip():
            cpf_limpo = ''.join(filter(str.isdigit, filtros['cpf']))
            if cpf_limpo:
                filtros_validos['cpf'] = cpf_limpo
        
        if 'municipio' in filtros and filtros.get('municipio') and filtros['municipio'].strip():
            filtros_validos['municipio'] = filtros['municipio'].strip()
        
        if 'memorando' in filtros and filtros.get('memorando') and filtros['memorando'].strip():
            filtros_validos['memorando'] = filtros['memorando'].strip()
        
        if 'periodo' in filtros and filtros.get('periodo'):
            filtros_validos['periodo'] = filtros['periodo']
        
        return filtros_validos