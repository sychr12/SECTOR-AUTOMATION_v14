# -*- coding: utf-8 -*-
"""
ui_logic.py — Lógica de negócio da UI: carregamento, filtros e stats.

Contém os workers de thread, carregadores de dados, preenchimento
de tabelas e atualização de contadores. Não cria widgets nem
responde a eventos de formulário diretamente.
"""
import threading
from tkinter import messagebox

import customtkinter as ctk

from app.theme import AppTheme

_VERDE = "#22c55e"
_AZUL  = "#3b82f6"
_VERM  = "#ef4444"
_MUTED = "#64748b"


class LancamentoLogic:
    """
    Mixin de lógica — herdado por LancamentoUI.

    Depende de atributos criados por LancamentoLayout e pelo __init__
    de LancamentoUI (self.controller, self._cpp_service, etc.).
    """

    # =========================================================================
    # Stats
    # =========================================================================
    def _atualizar_stats(self):
        def _w():
            try:
                s = self.controller.estatisticas()
            except Exception:
                s = {}

            # Usar contagens do banco diretamente — as listas locais podem
            # estar vazias no momento da chamada (race condition)
            pendentes  = s.get("pendentes",  0)
            prontos    = s.get("prontos",    0)
            lancados   = s.get("lancados",   0)
            urgentes   = s.get("urgentes",   0)
            devolucoes = s.get("devolucoes", 0)

            def _safe(lbl, val):
                try:
                    if lbl and lbl.winfo_exists():
                        lbl.configure(text=str(val))
                except Exception:
                    pass

            self.after(0, _safe, self._lbl_pendentes,  pendentes)
            self.after(0, _safe, self._lbl_prontos,    prontos)
            self.after(0, _safe, self._lbl_lancados,   lancados)
            self.after(0, _safe, self._lbl_urgentes,   urgentes)
            self.after(0, _safe, getattr(self, "_lbl_devolucoes", None), devolucoes)

        threading.Thread(target=_w, daemon=True).start()

    # =========================================================================
    # Aba Lista — Falta Revisar / Prontos
    # =========================================================================
    def _carregar_modo(self, modo: str):
        if modo == "revisar":
            self._carregar_revisar()
        elif modo == "prontos":
            self._carregar_prontos()
        else:
            self._carregar_devolucoes()

    def _carregar_revisar(self):
        self._limpar_tabela("revisar")
        threading.Thread(
            target=self._worker_carregar, args=("revisar",), daemon=True
        ).start()

    def _carregar_prontos(self):
        self._limpar_tabela("prontos")
        threading.Thread(
            target=self._worker_carregar, args=("prontos",), daemon=True
        ).start()

    def _carregar_devolucoes(self):
        self._limpar_tabela("devolucoes")
        threading.Thread(
            target=self._worker_carregar, args=("devolucoes",), daemon=True
        ).start()

    def _filtrar_devolucoes(self):
        """Filtra a tabela de devoluções em tempo real pelo termo digitado."""
        termo = getattr(self, "_dev_busca_var", None)
        termo = termo.get().lower().strip() if termo else ""
        dados = getattr(self, "_dados_devolucoes", [])

        tabela = getattr(self, "_tabela_devolucoes", None)
        if not tabela:
            return
        try:
            if not tabela.winfo_exists():
                return
        except Exception:
            return

        for w in tabela.winfo_children():
            w.destroy()

        filtrados = dados
        if termo:
            filtrados = [
                r for r in dados
                if termo in (r.get("nome_pdf")      or "").lower()
                or termo in (r.get("cpf")           or "").lower()
                or termo in (r.get("motivo")        or "").lower()
                or termo in (r.get("analisado_por") or "").lower()
            ]

        if not filtrados:
            ctk.CTkLabel(tabela,
                         text="Nenhum processo encontrado.",
                         text_color=_MUTED,
                         font=("Segoe UI", 13)).pack(pady=40)
            return

        for reg in filtrados:
            self._criar_linha(reg, tabela, "devolucoes")

    def _limpar_tabela(self, modo: str):
        tabela = getattr(self, f"_tabela_{modo}", None)
        if tabela:
            for w in tabela.winfo_children():
                w.destroy()
            ctk.CTkLabel(tabela, text="Carregando...",
                         text_color=_MUTED,
                         font=("Segoe UI", 12)).pack(pady=30)
        self._selecionado   = None
        self._linha_sel     = None
        self._linha_sel_reg = None

    def _worker_carregar(self, modo: str):
        try:
            if modo == "revisar":
                dados = self.controller.carregar_para_revisar()
            elif modo == "prontos":
                dados = self.controller.carregar_prontos()
            else:
                dados = self.controller.carregar_devolucoes()
            def _aplicar():
                try:
                    if self.winfo_exists():
                        self._preencher_tabela(dados, modo)
                except Exception:
                    pass
            self.after(0, _aplicar)
        except Exception as exc:
            def _erro():
                try:
                    if self.winfo_exists():
                        messagebox.showerror("Erro", f"Erro ao carregar:\n{exc}")
                except Exception:
                    pass
            self.after(0, _erro)

    def _preencher_tabela(self, dados: list, modo: str):
        tabela = getattr(self, f"_tabela_{modo}", None)
        if not tabela:
            return
        try:
            if not tabela.winfo_exists():
                return
        except Exception:
            return

        for w in tabela.winfo_children():
            w.destroy()

        if modo == "revisar":
            self._dados_revisar = dados
        elif modo == "prontos":
            self._dados_prontos = dados
        else:
            self._dados_devolucoes = dados

        self._selecionado   = None
        self._linha_sel     = None
        self._linha_sel_reg = None

        if not dados:
            msg = ("Nenhum processo aguardando revisão."
                   if modo == "revisar"
                   else "Nenhum processo pronto para impressão.")
            ctk.CTkLabel(tabela, text=msg,
                         text_color=_MUTED,
                         font=("Segoe UI", 13)).pack(pady=40)
            self.after(0, self._atualizar_stats)
            return

        for reg in dados:
            self._criar_linha(reg, tabela, modo)

        self.after(0, self._atualizar_stats)

    # =========================================================================
    # Aba Histórico
    # =========================================================================
    def _carregar_historico(self):
        def _w():
            try:
                self._hist_dados = self.controller.historico()
                self.after(0, self._filtrar_historico)
            except Exception as exc:
                self.after(0, messagebox.showerror, "Erro", str(exc))
        threading.Thread(target=_w, daemon=True).start()

    def _filtrar_historico(self):
        termo = self._hist_busca.get().lower()
        dados = getattr(self, "_hist_dados", [])
        if termo:
            dados = [d for d in dados
                     if termo in (d.get("nome_pdf")      or "").lower()
                     or termo in (d.get("lancado_por")   or "").lower()
                     or termo in (d.get("analisado_por") or "").lower()
                     or termo in (d.get("cpf")           or "").lower()]

        for item in self._hist_tree.get_children():
            self._hist_tree.delete(item)

        for i, r in enumerate(dados):
            self._hist_tree.insert(
                "", "end",
                values=(r.get("nome_pdf",      "—"),
                        r.get("cpf",           "—"),
                        r.get("analisado_por", "—"),
                        r.get("lancado_por",   "—"),
                        r.get("criado_em",     "—")),
                tags=("par" if i % 2 == 0 else "impar",))

    def _limpar_cpp(self):
        """Placeholder — lógica de CPP gerenciada pelo módulo bancoantigo."""
        pass