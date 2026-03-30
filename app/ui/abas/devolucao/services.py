# -*- coding: utf-8 -*-
"""
Services para configuração e utilidades da devolução
"""

import json
import os
from datetime import datetime

class ConfiguracaoService:
    """Service para gerenciamento de configurações"""
    
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.config_path = os.path.join(self.base_dir, "jsons files", "config_devolucao.json")
        self._carregar_config()
    
    def _carregar_config(self):
        """Carrega configurações do arquivo JSON"""
        self.config = {
            'destinatarios_padrao': ["email@exemplo.com"],
            'assunto_padrao': "Devolução",
            'caminho_padrao_pdf': os.path.join(self.base_dir, "pdfs", "devolucoes"),
            'log_enabled': True
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                    self.config.update(dados)
        except Exception as e:
            print(f"Erro ao carregar configuração: {e}")
    
    def salvar_config(self):
        """Salva configurações no arquivo JSON"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erro ao salvar configuração: {e}")
            return False
    
    def obter_destinatarios(self):
        """Retorna lista de destinatários"""
        return self.config.get('destinatarios_padrao', [])
    
    def adicionar_destinatario(self, email):
        """Adiciona um destinatário à lista"""
        destinatarios = self.obter_destinatarios()
        if email not in destinatarios:
            destinatarios.append(email)
            self.config['destinatarios_padrao'] = destinatarios
            self.salvar_config()
    
    def remover_destinatario(self, email):
        """Remove um destinatário da lista"""
        destinatarios = self.obter_destinatarios()
        if email in destinatarios:
            destinatarios.remove(email)
            self.config['destinatarios_padrao'] = destinatarios
            self.salvar_config()
    
    def obter_caminho_pdf(self):
        """Retorna caminho para salvar PDFs"""
        caminho = self.config.get('caminho_padrao_pdf', '')
        if caminho and not os.path.exists(caminho):
            os.makedirs(caminho, exist_ok=True)
        return caminho

class HistoricoService:
    """Service para gerenciamento de histórico de devoluções"""
    
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.historico_path = os.path.join(self.base_dir, "jsons files", "historico_devolucoes.json")
        self.historico = []
        self._carregar_historico()
    
    def _carregar_historico(self):
        """Carrega histórico do arquivo JSON"""
        try:
            if os.path.exists(self.historico_path):
                with open(self.historico_path, 'r', encoding='utf-8') as f:
                    self.historico = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar histórico: {e}")
            self.historico = []
    
    def _salvar_historico(self):
        """Salva histórico no arquivo JSON"""
        try:
            os.makedirs(os.path.dirname(self.historico_path), exist_ok=True)
            with open(self.historico_path, 'w', encoding='utf-8') as f:
                json.dump(self.historico, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erro ao salvar histórico: {e}")
            return False
    
    def registrar_devolucao(self, usuario, tipo, conteudo, sucesso=True, detalhes=""):
        """Registra uma devolução no histórico"""
        registro = {
            'data_hora': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            'usuario': usuario,
            'tipo': tipo,  # 'pdf', 'email', 'ambos'
            'sucesso': sucesso,
            'conteudo_resumo': conteudo[:100] + "..." if len(conteudo) > 100 else conteudo,
            'detalhes': detalhes
        }
        
        self.historico.append(registro)
        
        # Manter apenas os últimos 100 registros
        if len(self.historico) > 100:
            self.historico = self.historico[-100:]
        
        self._salvar_historico()
        return registro
    
    def obter_historico(self, limite=50):
        """Retorna histórico de devoluções"""
        return self.historico[-limite:] if limite else self.historico
    
    def limpar_historico(self):
        """Limpa todo o histórico"""
        self.historico = []
        self._salvar_historico()