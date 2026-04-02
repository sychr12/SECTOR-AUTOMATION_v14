# -*- coding: utf-8 -*-
"""
AnexarUI — interface principal do módulo Anexar.
Design corporativo com ícones personalizados.
"""
import threading
import os
import tempfile
import webbrowser
from tkinter import messagebox, filedialog, ttk
from PIL import Image
from datetime import datetime
from .errors import ErrorsTable
import customtkinter as ctk

from .controller import AnexarController
from .repository import AnexarRepository
from .services import AnexarService
from .views import (
    CarteirasTable, EmAnaliseTable, HistoricoTable, LogTable,
    ProntosView,
    safe_print,
)


# ── Paleta Corporativa ──────────────────────────────────────────────────────────
_PRIMARY_DARK    = "#0a2540"
_PRIMARY         = "#1a4b6e"
_ACCENT          = "#2c6e9e"
_ACCENT_DARK     = "#1e4a6e"
_ACCENT_LIGHT    = "#e8f0f8"
_BRANCO          = "#ffffff"
_CINZA_BG        = "#f8fafc"
_CINZA_BORDER    = "#e2e8f0"
_CINZA_MEDIO     = "#5a6e8a"
_CINZA_TEXTO     = "#1e2f3e"
_VERDE_STATUS    = "#10b981"
_VERDE_DARK      = "#059669"
_VERDE_LIGHT     = "#d1fae5"
_AMARELO         = "#f59e0b"
_VERMELHO        = "#ef4444"
_VERMELHO_DARK   = "#dc2626"
_AZUL            = "#3b82f6"
_AZUL_DARK       = "#2563eb"
_MUTED           = "#5a6e8a"
_ICON_COLOR      = "#1e293b"


class IconManager:
    """Gerenciador de ícones para a interface de anexos"""

    def __init__(self):
        self.icons = {}
        self.icons_dir = None
        self._find_icons_path()

    def _find_icons_path(self):
        """Encontra o caminho correto para a pasta de ícones"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        possible_paths = [
            os.path.join(current_dir, "..", "..", "images", "icons", "anexos"),
            os.path.join(current_dir, "..", "images", "icons", "anexos"),
            os.path.join(os.path.dirname(current_dir), "images", "icons", "anexos"),
            r"C:\Users\Administrador\Documents\SECTOR AUTOMATION_v14\images\icons\anexos",
            r"Q:\ARQUIVOS CPCPR\SECTOR AUTOMATION\images\icons\anexos",
        ]

        for path in possible_paths:
            if os.path.exists(path):
                self.icons_dir = path
                print(f"[IconManager] ✅ Ícones encontrados em: {self.icons_dir}")
                return

        self.icons_dir = possible_paths[0] if possible_paths else ""
        print(f"[IconManager] ⚠️ Pasta de ícones não encontrada: {self.icons_dir}")

    def load_icon(self, filename, size=(24, 24), colorize_to=None):
        """Carrega um ícone da pasta e aplica cor se necessário"""
        if not self.icons_dir:
            return None

        try:
            path = os.path.join(self.icons_dir, filename)
            if os.path.exists(path):
                img = Image.open(path)
                img = img.resize(size, Image.Resampling.LANCZOS)

                if colorize_to:
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')

                    data = img.getdata()
                    new_data = []

                    if isinstance(colorize_to, tuple):
                        target_r, target_g, target_b = colorize_to
                    else:
                        hex_color = colorize_to.lstrip('#')
                        target_r, target_g, target_b = tuple(
                            int(hex_color[i:i + 2], 16) for i in (0, 2, 4)
                        )

                    for item in data:
                        r, g, b, a = item
                        if a > 0:
                            new_data.append((target_r, target_g, target_b, a))
                        else:
                            new_data.append((r, g, b, a))

                    img.putdata(new_data)

                return ctk.CTkImage(light_image=img, dark_image=img, size=size)
        except Exception as e:
            print(f"[IconManager] Erro ao carregar {filename}: {e}")
        return None

    def setup_icons(self):
        """Configura todos os ícones com cor preta"""
        icons_config = {
            "analise":   ("analise.png",   (22, 22), _ICON_COLOR),
            "check":     ("check.png",     (22, 22), _ICON_COLOR),
            "clip":      ("clip.png",      (32, 32), _ICON_COLOR),
            "delete":    ("delete.png",    (20, 20), _ICON_COLOR),
            "error":     ("error.png",     (26, 26), _ICON_COLOR),
            "historico": ("historico.png", (22, 22), _ICON_COLOR),
            "keep":      ("keep.png",      (22, 22), _ICON_COLOR),
            "logs":      ("logs.png",      (22, 22), _ICON_COLOR),
            "pause":     ("pause.png",     (20, 20), _ICON_COLOR),
            "play":      ("play.png",      (20, 20), _ICON_COLOR),
            "reload":    ("reload.png",    (20, 20), _ICON_COLOR),
            "relogio":   ("relogio.png",   (26, 26), _ICON_COLOR),
            "successo":  ("successo.png",  (26, 26), _ICON_COLOR),
            "task":      ("task.png",      (22, 22), _ICON_COLOR),
            "todos":     ("todos.png",     (26, 26), _ICON_COLOR),
            "pendentes": ("relogio.png",   (26, 26), _ICON_COLOR),
            "com_pdf":   ("check.png",     (26, 26), _ICON_COLOR),
            "sucesso":   ("successo.png",  (26, 26), _ICON_COLOR),
            "erros":     ("error.png",     (26, 26), _ICON_COLOR),
        }

        for name, (filename, size, color) in icons_config.items():
            self.icons[name] = self.load_icon(filename, size, color)

        return self.icons

    def get(self, name):
        """Retorna um ícone pelo nome"""
        return self.icons.get(name)


class AnexarUI(ctk.CTkFrame):

    def __init__(self, master, usuario=None):
        super().__init__(master)
        self.usuario    = usuario
        self.controller = AnexarController(usuario)
        self.repository = AnexarRepository()
        self._sucesso   = 0
        self._erro      = 0

        self.tree_erros = None

        # Inicializar gerenciador de ícones
        self.icon_manager = IconManager()
        self.icons = self.icon_manager.setup_icons()

        # Referências às tabelas
        self.lista_cart   = None
        self.tree_log     = None
        self.tree_hist    = None
        self.tree_analise = None
        self._prontos_view: ProntosView | None = None

        self.controller.set_callbacks(
            log_callback=self._log,
            status_callback=self._set_status,
            update_buttons_callback=self._set_botoes,
        )

        self.configure(fg_color=_CINZA_BG)
        self._build()
        self._recarregar()

    # ── Layout ───────────────────────────────────────────────────────────────

    def _build(self):
        """Monta a interface principal"""
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=32, pady=28)

        self._build_header(main_container)
        self._build_barra_acao(main_container)
        self._build_info_cards(main_container)
        self._build_stat_cards(main_container)

        separator = ctk.CTkFrame(main_container, height=1, fg_color=_CINZA_BORDER)
        separator.pack(fill="x", pady=(20, 20))

        self._build_notebook(main_container)

    def _build_header(self, parent):
        """Cabeçalho com título"""
        hdr = ctk.CTkFrame(parent, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 20))

        title = ctk.CTkFrame(hdr, fg_color="transparent")
        title.pack(side="left")

        if self.icons.get("clip"):
            ctk.CTkLabel(
                title, text="", image=self.icons["clip"],
                width=36, height=36
            ).pack(side="left", padx=(0, 12))

        title_text = ctk.CTkFrame(title, fg_color="transparent")
        title_text.pack(side="left")

        ctk.CTkLabel(title_text, text="Anexar Processos",
                     font=("Segoe UI", 26, "bold"),
                     text_color=_CINZA_TEXTO).pack(anchor="w")
        ctk.CTkLabel(title_text, text="SIGED | Carteiras Digitais",
                     font=("Segoe UI", 11),
                     text_color=_MUTED).pack(anchor="w", pady=(2, 0))

        self._status_badge = ctk.CTkLabel(
            hdr, text="● Pronto",
            font=("Segoe UI", 11, "bold"), text_color=_VERDE_STATUS,
            fg_color=_BRANCO, corner_radius=20, padx=14, pady=6
        )
        self._status_badge.pack(side="right")

    def _build_barra_acao(self, parent):
        """Barra de ações com botões"""
        bar = ctk.CTkFrame(parent, fg_color="transparent")
        bar.pack(fill="x", pady=(0, 20))

        btns = ctk.CTkFrame(bar, fg_color="transparent")
        btns.pack(side="left")

        # Botão Iniciar
        self.btn_iniciar = ctk.CTkButton(
            btns, text=" Iniciar Anexação",
            image=self.icons.get("play"), compound="left",
            command=self._iniciar,
            height=44, corner_radius=10,
            fg_color=_VERDE_STATUS, hover_color=_VERDE_DARK,
            font=("Segoe UI", 13, "bold"), text_color=_BRANCO
        )
        self.btn_iniciar.pack(side="left")

        # Botão Parar
        self.btn_parar = ctk.CTkButton(
            btns, text=" Parar",
            image=self.icons.get("pause"), compound="left",
            command=self._parar,
            height=44, corner_radius=10,
            fg_color=_VERMELHO, hover_color=_VERMELHO_DARK,
            font=("Segoe UI", 13, "bold"), text_color=_BRANCO,
            state="disabled"
        )
        self.btn_parar.pack(side="left", padx=(12, 0))

        # Botão Recarregar
        ctk.CTkButton(
            btns, text=" Recarregar",
            image=self.icons.get("reload"), compound="left",
            command=self._recarregar,
            height=44, corner_radius=10,
            fg_color=_CINZA_BG, hover_color=_CINZA_BORDER,
            font=("Segoe UI", 13), text_color=_CINZA_TEXTO
        ).pack(side="left", padx=(12, 0))

        # Botão Limpar Log
        ctk.CTkButton(
            btns, text=" Limpar Log",
            image=self.icons.get("delete"), compound="left",
            command=self._limpar_log,
            height=44, corner_radius=10,
            fg_color=_CINZA_BG, hover_color=_CINZA_BORDER,
            font=("Segoe UI", 13), text_color=_CINZA_TEXTO
        ).pack(side="left", padx=(12, 0))

        # Separador vertical
        ctk.CTkFrame(bar, width=1, height=32, fg_color=_CINZA_BORDER).pack(
            side="left", padx=20
        )

        # Filtros
        filtros = ctk.CTkFrame(bar, fg_color="transparent")
        filtros.pack(side="left")

        ctk.CTkLabel(filtros, text="Filtrar:",
                     font=("Segoe UI", 11), text_color=_MUTED).pack(side="left")

        self._filtro = ctk.StringVar(value="pendentes")

        ctk.CTkRadioButton(
            filtros, text=" Pendentes", variable=self._filtro, value="pendentes",
            font=("Segoe UI", 11), text_color=_CINZA_TEXTO,
            fg_color=_ACCENT, command=self._recarregar,
        ).pack(side="left", padx=(12, 0))

        ctk.CTkRadioButton(
            filtros, text=" Todas", variable=self._filtro, value="todas",
            font=("Segoe UI", 11), text_color=_CINZA_TEXTO,
            fg_color=_ACCENT, command=self._recarregar,
        ).pack(side="left", padx=(12, 0))

        # Search Bar
        search_frame = ctk.CTkFrame(
            bar, fg_color=_BRANCO, corner_radius=10,
            border_width=1, border_color=_CINZA_BORDER
        )
        search_frame.pack(side="right", padx=(20, 0))

        ctk.CTkLabel(
            search_frame, text="🔍",
            font=("Segoe UI", 14), text_color=_MUTED
        ).pack(side="left", padx=(12, 6))

        self._search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Buscar por nome ou CPF...",
            height=36, width=240, corner_radius=8,
            fg_color="transparent", border_width=0,
            font=("Segoe UI", 12)
        )
        self._search_entry.pack(side="left", fill="x", expand=True, padx=(0, 12))
        self._search_entry.bind(
            "<KeyRelease>", lambda e: self._on_search(self._search_entry.get())
        )

    def _build_info_cards(self, parent):
        """Cards de informações com design elegante"""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(0, 20))

        for i in range(3):
            row.columnconfigure(i, weight=1)

        # Card Banco de Dados
        self._card_db = ctk.CTkFrame(
            row, fg_color=_BRANCO, corner_radius=12,
            border_width=1, border_color=_CINZA_BORDER
        )
        self._card_db.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        db_inner = ctk.CTkFrame(self._card_db, fg_color="transparent")
        db_inner.pack(fill="x", padx=20, pady=16)

        top = ctk.CTkFrame(db_inner, fg_color="transparent")
        top.pack(fill="x")

        if self.icons.get("keep"):
            ctk.CTkLabel(
                top, text="", image=self.icons["keep"],
                width=24, height=24
            ).pack(side="left")

        ctk.CTkLabel(
            top, text="Banco de Dados",
            font=("Segoe UI", 11, "bold"),
            text_color=_MUTED
        ).pack(side="left", padx=(8, 0))

        self._lbl_db = ctk.CTkLabel(
            db_inner, text="Conectando...",
            font=("Segoe UI", 14, "bold"),
            text_color=_CINZA_TEXTO
        )
        self._lbl_db.pack(anchor="w", pady=(12, 0))

        # Card Tabela
        card_tabela = ctk.CTkFrame(
            row, fg_color=_BRANCO, corner_radius=12,
            border_width=1, border_color=_CINZA_BORDER
        )
        card_tabela.grid(row=0, column=1, sticky="nsew", padx=12)

        tabela_inner = ctk.CTkFrame(card_tabela, fg_color="transparent")
        tabela_inner.pack(fill="x", padx=20, pady=16)

        top2 = ctk.CTkFrame(tabela_inner, fg_color="transparent")
        top2.pack(fill="x")

        if self.icons.get("task"):
            ctk.CTkLabel(
                top2, text="", image=self.icons["task"],
                width=24, height=24
            ).pack(side="left")

        ctk.CTkLabel(
            top2, text="Tabela",
            font=("Segoe UI", 11, "bold"),
            text_color=_MUTED
        ).pack(side="left", padx=(8, 0))

        ctk.CTkLabel(
            tabela_inner, text="carteiras_digitais",
            font=("Segoe UI", 14, "bold"),
            text_color=_CINZA_TEXTO
        ).pack(anchor="w", pady=(12, 0))

        # Card Credencial SEFAZ
        self._card_cred = ctk.CTkFrame(
            row, fg_color=_BRANCO, corner_radius=12,
            border_width=1, border_color=_CINZA_BORDER
        )
        self._card_cred.grid(row=0, column=2, sticky="nsew", padx=(12, 0))

        cred_inner = ctk.CTkFrame(self._card_cred, fg_color="transparent")
        cred_inner.pack(fill="x", padx=20, pady=16)

        top3 = ctk.CTkFrame(cred_inner, fg_color="transparent")
        top3.pack(fill="x")

        if self.icons.get("check"):
            ctk.CTkLabel(
                top3, text="", image=self.icons["check"],
                width=24, height=24
            ).pack(side="left")

        ctk.CTkLabel(
            top3, text="Credencial SEFAZ",
            font=("Segoe UI", 11, "bold"),
            text_color=_MUTED
        ).pack(side="left", padx=(8, 0))

        self._lbl_cred = ctk.CTkLabel(
            cred_inner, text="...",
            font=("Segoe UI", 14, "bold"),
            text_color=_CINZA_TEXTO
        )
        self._lbl_cred.pack(anchor="w", pady=(12, 0))

    def _build_stat_cards(self, parent):
        """Cards de estatísticas com design elegante"""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(0, 20))

        for i in range(5):
            row.columnconfigure(i, weight=1)

        cards_config = [
            ("total",    "Total",     _AZUL,         "todos"),
            ("pendente", "Pendentes", _AMARELO,       "pendentes"),
            ("gerado",   "Com PDF",   _VERDE_STATUS,  "com_pdf"),
            ("sucesso",  "Sucesso",   _VERDE_STATUS,  "sucesso"),
            ("erro",     "Erros",     _VERMELHO,      "erros"),
        ]

        self._stat_cards = {}

        for i, (key, titulo, cor, icon_key) in enumerate(cards_config):
            card = ctk.CTkFrame(
                row, fg_color=_BRANCO, corner_radius=12,
                border_width=1, border_color=_CINZA_BORDER
            )
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 8, 0))

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=20, pady=16)

            top = ctk.CTkFrame(inner, fg_color="transparent")
            top.pack(fill="x")

            if self.icons.get(icon_key):
                ctk.CTkLabel(
                    top, text="", image=self.icons[icon_key],
                    width=28, height=28
                ).pack(side="left")

            lbl_valor = ctk.CTkLabel(
                top, text="0",
                font=("Segoe UI", 32, "bold"),
                text_color=cor
            )
            lbl_valor.pack(side="right")
            self._stat_cards[key] = lbl_valor

            ctk.CTkLabel(
                inner, text=titulo,
                font=("Segoe UI", 12, "bold"),
                text_color=_MUTED
            ).pack(anchor="w", pady=(12, 0))

            ctk.CTkFrame(
                inner, height=2, fg_color=cor, corner_radius=1
            ).pack(fill="x", pady=(8, 0))

    def _build_notebook(self, parent):
        """Abas da interface"""
        style = ttk.Style()
        style.configure("Anx.TNotebook", background=_CINZA_BG, borderwidth=0)
        style.configure("Anx.TNotebook.Tab",
                        background=_CINZA_BG, foreground=_MUTED,
                        font=("Segoe UI", 11), padding=(24, 10))
        style.map("Anx.TNotebook.Tab",
                  background=[("selected", _BRANCO)],
                  foreground=[("selected", _ACCENT)])

        nb = ttk.Notebook(parent, style="Anx.TNotebook")
        nb.pack(fill="both", expand=True)
        self._nb = nb

        def _aba(texto):
            f = ctk.CTkFrame(nb, fg_color=_BRANCO, corner_radius=0)
            nb.add(f, text=texto)
            return f

        # Aba Carteiras
        aba_carteiras = _aba(" Carteiras ")
        self.lista_cart, c1 = CarteirasTable.criar(
            aba_carteiras,
            self._baixar_pdf,
            self._visualizar_pdf,
            self._excluir_pdf,
        )
        c1.pack(fill="both", expand=True, padx=12, pady=12)

        # Aba Em Análise
        aba_analise = _aba(" Em Análise ")
        self.tree_analise, c2 = EmAnaliseTable.criar(aba_analise)
        c2.pack(fill="both", expand=True, padx=12, pady=12)

        # Aba Histórico
        aba_historico = _aba(" Histórico ")
        self.tree_hist, c3 = HistoricoTable.criar(aba_historico)
        c3.pack(fill="both", expand=True, padx=12, pady=12)

        # Aba Log
        aba_log = _aba(" Log ")
        self.tree_log, c4 = LogTable.criar(aba_log)
        c4.pack(fill="both", expand=True, padx=12, pady=12)

        # Aba Erros
        aba_erros = _aba(" Erros ")
        self.tree_erros, c5 = ErrorsTable.criar(aba_erros)
        c5.pack(fill="both", expand=True, padx=12, pady=12)

        # Aba Prontos
        aba_prontos = _aba(" Prontos ")
        self._prontos_view = ProntosView(aba_prontos, self.repository)
        self._prontos_view.pack(fill="both", expand=True, padx=12, pady=12)

    # ── Dados ─────────────────────────────────────────────────────────────────

    def _recarregar(self):
        """Recarrega todos os dados"""
        def _worker():
            try:
                cred   = self.repository.buscar_credencial_sefaz()
                rows   = (self.repository.buscar_carteiras_pendentes()
                          if self._filtro.get() == "pendentes"
                          else self.repository.buscar_todas_carteiras())
                hist   = self.repository.buscar_historico_anexados()
                analise = self.repository.buscar_em_analise()
                stats  = self.repository.estatisticas()

                self.after(0, self._lbl_cred.configure,
                           {"text": cred['usuario'] if cred else "NENHUMA ATIVA"})
                self.after(0, self._lbl_db.configure,
                           {"text": f"Conectado · {len(rows)} registro(s)"})
                self.after(0, CarteirasTable.carregar,
                           self.lista_cart, rows,
                           self._baixar_pdf, self._visualizar_pdf, self._excluir_pdf)
                self.after(0, HistoricoTable.carregar, self.tree_hist, hist)
                self.after(0, EmAnaliseTable.carregar, self.tree_analise, analise)
                self.after(0, self._atualizar_stats,
                           int(stats.get("total") or 0),
                           int(stats.get("pendentes") or 0),
                           int(stats.get("gerados") or 0))
                if self._prontos_view:
                    self.after(0, self._prontos_view.recarregar)
            except Exception as exc:
                self.after(0, self._lbl_db.configure, {"text": f"⚠️ Erro: {exc}"})
                self.after(0, messagebox.showerror, "Erro de conexão", str(exc))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_search(self, query):
        """Busca por nome ou CPF"""
        if not query.strip():
            self._recarregar()
            return

        def _worker():
            try:
                rows = (self.repository.buscar_carteiras_pendentes()
                        if self._filtro.get() == "pendentes"
                        else self.repository.buscar_todas_carteiras())
                q = query.lower()
                filtrados = [r for r in rows
                             if q in str(r.get("nome", "")).lower()
                             or q in str(r.get("cpf", ""))]
                self.after(0, CarteirasTable.carregar,
                           self.lista_cart, filtrados,
                           self._baixar_pdf, self._visualizar_pdf, self._excluir_pdf)
                self.after(0, self._lbl_db.configure,
                           {"text": f"Conectado · {len(filtrados)} resultado(s)"})
            except Exception as exc:
                self.after(0, messagebox.showerror, "Erro", str(exc))

        threading.Thread(target=_worker, daemon=True).start()

    def _atualizar_stats(self, total, pendente, gerado):
        """Atualiza os cards de estatísticas"""
        self._stat_cards["total"].configure(text=str(total))
        self._stat_cards["pendente"].configure(text=str(pendente))
        self._stat_cards["gerado"].configure(text=str(gerado))
        self._stat_cards["sucesso"].configure(text=str(self._sucesso))
        self._stat_cards["erro"].configure(text=str(self._erro))

    # ── PDF ───────────────────────────────────────────────────────────────────

    def _baixar_pdf(self, record_id: int):
        """Baixa PDF do registro"""
        def _worker():
            try:
                res = self.repository.buscar_pdf_por_id(record_id)
                if not res:
                    self.after(0, messagebox.showwarning,
                               "Aviso", "PDF ainda não gerado para este registro.")
                    return
                nome, dados = res
                self.after(0, self._salvar_dialog, nome, dados)
            except Exception as exc:
                self.after(0, messagebox.showerror, "Erro", str(exc))

        threading.Thread(target=_worker, daemon=True).start()

    def _salvar_dialog(self, nome: str, dados: bytes):
        """Salva o PDF com diálogo"""
        destino = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf"), ("Todos", "*.*")],
            initialfile=nome, title="Salvar carteira como...")
        if not destino:
            return
        with open(destino, "wb") as f:
            f.write(dados)
        messagebox.showinfo("Salvo", f"✅ PDF salvo em:\n{destino}")

    def _visualizar_pdf(self, record_id: int):
        """Visualiza o PDF do registro em um visualizador externo"""
        def _worker():
            try:
                res = self.repository.buscar_pdf_por_id(record_id)
                if not res:
                    self.after(0, messagebox.showwarning,
                               "Aviso", "PDF ainda não gerado para este registro.")
                    return
                nome, dados = res

                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(dados)
                    tmp_path = tmp.name

                webbrowser.open(tmp_path)

                # Remove o arquivo temporário após 5 segundos
                self.after(
                    5000,
                    lambda: os.unlink(tmp_path) if os.path.exists(tmp_path) else None,
                )
            except Exception as exc:
                self.after(0, messagebox.showerror, "Erro", str(exc))

        threading.Thread(target=_worker, daemon=True).start()

    def _excluir_pdf(self, record_id: int, nome: str):
        """Exclui o PDF do registro"""
        if not messagebox.askyesno(
            "Confirmação", f"Tem certeza que deseja excluir o PDF '{nome}'?"
        ):
            return

        def _worker():
            try:
                sucesso = self.repository.excluir_pdf_por_id(record_id)
                if sucesso:
                    self.after(0, lambda: messagebox.showinfo(
                        "Excluído", f"✅ PDF '{nome}' excluído com sucesso."))
                    self.after(0, self._recarregar)
                else:
                    self.after(0, lambda: messagebox.showwarning(
                        "Aviso", f"Nenhum PDF encontrado para '{nome}'."))
            except Exception as exc:
                self.after(0, lambda: messagebox.showerror("Erro", str(exc)))

        threading.Thread(target=_worker, daemon=True).start()

    # ── Callbacks do controller ───────────────────────────────────────────────

    def _log(self, status, mensagem, tag="info"):
        """Adiciona mensagem ao log"""
        safe_print(f"[{status}] {mensagem}")
        self.after(0, LogTable.add, self.tree_log, status, mensagem, tag)

        if tag.lower() == "sucesso":
            self._sucesso += 1
            self.after(0, lambda v=self._sucesso:
                       self._stat_cards["sucesso"].configure(text=str(v)))
            if self._prontos_view:
                self.after(500, self._prontos_view.recarregar)
        elif tag.lower() == "erro":
            self._erro += 1
            self.after(0, lambda v=self._erro:
                       self._stat_cards["erro"].configure(text=str(v)))
            if self.tree_erros is not None:
                self.after(0, ErrorsTable.adicionar, self.tree_erros,
                           status, mensagem, "erro")

    def _set_status(self, texto, tipo="info"):
        """Atualiza o status badge"""
        cores = {
            "primary": _ACCENT,
            "success": _VERDE_STATUS,
            "error":   _VERMELHO,
            "warning": _AMARELO,
            "info":    _MUTED,
        }
        self.after(0, self._status_badge.configure,
                   {"text": f"● {texto}",
                    "text_color": cores.get(tipo, _MUTED)})

    def _set_botoes(self, habilitar_iniciar, habilitar_parar):
        """Habilita/desabilita botões"""
        self.after(0, self.btn_iniciar.configure,
                   {"state": "normal" if habilitar_iniciar else "disabled"})
        self.after(0, self.btn_parar.configure,
                   {"state": "normal" if habilitar_parar else "disabled"})

    # ── Ações ─────────────────────────────────────────────────────────────────

    def _iniciar(self):
        """Inicia o processamento"""
        if self.controller.verificar_processando():
            messagebox.showwarning("Aviso", "Processamento já em andamento!")
            return

        faltantes = AnexarService.verificar_dependencias()
        if faltantes:
            messagebox.showerror(
                "Dependências faltando",
                "Instale os seguintes pacotes:\n" + "\n".join(faltantes)
            )
            return

        if not self.controller.iniciar_processamento():
            return

        self._sucesso = 0
        self._erro    = 0
        self._stat_cards["sucesso"].configure(text="0")
        self._stat_cards["erro"].configure(text="0")
        if self._nb:
            self._nb.select(3)  # Seleciona a aba de Log

        threading.Thread(
            target=self.controller.executar_processamento, daemon=True
        ).start()

    def _parar(self):
        """Para o processamento"""
        self.controller.parar_processamento()

    def _limpar_log(self):
        """Limpa o log"""
        LogTable.limpar(self.tree_log)
        self._set_status("Pronto", "info")

    def destroy(self):
        """Destrói a interface"""
        self.controller.parar_processamento()
        super().destroy()