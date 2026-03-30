# -*- coding: utf-8 -*-
"""Interface principal de Relatórios SEFAZ."""
import threading
from tkinter import messagebox
import customtkinter as ctk

from .controller   import RelatoriosController
from .icon_manager import IconManager
from .widgets      import StatCard               # ← agora existe em widgets/
from .tabs         import GerarTab, HistoricoTab # ← agora existe em tabs/


class RelatoriosUI(ctk.CTkFrame):
    """Frame raiz da interface de relatórios."""

    def __init__(self, parent, usuario: str):
        super().__init__(parent)
        self.usuario    = usuario
        self.controller = RelatoriosController(self, usuario)

        # Ícones
        self.icon_manager = IconManager()
        self.icons        = self.icon_manager.icons

        # municipio_vars é preenchido pela GerarTab e lido pelo controller
        self.municipio_vars: dict = {}

        self.configure(fg_color="#f5f7fc")
        self.pack(fill="both", expand=True)

        self._build()
        self._atualizar_stats()
        self.after(100, self.historico_tab.carregar_historico)

    # ── Montagem ──────────────────────────────────────────────────────────────
    def _build(self):
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=32, pady=24)

        self._build_header(wrap)
        self._build_stats(wrap)
        self._build_tabs(wrap)

    def _build_header(self, parent):
        hdr = ctk.CTkFrame(parent, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 20))

        left_hdr = ctk.CTkFrame(hdr, fg_color="transparent")
        left_hdr.pack(side="left")

        if self.icons.get("settings"):
            ctk.CTkLabel(
                left_hdr, text="", image=self.icons["settings"],
                width=32, height=32,
            ).pack(side="left", padx=(0, 12))

        title_frame = ctk.CTkFrame(left_hdr, fg_color="transparent")
        title_frame.pack(side="left")

        ctk.CTkLabel(
            title_frame, text="Relatórios SEFAZ",
            font=("Segoe UI", 24, "bold"), text_color="#1e2f3e",
        ).pack(anchor="w")
        ctk.CTkLabel(
            title_frame,
            text="Geração automática de relatórios de produtor rural",
            font=("Segoe UI", 11), text_color="#64748b",
        ).pack(anchor="w", pady=(2, 0))

        ctk.CTkButton(
            hdr, text=" Atualizar",
            image=self.icons.get("reload"), compound="left",
            width=120, height=36, corner_radius=8,
            fg_color="#d1fae5", hover_color="#e2e8f0",
            text_color="#10b981", font=("Segoe UI", 11, "bold"),
            command=self._atualizar_stats,
        ).pack(side="right")

    def _build_stats(self, parent):
        stats = ctk.CTkFrame(parent, fg_color="transparent")
        stats.pack(fill="x", pady=(0, 20))
        for i in range(4):
            stats.grid_columnconfigure(i, weight=1)

        self.sc_total = StatCard(stats, "total",      "Total Gerados",    icons=self.icons, cor="#3b82f6")
        self.sc_total.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.sc_muni  = StatCard(stats, "municipios", "Municípios",        icons=self.icons, cor="#f59e0b")
        self.sc_muni.grid(row=0, column=1, sticky="nsew", padx=4)

        self.sc_insc  = StatCard(stats, "inscricoes", "Total Inscrições",  icons=self.icons, cor="#10b981")
        self.sc_insc.grid(row=0, column=2, sticky="nsew", padx=4)

        self.sc_renov = StatCard(stats, "renovacoes", "Total Renovações",  icons=self.icons, cor="#ef4444")
        self.sc_renov.grid(row=0, column=3, sticky="nsew", padx=(8, 0))

    def _build_tabs(self, parent):
        tab_bar = ctk.CTkFrame(
            parent, fg_color="#ffffff", corner_radius=12,
            border_width=1, border_color="#e2e8f0",
        )
        tab_bar.pack(fill="x", pady=(0, 0))

        self.tab_btns: list = []

        tab_row = ctk.CTkFrame(tab_bar, fg_color="transparent")
        tab_row.pack(fill="x", padx=8, pady=6)

        for i, (icone, texto) in enumerate([
            ("⚙️", "Gerar Relatórios"),
            ("📋", "Histórico"),
        ]):
            btn = ctk.CTkButton(
                tab_row, text=f"{icone}  {texto}",
                font=("Segoe UI", 12, "bold"), height=36, corner_radius=8,
                fg_color="#2c6e9e" if i == 0 else "transparent",
                hover_color="#e8f0f8",
                text_color="#ffffff" if i == 0 else "#64748b",
                command=lambda idx=i: self._switch_tab(idx),
            )
            btn.pack(side="left", padx=(0, 6))
            self.tab_btns.append(btn)

        self.tab_container = ctk.CTkFrame(parent, fg_color="transparent")
        self.tab_container.pack(fill="both", expand=True, pady=(8, 0))
        self.tab_container.grid_columnconfigure(0, weight=1)
        self.tab_container.grid_rowconfigure(0, weight=1)

        # Aba Gerar
        self.gerar_tab = GerarTab(
            self.tab_container, self.controller, self.icons,
            on_gerar           = self._iniciar_geracao,
            on_atualizar_stats = self._atualizar_stats,
        )
        self.gerar_tab.grid(row=0, column=0, sticky="nsew")

        # Compartilha municipio_vars com o controller
        self.municipio_vars = self.gerar_tab.municipio_vars

        # Aba Histórico
        self.historico_tab = HistoricoTab(self.tab_container, self.controller, self.icons)
        self.historico_tab.grid(row=0, column=0, sticky="nsew")

        self._switch_tab(0)

    def _switch_tab(self, idx: int):
        frames = [self.gerar_tab, self.historico_tab]
        for i, (btn, frame) in enumerate(zip(self.tab_btns, frames)):
            if i == idx:
                btn.configure(fg_color="#2c6e9e", text_color="#ffffff")
                frame.tkraise()
            else:
                btn.configure(fg_color="transparent", text_color="#64748b")
        if idx == 1:
            self.historico_tab.carregar_historico()

<<<<<<< HEAD
    # ── aba Gerar ─────────────────────────────────────────────────────────────
    def _build_gerar(self, parent):
        parent.grid_columnconfigure(0, weight=2)
        parent.grid_columnconfigure(1, weight=3)
        parent.grid_rowconfigure(0, weight=1)

        # ── coluna esquerda ───────────────────────────────────────────────────
        esq = ctk.CTkFrame(
            parent, fg_color=_BRANCO, corner_radius=18,
            border_width=1, border_color=_BORDER,
        )
        esq.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=8)

        # Seção período
        _sec_titulo(esq, "📅", "Período", pad=(24, 24, 0, 10))

        for label, attr in [("Data Inicial", "_entry_ini"),
                             ("Data Final",   "_entry_fim")]:
            ctk.CTkLabel(
                esq, text=label,
                font=("Segoe UI", 11), text_color=_MUTED,
            ).pack(anchor="w", padx=24, pady=(8, 4))

            var   = ctk.StringVar()
            entry = ctk.CTkEntry(
                esq,
                textvariable=var,
                placeholder_text="DD/MM/AAAA",
                height=42, corner_radius=10,
                fg_color=_CINZA,
                border_color=_BORDER, border_width=1,
                font=("Segoe UI", 13),
                text_color=_SIDEBAR_BG,
            )
            entry.pack(fill="x", padx=24)
            setattr(self, attr, entry)
            setattr(self, attr + "_var", var)
            var.trace_add("write",
                          lambda *_, v=var, e=entry: self._mascara(v, e))

        # Atalhos rápidos de período
        atalhos = ctk.CTkFrame(esq, fg_color="transparent")
        atalhos.pack(fill="x", padx=24, pady=(10, 0))
        ctk.CTkLabel(atalhos, text="Atalhos:", font=("Segoe UI", 10),
                     text_color=_MUTED).pack(side="left", padx=(0, 8))
        for txt, fn in [("Este mês",  self._periodo_mes_atual),
                        ("Mês ant.",  self._periodo_mes_anterior),
                        ("Este ano",  self._periodo_ano_atual)]:
            ctk.CTkButton(
                atalhos, text=txt, width=75, height=26, corner_radius=6,
                fg_color=_VERDE_HOVER, hover_color=_BORDER,
                text_color=_VERDE_ESCURO, font=("Segoe UI", 10, "bold"),
                command=fn,
            ).pack(side="left", padx=(0, 6))

        # Separador
        ctk.CTkFrame(esq, height=1, fg_color=_BORDER).pack(
            fill="x", padx=24, pady=(18, 0))

        # Progresso
        _sec_titulo(esq, "📡", "Progresso", pad=(24, 16, 0, 8))
        self._prog = _ProgressoCard(esq)
        self._prog.pack(fill="x", padx=24)

        # Botão principal
        self._btn_gerar = ctk.CTkButton(
            esq, text="▶  Gerar Relatórios",
            height=50, corner_radius=14,
            fg_color=_VERDE, hover_color=_VERDE_DARK,
            font=("Segoe UI", 14, "bold"),
            text_color=_BRANCO,
            command=self._iniciar,
        )
        self._btn_gerar.pack(fill="x", padx=24, pady=(14, 0))

        # Separador
        ctk.CTkFrame(esq, height=1, fg_color=_BORDER).pack(
            fill="x", padx=24, pady=(18, 0))

        # Pastas de saída
        _sec_titulo(esq, "📁", "Pastas de saída", pad=(24, 16, 0, 8))
        self._lbl_pasta_dl = _PastaRow(
            esq, "Downloads:", self.pasta_download,
            lambda: self._escolher_pasta("download"),
        )
        self._lbl_pasta_dl.pack(fill="x", padx=24, pady=(0, 6))
        self._lbl_pasta_rel = _PastaRow(
            esq, "Relatórios:", self.pasta_relatorios,
            lambda: self._escolher_pasta("relatorios"),
        )
        self._lbl_pasta_rel.pack(fill="x", padx=24)

        # Separador
        ctk.CTkFrame(esq, height=1, fg_color=_BORDER).pack(
            fill="x", padx=24, pady=(18, 0))

        # Log
        log_hdr = ctk.CTkFrame(esq, fg_color="transparent")
        log_hdr.pack(fill="x", padx=24, pady=(14, 6))
        _sec_titulo(log_hdr, "📋", "Log de execução")
        ctk.CTkButton(
            log_hdr, text="Limpar", width=60, height=22, corner_radius=6,
            fg_color=_CINZA, hover_color=_BORDER,
            text_color=_MUTED, font=("Segoe UI", 10),
            command=self._limpar_log,
        ).pack(side="right")

        self._log_box = ctk.CTkTextbox(
            esq, height=140,
            fg_color=_CINZA,
            text_color=_SIDEBAR_BG,
            font=("Consolas", 10),
            state="disabled",
            border_width=1, border_color=_BORDER,
            corner_radius=10,
        )
        self._log_box.pack(fill="x", padx=24, pady=(0, 24))

        # ── coluna direita: municípios ────────────────────────────────────────
        dir_ = ctk.CTkFrame(
            parent, fg_color=_BRANCO, corner_radius=18,
            border_width=1, border_color=_BORDER,
        )
        dir_.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=8)

        # Cabeçalho
        muni_hdr = ctk.CTkFrame(dir_, fg_color="transparent")
        muni_hdr.pack(fill="x", padx=24, pady=(24, 0))
        _sec_titulo(muni_hdr, "🗺️", "Municípios")
        self._lbl_sel = ctk.CTkLabel(
            muni_hdr, text="0 selecionados",
            font=("Segoe UI", 11), text_color=_MUTED,
        )
        self._lbl_sel.pack(side="right")

        # Botões selecionar / desmarcar
        muni_btns = ctk.CTkFrame(dir_, fg_color="transparent")
        muni_btns.pack(fill="x", padx=24, pady=(10, 0))
        ctk.CTkButton(
            muni_btns, text="✓  Todos", width=90, height=30, corner_radius=8,
            fg_color=_VERDE, hover_color=_VERDE_DARK,
            text_color=_BRANCO, font=("Segoe UI", 11, "bold"),
            command=lambda: self._set_todos(True),
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            muni_btns, text="✕  Nenhum", width=90, height=30, corner_radius=8,
            fg_color=_CINZA, hover_color=_BORDER,
            text_color=_MUTED, font=("Segoe UI", 11, "bold"),
            command=lambda: self._set_todos(False),
        ).pack(side="left")

        # Campo de busca
        self._busca_var = ctk.StringVar()
        self._busca_var.trace_add("write", lambda *_: self._filtrar_municipios())
        busca_frame = ctk.CTkFrame(
            dir_, fg_color=_CINZA, corner_radius=10,
            border_width=1, border_color=_BORDER,
        )
        busca_frame.pack(fill="x", padx=24, pady=(10, 0))
        ctk.CTkLabel(busca_frame, text="🔍", font=("Segoe UI Emoji", 14),
                     text_color=_MUTED).pack(side="left", padx=(10, 4))
        ctk.CTkEntry(
            busca_frame,
            textvariable=self._busca_var,
            placeholder_text="Filtrar municípios...",
            height=36, corner_radius=8,
            fg_color="transparent", border_width=0,
            font=("Segoe UI", 12),
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))

        self._lbl_filtro = ctk.CTkLabel(
            dir_, text="", font=("Segoe UI", 10), text_color=_MUTED,
        )
        self._lbl_filtro.pack(anchor="e", padx=28)

        # Lista scrollável
        self._scroll_muni = ctk.CTkScrollableFrame(
            dir_, fg_color=_CINZA, corner_radius=10,
            border_width=1, border_color=_BORDER,
            scrollbar_button_color=_VERDE_HOVER,
            scrollbar_button_hover_color=_VERDE,
        )
        self._scroll_muni.pack(fill="both", expand=True, padx=24, pady=(4, 24))

        self._checkboxes: dict[str, ctk.CTkCheckBox] = {}
        for municipio in self.controller.obter_municipios():
            var = ctk.BooleanVar()
            cb  = ctk.CTkCheckBox(
                self._scroll_muni,
                text=municipio.nome,
                variable=var,
                command=self._verificar_todos,
                fg_color=_VERDE,
                hover_color=_VERDE_DARK,
                checkmark_color=_BRANCO,
                font=("Segoe UI", 11),
                text_color=_SIDEBAR_BG,
            )
            cb.pack(anchor="w", padx=12, pady=3)
            self.municipio_vars[municipio.nome] = var
            self._checkboxes[municipio.nome]    = cb

        self._verificar_todos()

    # ── aba Histórico ─────────────────────────────────────────────────────────
    def _build_historico(self, parent):
        ano_atual = str(datetime.today().year)

        # ── Painel de filtros ─────────────────────────────────────────────────
        filtros_card = ctk.CTkFrame(
            parent, fg_color=_BRANCO, corner_radius=14,
            border_width=1, border_color=_BORDER,
        )
        filtros_card.pack(fill="x", pady=(8, 8))

        filtros_inner = ctk.CTkFrame(filtros_card, fg_color="transparent")
        filtros_inner.pack(fill="x", padx=16, pady=10)

        # ── Filtro Ano ──────────────────────────────────────────────────────
        ctk.CTkLabel(filtros_inner, text="📅 Ano:",
                     font=("Segoe UI", 11, "bold"), text_color=_MUTED,
                     ).pack(side="left", padx=(0, 6))

        self._filt_ano = ctk.StringVar(value="Todos")
        anos = ["Todos"] + [str(a) for a in range(datetime.today().year, 2018, -1)]
        self._combo_ano = ctk.CTkOptionMenu(
            filtros_inner,
            values=anos,
            variable=self._filt_ano,
            width=90, height=32, corner_radius=8,
            fg_color=_CINZA, button_color=_VERDE,
            button_hover_color=_VERDE_DARK,
            text_color=_SIDEBAR_BG,
            font=("Segoe UI", 11),
            command=lambda _: self._carregar_historico(),
        )
        self._combo_ano.pack(side="left", padx=(0, 16))

        # ── Filtro Município ────────────────────────────────────────────────
        ctk.CTkLabel(filtros_inner, text="📍 Município:",
                     font=("Segoe UI", 11, "bold"), text_color=_MUTED,
                     ).pack(side="left", padx=(0, 6))

        self._hist_busca = ctk.StringVar()
        # trace removido — busca é disparada pelo botão Buscar ou ao trocar de aba
        ctk.CTkEntry(
            filtros_inner,
            textvariable=self._hist_busca,
            placeholder_text="Digite o município...",
            height=32, width=200, corner_radius=8,
            fg_color=_CINZA, border_color=_BORDER, border_width=1,
            font=("Segoe UI", 11),
        ).pack(side="left", padx=(0, 16))

        # ── Filtro Data início ───────────────────────────────────────────────
        ctk.CTkLabel(filtros_inner, text="🗓 De:",
                     font=("Segoe UI", 11, "bold"), text_color=_MUTED,
                     ).pack(side="left", padx=(0, 6))

        self._filt_de = ctk.StringVar()
        entry_de = ctk.CTkEntry(
            filtros_inner, textvariable=self._filt_de,
            placeholder_text="DD/MM/AAAA",
            height=32, width=110, corner_radius=8,
            fg_color=_CINZA, border_color=_BORDER, border_width=1,
            font=("Segoe UI", 11),
        )
        entry_de.pack(side="left", padx=(0, 8))
        self._filt_de.trace_add("write",
            lambda *_: self._mascara(self._filt_de, entry_de))

        # ── Filtro Data fim ──────────────────────────────────────────────────
        ctk.CTkLabel(filtros_inner, text="até:",
                     font=("Segoe UI", 11), text_color=_MUTED,
                     ).pack(side="left", padx=(0, 6))

        self._filt_ate = ctk.StringVar()
        entry_ate = ctk.CTkEntry(
            filtros_inner, textvariable=self._filt_ate,
            placeholder_text="DD/MM/AAAA",
            height=32, width=110, corner_radius=8,
            fg_color=_CINZA, border_color=_BORDER, border_width=1,
            font=("Segoe UI", 11),
        )
        entry_ate.pack(side="left", padx=(0, 16))
        self._filt_ate.trace_add("write",
            lambda *_: self._mascara(self._filt_ate, entry_ate))

        # ── Botões ───────────────────────────────────────────────────────────
        ctk.CTkButton(
            filtros_inner, text="↻  Buscar",
            width=90, height=32, corner_radius=8,
            fg_color=_VERDE, hover_color=_VERDE_DARK,
            text_color=_BRANCO, font=("Segoe UI", 11, "bold"),
            command=self._carregar_historico,
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            filtros_inner, text="✕  Limpar",
            width=80, height=32, corner_radius=8,
            fg_color=_CINZA, hover_color=_BORDER,
            text_color=_MUTED, font=("Segoe UI", 11),
            command=self._limpar_filtros,
        ).pack(side="left")

        # ── Status e contagem ────────────────────────────────────────────────
        status_row = ctk.CTkFrame(parent, fg_color="transparent")
        status_row.pack(fill="x", padx=2, pady=(0, 4))

        self._lbl_hist_status = ctk.CTkLabel(
            status_row, text="",
            font=("Segoe UI", 11), text_color=_MUTED, anchor="w",
        )
        self._lbl_hist_status.pack(side="left")

        # ── Tabela ───────────────────────────────────────────────────────────
        frame_tb = ctk.CTkFrame(
            parent, fg_color=_BRANCO, corner_radius=14,
            border_width=1, border_color=_BORDER,
        )
        frame_tb.pack(fill="both", expand=True)

        style = ttk.Style()
        style.configure(
            "Hist.Treeview",
            background=_BRANCO, fieldbackground=_BRANCO,
            foreground=_SIDEBAR_BG, rowheight=36,
            font=("Segoe UI", 11), borderwidth=0,
        )
        style.configure(
            "Hist.Treeview.Heading",
            background=_CINZA, foreground=_MUTED,
            font=("Segoe UI", 10, "bold"), relief="flat",
        )
        style.map(
            "Hist.Treeview",
            background=[("selected", _VERDE_HOVER)],
            foreground=[("selected", _SIDEBAR_BG)],
        )

        # Colunas: id oculto, município, período, insc, renov, usuário, gerado em, hora
        cols = ("municipio", "ano", "periodo", "insc", "renov",
                "usuario", "data", "hora")
        self._tree = ttk.Treeview(
            frame_tb, columns=cols, show="headings",
            style="Hist.Treeview", selectmode="browse",
        )
        hdrs = [
            ("municipio", "Município",     200),
            ("ano",       "Ano",            50),
            ("periodo",   "Período",       185),
            ("insc",      "Inscrições",     80),
            ("renov",     "Renovações",     80),
            ("usuario",   "Usuário",       100),
            ("data",      "Data Geração",  100),
            ("hora",      "Horário",        65),
        ]
        for col, titulo, w in hdrs:
            self._tree.heading(col, text=titulo,
                               command=lambda c=col: self._sort_tree(c))
            # periodo e municipio se expandem juntos; o resto é fixo
            self._tree.column(col, width=w, minwidth=40,
                              stretch=(col in ("municipio", "periodo")))

        vsb = ttk.Scrollbar(frame_tb, orient="vertical",
                            command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y", padx=(0, 8), pady=8)
        self._tree.pack(fill="both", expand=True, padx=8, pady=8)

        self._tree.tag_configure("par",   background=_BRANCO)
        self._tree.tag_configure("impar", background=_CINZA)
        self._tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        # Duplo clique também baixa
        self._tree.bind("<Double-1>", lambda _: self._baixar_xls())

        # ── Rodapé ───────────────────────────────────────────────────────────
        rodape = ctk.CTkFrame(parent, fg_color="transparent")
        rodape.pack(fill="x", pady=(8, 0))

        self._lbl_sel_hist = ctk.CTkLabel(
            rodape, text="Selecione um registro para baixar os XLS",
            font=("Segoe UI", 11), text_color=_MUTED,
        )
        self._lbl_sel_hist.pack(side="left")

        # Pasta de destino do download direto
        self._pasta_download_hist = ctk.StringVar(
            value=os.path.join(os.getcwd(), "downloads_historico"))
        pasta_frame = ctk.CTkFrame(rodape, fg_color=_CINZA, corner_radius=8,
                                   border_width=1, border_color=_BORDER)
        pasta_frame.pack(side="right", padx=(0, 8))

        self._lbl_pasta_hist = ctk.CTkLabel(
            pasta_frame,
            text=self._trunc_path(self._pasta_download_hist.get()),
            font=("Segoe UI", 10), text_color=_SIDEBAR_BG,
        )
        self._lbl_pasta_hist.pack(side="left", padx=(10, 4), pady=4)

        ctk.CTkButton(
            pasta_frame, text="…", width=26, height=22, corner_radius=6,
            fg_color=_VERDE_HOVER, hover_color=_BORDER,
            text_color=_VERDE_ESCURO, font=("Segoe UI", 11, "bold"),
            command=self._escolher_pasta_hist,
        ).pack(side="right", padx=(0, 6), pady=4)

        ctk.CTkButton(
            rodape, text="⬇  Baixar XLS",
            height=40, corner_radius=12,
            fg_color=_VERDE, hover_color=_VERDE_DARK,
            font=("Segoe UI", 12, "bold"),
            text_color=_BRANCO,
            command=self._baixar_xls,
        ).pack(side="right", padx=(0, 8))

    # ── Iniciar geração ───────────────────────────────────────────────────────
    def _iniciar(self):
        from .controller import MUNICIPIOS as _MUN
        municipios = [(n, _MUN[n])
                      for n, v in self.municipio_vars.items() if v.get()]

        if not municipios:
=======
    # ── Geração ───────────────────────────────────────────────────────────────
    def _iniciar_geracao(self, municipios, data_inicio, data_fim,
                         pasta_download, pasta_relatorios, progress_cb, log_cb):
        n = len(municipios)
        if not n:
>>>>>>> f4a3e3b (.)
            messagebox.showwarning("Aviso", "Selecione ao menos um município.")
            return

        if not messagebox.askyesno(
            "Confirmar geração",
            f"Gerar relatórios para {n} município(s)?\n\nPeríodo: {data_inicio} → {data_fim}",
        ):
            return

        self.gerar_tab.desabilitar_botao()
        self.gerar_tab.progresso.reset()
        log_cb(f"Iniciando para {n} município(s)...", "info")
        log_cb(f"Período: {data_inicio} → {data_fim}", "info")

        def _ok():
            self.after(0, self.gerar_tab.habilitar_botao)
            self.after(0, self.gerar_tab.progresso_concluido)
            self.after(0, self._atualizar_stats)
            self.after(0, lambda: log_cb(f"✓ Concluído — {n} município(s)!", "sucesso"))
            self.after(0, lambda: messagebox.showinfo(
                "Concluído", f"Relatórios gerados!\n{n} município(s) processado(s)."))

        def _err(msg):
            self.after(0, self.gerar_tab.habilitar_botao)
            self.after(0, self.gerar_tab.progresso_erro)
            self.after(0, lambda: log_cb(f"✕ ERRO: {msg}", "erro"))
            self.after(0, lambda: messagebox.showerror("Erro", msg))

        self.controller.gerar_relatorios(
            municipios       = municipios,
            data_inicio      = data_inicio,
            data_fim         = data_fim,
            pasta_download   = pasta_download,
            pasta_relatorios = pasta_relatorios,
            callback_sucesso = _ok,
            callback_erro    = _err,
            progress_cb      = lambda a, t, nm: self.after(0, progress_cb, a, t, nm),
            log_cb           = log_cb,
        )

<<<<<<< HEAD
    # ── Histórico ─────────────────────────────────────────────────────────────
    def _carregar_historico(self):
        if not hasattr(self, "_tree") or not hasattr(self, "_lbl_hist_status"):
            return

        self._lbl_hist_status.configure(text="Carregando...", text_color=_MUTED)

        municipio = self._hist_busca.get().strip() if hasattr(self, "_hist_busca") else ""
        ano       = self._filt_ano.get()           if hasattr(self, "_filt_ano")   else "Todos"
        de        = self._filt_de.get().strip()    if hasattr(self, "_filt_de")    else ""
        ate       = self._filt_ate.get().strip()   if hasattr(self, "_filt_ate")   else ""

        def _worker():
            try:
                rows = self.controller.buscar_historico(municipio)
                print(f"[Historico] banco retornou {len(rows)} linha(s) | ano={ano!r} de={de!r} ate={ate!r}")
                rows = self._filtrar_rows(rows, ano, de, ate)
                print(f"[Historico] apos filtro: {len(rows)} linha(s)")
                self.after(0, self._preencher_tabela, rows)
            except Exception as exc:
                import traceback
                traceback.print_exc()
                msg = f"Erro ao carregar historico: {exc}"
                print(f"[Historico] {msg}")
                self.after(0, lambda m=msg: self._lbl_hist_status.configure(
                    text=m, text_color=_VERMELHO))

        threading.Thread(target=_worker, daemon=True).start()

    @staticmethod
    def _filtrar_rows(rows: list, ano: str, de: str, ate: str) -> list:
        resultado = []
        for r in rows:
            criado = r.get("criado_em", "")  # "DD/MM/AAAA HH:MM"

            if ano and ano != "Todos":
                try:
                    ano_reg = criado.split("/")[2].split(" ")[0].strip()
                    if ano_reg != ano:
                        continue
                except Exception:
                    continue

            if de and len(de) == 10:
                try:
                    d, m, a  = de.split("/")
                    dt_de    = datetime(int(a), int(m), int(d))
                    d2, m2, resto = criado.split("/")
                    dt_reg   = datetime(int(resto[:4]), int(m2), int(d2))
                    if dt_reg < dt_de:
                        continue
                except Exception:
                    pass

            if ate and len(ate) == 10:
                try:
                    d, m, a  = ate.split("/")
                    dt_ate   = datetime(int(a), int(m), int(d))
                    d2, m2, resto = criado.split("/")
                    dt_reg   = datetime(int(resto[:4]), int(m2), int(d2))
                    if dt_reg > dt_ate:
                        continue
                except Exception:
                    pass

            resultado.append(r)
        return resultado

    def _preencher_tabela(self, rows: list):
        for item in self._tree.get_children():
            self._tree.delete(item)

        if not rows:
            self._tree.insert("", "end",
                              values=("Nenhum registro encontrado.",
                                      "—", "—", "—", "—", "—", "—", "—"),
                              tags=("par",))
            self._lbl_hist_status.configure(
                text="Nenhum registro encontrado.", text_color=_MUTED)
            return

        self._lbl_hist_status.configure(
            text=f"{len(rows)} registro(s) encontrado(s).",
            text_color=_VERDE_ESCURO,
        )

        for i, r in enumerate(rows):
            criado  = r.get("criado_em", "—")
            partes  = criado.split(" ") if " " in criado else [criado, "—"]
            data_str = partes[0]
            hora_str = partes[1] if len(partes) > 1 else "—"
            try:
                ano_str = data_str.split("/")[2]
            except Exception:
                ano_str = "—"

            periodo = (
                f"{r.get('periodo_ini', '—').strip()}  →  "
                f"{r.get('periodo_fim', '—').strip()}"
            )
            tag = "par" if i % 2 == 0 else "impar"

            self._tree.insert(
                "", "end", iid=str(r["id"]),
                values=(
                    r.get("municipio",  "—"),
                    ano_str,
                    periodo,
                    r.get("total_insc",  0),
                    r.get("total_renov", 0),
                    r.get("usuario",    "—"),
                    data_str,
                    hora_str,
                ),
                tags=(tag,),
            )

    def _on_tree_select(self, _=None):
        sel = self._tree.selection()
        if sel:
            vals = self._tree.item(sel[0], "values")
            if vals and vals[0] != "Nenhum registro encontrado.":
                municipio = vals[0]
                data      = vals[6] if len(vals) > 6 else "—"
                hora      = vals[7] if len(vals) > 7 else "—"
                self._lbl_sel_hist.configure(
                    text=f"✓  {municipio}  —  {data}  {hora}  |  duplo clique ou ⬇ Baixar XLS",
                    text_color=_VERDE_ESCURO,
                )
        else:
            self._lbl_sel_hist.configure(
                text="Selecione um registro para baixar os XLS",
                text_color=_MUTED,
            )

    def _limpar_filtros(self):
        if hasattr(self, "_hist_busca"):  self._hist_busca.set("")
        if hasattr(self, "_filt_ano"):    self._filt_ano.set("Todos")
        if hasattr(self, "_filt_de"):     self._filt_de.set("")
        if hasattr(self, "_filt_ate"):    self._filt_ate.set("")
        self._carregar_historico()

    def _escolher_pasta_hist(self):
        pasta = filedialog.askdirectory(title="Pasta de destino para XLS")
        if pasta:
            self._pasta_download_hist.set(pasta)
            self._lbl_pasta_hist.configure(text=self._trunc_path(pasta))

    def _sort_tree(self, col: str):
        rows = [(self._tree.set(k, col), k)
                for k in self._tree.get_children("")]
        rows.sort(reverse=getattr(self, f"_sort_{col}_rev", False))
        setattr(self, f"_sort_{col}_rev",
                not getattr(self, f"_sort_{col}_rev", False))
        for idx, (_, k) in enumerate(rows):
            self._tree.move(k, "", idx)
            self._tree.item(k, tags=("par" if idx % 2 == 0 else "impar",))

    def _baixar_xls(self):
        sel = self._tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um registro na tabela.")
            return
        try:
            rec_id = int(sel[0])
        except ValueError:
            messagebox.showwarning("Aviso", "Registro inválido — linha sem dados.")
            return

        vals      = self._tree.item(sel[0], "values")
        municipio = vals[0] if vals else "relatorio"
        data_str  = vals[6] if len(vals) > 6 else ""
        hora_str  = vals[7] if len(vals) > 7 else ""

        # Pasta de destino — usa a configurada no rodapé ou pede ao usuário
        if hasattr(self, "_pasta_download_hist"):
            pasta_dest = self._pasta_download_hist.get()
        else:
            pasta_dest = os.path.join(os.getcwd(), "downloads_historico")

        os.makedirs(pasta_dest, exist_ok=True)

        def _worker():
            try:
                dados = self.controller.buscar_xls(rec_id)
                if not dados:
                    self.after(0, messagebox.showwarning,
                               "Aviso", "Nenhum XLS encontrado para este registro.")
                    return
                self.after(0, lambda d=dados: self._salvar_xls_direto(
                    d, municipio, data_str, hora_str, pasta_dest))
            except Exception as exc:
                import traceback
                traceback.print_exc()
                self.after(0, messagebox.showerror, "Erro ao buscar XLS", str(exc))

        threading.Thread(target=_worker, daemon=True).start()

    def _salvar_xls_direto(self, dados: dict, municipio: str,
                           data_str: str, hora_str: str, pasta_dest: str):
        """Salva INSCRICAO e RENOVACAO diretamente na pasta — sem diálogo."""
        sufixo = municipio.replace(" ", "_")
        if data_str and data_str != "—":
            try:
                d, m, a = data_str.split("/")
                sufixo += f"_{a}{m}{d}"
            except Exception:
                pass
        if hora_str and hora_str != "—":
            sufixo += f"_{hora_str.replace(':', '')}"

        salvos, erros = [], []

        for tipo, chave in [("INSCRICAO", "xls_insc"),
                            ("RENOVACAO", "xls_renov")]:
            conteudo = dados.get(chave)
            if not conteudo:
                continue
            if isinstance(conteudo, memoryview):
                conteudo = bytes(conteudo)

            caminho = os.path.join(pasta_dest, f"{tipo}_{sufixo}.xls")
            try:
                with open(caminho, "wb") as fh:
                    fh.write(conteudo)
                salvos.append(caminho)
                try:
                    self._log(f"✓ Salvo: {caminho}", "sucesso")
                except Exception:
                    pass
            except Exception as exc:
                erros.append(f"{tipo}: {exc}")

        if salvos:
            lista = "\n".join(f"  • {os.path.basename(p)}" for p in salvos)
            messagebox.showinfo(
                "Download concluído",
                f"{len(salvos)} arquivo(s) salvo(s) em:\n{pasta_dest}\n\n{lista}",
            )
        if erros:
            messagebox.showerror("Erros ao salvar", "\n".join(erros))
        if not salvos and not erros:
            messagebox.showwarning("Sem dados",
                                   "Este registro não possui arquivos XLS salvos.")

    # ── Helpers de seleção ────────────────────────────────────────────────────
    @staticmethod
    def _trunc_path(p: str, n: int = 34) -> str:
        return f"…{p[-(n-1):]}" if len(p) > n else p
    def _set_todos(self, estado: bool):
        for v in self.municipio_vars.values():
            v.set(estado)
        self._atualizar_contador()

    def _verificar_todos(self):
        self._atualizar_contador()

    def _atualizar_contador(self):
        sel   = sum(1 for v in self.municipio_vars.values() if v.get())
        total = len(self.municipio_vars)
        self._lbl_sel.configure(
            text=f"{sel} / {total} selecionados",
            text_color=_VERDE_ESCURO if sel else _MUTED,
        )

    def _filtrar_municipios(self):
        termo    = self._busca_var.get().lower()
        visiveis = 0
        for nome, cb in self._checkboxes.items():
            if termo in nome.lower():
                cb.pack(anchor="w", padx=12, pady=3)
                visiveis += 1
            else:
                cb.pack_forget()
        if termo:
            self._lbl_filtro.configure(
                text=f'{visiveis} resultado(s) para "{termo}"',
                text_color=_VERDE_ESCURO if visiveis else _VERMELHO,
            )
        else:
            self._lbl_filtro.configure(text="")

    # ── Atalhos de período ────────────────────────────────────────────────────
    def _set_periodo(self, ini: str, fim: str):
        self._entry_ini_var.set(ini)
        self._entry_fim_var.set(fim)

    def _periodo_mes_atual(self):
        hoje = datetime.today()
        self._set_periodo(
            hoje.replace(day=1).strftime("%d/%m/%Y"),
            hoje.strftime("%d/%m/%Y"),
        )

    def _periodo_mes_anterior(self):
        import calendar
        hoje     = datetime.today()
        primeiro = hoje.replace(day=1)
        mes      = primeiro.month - 1 or 12
        ano      = primeiro.year if primeiro.month > 1 else primeiro.year - 1
        ultimo   = calendar.monthrange(ano, mes)[1]
        self._set_periodo(
            f"01/{mes:02d}/{ano}",
            f"{ultimo:02d}/{mes:02d}/{ano}",
        )

    def _periodo_ano_atual(self):
        ano = datetime.today().year
        self._set_periodo(f"01/01/{ano}", f"31/12/{ano}")

    # ── Escolher pasta ────────────────────────────────────────────────────────
    def _escolher_pasta(self, tipo: str):
        pasta = filedialog.askdirectory(title="Selecionar pasta")
        if not pasta:
            return
        if tipo == "download":
            self.pasta_download = pasta
            self._lbl_pasta_dl.set_path(pasta)
        else:
            self.pasta_relatorios = pasta
            self._lbl_pasta_rel.set_path(pasta)

=======
>>>>>>> f4a3e3b (.)
    # ── Stats ─────────────────────────────────────────────────────────────────
    def _atualizar_stats(self):
        def _worker():
            try:
                s = self.controller.estatisticas()
                self.after(0, self.sc_total.set, s.get("total",      0))
                self.after(0, self.sc_muni.set,  s.get("municipios", 0))
                self.after(0, self.sc_insc.set,  s.get("insc",       0))
                self.after(0, self.sc_renov.set, s.get("renov",      0))
            except Exception:
                pass
        threading.Thread(target=_worker, daemon=True).start()
