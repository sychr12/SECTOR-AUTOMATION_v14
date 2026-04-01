import os
import json


class AnexarService:
    @staticmethod
    def carregar_configuracao():
        """Carrega configurações do sistema"""
        config_path = os.path.join(
            os.path.expanduser("~"),
            "Documents",
            "fabio jr",
            "SECTOR AUTOMATION",
            "jsons files",
            "config_anexar.json"
        )

        config_padrao = {
            "usuario_login": "03483401253",
            "url_login": "https://online.sefaz.am.gov.br/cas/login?service=https://sistemas.sefaz.am.gov.br/siged/cas",
            "timeout_padrao": 30,
            "diretorio_base": "Processos para anexar"
        }

        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8-sig") as f:
                    config = json.load(f)
                    config_padrao.update(config)
                    return config_padrao
            except Exception:
                return config_padrao
        return config_padrao

    @staticmethod
    def verificar_dependencias():
        """
        Verifica se todas as dependências estão instaladas.

        Mapeia nome-do-pacote (pip) → nome-do-módulo (import), pois
        alguns pacotes têm nomes diferentes entre os dois:
          - webdriver-manager  → webdriver_manager
          - winsound           → embutido no Python no Windows, nunca falta
        """
        import importlib
        import sys

        # (nome_pip, nome_import)
        dependencias = [
            ("selenium",          "selenium"),
            ("webdriver-manager", "webdriver_manager"),   # FIX: hífen → underline
            ("pyperclip",         "pyperclip"),
            # winsound é módulo builtin do Windows — não precisa verificar
        ]

        faltantes = []
        for nome_pip, nome_import in dependencias:
            try:
                importlib.import_module(nome_import)
            except ImportError:
                faltantes.append(nome_pip)

        return faltantes

    @staticmethod
    def criar_estrutura_pastas(base_dir):
        """Cria estrutura de pastas para processamento"""
        pastas = [
            base_dir,
            os.path.join(base_dir, "ANEXADOS"),
            os.path.join(base_dir, "CPF NAO ENCONTRADO"),
            os.path.join(base_dir, "ERRO"),
        ]
        for pasta in pastas:
            os.makedirs(pasta, exist_ok=True)
        return pastas

    @staticmethod
    def listar_pdfs(diretorio):
        """Lista todos os PDFs em um diretório"""
        if not os.path.exists(diretorio):
            return []
        return sorted(
            f for f in os.listdir(diretorio) if f.lower().endswith(".pdf")
        )