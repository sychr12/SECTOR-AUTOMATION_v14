# services.py (na raiz da pasta Carteira)
# -*- coding: utf-8 -*-
"""
services.py — Camada de serviço da Carteira Digital.
Local: app/ui/abas/Carteira/carteira_service.py
"""

from .services.carteira_repository import CarteirasRepository
from .services.credenciais_service import SefazCredentialRepository


class CarteiraService:
    """Serviço principal da carteira digital"""

    def __init__(self):
        self.repo = CarteirasRepository()
        self.sefaz_repo = SefazCredentialRepository()

    def salvar(self, registro, cpf, nome, propriedade, unloc, inicio, validade,
               endereco, atividade1, atividade2, georef, pdf_conteudo,
               foto1, foto2, foto3, usuario):
        """Salva carteira no banco"""
        return self.repo.salvar(
            registro=registro, cpf=cpf, nome=nome,
            propriedade=propriedade, unloc=unloc, inicio=inicio,
            validade=validade, endereco=endereco, atividade1=atividade1,
            atividade2=atividade2, georef=georef, pdf_conteudo=pdf_conteudo,
            foto1=foto1, foto2=foto2, foto3=foto3, usuario=usuario,
        )

    def buscar_com_filtros(self, termo_pesquisa="", periodo="TODOS", usuario="TODOS"):
        """Busca carteiras com filtros"""
        return self.repo.buscar_com_filtros(termo_pesquisa, periodo, usuario)

    def buscar_pdf_por_id(self, carteira_id):
        """Busca PDF por ID"""
        return self.repo.buscar_pdf_por_id(carteira_id)

    def contar_total(self):
        """Conta total de carteiras"""
        return self.repo.contar_total()

    def buscar_usuarios_unicos(self):
        """Busca usuários únicos"""
        return self.repo.buscar_usuarios_unicos()

    def buscar_por_cpf(self, cpf: str):
        """Busca carteira por CPF"""
        return self.repo.buscar_por_cpf(cpf)