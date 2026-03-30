# -*- coding: utf-8 -*-
"""
services.py — Camada de serviço da Carteira Digital.
<<<<<<< HEAD

Expõe:
  • CarteiraService  — operações sobre carteiras (salvar, buscar, etc.)
  • sefaz_repo       — atributo opcional para credenciais do SEFAZ no banco
                       (utilizado pelo BatchCarteiraController no lote)

Para ativar o repositório de credenciais SEFAZ, basta criar a classe
SefazCredentialRepository em services/sefaz_repository.py com o método:

    def obter_credencial(self) -> dict | None:
        \"\"\"Retorna {'usuario': str, 'senha': str} ou None.\"\"\"

e descomentá-la aqui.
"""
from services.carteira_repository import CarteirasRepository
=======
Local: app/ui/abas/Carteira/services.py
"""

from .services.carteira_repository import CarteirasRepository
from .services.sefaz_repository import SefazRepository
>>>>>>> f4a3e3b (.)

# ── Repositório de credenciais SEFAZ (opcional) ───────────────────────────────
# Descomente e implemente SefazCredentialRepository para ativar o lote SEFAZ.
#
# try:
#     from services.sefaz_repository import SefazCredentialRepository as _SefazRepo
#     _sefaz_repo_instance = _SefazRepo()
# except ImportError:
#     _sefaz_repo_instance = None


class CarteiraService:
<<<<<<< HEAD
    """
    Serviço principal de carteiras digitais.

    Atributo `sefaz_repo`:
        Injetado pelo UI ao instanciar BatchCarteiraView.
        Deve ter o método obter_credencial() -> dict | None.
        Se None, o lote SEFAZ não abrirá o Chrome.
    """

    def __init__(self):
        self.repo = CarteirasRepository()

        # Para habilitar o lote com automação SEFAZ, atribua aqui:
        #   self.sefaz_repo = _sefaz_repo_instance
        # Por padrão fica None → BatchCarteiraView avisa sobre credenciais.
        self.sefaz_repo = None

    # ── Carteiras ──────────────────────────────────────────────────────────────
=======

    def __init__(self):
        self.repo = CarteirasRepository()
        self.sefaz_repo = SefazRepository()

    # ──────────────────────────────────────────────────────────────────────────
    # Carteiras
    # ──────────────────────────────────────────────────────────────────────────
>>>>>>> f4a3e3b (.)

    def salvar(self, registro, cpf, nome, propriedade, unloc, inicio, validade,
               endereco, atividade1, atividade2, georef, pdf_conteudo,
               foto1, foto2, foto3, usuario):
<<<<<<< HEAD
        """Salva carteira no banco e retorna o ID gerado."""
        return self.repo.salvar(
            registro     = registro,
            cpf          = cpf,
            nome         = nome,
            propriedade  = propriedade,
            unloc        = unloc,
            inicio       = inicio,
            validade     = validade,
            endereco     = endereco,
            atividade1   = atividade1,
            atividade2   = atividade2,
            georef       = georef,
            pdf_conteudo = pdf_conteudo,
            foto1        = foto1,
            foto2        = foto2,
            foto3        = foto3,
            usuario      = usuario,
        )

    def buscar_com_filtros(self, termo_pesquisa="", periodo="TODOS", usuario="TODOS"):
        """Busca carteiras com filtros de texto, período e usuário."""
        return self.repo.buscar_com_filtros(termo_pesquisa, periodo, usuario)

    def buscar_pdf_por_id(self, carteira_id):
        """Retorna dict com pdf_conteudo (bytes) ou None."""
        return self.repo.buscar_pdf_por_id(carteira_id)

    def contar_total(self):
        """Retorna o total de carteiras cadastradas."""
        return self.repo.contar_total()

    def buscar_usuarios_unicos(self):
        """Retorna lista de usuários distintos que geraram carteiras."""
=======
        return self.repo.salvar(
            registro=registro,
            cpf=cpf,
            nome=nome,
            propriedade=propriedade,
            unloc=unloc,
            inicio=inicio,
            validade=validade,
            endereco=endereco,
            atividade1=atividade1,
            atividade2=atividade2,
            georef=georef,
            pdf_conteudo=pdf_conteudo,
            foto1=foto1,
            foto2=foto2,
            foto3=foto3,
            usuario=usuario,
        )

    def buscar_com_filtros(self, termo_pesquisa="", periodo="TODOS", usuario="TODOS"):
        return self.repo.buscar_com_filtros(termo_pesquisa, periodo, usuario)

    def buscar_pdf_por_id(self, carteira_id):
        return self.repo.buscar_pdf_por_id(carteira_id)

    def contar_total(self):
        return self.repo.contar_total()

    def buscar_usuarios_unicos(self):
>>>>>>> f4a3e3b (.)
        return self.repo.buscar_usuarios_unicos()