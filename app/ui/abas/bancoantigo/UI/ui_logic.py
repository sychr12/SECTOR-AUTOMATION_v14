# -*- coding: utf-8 -*-
"""
ui_logic.py — Carregamento, filtros e stats.
Não cria widgets nem responde a eventos diretamente.
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

    # ── Stats ─────────────────────────────────────────────────────────────────
    def _atualizar_stats(self):
        def _w():
            s       = self.controller.estatisticas()
            revisar = len(self._dados_revisar)
            prontos = len(self._dados_prontos)
            self.after(0, self._lbl_pendentes.configure, {"text": str(revisar)})
            self.after(0, self._lbl_prontos.configure,   {"text": str(prontos)})
            self.after(0, self._lbl_lancados.configure,  {"text": str(s.get("lancados", 0))})
            self.after(0, self._lbl_urgentes.configure,  {"text": str(s.get("urgentes", 0))})
        threading.Thread(target=_w, daemon=True).start()

    # ── Aba Lista — Falta Revisar / Prontos ───────────────────────────────────
    def _carregar_modo(self, modo: str):
        if modo == "revisar":
            self._carregar_revisar()
        else:
            self._carregar_prontos()

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
            dados = (self.controller.carregar_para_revisar()
                     if modo == "revisar"
                     else self.controller.carregar_prontos())
            self.after(0, self._preencher_tabela, dados, modo)
        except Exception as exc:
            self.after(0, messagebox.showerror, "Erro",
                       f"Erro ao carregar:\n{exc}")

    def _preencher_tabela(self, dados: list, modo: str):
        tabela = getattr(self, f"_tabela_{modo}")
        for w in tabela.winfo_children():
            w.destroy()

        if modo == "revisar":
            self._dados_revisar = dados
        else:
            self._dados_prontos = dados

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
            return

        for reg in dados:
            self._criar_linha(reg, tabela, modo)

        self.after(0, self._atualizar_stats)

    # ── Aba Histórico ─────────────────────────────────────────────────────────
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