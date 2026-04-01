# -*- coding: utf-8 -*-
"""Histórico de Lançamentos."""
import os
from tkinter import filedialog, messagebox

import customtkinter as ctk

from app.theme import AppTheme   # ← CORRIGIDO (era: from theme import AppTheme)


class HistoricoView(ctk.CTkToplevel):

    def __init__(self, master, usuario, controller, service):
        super().__init__(master)
        self.usuario    = usuario
        self.controller = controller
        self.service    = service

        self.title("Histórico de Lançamentos")
        self.geometry("1050x650")
        self.configure(fg_color=AppTheme.BG_APP)
        self.grab_set()

        self._centralizar()
        self._build()
        self._carregar()

    def _centralizar(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth()  // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ── Layout ──────────────────────────────────────────────────────
    def _build(self):
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=24, pady=20)

        ctk.CTkLabel(wrap, text="Histórico de Lançamentos",
                     font=("Segoe UI", 22, "bold"),
                     text_color=AppTheme.TXT_MAIN
                     ).pack(anchor="w", pady=(0, 16))

        # barra de filtro
        bar = ctk.CTkFrame(wrap, fg_color=AppTheme.BG_CARD,
                           corner_radius=14)
        bar.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(bar, text="Pesquisar:",
                     font=("Segoe UI", 12, "bold"),
                     text_color="#64748b"
                     ).pack(side="left", padx=(16, 8), pady=14)

        self.pesquisa_var = ctk.StringVar()
        self.pesquisa_var.trace_add("write",
                                    lambda *_: self._pesquisar())
        ctk.CTkEntry(bar,
                     textvariable=self.pesquisa_var,
                     placeholder_text="Nome do arquivo, CPF ou analista...",
                     height=36, corner_radius=10, width=340,
                     fg_color=AppTheme.BG_INPUT,
                     border_color=AppTheme.BG_INPUT,
                     font=("Segoe UI", 12),
                     text_color=AppTheme.TXT_MAIN,
                     ).pack(side="left", padx=(0, 8), pady=14)

        ctk.CTkButton(bar, text="Limpar",
                      width=90, height=36, corner_radius=10,
                      fg_color=AppTheme.BG_INPUT,
                      hover_color=AppTheme.BG_APP,
                      font=("Segoe UI", 11),
                      text_color="#64748b",
                      command=lambda: self.pesquisa_var.set("")
                      ).pack(side="left", pady=14)

        # lista
        self._lista_wrap = ctk.CTkFrame(wrap, fg_color="transparent")
        self._lista_wrap.pack(fill="both", expand=True)

    # ── Carregar ─────────────────────────────────────────────────────
    def _carregar(self):
        try:
            self.registros = self.service.listar_ultimos(100)
            self._renderizar("")
        except Exception as exc:
            ctk.CTkLabel(self._lista_wrap,
                         text=f"Erro ao carregar: {exc}",
                         text_color="#ef4444",
                         font=("Segoe UI", 12)).pack(pady=50)

    def _pesquisar(self):
        self._renderizar(self.pesquisa_var.get().lower().strip())

    def _renderizar(self, termo: str):
        for w in self._lista_wrap.winfo_children():
            w.destroy()

        lista = ctk.CTkScrollableFrame(
            self._lista_wrap,
            fg_color=AppTheme.BG_CARD,
            corner_radius=14,
            scrollbar_button_color=AppTheme.BG_INPUT)
        lista.pack(fill="both", expand=True)

        registros = self.registros
        if termo:
            registros = [
                r for r in registros
                if termo in (r.get("nome_pdf")     or "").lower()
                or termo in (r.get("cpf")          or "").lower()
                or termo in (r.get("analisado_por") or "").lower()
                or termo in (r.get("lancado_por")   or "").lower()
            ]

        if not registros:
            ctk.CTkLabel(lista,
                         text="Nenhum registro encontrado.",
                         text_color="#64748b",
                         font=("Segoe UI", 13)).pack(pady=50)
            return

        for idx, r in enumerate(registros):
            bg = AppTheme.BG_APP if idx % 2 == 0 else AppTheme.BG_CARD
            self._card(lista, r, bg)

    def _card(self, parent, r: dict, bg: str):
        card = ctk.CTkFrame(parent, fg_color=bg, corner_radius=12)
        card.pack(fill="x", pady=4, padx=6)

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, padx=14, pady=12)

        nome = r.get("nome_pdf", "—")
        ext  = os.path.splitext(nome)[1].lower()
        icon = "📄" if ext == ".pdf" else "📝" if ext in (".docx", ".doc") else "📎"

        lbl = ctk.CTkLabel(info, text=f"{icon}  {nome}",
                           font=("Segoe UI", 12, "bold"),
                           anchor="w", cursor="hand2",
                           text_color="#3b82f6")
        lbl.pack(anchor="w", pady=2)
        lbl.bind("<Button-1>",
                 lambda _, rid=r.get("id"): self._visualizar(rid))

        cpf = r.get("cpf", "")
        if cpf and len(cpf) == 11:
            cpf = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

        for txt in filter(None, [
            f"CPF: {cpf}"                          if cpf  else None,
            f"Analisado por: {r.get('analisado_por','')}" if r.get("analisado_por") else None,
            f"Lançado por:   {r.get('lancado_por', '')}"  if r.get("lancado_por")   else None,
            r.get("criado_em", ""),
        ]):
            ctk.CTkLabel(info, text=txt,
                         font=("Segoe UI", 10),
                         text_color="#64748b",
                         anchor="w").pack(anchor="w", pady=1)

        # botões
        btns = ctk.CTkFrame(card, fg_color="transparent")
        btns.pack(side="right", padx=12, pady=12)

        ctk.CTkButton(
            btns, text="Ver",
            width=80, height=32, corner_radius=10,
            fg_color="#3b82f6", hover_color="#2563eb",
            font=("Segoe UI", 11, "bold"), text_color="#fff",
            command=lambda rid=r.get("id"): self._visualizar(rid)
        ).pack(pady=(0, 6))

        ctk.CTkButton(
            btns, text="Baixar",
            width=80, height=32, corner_radius=10,
            fg_color=AppTheme.BG_INPUT,
            hover_color=AppTheme.BG_APP,
            font=("Segoe UI", 11),
            text_color=AppTheme.TXT_MAIN,
            command=lambda rid=r.get("id"), n=nome: self._baixar(rid, n)
        ).pack()

    # ── Ações ────────────────────────────────────────────────────────
    def _visualizar(self, lancamento_id):
        if not lancamento_id:
            messagebox.showwarning("Aviso", "PDF não disponível.")
            return
        # ← usa visualizar_pdf_banco (método correto do LancamentoController)
        ok, msg = self.controller.visualizar_pdf_banco(lancamento_id)
        if not ok:
            messagebox.showerror("Erro", msg)

    def _baixar(self, lancamento_id, nome_arquivo: str):
        if not lancamento_id:
            messagebox.showwarning("Aviso", "PDF não disponível.")
            return

        ext = os.path.splitext(nome_arquivo)[1] or ".pdf"
        caminho = filedialog.asksaveasfilename(
            title="Salvar Arquivo",
            defaultextension=ext,
            initialfile=nome_arquivo,
            filetypes=[("PDF", "*.pdf"), ("Word", "*.docx"),
                       ("Todos", "*.*")]
        )
        if not caminho:
            return

        # ← usa baixar_pdf_banco (método correto do LancamentoController)
        ok, msg = self.controller.baixar_pdf_banco(
            lancamento_id, nome_arquivo, caminho)

        if ok:
            messagebox.showinfo("Salvo", f"Arquivo salvo!\n{msg}")
            if messagebox.askyesno("Abrir?", "Deseja abrir o arquivo agora?"):
                self.controller.abrir_arquivo(msg)
        else:
            messagebox.showerror("Erro", msg)