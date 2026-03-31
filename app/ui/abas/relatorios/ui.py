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

    # ── Geração ───────────────────────────────────────────────────────────────
    def _iniciar_geracao(self, municipios, data_inicio, data_fim,
                         pasta_download, pasta_relatorios, progress_cb, log_cb):
        n = len(municipios)
        if not n:
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
