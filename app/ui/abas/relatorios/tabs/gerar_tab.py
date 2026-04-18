# -*- coding: utf-8 -*-
"""Aba de geração de relatórios SEFAZ."""
import os
import calendar
from PyQt6.QtWidgets import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import *

from ..widgets   import ProgressCard, PastaRow, LogBox
from ..utils     import DateUtils


class GerarTab(ctk.CTkFrame):
    """Aba principal para configurar e disparar a geração de relatórios."""

    _DEFAULT_DOWNLOAD    = os.path.join(os.path.expanduser("~"), "Downloads", "SEFAZ_XLS")
    _DEFAULT_RELATORIOS  = os.path.join(os.path.expanduser("~"), "Documents", "Relatorios Gerados")

    def __init__(self, parent, controller, icons, on_gerar, on_atualizar_stats):
        super().__init__(parent, fg_color="transparent")
        self.controller        = controller
        self.icons             = icons
        self._on_gerar         = on_gerar
        self._on_atualizar     = on_atualizar_stats

        self.municipio_vars: dict[str, ctk.BooleanVar] = {}
        self._pasta_download   = self._DEFAULT_DOWNLOAD
        self._pasta_relatorios = self._DEFAULT_RELATORIOS
        self._aplicando_ini    = [False]
        self._aplicando_fim    = [False]

        self._build()
        self._carregar_municipios()

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # ── Coluna esquerda: configurações ────────────────────────────────────
        left = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=12,
                            border_width=1, border_color="#e2e8f0")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=0)
        left.grid_columnconfigure(0, weight=1)

        # Período
        per_frame = ctk.CTkFrame(left, fg_color="transparent")
        per_frame.pack(fill="x", padx=16, pady=(16, 8))

        ctk.CTkLabel(per_frame, text="Período", font=("Segoe UI", 13, "bold"),
                     text_color="#1e2f3e").pack(anchor="w")

        # Linha datas
        dates_row = ctk.CTkFrame(per_frame, fg_color="transparent")
        dates_row.pack(fill="x", pady=(8, 0))

        self._var_ini = ctk.StringVar()
        self._var_fim = ctk.StringVar()

        for col, (label, var, flag) in enumerate([
            ("De", self._var_ini, self._aplicando_ini),
            ("Até", self._var_fim, self._aplicando_fim),
        ]):
            f = ctk.CTkFrame(dates_row, fg_color="transparent")
            f.pack(side="left", fill="x", expand=True, padx=(0 if col == 0 else 8, 0))
            ctk.CTkLabel(f, text=label, font=("Segoe UI", 10),
                         text_color="#64748b").pack(anchor="w")
            ent = ctk.CTkEntry(f, textvariable=var, placeholder_text="DD/MM/AAAA",
                               height=34, corner_radius=8,
                               fg_color="#f5f7fc", border_color="#e2e8f0")
            ent.pack(fill="x")
            var.trace_add("write",
                          lambda *_, v=var, e=ent, fl=flag:
                              DateUtils.aplicar_mascara(v, e, fl))

        # Atalhos de período
        atalhos = ctk.CTkFrame(per_frame, fg_color="transparent")
        atalhos.pack(fill="x", pady=(8, 0))
        for txt, fn in [
            ("Mês atual",    DateUtils.periodo_mes_atual),
            ("Mês anterior", DateUtils.periodo_mes_anterior),
            ("Ano atual",    DateUtils.periodo_ano_atual),
        ]:
            ctk.CTkButton(
                atalhos, text=txt, height=26, corner_radius=6,
                font=("Segoe UI", 10), fg_color="#e8f0f8",
                hover_color="#d1e0f0", text_color="#2c6e9e",
                command=lambda f=fn: self._aplicar_periodo(f()),
            ).pack(side="left", padx=(0, 4))

        # Separador
        ctk.CTkFrame(left, height=1, fg_color="#e2e8f0").pack(fill="x", padx=16, pady=8)

        # Pastas
        pasta_frame = ctk.CTkFrame(left, fg_color="transparent")
        pasta_frame.pack(fill="x", padx=16, pady=(0, 8))

        ctk.CTkLabel(pasta_frame, text="Pastas", font=("Segoe UI", 13, "bold"),
                     text_color="#1e2f3e").pack(anchor="w", pady=(0, 6))

        self._row_download = PastaRow(
            pasta_frame, "Download:", self._pasta_download,
            command=self._escolher_download, icons=self.icons,
        )
        self._row_download.pack(fill="x", pady=(0, 6))

        self._row_relatorios = PastaRow(
            pasta_frame, "Relatórios:", self._pasta_relatorios,
            command=self._escolher_relatorios, icons=self.icons,
        )
        self._row_relatorios.pack(fill="x")

        # Separador
        ctk.CTkFrame(left, height=1, fg_color="#e2e8f0").pack(fill="x", padx=16, pady=8)

        # Municípios
        muni_frame = ctk.CTkFrame(left, fg_color="transparent")
        muni_frame.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        muni_header = ctk.CTkFrame(muni_frame, fg_color="transparent")
        muni_header.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(muni_header, text="Municípios", font=("Segoe UI", 13, "bold"),
                     text_color="#1e2f3e").pack(side="left")

        self._var_todos = ctk.BooleanVar()
        ctk.CTkCheckBox(
            muni_header, text="Todos", variable=self._var_todos,
            font=("Segoe UI", 11), fg_color="#2c6e9e",
            command=self._toggle_todos,
        ).pack(side="right")

        # Campo de busca
        self._var_busca = ctk.StringVar()
        busca_entry = ctk.CTkEntry(
            muni_frame, textvariable=self._var_busca,
            placeholder_text="🔍  Filtrar município...",
            height=32, corner_radius=8,
            fg_color="#f5f7fc", border_color="#e2e8f0",
        )
        busca_entry.pack(fill="x", pady=(0, 6))
        self._var_busca.trace_add("write", lambda *_: self._filtrar_checkboxes())

        self._scroll = ctk.CTkScrollableFrame(
            muni_frame, fg_color="#f5f7fc",
            border_width=1, border_color="#e2e8f0",
        )
        self._scroll.pack(fill="both", expand=True)
        self._checkboxes: dict[str, ctk.CTkCheckBox] = {}

        # ── Painel direito: progresso e log ───────────────────────────────────
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)

        self.progresso = ProgressCard(right, icons=self.icons)
        self.progresso.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self._log = LogBox(right)
        self._log.grid(row=1, column=0, sticky="nsew", pady=(0, 8))

        self._btn_gerar = ctk.CTkButton(
            right, text="🚀  Gerar Relatórios",
            height=46, corner_radius=10,
            fg_color="#2c6e9e", hover_color="#1e5a8a",
            font=("Segoe UI", 14, "bold"),
            command=self._iniciar,
        )
        self._btn_gerar.grid(row=2, column=0, sticky="ew")

    # ── Municípios ────────────────────────────────────────────────────────────
    def _carregar_municipios(self):
        for widget in self._scroll.winfo_children():
            widget.destroy()
        self.municipio_vars.clear()
        self._checkboxes.clear()

        for m in self.controller.obter_municipios():
            var = ctk.BooleanVar(value=False)
            cb  = ctk.CTkCheckBox(
                self._scroll, text=m.nome, variable=var,
                font=("Segoe UI", 11), fg_color="#2c6e9e",
                command=self._atualizar_todos_checkbox,
            )
            cb.pack(anchor="w", pady=1)
            self.municipio_vars[m.nome] = var
            self._checkboxes[m.nome]    = cb

    def _filtrar_checkboxes(self):
        busca = self._var_busca.get().strip().upper()
        for nome, cb in self._checkboxes.items():
            if busca in nome:
                cb.pack(anchor="w", pady=1)
            else:
                cb.pack_forget()

    def _toggle_todos(self):
        sel = self._var_todos.get()
        for var in self.municipio_vars.values():
            var.set(sel)

    def _atualizar_todos_checkbox(self):
        todos = all(v.get() for v in self.municipio_vars.values())
        self._var_todos.set(todos)

    # ── Pastas ────────────────────────────────────────────────────────────────
    def _escolher_download(self):
        p = filedialog.askdirectory(title="Pasta de download XLS")
        if p:
            self._pasta_download = p
            self._row_download.set_path(p)

    def _escolher_relatorios(self):
        p = filedialog.askdirectory(title="Pasta de relatórios")
        if p:
            self._pasta_relatorios = p
            self._row_relatorios.set_path(p)

    # ── Período ───────────────────────────────────────────────────────────────
    def _aplicar_periodo(self, periodo: tuple):
        ini, fim = periodo
        self._var_ini.set(ini)
        self._var_fim.set(fim)

    # ── Geração ───────────────────────────────────────────────────────────────
    def _iniciar(self):
        municipios = [
            (nome, cod)
            for nome, var in self.municipio_vars.items()
            if var.get()
            for cod in [self.controller.obter_municipios()]  # obtem código
        ]
        # monta lista (nome, codigo) corretamente
        from ..controller import MUNICIPIOS as _MUN
        municipios = [
            (nome, _MUN[nome])
            for nome, var in self.municipio_vars.items()
            if var.get()
        ]

        data_inicio = self._var_ini.get().strip()
        data_fim    = self._var_fim.get().strip()

        self._on_gerar(
            municipios       = municipios,
            data_inicio      = data_inicio,
            data_fim         = data_fim,
            pasta_download   = self._pasta_download,
            pasta_relatorios = self._pasta_relatorios,
            progress_cb      = self.progresso.update,
            log_cb           = self._log.log,
        )

    # ── API pública (chamada por ui.py) ───────────────────────────────────────
    def desabilitar_botao(self):
        self._btn_gerar.configure(state="disabled", text="⏳  Gerando...")

    def habilitar_botao(self):
        self._btn_gerar.configure(state="normal", text="🚀  Gerar Relatórios")

    def progresso_concluido(self):
        self.progresso.concluido()

    def progresso_erro(self):
        self.progresso.erro()

