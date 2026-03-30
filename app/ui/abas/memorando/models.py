# -*- coding: utf-8 -*-
"""
Modelos de dados para memorandos
"""

from datetime import datetime

class MemorandoModel:
    """Modelo de dados para um memorando"""
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.numero = kwargs.get('numero', '')
        self.descricao = kwargs.get('descricao', '')
        self.data_emissao = kwargs.get('data_emissao')
        self.unloc = kwargs.get('unloc', '')
        self.municipio = kwargs.get('municipio', '')
        self.memo_entrada = kwargs.get('memo_entrada', '')
        self.quantidade = kwargs.get('quantidade', 0)
        self.word_conteudo = kwargs.get('word_conteudo')
        self.usuario = kwargs.get('usuario', '')
        self.criado_em = kwargs.get('criado_em')
        
    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            'id': self.id,
            'numero': self.numero,
            'descricao': self.descricao,
            'data_emissao': self.data_emissao.strftime('%d/%m/%Y') if self.data_emissao else '',
            'unloc': self.unloc,
            'municipio': self.municipio,
            'memo_entrada': self.memo_entrada,
            'quantidade': self.quantidade,
            'usuario': self.usuario,
            'criado_em': self.criado_em.strftime('%d/%m/%Y %H:%M:%S') if self.criado_em else ''
        }