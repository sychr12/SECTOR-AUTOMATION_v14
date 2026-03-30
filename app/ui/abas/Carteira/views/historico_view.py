# -*- coding: utf-8 -*-
"""Histórico de Carteiras Digitais."""
import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox, ttk

from app.theme import AppTheme   # BUG CORRIGIDO: era "from theme import AppTheme"

_VERDE  = "#22c55e"
_VERDEH = "#16a34a"
_AZUL   = "#3b82f6"
_AZULH  = "#2563eb"
_MUTED  = "#64748b"
_VERM   = "#ef4444"


class HistoricoView(ctk.CTkToplevel):

    def __init__(self, master, usuario, controller):
        super().__init__(master)
        self.usuario    = usuario
        self.controller = controller

        self.title("Histórico de Carteiras Digitais")
        self.geometry("1200x720")
        self.configure(fg_color=AppTheme.BG_APP)
        self.grab_set()
        self._centralizar()
        self._build()
        self._atualizar()

    def _centralizar(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth()  // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ── Layout ───────────────────────────────────────────────────────────
    def _build(self):
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=24, pady=20)

        # Cabeçalho
        hdr = ctk.CTkFrame(wrap, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(hdr, text="Histórico de Carteiras",
                     font=("Segoe UI", 22, "bold"),
                     text_color=AppTheme.TXT_MAIN).pack(side="left")
        self._lbl_contadores = ctk.CTkLabel(
            hdr, text="",
            font=("Segoe UI", 11),
            text_color=_MUTED)
        self._lbl_contadores.pack(side="right", pady=(6, 0))

        # Filtros
        self._build_filtros(wrap)

        # Tabela
        self._build_tabela(wrap)

    def _build_filtros(self, parent):
        bar = ctk.CTkFrame(parent, fg_color=AppTheme.BG_CARD,
                           corner_radius=14,
                           border_width=1, border_color=AppTheme.BORDER)
        bar.pack(fill="x", pady=(0, 12))

        # Linha 1 — busca
        l1 = ctk.CTkFrame(bar, fg_color="transparent")
        l1.pack(fill="x", padx=16, pady=(14, 6))

        ctk.CTkLabel(l1, text="🔍",
                     font=("Segoe UI", 14),
                     text_color=_MUTED).pack(side="left", padx=(0, 6))

        self._busca_var = ctk.StringVar()
        self._busca_var.trace_add("write", lambda *_: self._atualizar())
        ctk.CTkEntry(
            l1, textvariable=self._busca_var,
            placeholder_text="Nome, CPF ou UNLOC...",
            height=36, width=320, corner_radius=10,
            fg_color=AppTheme.BG_INPUT,
            border_color=AppTheme.BG_INPUT,
            font=("Segoe UI", 12),
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            l1, text="Limpar", width=80, height=36,
            corner_radius=10,
            fg_color=AppTheme.BG_INPUT,
            hover_color=AppTheme.BG_APP,
            text_color=_MUTED,
            font=("Segoe UI", 11),
            command=self._limpar_filtros,
        ).pack(side="left")

        ctk.CTkButton(
            l1, text="↺ Atualizar", width=100, height=36,
            corner_radius=10,
            fg_color=_AZUL, hover_color=_AZULH,
            text_color="#fff",
            font=("Segoe UI", 11, "bold"),
            command=self._atualizar,
        ).pack(side="right")

        # Linha 2 — período
        l2 = ctk.CTkFrame(bar, fg_color="transparent")
        l2.pack(fill="x", padx=16, pady=(0, 14))

        ctk.CTkLabel(l2, text="Período:",
                     font=("Segoe UI", 11, "bold"),
                     text_color=_MUTED).pack(side="left", padx=(0, 10))

        self._periodo_var = ctk.StringVar(value="TODOS")
        for txt, val in [("Todos", "TODOS"), ("Hoje", "HOJE"),
                          ("Semana", "SEMANA"), ("Mês", "MES"), ("Ano", "ANO")]:
            ctk.CTkRadioButton(
                l2, text=txt,
                variable=self._periodo_var, value=val,
                command=self._atualizar,
                font=("Segoe UI", 11),
                text_color=AppTheme.TXT_MAIN,
                fg_color=_VERDE,
            ).pack(side="left", padx=6)

        # Separador
        ctk.CTkLabel(l2, text="|", text_color=_MUTED).pack(side="left", padx=10)

        ctk.CTkLabel(l2, text="Usuário:",
                     font=("Segoe UI", 11, "bold"),
                     text_color=_MUTED).pack(side="left", padx=(0, 8))

        self._usuario_var = ctk.StringVar(value="TODOS")
        try:
            usuarios = self.controller.buscar_usuarios_unicos()
            for txt, val in [("Todos", "TODOS")] + [(u, u) for u in usuarios[:4]]:
                ctk.CTkRadioButton(
                    l2, text=txt,
                    variable=self._usuario_var, value=val,
                    command=self._atualizar,
                    font=("Segoe UI", 11),
                    text_color=AppTheme.TXT_MAIN,
                    fg_color=_AZUL,
                ).pack(side="left", padx=6)
        except Exception:
            pass

    def _build_tabela(self, parent):
        # Cabeçalho da tabela
        thead = ctk.CTkFrame(parent, fg_color=AppTheme.BG_INPUT,
                             corner_radius=10)
        thead.pack(fill="x", pady=(0, 4))

        cols = [("Nome", 240), ("CPF", 130), ("UNLOC", 90),
                ("Usuário", 120), ("Data", 140), ("Ações", 90)]
        for i, (txt, w) in enumerate(cols):
            ctk.CTkLabel(thead, text=txt, width=w, anchor="w",
                         font=("Segoe UI", 11, "bold"),
                         text_color=_MUTED
                         ).grid(row=0, column=i, padx=(16 if i == 0 else 8),
                                pady=10, sticky="w")

        # Scroll da lista
        self._lista = ctk.CTkScrollableFrame(
            parent, fg_color=AppTheme.BG_CARD,
            corner_radius=14,
            scrollbar_button_color=AppTheme.BG_INPUT,
            border_width=1, border_color=AppTheme.BORDER,
        )
        self._lista.pack(fill="both", expand=True)

    # ── Dados ────────────────────────────────────────────────────────────
    def _limpar_filtros(self):
        self._busca_var.set("")
        self._periodo_var.set("TODOS")
        self._usuario_var.set("TODOS")

    def _atualizar(self, *_):
        for w in self._lista.winfo_children():
            w.destroy()

        try:
            rows  = self.controller.carregar_historico(
                self._busca_var.get().strip(),
                self._periodo_var.get(),
                self._usuario_var.get(),
            )
            total = self.controller.contar_total_carteiras()
            self._lbl_contadores.configure(
                text=f"Total: {total}   |   Filtrados: {len(rows)}")

            if not rows:
                ctk.CTkLabel(self._lista,
                             text="Nenhuma carteira encontrada.",
                             text_color=_MUTED,
                             font=("Segoe UI", 13)
                             ).pack(pady=50)
                return

            for i, r in enumerate(rows):
                self._linha(r, i % 2 == 0)

        except Exception as exc:
            ctk.CTkLabel(self._lista,
                         text=f"Erro: {exc}",
                         text_color=_VERM,
                         font=("Segoe UI", 12)
                         ).pack(pady=30)

    def _linha(self, r: dict, par: bool):
        bg = AppTheme.BG_APP if par else AppTheme.BG_CARD
        row = ctk.CTkFrame(self._lista, fg_color=bg, corner_radius=10)
        row.pack(fill="x", pady=2, padx=4)

        # Nome
        ctk.CTkLabel(row,
                     text=r.get("nome", "—"),
                     width=240, anchor="w",
                     font=("Segoe UI", 11),
                     text_color=_AZUL,
                     ).pack(side="left", padx=(14, 0), pady=8)

        # CPF
        ctk.CTkLabel(row,
                     text=self.controller.formatar_cpf_exibicao(
                         r.get("cpf")) or "—",
                     width=130, anchor="w",
                     font=("Segoe UI", 10),
                     text_color=AppTheme.TXT_MAIN,
                     ).pack(side="left")

        # UNLOC
        ctk.CTkLabel(row, text=r.get("unloc") or "—",
                     width=90, anchor="w",
                     font=("Segoe UI", 10),
                     text_color=_MUTED,
                     ).pack(side="left")

        # Usuário
        ctk.CTkLabel(row, text=r.get("usuario") or "—",
                     width=120, anchor="w",
                     font=("Segoe UI", 10),
                     text_color=_MUTED,
                     ).pack(side="left")

        # Data
        try:
            d = r.get("criado_em")
            if isinstance(d, str):
                d = datetime.fromisoformat(d)
            data_txt = d.strftime("%d/%m/%Y %H:%M") if d else "—"
        except Exception:
            data_txt = "—"
        ctk.CTkLabel(row, text=data_txt,
                     width=140, anchor="w",
                     font=("Segoe UI", 10),
                     text_color=_MUTED,
                     ).pack(side="left")

        # Botões
        btns = ctk.CTkFrame(row, fg_color="transparent")
        btns.pack(side="left", padx=8, pady=6)

        ctk.CTkButton(
            btns, text="👁", width=34, height=28,
            corner_radius=8,
            fg_color=_AZUL, hover_color=_AZULH,
            text_color="#fff",
            command=lambda rid=r.get("id"): self._ver(rid),
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            btns, text="⬇", width=34, height=28,
            corner_radius=8,
            fg_color=_VERDE, hover_color=_VERDEH,
            text_color="#fff",
            command=lambda rid=r.get("id"), n=r.get("nome", "Carteira"):
                self._baixar(rid, n),
        ).pack(side="left", padx=2)

    # ── Ações ────────────────────────────────────────────────────────────
    def _ver(self, cid):
        ok, msg = self.controller.visualizar_pdf(cid)
        if not ok:
            messagebox.showerror("Erro", msg)

    def _baixar(self, cid, nome):
        # BUG CORRIGIDO: controller.baixar_pdf retorna (ok, resultado)
        # controller.abrir_pdf retorna True ou (False, msg) — normalizado abaixo
        ok, result = self.controller.baixar_pdf(cid, nome)
        if ok:
            if messagebox.askyesno("Abrir?", "Deseja abrir o PDF agora?"):
                ok2, msg2 = self.controller.abrir_pdf(result)
                if not ok2:
                    messagebox.showerror("Erro", msg2)
        elif result != "Operação cancelada":
            messagebox.showerror("Erro", result)