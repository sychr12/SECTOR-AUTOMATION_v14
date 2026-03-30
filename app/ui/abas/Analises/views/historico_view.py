# -*- coding: utf-8 -*-
"""Histórico de Processos — design refinado com ttk.Treeview."""
import threading
from datetime import datetime
from tkinter import messagebox, ttk

import customtkinter as ctk

from app.theme import AppTheme

_VERDE   = "#22c55e"
_VERDE_H = "#16a34a"
_AZUL    = "#3b82f6"
_AZUL_H  = "#2563eb"
_VERM    = "#ef4444"
_AMBER   = "#f59e0b"
_MUTED   = "#64748b"

STATUS_COR = {
    "DEVOLUCAO": _VERM,
    "RENOVACAO": _VERDE,
    "INSCRICAO": _AZUL,
    "PENDENTE":  _MUTED,
}


class HistoricoView(ctk.CTkToplevel):

    def __init__(self, master, usuario, controller):
        super().__init__(master)
        self.usuario    = usuario
        self.controller = controller

        self.title("Histórico de Movimentações")
        self.geometry("1200x700")
        self.configure(fg_color=AppTheme.BG_APP)
        self.grab_set()
        self._build()
        self._carregar()
        # Centralizar após a janela ser desenhada
        self.after(0, self._centralizar)

    def _centralizar(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth()  // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ── Layout ──────────────────────────────────────────────────────
    def _build(self):
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=32, pady=24)

        # Cabeçalho
        hdr = ctk.CTkFrame(wrap, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(hdr, text="Histórico de Movimentações",
                     font=("Segoe UI", 22, "bold"),
                     text_color=AppTheme.TXT_MAIN).pack(side="left")

        # Painel de filtros
        filtro = ctk.CTkFrame(wrap, fg_color=AppTheme.BG_CARD,
                              corner_radius=14)
        filtro.pack(fill="x", pady=(0, 16))

        linha1 = ctk.CTkFrame(filtro, fg_color="transparent")
        linha1.pack(fill="x", padx=20, pady=(14, 6))

        ctk.CTkLabel(linha1, text="Status:",
                     font=("Segoe UI", 11, "bold"),
                     text_color=_MUTED).pack(side="left", padx=(0, 12))

        self.filtro_var = ctk.StringVar(value="TODOS")
        for txt, val, cor in [
            ("Todos",     "TODOS",     _MUTED),
            ("Devolução", "DEVOLUCAO", _VERM),
            ("Renovação", "RENOVACAO", _VERDE),
            ("Inscrição", "INSCRICAO", _AZUL),
        ]:
            ctk.CTkRadioButton(
                linha1, text=txt,
                variable=self.filtro_var, value=val,
                fg_color=cor, hover_color=cor,
                text_color=AppTheme.TXT_MAIN,
                font=("Segoe UI", 12),
                command=self._atualizar,
            ).pack(side="left", padx=10)

        linha2 = ctk.CTkFrame(filtro, fg_color="transparent")
        linha2.pack(fill="x", padx=20, pady=(0, 14))

        self.pesquisa_var = ctk.StringVar()
        self.pesquisa_var.trace_add("write", lambda *_: self._atualizar())

        ctk.CTkEntry(linha2,
                     textvariable=self.pesquisa_var,
                     placeholder_text="Buscar por nome do arquivo ou usuário...",
                     height=36, corner_radius=10,
                     fg_color=AppTheme.BG_INPUT,
                     border_color=AppTheme.BG_INPUT,
                     font=("Segoe UI", 12),
                     text_color=AppTheme.TXT_MAIN,
                     ).pack(side="left", fill="x", expand=True)

        ctk.CTkButton(linha2, text="Limpar",
                      width=80, height=36, corner_radius=10,
                      fg_color=AppTheme.BG_INPUT,
                      hover_color=AppTheme.BG_APP,
                      font=("Segoe UI", 11),
                      text_color=_MUTED,
                      command=lambda: (self.pesquisa_var.set(""),
                                       self.filtro_var.set("TODOS"))
                      ).pack(side="right", padx=(10, 0))

        # Tabela com ttk.Treeview (muito mais performática que CTkFrame por linha)
        frame_tb = ctk.CTkFrame(wrap, fg_color=AppTheme.BG_CARD,
                                corner_radius=14)
        frame_tb.pack(fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Hist.Treeview",
                        background=AppTheme.BG_CARD,
                        fieldbackground=AppTheme.BG_CARD,
                        foreground=AppTheme.TXT_MAIN,
                        rowheight=36,
                        font=("Segoe UI", 11),
                        borderwidth=0)
        style.configure("Hist.Treeview.Heading",
                        background=AppTheme.BG_INPUT,
                        foreground=_MUTED,
                        font=("Segoe UI", 10, "bold"),
                        relief="flat")
        style.map("Hist.Treeview",
                  background=[("selected", "#1e3a5f")])

        cols = ("arquivo", "anterior", "atual", "usuario",
                "data", "motivo")
        self._tree = ttk.Treeview(frame_tb, columns=cols,
                                  show="headings",
                                  style="Hist.Treeview",
                                  selectmode="browse")

        hdrs = [("arquivo",  "Arquivo PDF",     280),
                ("anterior", "Status Anterior",  120),
                ("atual",    "Status Atual",      120),
                ("usuario",  "Usuário",           120),
                ("data",     "Data/Hora",         130),
                ("motivo",   "Motivo",            200)]

        for col, titulo, w in hdrs:
            self._tree.heading(col, text=titulo)
            self._tree.column(col, width=w, minwidth=60,
                              stretch=(col in ("arquivo", "motivo")))

        vsb = ttk.Scrollbar(frame_tb, orient="vertical",
                            command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y", pady=8)
        self._tree.pack(fill="both", expand=True, padx=8, pady=8)

        # Tags de cor por status
        self._tree.tag_configure("DEVOLUCAO", foreground=_VERM)
        self._tree.tag_configure("RENOVACAO", foreground=_VERDE)
        self._tree.tag_configure("INSCRICAO", foreground=_AZUL)
        self._tree.tag_configure("par",   background=AppTheme.BG_CARD)
        self._tree.tag_configure("impar", background=AppTheme.BG_INPUT)

        # Duplo clique → visualizar PDF
        self._tree.bind("<Double-1>",
                        lambda e: self._visualizar_selecionado())

        # Rodapé
        rodape = ctk.CTkFrame(wrap, fg_color="transparent")
        rodape.pack(fill="x", pady=(12, 0))

        ctk.CTkLabel(rodape,
                     text="Duplo clique para visualizar o PDF",
                     font=("Segoe UI", 11),
                     text_color=_MUTED).pack(side="left")

        ctk.CTkButton(rodape, text="Baixar PDF selecionado",
                      height=38, corner_radius=10,
                      fg_color=_AZUL, hover_color=_AZUL_H,
                      font=("Segoe UI", 12, "bold"),
                      text_color="#fff",
                      command=self._baixar_selecionado
                      ).pack(side="right")

    # ── Dados ────────────────────────────────────────────────────────
    def _carregar(self):
        threading.Thread(target=self._worker_carregar,
                         daemon=True).start()

    def _worker_carregar(self):
        try:
            dados = self.controller.carregar_historico()
            self._dados = dados
            self.after(0, self._atualizar)
        except Exception as exc:
            self.after(0, messagebox.showerror,
                       "Erro", f"Erro ao carregar histórico:\n{exc}")

    def _atualizar(self):
        if not hasattr(self, "_dados"):
            return

        filtro   = self.filtro_var.get()
        pesquisa = self.pesquisa_var.get().lower()

        dados = self._dados
        if filtro != "TODOS":
            dados = [d for d in dados if d["novo_status"] == filtro]
        if pesquisa:
            dados = [d for d in dados
                     if pesquisa in d["nome_pdf"].lower()
                     or pesquisa in d["usuario"].lower()]

        for item in self._tree.get_children():
            self._tree.delete(item)

        for i, h in enumerate(dados):
            data = h.get("data_acao")
            if isinstance(data, str):
                try:
                    data = datetime.fromisoformat(data)
                except ValueError:
                    data = None
            data_txt = data.strftime("%d/%m/%Y %H:%M") if data else "—"

            tag_linha = "par" if i % 2 == 0 else "impar"
            tag_status = h.get("novo_status", "")

            self._tree.insert("", "end",
                              iid=f"{h.get('analise_id','')}__{i}",
                              values=(
                                  h.get("nome_pdf",        "—"),
                                  h.get("status_anterior", "—"),
                                  h.get("novo_status",     "—"),
                                  h.get("usuario",         "—"),
                                  data_txt,
                                  h.get("motivo",          ""),
                              ),
                              tags=(tag_linha, tag_status))

    def _get_analise_id(self): 
        sel = self._tree.selection()
        if not sel:
            return None
        iid = sel[0]
        # iid = "{analise_id}__{idx}"
        parte = iid.split("__")[0]
        try:
            return int(parte) if parte else None
        except ValueError:
            return None

    def _visualizar_selecionado(self):
        aid = self._get_analise_id()
        if not aid:
            messagebox.showwarning("Aviso", "Selecione um registro com PDF.")
            return
        ok, msg = self.controller.visualizar_pdf(aid)
        if not ok:
            messagebox.showerror("Erro", msg)

    def _baixar_selecionado(self):
        aid = self._get_analise_id()
        if not aid:
            messagebox.showwarning("Aviso", "Selecione um registro com PDF.")
            return
        sel  = self._tree.selection()[0]
        nome = self._tree.item(sel, "values")[0]
        ok, msg = self.controller.baixar_pdf(aid, nome)
        if ok:
            messagebox.showinfo("Salvo", f"PDF salvo em:\n{msg}")
        elif msg != "Operação cancelada":
            messagebox.showerror("Erro", msg)