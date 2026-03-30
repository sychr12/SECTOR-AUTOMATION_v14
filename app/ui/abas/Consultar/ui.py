# -*- coding: utf-8 -*-
"""
ConsultarUI — interface de consulta de registros na tabela analise_ap.

Bugs corrigidos:
  - editar_linha usava CTkInputDialog (só editava nome) → agora abre FormularioEdicao
  - menu de contexto era vinculado ao frame container em vez do Treeview interno
  - controller sem RealDictCursor → rows eram tuplas, quebrava row["campo"]
"""

import threading
from tkinter import messagebox
import customtkinter as ctk

from ui.base_ui import BaseUI
from app.theme import AppTheme
from .controller import ConsultaController
from .services   import FiltroService
from .views      import (HeaderCard, FiltrosCard, TabelaConsulta,
                         MenuContexto, FormularioEdicao)


class ConsultarUI(BaseUI):
    """Interface de consulta de registros."""

    def __init__(self, parent, usuario, conectar_bd):
        super().__init__(parent)
        self.usuario = usuario
        self.configure(fg_color=AppTheme.BG_APP)

        try:
            self.controller = ConsultaController(conectar_bd, usuario)
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
            return

        self.filtro_service = FiltroService()

        self._criar_interface()
        self._configurar_menu_contexto()
        self.after(200, self.pesquisar)

    # ── Layout ────────────────────────────────────────────────────────────────
    def _criar_interface(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=24)

        HeaderCard(container, title="Consulta de Dados",
                   subtitle="Pesquise registros da tabela analise_ap"
                   ).pack(pady=(0, 16))

        self.filtros_card = FiltrosCard(container,
                                        on_pesquisar=self.pesquisar)
        self.filtros_card.pack(fill="x", pady=(0, 16))

        self.tabela = TabelaConsulta(container)
        self.tabela.pack(fill="both", expand=True)

    # ── Menu de contexto ──────────────────────────────────────────────────────
    def _configurar_menu_contexto(self):
        self.menu_contexto = MenuContexto(
            self.tabela.tree,           # pai = Treeview real
            on_editar  = self.editar_linha,
            on_excluir = self.excluir_linha,
        )
        # BUG 3 corrigido: bind no Treeview interno, não no frame wrapper
        self.tabela.bind_treeview(
            "<Button-3>",
            lambda e: self.menu_contexto.mostrar(e, self.tabela)
        )

    # ── Pesquisa ──────────────────────────────────────────────────────────────
    def pesquisar(self):
        filtros = self.filtros_card.obter_filtros()
        filtros_validos = self.filtro_service.validar_filtros(filtros)

        self.tabela.adicionar_dados([])
        self.filtros_card.desabilitar_botao()
        self.filtros_card.mostrar_progresso()

        threading.Thread(
            target=self._worker_pesquisa,
            args=(filtros_validos,),
            daemon=True,
        ).start()

    def _worker_pesquisa(self, filtros):
        try:
            sql, params = self.controller.construir_query(filtros)
            dados = self.controller.executar_consulta(sql, params)
            dados_fmt = self.controller.formatar_data_resultados(dados)
            self.after(0, self._finalizar_pesquisa, dados_fmt)
        except Exception as e:
            import traceback; traceback.print_exc()
            self.after(0, messagebox.showerror,
                       "Erro", f"Erro ao pesquisar:\n{e}")
            self.after(0, self._finalizar_pesquisa, [])

    def _finalizar_pesquisa(self, dados):
        self.filtros_card.esconder_progresso()
        self.filtros_card.habilitar_botao()
        self.tabela.adicionar_dados(dados)

    # ── Editar ────────────────────────────────────────────────────────────────
    def editar_linha(self):
        """
        Abre FormularioEdicao com todos os campos editáveis.
        BUG 2 corrigido: antes usava CTkInputDialog que só editava 'nome'.
        """
        valores = self.tabela.obter_linha_selecionada()
        if not valores:
            messagebox.showwarning("Aviso",
                                   "Selecione um registro para editar.")
            return

        def _on_salvar(id_registro, valores_alterados: dict):
            for campo, novo_valor in valores_alterados.items():
                sucesso, msg = self.controller.editar_registro(
                    id_registro, campo, novo_valor)
                if not sucesso:
                    messagebox.showerror("Erro", msg)
                    return
            messagebox.showinfo("Sucesso",
                                "Registro atualizado com sucesso!")
            self.pesquisar()

        FormularioEdicao(self, valores, on_salvar=_on_salvar)

    # ── Excluir ───────────────────────────────────────────────────────────────
    def excluir_linha(self):
        valores = self.tabela.obter_linha_selecionada()
        if not valores:
            messagebox.showwarning("Aviso",
                                   "Selecione um registro para excluir.")
            return

        id_registro  = valores[0]
        nome_registro = valores[1]

        if not messagebox.askyesno(
            "Confirmar Exclusão",
            f"Excluir o registro de '{nome_registro}'?\n\n"
            f"Esta ação não pode ser desfeita."
        ):
            return

        sucesso, msg = self.controller.excluir_registro(id_registro)
        if sucesso:
            messagebox.showinfo("Sucesso", msg)
            self.pesquisar()
        else:
            messagebox.showerror("Erro", msg)