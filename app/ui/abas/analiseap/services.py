# -*- coding: utf-8 -*-
import os
import json

class AnaliseapServices:
    def __init__(self, base_dir):
        self.BASE_DIR = base_dir
        self.lista_municipios = {}
        self.carregar_municipios()
    
    def carregar_municipios(self):
        """Carrega lista de municípios do JSON"""
        path = os.path.join(self.BASE_DIR, "jsons files", "municipios.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                self.lista_municipios = json.load(f)
        else:
            self.lista_municipios = {}
    
    def filtrar_cidade(self, texto):
        """Filtra cidade com base no texto digitado"""
        texto = texto.lower()
        if len(texto) < 2:
            return None

        for municipio in self.lista_municipios.values():
            if municipio.lower().startswith(texto):
                return municipio
        return None
    
    def obter_todos_municipios(self):
        """Retorna todos os municípios"""
        return list(self.lista_municipios.values())