# -*- coding: utf-8 -*-
"""
Modelos de dados para relatórios SEFAZ
"""

from dataclasses import dataclass, asdict
from typing import List, Tuple, Dict
from datetime import datetime
import os

@dataclass
class MunicipioModel:
    """Modelo de município"""
    nome: str
    codigo: str
    selecionado: bool = False
    
    @property
    def codigo_int(self) -> int:
        """Retorna código como inteiro"""
        try:
            return int(self.codigo)
        except ValueError:
            return 0

@dataclass
class PeriodoModel:
    """Modelo de período de datas"""
    data_inicio: str
    data_fim: str
    
    def validar(self) -> Tuple[bool, str]:
        """Valida o período"""
        if not self.data_inicio or not self.data_fim:
            return False, "Datas inicial e final são obrigatórias"
        
        try:
            # Verificar formato DD/MM/AAAA
            dia_inicio, mes_inicio, ano_inicio = map(int, self.data_inicio.split('/'))
            dia_fim, mes_fim, ano_fim = map(int, self.data_fim.split('/'))
            
            # Verificar valores válidos
            if not (1 <= dia_inicio <= 31 and 1 <= mes_inicio <= 12 and ano_inicio > 1900):
                return False, "Data inicial inválida"
            
            if not (1 <= dia_fim <= 31 and 1 <= mes_fim <= 12 and ano_fim > 1900):
                return False, "Data final inválida"
            
            return True, "Período válido"
            
        except (ValueError, IndexError):
            return False, "Formato de data inválido. Use DD/MM/AAAA"

@dataclass
class ConfigRelatorioModel:
    """Modelo de configuração para relatórios"""
    municipios_selecionados: List[MunicipioModel]
    periodo: PeriodoModel
    pasta_download: str
    pasta_relatorios: str
    
    def __init__(self, base_dir: str):
        self.pasta_download = os.path.join(base_dir, "downloads")
        self.pasta_relatorios = os.path.join(base_dir, "Relatorios Gerados")
        self.municipios_selecionados = []
        self.periodo = PeriodoModel("", "")
    
    def preparar_diretorios(self):
        """Cria os diretórios necessários"""
        os.makedirs(self.pasta_download, exist_ok=True)
        os.makedirs(self.pasta_relatorios, exist_ok=True)
    
    def municipios_para_processar(self) -> List[Tuple[str, str]]:
        """Retorna lista de (nome, código) dos municípios selecionados"""
        return [
            (m.nome, m.codigo) 
            for m in self.municipios_selecionados 
            if m.selecionado
        ]
    
    def validar(self) -> Tuple[bool, str]:
        """Valida configuração completa"""
        # Validar período
        valido_periodo, msg_periodo = self.periodo.validar()
        if not valido_periodo:
            return False, msg_periodo
        
        # Validar municípios selecionados
        municipios = self.municipios_para_processar()
        if not municipios:
            return False, "Selecione ao menos um município"
        
        return True, "Configuração válida"

@dataclass
class RelatorioGeradoModel:
    """Modelo para relatório gerado"""
    nome_arquivo: str
    municipio: str
    tipo: str  # "INSCRICAO" ou "RENOVACAO"
    caminho: str
    data_geracao: datetime
    total_registros: int = 0
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            "ARQUIVO": f"{self.tipo}_{self.municipio}",
            "MUNICIPIO": self.municipio,
            "TIPO": self.tipo,
            "TOTAL": self.total_registros,
            "DATA_GERACAO": self.data_geracao.strftime("%d/%m/%Y %H:%M:%S"),
            "CAMINHO": self.caminho
        }