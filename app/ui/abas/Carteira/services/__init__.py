# -*- coding: utf-8 -*-
"""
services/__init__.py — Serviços da Carteira Digital.
Local: app/ui/abas/Carteira/services/__init__.py
"""

from .credenciais_service import SefazCredentialRepository
from .carteira_repository import CarteirasRepository


class CarteiraService:
    """
    Serviço principal de carteiras digitais.
    Centraliza acesso ao repositório e às credenciais SEFAZ.
    """

    def __init__(self):
        self.repo = CarteirasRepository()
        self.sefaz_repo = SefazCredentialRepository()

    def salvar(self, registro, cpf, nome, propriedade, unloc, inicio, validade,
               endereco, atividade1, atividade2, georef, pdf_conteudo,
               foto1, foto2, foto3, usuario):
        return self.repo.salvar(
            registro=registro, cpf=cpf, nome=nome,
            propriedade=propriedade, unloc=unloc, inicio=inicio,
            validade=validade, endereco=endereco, atividade1=atividade1,
            atividade2=atividade2, georef=georef, pdf_conteudo=pdf_conteudo,
            foto1=foto1, foto2=foto2, foto3=foto3, usuario=usuario,
        )

    def buscar_com_filtros(self, termo_pesquisa="", periodo="TODOS", usuario="TODOS"):
        return self.repo.buscar_com_filtros(termo_pesquisa, periodo, usuario)

    def buscar_pdf_por_id(self, carteira_id):
        return self.repo.buscar_pdf_por_id(carteira_id)

    def contar_total(self):
        return self.repo.contar_total()

    def buscar_usuarios_unicos(self):
        return self.repo.buscar_usuarios_unicos()


__all__ = ['CarteiraService', 'SefazCredentialRepository', 'CarteirasRepository']