# -*- coding: utf-8 -*-
"""
ui_events.py — Handlers de eventos e ações disparadas pelo usuário.
"""
import os
import threading
from tkinter import filedialog, messagebox

import customtkinter as ctk

_VERDE = "#22c55e"
_VERM  = "#ef4444"
_MUTED = "#64748b"


class LancamentoEvents:

    # =========================================================================
    # Navegação entre abas
    # =========================================================================
    def _on_tab(self):
        try:
            idx  = self._nb.index("current")
            text = self._nb.tab(idx, "text").strip()
            if   "Revisar"   in text or idx == 0: self._carregar_revisar()
            elif "Renova"    in text or idx == 1: self._carregar_renovacao()
            elif "Inscri"    in text or idx == 2: self._carregar_inscricao()
            elif "Devolu"    in text or idx == 3: self._carregar_devolucoes()
            elif "Hist"      in text or idx == 5: self._carregar_historico()
        except Exception:
            pass

    # =========================================================================
    # Seleção de linha na tabela
    # =========================================================================
    def _selecionar_linha(self, reg: dict, frame: ctk.CTkFrame):
        from app.theme import AppTheme
        if self._linha_sel and self._linha_sel.winfo_exists():
            reg_ant = self._linha_sel_reg or {}
            urg_ant = reg_ant.get("urgencia", False)
            lan_ant = bool(reg_ant.get("lancado_por"))
            bg_ant  = "#1c1007" if urg_ant and not lan_ant else AppTheme.BG_CARD
            self._linha_sel.configure(fg_color=bg_ant)

        self._selecionado   = reg
        self._linha_sel     = frame
        self._linha_sel_reg = reg
        frame.configure(fg_color="#1e3a5f")

    # =========================================================================
    # Pasta de origem
    # =========================================================================
    def _selecionar_pasta(self):
        from app.theme import AppTheme
        pasta = filedialog.askdirectory(title="Selecionar pasta de PDFs")
        if pasta:
            self._pasta_origem = pasta
            nome = os.path.basename(pasta)
            for attr in ("_lbl_pasta_revisar", "_lbl_pasta_prontos",
                         "_lbl_pasta_devolucoes"):
                lbl = getattr(self, attr, None)
                if lbl:
                    lbl.configure(text=nome, text_color=AppTheme.TXT_MAIN)

    # =========================================================================
    # PDF
    # =========================================================================
    def _abrir_pdf(self, analise_id: int):
        def _w():
            ok, msg = self.controller.abrir_pdf(analise_id)
            if not ok:
                self.after(0, messagebox.showerror, "Erro", msg)
        threading.Thread(target=_w, daemon=True).start()

    # =========================================================================
    # Lançamento
    # =========================================================================
    def _lancar_por_cpf(self, event=None):
        cpf_txt = self._cpf_var.get().strip()
        if not cpf_txt:
            return

        def _w():
            ok, msg = self.controller.registrar_por_cpf(cpf_txt)
            cor = _VERDE if ok else _VERM
            self.after(0, self._lbl_cpf_status.configure,
                       {"text": msg, "text_color": cor})
            if ok:
                self.after(0, self._cpf_var.set, "")
                self.after(0, self._carregar_revisar)
                self.after(0, self._carregar_prontos)
                self.after(0, self._atualizar_stats)
        threading.Thread(target=_w, daemon=True).start()

    def _lancar_linha(self, reg: dict):
        def _w():
            ok, msg = self.controller.enviar_para_impressao(
                analise_id   = reg["id"],
                nome_pdf     = reg["nome_pdf"],
                pasta_origem = self._pasta_origem,
            )
            if ok:
                self.after(0, self._carregar_revisar)
                self.after(0, self._carregar_prontos)
                self.after(0, self._atualizar_stats)
                self.after(0, messagebox.showinfo, "Sucesso", msg)
            else:
                self.after(0, messagebox.showerror, "Erro", msg)
        threading.Thread(target=_w, daemon=True).start()

    def _enviar_impressao(self):
        if not self._selecionado:
            messagebox.showwarning("Atenção", "Selecione um processo na tabela.")
            return
        self._lancar_linha(self._selecionado)

    # =========================================================================
    # Consulta CPF — eventos de formulário
    # =========================================================================
    def _mascara_consulta_cpf(self, *_):
        if self._aplicando_consulta_cpf:
            return
        self._aplicando_consulta_cpf = True
        try:
            t = self._consulta_cpf_var.get()
            d = "".join(c for c in t if c.isdigit())[:11]
            if   len(d) <= 3: r = d
            elif len(d) <= 6: r = d[:3] + "." + d[3:]
            elif len(d) <= 9: r = d[:3] + "." + d[3:6] + "." + d[6:]
            else:             r = d[:3] + "." + d[3:6] + "." + d[6:9] + "-" + d[9:]
            if r != t:
                self._consulta_cpf_var.set(r)
                self._entry_consulta.after(
                    0, lambda: self._entry_consulta.icursor("end"))
        finally:
            self._aplicando_consulta_cpf = False

    def _executar_consulta_cpf(self, event=None):
        cpf_txt = self._consulta_cpf_var.get().strip()
        if not cpf_txt:
            return

        for w in self._consulta_resultado.winfo_children():
            w.destroy()
        ctk.CTkLabel(self._consulta_resultado, text="Consultando...",
                     text_color=_MUTED, font=("Segoe UI", 12)).pack(pady=20)

        def _w():
            resultado = self.controller.consultar_cpf(cpf_txt)
            self.after(0, self._exibir_consulta, resultado, cpf_txt)
        threading.Thread(target=_w, daemon=True).start()

    def _limpar_consulta(self):
        self._consulta_cpf_var.set("")
        for w in self._consulta_resultado.winfo_children():
            w.destroy()
        ctk.CTkLabel(self._consulta_resultado,
                     text="Digite um CPF acima e clique em Consultar.",
                     text_color=_MUTED,
                     font=("Segoe UI", 13)).pack(pady=40)

    # =========================================================================
    # Máscara CPF — aba registro
    # =========================================================================
    def _mascara_cpf(self, *_):
        if self._aplicando_cpf:
            return
        self._aplicando_cpf = True
        try:
            t = self._cpf_var.get()
            d = "".join(c for c in t if c.isdigit())[:11]
            if   len(d) <= 3: r = d
            elif len(d) <= 6: r = d[:3] + "." + d[3:]
            elif len(d) <= 9: r = d[:3] + "." + d[3:6] + "." + d[6:]
            else:             r = d[:3] + "." + d[3:6] + "." + d[6:9] + "-" + d[9:]
            if r != t:
                self._cpf_var.set(r)
                self._entry_cpf.after(
                    0, lambda: self._entry_cpf.icursor("end"))
        finally:
            self._aplicando_cpf = False