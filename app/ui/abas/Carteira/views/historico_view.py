# views/historico_view.py
# -*- coding: utf-8 -*-
"""
Histórico de Carteiras Digitais.

BUG CORRIGIDO: classe estava truncada com comentário "# ... resto do código..."
deixando _build() e _atualizar() ausentes, causando AttributeError em runtime.
"""
import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox, ttk

from app.theme import AppTheme
from ..utils.constants import VERDE, VERDE_HOVER, AZUL, AZUL_HOVER, MUTED, VERMELHO
from ..utils.formatters import format_cpf


class HistoricoView(ctk.CTkToplevel):

    def __init__(self, master, usuario, controller):
        super().__init__(master)
        self.usuario    = usuario
        self.controller = controller

        self.title("Histórico de Carteiras Digitais")
        self.geometry("1440x900")
        self.configure(fg_color=AppTheme.BG_APP)
        self.grab_set()
        self._centralizar()
        self._build()
        self._atualizar()

    # ── Centralização ─────────────────────────────────────────────────────────

    def _centralizar(self):
        self.update_idletasks()
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        x = (self.winfo_screenwidth()  // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self):
        # Cabeçalho
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(20, 8))

        ctk.CTkLabel(
            hdr, text="Histórico de Carteiras Digitais",
            font=("Segoe UI", 20, "bold"),
            text_color=AppTheme.TXT_MAIN,
        ).pack(side="left")

        ctk.CTkButton(
            hdr, text="✕ Fechar",
            width=90, height=34, corner_radius=8,
            fg_color=AppTheme.BG_INPUT, hover_color=AppTheme.BORDER,
            text_color=MUTED, font=("Segoe UI", 11),
            command=self.destroy,
        ).pack(side="right")

        # Filtros
        filtros = ctk.CTkFrame(self, fg_color=AppTheme.BG_CARD,
                               corner_radius=12)
        filtros.pack(fill="x", padx=24, pady=(0, 12))

        linha = ctk.CTkFrame(filtros, fg_color="transparent")
        linha.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(linha, text="Pesquisar:",
                     font=("Segoe UI", 11), text_color=MUTED).pack(side="left")

        self._entry_busca = ctk.CTkEntry(
            linha,
            placeholder_text="Nome, CPF ou UNLOC...",
            fg_color=AppTheme.BG_INPUT, border_color=AppTheme.BORDER,
            text_color=AppTheme.TXT_MAIN, height=34, corner_radius=8, width=280,
        )
        self._entry_busca.pack(side="left", padx=(8, 16))
        self._entry_busca.bind("<KeyRelease>", lambda _: self._atualizar())

        ctk.CTkLabel(linha, text="Período:",
                     font=("Segoe UI", 11), text_color=MUTED).pack(side="left")

        self._periodo = ctk.CTkComboBox(
            linha,
            values=["TODOS", "HOJE", "SEMANA", "MES", "ANO"],
            fg_color=AppTheme.BG_INPUT, border_color=AppTheme.BORDER,
            text_color=AppTheme.TXT_MAIN, height=34, width=130,
            command=lambda _: self._atualizar(),
        )
        self._periodo.set("TODOS")
        self._periodo.pack(side="left", padx=(8, 16))

        ctk.CTkLabel(linha, text="Usuário:",
                     font=("Segoe UI", 11), text_color=MUTED).pack(side="left")

        usuarios = ["TODOS"] + self.controller.buscar_usuarios_unicos()
        self._usuario_combo = ctk.CTkComboBox(
            linha,
            values=usuarios,
            fg_color=AppTheme.BG_INPUT, border_color=AppTheme.BORDER,
            text_color=AppTheme.TXT_MAIN, height=34, width=160,
            command=lambda _: self._atualizar(),
        )
        self._usuario_combo.set("TODOS")
        self._usuario_combo.pack(side="left", padx=(8, 0))

        ctk.CTkButton(
            linha, text="🔄 Atualizar",
            width=110, height=34, corner_radius=8,
            fg_color=AZUL, hover_color=AZUL_HOVER,
            text_color="#fff", font=("Segoe UI", 11),
            command=self._atualizar,
        ).pack(side="right")

        # Contador
        self._lbl_total = ctk.CTkLabel(
            self, text="",
            font=("Segoe UI", 11), text_color=MUTED,
        )
        self._lbl_total.pack(anchor="w", padx=24, pady=(0, 6))

        # Treeview
        frame_tree = ctk.CTkFrame(self, fg_color=AppTheme.BG_CARD,
                                  corner_radius=12)
        frame_tree.pack(fill="both", expand=True, padx=24, pady=(0, 8))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Hist.Treeview",
                        background=AppTheme.BG_INPUT,
                        fieldbackground=AppTheme.BG_INPUT,
                        foreground=AppTheme.TXT_MAIN,
                        rowheight=32, font=("Segoe UI", 11),
                        borderwidth=0)
        style.configure("Hist.Treeview.Heading",
                        background=AppTheme.BG_CARD,
                        foreground=MUTED,
                        font=("Segoe UI", 10, "bold"),
                        relief="flat")
        style.map("Hist.Treeview",
                  background=[("selected", "#1e3a5f")])

        self._tree = ttk.Treeview(
            frame_tree,
            columns=("id", "nome", "cpf", "unloc", "validade", "usuario", "data"),
            show="headings",
            style="Hist.Treeview",
            selectmode="browse",
        )
        cols_cfg = [
            ("id",       "ID",       55,  False),
            ("nome",     "Nome",     220, True),
            ("cpf",      "CPF",      130, False),
            ("unloc",    "UNLOC",    100, False),
            ("validade", "Validade", 100, False),
            ("usuario",  "Usuário",  130, False),
            ("data",     "Data",     140, False),
        ]
        for col_id, titulo, w, stretch in cols_cfg:
            self._tree.heading(col_id, text=titulo,
                               command=lambda c=col_id: self._sort_by(c))
            self._tree.column(col_id, width=w, minwidth=50, stretch=stretch)

        vsb = ttk.Scrollbar(frame_tree, orient="vertical",
                            command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y", pady=6)
        self._tree.pack(fill="both", expand=True, padx=6, pady=6)
        self._tree.bind("<Double-1>", self._on_duplo_clique)

        # Botões de ação
        acoes = ctk.CTkFrame(self, fg_color="transparent")
        acoes.pack(fill="x", padx=24, pady=(0, 16))

        ctk.CTkButton(
            acoes, text="👁️ Visualizar PDF",
            height=38, corner_radius=10,
            fg_color=AZUL, hover_color=AZUL_HOVER,
            text_color="#fff", font=("Segoe UI", 12),
            command=self._visualizar_pdf,
        ).pack(side="left")

        ctk.CTkButton(
            acoes, text="⬇️ Baixar PDF",
            height=38, corner_radius=10,
            fg_color=AppTheme.BG_INPUT, hover_color=AppTheme.BORDER,
            text_color=AppTheme.TXT_MAIN, font=("Segoe UI", 12),
            command=self._baixar_pdf,
        ).pack(side="left", padx=(8, 0))

        self._lbl_status = ctk.CTkLabel(
            acoes, text="",
            font=("Segoe UI", 11), text_color=MUTED,
        )
        self._lbl_status.pack(side="left", padx=16)

    # ── Dados ─────────────────────────────────────────────────────────────────

    def _atualizar(self):
        termo   = self._entry_busca.get().strip()
        periodo = self._periodo.get()
        usuario = self._usuario_combo.get()

        try:
            registros = self.controller.carregar_historico(termo, periodo, usuario)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar histórico:\n{e}", parent=self)
            return

        for item in self._tree.get_children():
            self._tree.delete(item)

        for reg in registros:
            data_str = ""
            if reg.get("criado_em"):
                try:
                    dt = reg["criado_em"]
                    if isinstance(dt, datetime):
                        data_str = dt.strftime("%d/%m/%Y %H:%M")
                    else:
                        data_str = str(dt)
                except Exception:
                    data_str = str(reg["criado_em"])

            self._tree.insert("", "end", values=(
                reg.get("id", ""),
                reg.get("nome", ""),
                format_cpf(reg.get("cpf", "") or ""),
                reg.get("unloc", ""),
                reg.get("validade", ""),
                reg.get("usuario", ""),
                data_str,
            ))

        total = len(registros)
        self._lbl_total.configure(
            text=f"{total} registro(s) encontrado(s)",
            text_color=AppTheme.TXT_MAIN if total else MUTED,
        )

    def _sort_by(self, col):
        """Ordena a treeview pela coluna clicada."""
        items = [(self._tree.set(k, col), k) for k in self._tree.get_children("")]
        items.sort()
        for index, (_, k) in enumerate(items):
            self._tree.move(k, "", index)

    def _get_selected(self):
        """Retorna (carteira_id, nome) da linha selecionada ou (None, None)."""
        sel = self._tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um registro na lista.", parent=self)
            return None, None
        values = self._tree.item(sel[0], "values")
        return values[0], values[1]  # id, nome

    def _on_duplo_clique(self, _event):
        self._visualizar_pdf()

    def _visualizar_pdf(self):
        carteira_id, nome = self._get_selected()
        if not carteira_id:
            return
        self._lbl_status.configure(text="Abrindo PDF...", text_color=MUTED)
        self.update_idletasks()
        ok, msg = self.controller.visualizar_pdf(carteira_id)
        self._lbl_status.configure(
            text=msg if ok else f"❌ {msg}",
            text_color=VERDE if ok else VERMELHO,
        )

    def _baixar_pdf(self):
        carteira_id, nome = self._get_selected()
        if not carteira_id:
            return
        self._lbl_status.configure(text="Baixando...", text_color=MUTED)
        self.update_idletasks()
        ok, msg = self.controller.baixar_pdf(carteira_id, nome)
        if ok:
            self._lbl_status.configure(text="✅ PDF salvo.", text_color=VERDE)
            messagebox.showinfo("Sucesso", f"PDF salvo em:\n{msg}", parent=self)
        else:
            self._lbl_status.configure(text=f"❌ {msg}", text_color=VERMELHO)
            if msg != "Operação cancelada":
                messagebox.showerror("Erro", msg, parent=self)