# app/ui/abas/Carteira/models.py
# -*- coding: utf-8 -*-
"""
Modelos de dados para Carteira Digital
"""

from dataclasses import dataclass
from typing import Optional, Dict, List
from datetime import datetime


@dataclass
class Produtor:
    """Modelo do produtor rural"""
    registro: str
    cpf: str
    nome: str
    propriedade: str
    unloc: str
    inicio_atividade: Optional[str] = None
    validade: Optional[str] = None
    endereco: Optional[str] = None
    atividade_primaria: Optional[str] = None
    atividade_secundaria: Optional[str] = None
    georeferenciamento: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            "registro": self.registro,
            "cpf": self.cpf,
            "nome": self.nome,
            "propriedade": self.propriedade,
            "unloc": self.unloc,
            "inicio": self.inicio_atividade,
            "validade": self.validade,
            "endereco": self.endereco,
            "atividade1": self.atividade_primaria,
            "atividade2": self.atividade_secundaria,
            "georef": self.georeferenciamento,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Produtor":
        """Cria instância a partir de dicionário"""
        return cls(
            registro=data.get("registro", ""),
            cpf=data.get("cpf", ""),
            nome=data.get("nome", ""),
            propriedade=data.get("propriedade", ""),
            unloc=data.get("unloc", ""),
            inicio_atividade=data.get("inicio"),
            validade=data.get("validade"),
            endereco=data.get("endereco"),
            atividade_primaria=data.get("atividade1"),
            atividade_secundaria=data.get("atividade2"),
            georeferenciamento=data.get("georef"),
        )


@dataclass
class Carteira:
    """Modelo da carteira digital"""
    id: Optional[int]
    produtor: Produtor
    fotos: Dict[str, Optional[str]]
    pdf_data: Optional[bytes] = None
    
    def validate(self) -> tuple[bool, list[str]]:
        """Valida os dados da carteira"""
        errors = []
        
        if not self.produtor.registro:
            errors.append("Registro estadual é obrigatório")
        if not self.produtor.cpf:
            errors.append("CPF é obrigatório")
        if not self.produtor.nome:
            errors.append("Nome do produtor é obrigatório")
        if not self.produtor.propriedade:
            errors.append("Propriedade é obrigatória")
        
        return len(errors) == 0, errors