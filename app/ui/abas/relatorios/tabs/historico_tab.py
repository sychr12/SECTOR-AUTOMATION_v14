# -*- coding: utf-8 -*-
"""Aba de histórico de relatórios SEFAZ."""
import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk

from ..utils import DateUtils, TableUtils


class HistoricoTab(ctk.CTkFrame):
    """Aba que exibe o histórico de relatórios gerados."""

    _COLUNAS = [
        ("municipio", "Município",  160),
        ("ano",       "Ano",         60),
        ("periodo",   "Período",    200),
        ("insc",      "Inscrições",  90),
        ("renov",     "Renovações",  90),
        ("usuario",   "Usuário",    110),
        ("data",      "Data",        90),
        ("hora",      "Hora",        70),
    ]

    def __init__(self, parent, controller, icons):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.icons      = icons
        self._rows_raw: list = []

        self._build()

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ── Barra de filtros ──────────────────────────────────────────────────
        bar = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=10,
                           border_width=1, border_color="#e2e8f0")
        bar.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=8)

        # Filtro município
        ctk.CTkLabel(inner, text="Município:", font=("Segoe UI", 11),
                     text_color="#64748b").pack(side="left")
        self._var_filtro = ctk.StringVar()
        ctk.CTkEntry(inner, textvariable=self._var_filtro, width=160, height=32,
                     placeholder_text="Filtrar...", corner_radius=8,
                     fg_color="#f5f7fc", border_color="#e2e8f0",
                     ).pack(side="left", padx=(4, 12))

        # Filtro ano
        ctk.CTkLabel(inner, text="Ano:", font=("Segoe UI", 11),
                     text_color="#64748b").pack(side="left")
        self._var_ano = ctk.StringVar(value="Todos")
        self._combo_ano = ctk.CTkComboBox(
            inner, variable=self._var_ano,
            values=["Todos"] + [str(a) for a in range(2020, 2031)],
            width=90, height=32, corner_radius=8,
            fg_color="#f5f7fc", border_color="#e2e8f0",
            command=lambda _: self._aplicar_filtros(),
        )
        self._combo_ano.pack(side="left", padx=(4, 12))

        # De / Até
        self._aplicando_de  = [False]
        self._aplicando_ate = [False]

        for lbl, attr_var, flag in [
            ("De:",  "_var_de",  self._aplicando_de),
            ("Até:", "_var_ate", self._aplicando_ate),
        ]:
            ctk.CTkLabel(inner, text=lbl, font=("Segoe UI", 11),
                         text_color="#64748b").pack(side="left")
            v = ctk.StringVar()
            setattr(self, attr_var, v)
            e = ctk.CTkEntry(inner, textvariable=v, width=110, height=32,
                             placeholder_text="DD/MM/AAAA", corner_radius=8,
                             fg_color="#f5f7fc", border_color="#e2e8f0")
            e.pack(side="left", padx=(4, 12))
            v.trace_add("write",
                        lambda *_, vv=v, ee=e, fl=flag:
                            DateUtils.aplicar_mascara(vv, ee, fl))

        ctk.CTkButton(
            inner, text="🔍 Buscar", height=32, width=90, corner_radius=8,
            fg_color="#2c6e9e", hover_color="#1e5a8a",
            font=("Segoe UI", 11, "bold"),
            command=self.carregar_historico,
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            inner, text="↺ Limpar", height=32, width=80, corner_radius=8,
            fg_color="#e2e8f0", hover_color="#d1dde9",
            text_color="#64748b", font=("Segoe UI", 11),
            command=self._limpar_filtros,
        ).pack(side="left")

        # Botão download (direita)
        self._btn_dl = ctk.CTkButton(
            inner, text="⬇ Baixar XLS", height=32, width=110, corner_radius=8,
            fg_color="#10b981", hover_color="#059669",
            font=("Segoe UI", 11, "bold"),
            command=self._baixar_xls,
        )
        self._btn_dl.pack(side="right")

        # ── Tabela ────────────────────────────────────────────────────────────
        card = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=12,
                            border_width=1, border_color="#e2e8f0")
        card.grid(row=1, column=0, sticky="nsew")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Hist.Treeview",
                        background="#ffffff", foreground="#1e2f3e",
                        rowheight=28, fieldbackground="#ffffff",
                        borderwidth=0, font=("Segoe UI", 11))
        style.configure("Hist.Treeview.Heading",
                        background="#f5f7fc", foreground="#64748b",
                        font=("Segoe UI", 11, "bold"), relief="flat")
        style.map("Hist.Treeview",
                  background=[("selected", "#dbeafe")],
                  foreground=[("selected", "#1e2f3e")])

        columns = [c[0] for c in self._COLUNAS]
        self._tree = ttk.Treeview(
            card, columns=columns, show="headings",
            style="Hist.Treeview", selectmode="browse",
        )
        for col, titulo, largura in self._COLUNAS:
            self._tree.heading(col, text=titulo,
                               command=lambda c=col: self._ordenar(c))
            self._tree.column(col, width=largura, minwidth=50, anchor="w")

        vsb = ttk.Scrollbar(card, orient="vertical",   command=self._tree.yview)
        hsb = ttk.Scrollbar(card, orient="horizontal",  command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self._tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        card.grid_rowconfigure(0, weight=1)
        card.grid_columnconfigure(0, weight=1)

        # Rodapé com contagem
        self._lbl_count = ctk.CTkLabel(card, text="", font=("Segoe UI", 10),
                                        text_color="#64748b")
        self._lbl_count.grid(row=2, column=0, sticky="w", padx=12, pady=4)

        # Alternância de cores de linha
        self._tree.tag_configure("par",   background="#f8fafc")
        self._tree.tag_configure("impar", background="#ffffff")

        # IDs dos registros para download
        self._ids_rows: list[int] = []

        # Ordenação
        self._sort_col = ""
        self._sort_rev = False

    # ── Carregar / filtrar ────────────────────────────────────────────────────
    def carregar_historico(self):
        filtro = self._var_filtro.get().strip()

        def _worker():
            try:
                rows = self.controller.buscar_historico(filtro)
                self.after(0, self._popular_tabela, rows)
            except Exception as exc:
                self.after(0, messagebox.showerror, "Erro",
                           f"Falha ao carregar histórico:\n{exc}")

        threading.Thread(target=_worker, daemon=True).start()

    def _popular_tabela(self, rows: list):
        self._rows_raw = rows
        self._aplicar_filtros()

    def _aplicar_filtros(self):
        rows = TableUtils.filtrar_rows(
            self._rows_raw,
            ano=self._var_ano.get(),
            de=self._var_de.get().strip(),
            ate=self._var_ate.get().strip(),
        )

        # Limpa tabela
        for item in self._tree.get_children():
            self._tree.delete(item)
        self._ids_rows.clear()

        for i, r in enumerate(rows):
            fmt  = TableUtils.formatar_registro(r)
            tag  = "par" if i % 2 == 0 else "impar"
            self._tree.insert("", "end", iid=str(i), tags=(tag,),
                              values=(
                                  fmt["municipio"], fmt["ano"], fmt["periodo"],
                                  fmt["insc"],      fmt["renov"],
                                  fmt["usuario"],   fmt["data"], fmt["hora"],
                              ))
            self._ids_rows.append(r.get("id", -1))

        n = len(rows)
        self._lbl_count.configure(text=f"{n} registro{'s' if n != 1 else ''}")

    def _limpar_filtros(self):
        self._var_filtro.set("")
        self._var_ano.set("Todos")
        self._var_de.set("")
        self._var_ate.set("")
        self.carregar_historico()

    # ── Ordenação ─────────────────────────────────────────────────────────────
    def _ordenar(self, col: str):
        rows = [(self._tree.set(i, col), i) for i in self._tree.get_children()]
        reverse = (self._sort_col == col and not self._sort_rev)
        rows.sort(reverse=reverse)
        for idx, (_, item) in enumerate(rows):
            self._tree.move(item, "", idx)
            tag = "par" if idx % 2 == 0 else "impar"
            self._tree.item(item, tags=(tag,))
        self._sort_col = col
        self._sort_rev = reverse

    # ── Download XLS ──────────────────────────────────────────────────────────
    def _baixar_xls(self):
        sel = self._tree.selection()
        if not sel:
            messagebox.showinfo("Aviso", "Selecione um registro na tabela.")
            return

        idx        = int(sel[0])
        record_id  = self._ids_rows[idx]
        municipio  = self._tree.set(sel[0], "municipio")

        pasta = filedialog.askdirectory(title="Salvar XLS em...")
        if not pasta:
            return

        def _worker():
            try:
                row = self.controller.buscar_xls(record_id)
                if not row:
                    self.after(0, messagebox.showerror, "Erro",
                               "Registro não encontrado no banco.")
                    return

                mun    = row.get("municipio", municipio)
                p_ini  = str(row.get("periodo_ini", "")).replace("/", "-")
                p_fim  = str(row.get("periodo_fim", "")).replace("/", "-")

                salvos = []
                for chave, sufixo in [("xls_insc", "INSCRICAO"), ("xls_renov", "RENOVACAO")]:
                    dados = row.get(chave)
                    if dados:
                        nome_arq = f"{mun}_{sufixo}_{p_ini}_{p_fim}.xls"
                        caminho  = os.path.join(pasta, nome_arq)
                        with open(caminho, "wb") as fh:
                            fh.write(dados)
                        salvos.append(nome_arq)

                if salvos:
                    self.after(0, messagebox.showinfo, "Concluído",
                               f"Arquivos salvos:\n" + "\n".join(salvos))
                else:
                    self.after(0, messagebox.showwarning, "Aviso",
                               "Nenhum XLS encontrado para este registro.")
            except Exception as exc:
                self.after(0, messagebox.showerror, "Erro",
                           f"Falha ao baixar XLS:\n{exc}")

        threading.Thread(target=_worker, daemon=True).start()
