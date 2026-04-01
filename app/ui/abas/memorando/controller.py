# -*- coding: utf-8 -*-
import traceback
from datetime import datetime
from tkinter import filedialog
from .models import MemorandoModel
from .services import MemorandoService


class MemorandoController:

    def __init__(self, usuario):
        self.usuario = usuario

    def validar_dados_memorando(self, numero, data_str, unloc):
        erros = []
        if not numero.strip():
            erros.append("Número do memorando é obrigatório")
        if not unloc.strip():
            erros.append("UNLOC é obrigatório")
        if not data_str.strip():
            erros.append("Data de emissão é obrigatória")
        else:
            try:
                datetime.strptime(data_str, "%d/%m/%Y")
            except ValueError:
                erros.append("Data inválida. Use o formato DD/MM/AAAA")
        return erros

    def gerar_memorando(self, numero, data_str, unloc, memo_entrada=""):
        try:
            erros = self.validar_dados_memorando(numero, data_str, unloc)
            if erros:
                return False, "\n".join(erros), None

            data_emissao = datetime.strptime(data_str, "%d/%m/%Y").date()

            conteudo_word = MemorandoService.criar_memorando_word(
                numero=numero,
                data=data_str,
                unloc=unloc.upper(),
                memo_entrada=memo_entrada
            )

            dados_memorando = {
                'numero':        numero,
                'data_emissao':  data_emissao,
                'unloc':         unloc.upper(),
                'memo_entrada':  memo_entrada,
                'quantidade':    0,
                'word_conteudo': conteudo_word,
                'usuario':       self.usuario
            }

            resultado = MemorandoService.salvar_memorando_bd(dados_memorando)

            if resultado:
                return True, "Memorando gerado e salvo com sucesso!", resultado
            else:
                return False, "Erro ao salvar no banco de dados", None

        except Exception as e:
            traceback.print_exc()
            return False, f"{type(e).__name__}: {e}", None

    def buscar_historico(self, termo_pesquisa="", municipio="Todos", ano="Todos", ordem="Recentes"):
        try:
            registros = MemorandoService.buscar_memorandos(
                termo_pesquisa, 
                municipio, 
                ano,
                ordem
                
                )
            return True, "Histórico carregado com sucesso", registros
        except Exception as e:
            traceback.print_exc()
            return False, f"{type(e).__name__}: {e}", []

    def buscar_historico_com_filtros(self, termo="", codigo_municipio=None,
                                      ano=None, ordem="Recentes"):
        """
        Busca histórico com filtros avançados.

        Args:
            termo: Texto para buscar no número ou UNLOC
            codigo_municipio: Código do município (ex: "MAO")
            ano: Ano para filtrar (ex: "2024")
            ordem: "Recentes" ou "Antigos"

        Returns:
            tuple: (sucesso, mensagem, registros)
        """
        try:
            registros = MemorandoService.buscar_memorandos_com_filtros(
                termo=termo,
                codigo_municipio=codigo_municipio,
                ano=ano,
                ordem=ordem
            )
            return True, "Histórico carregado com sucesso", registros
        except Exception as e:
            traceback.print_exc()
            return False, f"{type(e).__name__}: {e}", []

    def listar_anos(self):
        """Lista todos os anos disponíveis nos memorandos"""
        try:
            anos = MemorandoService.listar_anos_disponiveis()
            return True, anos
        except Exception as e:
            traceback.print_exc()
            return False, []

    def visualizar_memorando(self, memorando_id):
        try:
            memorando = MemorandoService.buscar_memorando_por_id(memorando_id)
            if not memorando or not memorando.get('word_conteudo'):
                return False, "Memorando não encontrado no banco."
            conteudo = memorando['word_conteudo']
            if isinstance(conteudo, memoryview):
                conteudo = bytes(conteudo)
            MemorandoService.abrir_arquivo_temp(conteudo)
            return True, f"Memorando {memorando['numero']} aberto"
        except Exception as e:
            traceback.print_exc()
            return False, f"{type(e).__name__}: {e}"

    def baixar_memorando(self, memorando_id, numero):
        try:
            memorando = MemorandoService.buscar_memorando_por_id(memorando_id)
            if not memorando or not memorando.get('word_conteudo'):
                return False, "Memorando não encontrado no banco."

            nome_sugerido = f"MEMO_{memorando['numero']}_{memorando['unloc']}.docx"
            caminho_salvar = filedialog.asksaveasfilename(
                title="Salvar Memorando",
                defaultextension=".docx",
                initialfile=nome_sugerido,
                filetypes=[("Word Document", "*.docx"), ("All Files", "*.*")]
            )

            if not caminho_salvar:
                return False, "Operação cancelada pelo usuário"

            conteudo = memorando['word_conteudo']
            if isinstance(conteudo, memoryview):
                conteudo = bytes(conteudo)

            with open(caminho_salvar, 'wb') as f:
                f.write(conteudo)

            return True, f"Memorando salvo em:\n{caminho_salvar}"

        except Exception as e:
            traceback.print_exc()
            return False, f"{type(e).__name__}: {e}"
        