# -*- coding: utf-8 -*-
"""Histórico de memorandos — design corporativo com filtros e cores"""

import customtkinter as ctk
from tkinter import messagebox
from app.theme import AppTheme
import hashlib
from datetime import datetime

from app.ui.abas.memorando.views.municipio_selector import MunicipioSelector
from app.ui.abas.memorando.municipios import lista_formatada

from app.ui.abas.memorando.style import (
    FILTER_RADIUS,
    FILTER_BORDER,
    FILTER_HOVER,
    FILTER_INPUT_BG,
    FILTER_DROPDOWN_BG,
)

# Cores vibrantes para cada código de município
UNLOC_CORES = {
    "ALV": "#10b981",
    "AMT": "#3b82f6",
    "ANA": "#8b5cf6",
    "ANO": "#f59e0b",
    "APU": "#ec489a",
    "ATN": "#14b8a6",
    "ATZ": "#ef4444",
    "BAZ": "#84cc16",
    "BAR": "#06b6d4",
    "BJC": "#a855f7",
    "BER": "#d946ef",
    "BVR": "#f43f5e",
    "BOA": "#0ea5e9",
    "BBA": "#eab308",
    "CAP": "#22c55e",
    "CAN": "#6366f1",
    "CAF": "#e11d48",
    "CAR": "#ea580c",
    "CAZ": "#0891b2",
    "CIZ": "#c026d3",
    "COD": "#059669",
    "ERN": "#0284c7",
    "ENV": "#9333ea",
    "FBA": "#d97706",
    "GAJ": "#db2777",
    "HIA": "#0d9488",
    "IPX": "#e11d48",
    "IRB": "#7c3aed",
    "ITA": "#c2410c",
    "ITR": "#16a34a",
    "ITG": "#2563eb",
    "JPR": "#7e22ce",
    "JUR": "#ca8a04",
    "JUT": "#be185d",
    "LBR": "#0e7490",
    "MPU": "#4f46e5",
    "MQR": "#b45309",
    "MAO": "#10b981",
    "MAO-ZL": "#34d399",
    "MNX": "#f97316",
    "MTS-ATZ": "#fbbf24",
    "MRA": "#ef4444",
    "MBZ": "#3b82f6",
    "NMD": "#8b5cf6",
    "ITR-NRO": "#06b6d4",
    "MNX-MTP": "#84cc16",
    "LBR-VE": "#14b8a6",
    "VRC": "#a855f7",
    "PRF-BNA": "#ec489a",
    "VLD": "#f59e0b",
    "RLD": "#d946ef",
    "NON": "#0ea5e9",
    "NAR": "#eab308",
    "NAP": "#22c55e",
    "PAR": "#6366f1",
    "PUI": "#e11d48",
    "PRF": "#ea580c",
    "RPE": "#0891b2",
    "SIR": "#c026d3",
    "SAI": "#059669",
    "SJL": "#0284c7",
    "SPO": "#9333ea",
    "SSU": "#d97706",
    "SUL-CAN": "#db2777",
    "SLV": "#0d9488",
    "TBT": "#7c3aed",
    "TPA": "#c2410c",
    "TFF": "#16a34a",
    "TNT": "#2563eb",
    "UAN": "#7e22ce",
    "URC": "#ca8a04",
    "UCB": "#be185d",
    "FOZ": "#0e7490",
}

# Cores alternativas para UNLOC não listados (usar como fallback)
CORES_ALTERNATIVAS = [
    "#10b981", "#3b82f6", "#8b5cf6", "#f59e0b", "#ec489a",
    "#14b8a6", "#ef4444", "#84cc16", "#06b6d4", "#a855f7",
    "#d946ef", "#f43f5e", "#0ea5e9", "#eab308", "#22c55e",
    "#6366f1", "#e11d48", "#ea580c", "#0891b2", "#c026d3",
    "#059669", "#0284c7", "#9333ea", "#d97706", "#db2777",
    "#0d9488", "#7c3aed", "#c2410c", "#16a34a", "#2563eb",
    "#7e22ce", "#ca8a04", "#be185d", "#0e7490", "#4f46e5",
    "#b45309", "#34d399", "#f97316", "#fbbf24",
]


def get_unloc_color(unloc: str) -> str:
    """Retorna uma cor consistente para cada UNLOC"""
    if not unloc or unloc == "—":
        return "#64748b"
    
    unloc_upper = unloc.upper()
    
    # Extrair apenas o código principal (antes do - ou /)
    # Exemplos: "MAO-ZL" -> "MAO", "ITR-NRO" -> "ITR", "PR-123" -> "PR"
    if "-" in unloc_upper:
        codigo_principal = unloc_upper.split("-")[0]
    elif "/" in unloc_upper:
        codigo_principal = unloc_upper.split("/")[0]
    else:
        codigo_principal = unloc_upper
    
    # Se o código principal tiver mais de 3 letras, tenta pegar só as 3 primeiras
    if len(codigo_principal) > 3:
        # Tenta buscar o código completo primeiro
        if codigo_principal in UNLOC_CORES:
            return UNLOC_CORES[codigo_principal]
        # Se não achar, tenta só as 3 primeiras letras
        codigo_principal = codigo_principal[:3]
    
    # Busca a cor pelo código principal
    if codigo_principal in UNLOC_CORES:
        return UNLOC_CORES[codigo_principal]
    
    # Fallback: gerar cor baseada no hash
    hash_val = int(hashlib.md5(codigo_principal.encode()).hexdigest()[:8], 16)
    return CORES_ALTERNATIVAS[hash_val % len(CORES_ALTERNATIVAS)]


class HistoricoMemorandoView(ctk.CTkToplevel):
    
    def __init__(self, parent, controller,
                 on_visualizar=None, on_baixar=None, icons=None):
        super().__init__(parent)
        self.controller    = controller
        self.on_visualizar = on_visualizar
        self.on_baixar     = on_baixar
        self.icons         = icons or {}
        self._configure_window()
        self._create_widgets()
        self._carregar_dados()

    def _configure_window(self):
        self.title("Histórico de Memorandos")
        self.geometry("1200x750")
        self.configure(fg_color=AppTheme.BG_APP)
        self.grab_set()

        w, h = 1200, 750
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _create_widgets(self):
        root = ctk.CTkFrame(self, fg_color="transparent")
        root.pack(fill="both", expand=True, padx=36, pady=32)

        self._build_header(root)
        self._build_filters(root)
        
        separator = ctk.CTkFrame(root, height=1, fg_color=AppTheme.BG_CARD)
        separator.pack(fill="x", pady=(0, 20))

        self.lista_scroll = ctk.CTkScrollableFrame(
            root,
            fg_color="transparent",
            scrollbar_button_color=AppTheme.BG_CARD,
            scrollbar_button_hover_color=AppTheme.TXT_MUTED,
        )
        self.lista_scroll.pack(fill="both", expand=True)
        
    def _limpar_filtros(self):
        self.pesquisa_var.set("")
        self.municipio_selector.set("Todos")
        self.ano_var.set("Todos")
        self.ordem_var.set("Recentes")
        self._carregar_dados()

    def _build_header(self, parent):
        hdr = ctk.CTkFrame(parent, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 24))

        left = ctk.CTkFrame(hdr, fg_color="transparent")
        left.pack(side="left")
        
        if self.icons.get("history"):
            icon_label = ctk.CTkLabel(
                left, text="", image=self.icons["history"],
                width=28, height=28
            )
            icon_label.pack(side="left", padx=(0, 12))
        else:
            ctk.CTkLabel(
                left, text="📋", font=("Segoe UI", 28),
                text_color=AppTheme.TXT_MAIN
            ).pack(side="left", padx=(0, 12))
        
        title_frame = ctk.CTkFrame(left, fg_color="transparent")
        title_frame.pack(side="left")
        
        ctk.CTkLabel(title_frame, text="Histórico de Memorandos",
                     font=("Segoe UI", 26, "bold"),
                     text_color=AppTheme.TXT_MAIN).pack(anchor="w")
        
        ctk.CTkLabel(title_frame,
                     text="Visualize, abra e baixe memorandos gerados",
                     font=("Segoe UI", 12),
                     text_color=AppTheme.TXT_MUTED).pack(anchor="w", pady=(4, 0))

        status_badge = ctk.CTkLabel(
            hdr, text="Lista de memorandos",
            font=("Segoe UI", 14, "bold"), text_color=AppTheme.TXT_MUTED,
            fg_color=AppTheme.BG_CARD, corner_radius=20, padx=14, pady=6
        )
        status_badge.pack(side="right")

    def _build_filters(self, parent):
        bar = ctk.CTkFrame(parent, fg_color=AppTheme.BG_CARD, corner_radius=16)
        bar.pack(fill="x", pady=(0, 20))

        HEIGHT = 38
        PAD_X = 8
        PAD_Y = 10
        FONT = ("Segoe UI", 12)
        FONT_BOLD = ("Segoe UI", 11, "bold")

        if self.icons.get("search"):
            ctk.CTkLabel(
                bar,
                text="",
                image=self.icons["search"],
                width=18,
                height=18
            ).pack(side="left", padx=(16, 4), pady=PAD_Y)
            
        ctk.CTkLabel(bar, text="Buscar",
                     font=FONT_BOLD,
                     text_color=AppTheme.TXT_MUTED).pack(side="left", padx=(0, 6), pady=PAD_Y)

        self.pesquisa_var = ctk.StringVar()
        self.pesquisa_var.trace_add("write", lambda *_: self._carregar_dados())
        
        ctk.CTkEntry(
            bar,
            textvariable=self.pesquisa_var,
            placeholder_text="Número do memo ou UNLOC...",
            height=HEIGHT,
            corner_radius=FILTER_RADIUS,
            fg_color=FILTER_INPUT_BG,
            border_color=FILTER_BORDER,
            border_width=1,
            font=FONT,
            text_color=AppTheme.TXT_MAIN,
        ).pack(side="left", fill="x", expand=True, padx=(0, PAD_X), pady=PAD_Y)
        
        if self.icons.get("location"):
            ctk.CTkLabel(
                bar,
                text="",
                image=self.icons["location"],
                width=18,
                height=18
            ).pack(side="left", padx=(12, 4), pady=PAD_Y)
            
        ctk.CTkLabel(bar, text="Município",
                     font=FONT_BOLD,
                     text_color=AppTheme.TXT_MUTED).pack(side="left", padx=(0, 6), pady=PAD_Y)

        self.municipio_var = ctk.StringVar(value="Todos")

        lista_municipios = ["Todos"] + lista_formatada()

        self.municipio_selector = MunicipioSelector(
            bar,
            values=lista_municipios,
            default="Todos",
            width=200,
            height=HEIGHT,
            corner_radius=FILTER_RADIUS,
            fg_color=FILTER_INPUT_BG,
            text_color=AppTheme.TXT_MAIN,
            button_color=FILTER_INPUT_BG,
            button_hover_color=FILTER_HOVER,
            dropdown_fg_color=FILTER_DROPDOWN_BG,
            border_color=FILTER_BORDER,
            border_width=1,
            font=FONT,
            placeholder="Município",
            command=lambda _: self._carregar_dados(),
        )
        self.municipio_selector.pack(side="left", padx=(0, PAD_X), pady=PAD_Y)

        if self.icons.get("calendar_search"):
            ctk.CTkLabel(
                bar,
                text="",
                image=self.icons["calendar_search"],
                width=18,
                height=18
            ).pack(side="left", padx=(12, 4), pady=PAD_Y)
                    
        ctk.CTkLabel(bar, text="Ano",
                     font=FONT_BOLD,
                     text_color=AppTheme.TXT_MUTED).pack(side="left", padx=(0, 6), pady=PAD_Y)

        self.ano_var = ctk.StringVar(value="Todos")

        ok, anos = self.controller.listar_anos() if hasattr(self.controller, 'listar_anos') else (False, [])
        lista_anos = ["Todos"] + anos if ok and anos else ["Todos"]

        ano_wrap = ctk.CTkFrame(
            bar,
            width=100,
            height=HEIGHT,
            fg_color=FILTER_INPUT_BG,
            border_width=1,
            border_color=FILTER_BORDER,
            corner_radius=FILTER_RADIUS
        )
        ano_wrap.pack(side="left", padx=(0, PAD_X), pady=PAD_Y)
        ano_wrap.pack_propagate(False)

        self.ano_menu = ctk.CTkOptionMenu(
            ano_wrap,
            values=lista_anos,
            variable=self.ano_var,
            width=96,
            height=HEIGHT - 4,
            fg_color=FILTER_INPUT_BG,
            button_color=FILTER_INPUT_BG,
            button_hover_color=FILTER_HOVER,
            dropdown_fg_color=FILTER_DROPDOWN_BG,
            text_color=AppTheme.TXT_MAIN,
            dropdown_text_color=AppTheme.TXT_MAIN,
            corner_radius=FILTER_RADIUS - 2,
            font=FONT,
            dynamic_resizing=False,
            command=lambda _: self._carregar_dados()
        )
        self.ano_menu.place(relx=0.5, rely=0.5, anchor="center")
        
        if self.icons.get("filter"):
            ctk.CTkLabel(
                bar,
                text="",
                image=self.icons["filter"],
                width=18,
                height=18
            ).pack(side="left", padx=(12, 4), pady=PAD_Y)
            
        ctk.CTkLabel(bar, text="Ordem",
                     font=FONT_BOLD,
                     text_color=AppTheme.TXT_MUTED).pack(side="left", padx=(0, 6), pady=PAD_Y)

        self.ordem_var = ctk.StringVar(value="Recentes")

        ordem_wrap = ctk.CTkFrame(
            bar,
            width=120,
            height=HEIGHT,
            fg_color=FILTER_INPUT_BG,
            border_width=1,
            border_color=FILTER_BORDER,
            corner_radius=FILTER_RADIUS
        )
        ordem_wrap.pack(side="left", padx=(0, PAD_X), pady=PAD_Y)
        ordem_wrap.pack_propagate(False)

        self.ordem_menu = ctk.CTkOptionMenu(
            ordem_wrap,
            values=["Recentes", "Antigos"],
            variable=self.ordem_var,
            width=116,
            height=HEIGHT - 4,
            fg_color=FILTER_INPUT_BG,
            button_color=FILTER_INPUT_BG,
            button_hover_color=FILTER_HOVER,
            dropdown_fg_color=FILTER_DROPDOWN_BG,
            text_color=AppTheme.TXT_MAIN,
            dropdown_text_color=AppTheme.TXT_MAIN,
            corner_radius=FILTER_RADIUS - 2,
            font=FONT,
            dynamic_resizing=False,
            command=lambda _: self._carregar_dados()
        )
        self.ordem_menu.place(relx=0.5, rely=0.5, anchor="center")
        
        self.btn_limpar = ctk.CTkButton(
            bar,
            text=" Limpar Filtros",
            image=self.icons.get("delete") if self.icons.get("delete") else None,
            compound="left",
            width=130,
            height=HEIGHT,
            corner_radius=FILTER_RADIUS,
            fg_color=FILTER_INPUT_BG,
            hover_color=FILTER_HOVER,
            border_width=1,
            border_color=FILTER_BORDER,
            text_color=AppTheme.TXT_MUTED,
            font=("Segoe UI", 11),
            command=self._limpar_filtros
        )
        self.btn_limpar.pack(side="right", padx=14, pady=PAD_Y)
        
    def _carregar_dados(self):
        termo = self.pesquisa_var.get().strip()
        municipio = self.municipio_selector.get()
        ano = self.ano_var.get()
        ordem = self.ordem_var.get()
        
        codigo_municipio = None
        if municipio != "Todos" and " - " in municipio:
            codigo_municipio = municipio.split(" - ")[0]
        
        for w in self.lista_scroll.winfo_children():
            w.destroy()
        
        loading = ctk.CTkLabel(
            self.lista_scroll,
            text="⏳ Carregando...",
            font=("Segoe UI", 13),
            text_color=AppTheme.TXT_MUTED
        )
        loading.pack(pady=60)
        
        try:
            ok, msg, registros = self.controller.buscar_historico_com_filtros(
                termo=termo,
                codigo_municipio=codigo_municipio,
                ano=ano if ano != "Todos" else None,
                ordem=ordem
            )
            
            loading.destroy()
            
            if ok:
                self.atualizar_lista(registros)
            else:
                self._mostrar_erro(msg)
        except Exception as e:
            loading.destroy()
            self._mostrar_erro(f"Erro ao carregar dados: {str(e)}")

    def _mostrar_erro(self, mensagem: str):
        ctk.CTkLabel(
            self.lista_scroll,
            text=f"❌ Erro: {mensagem}",
            font=("Segoe UI", 13),
            text_color="#ef4444"
        ).pack(pady=60)

    def atualizar_lista(self, registros):
        for w in self.lista_scroll.winfo_children():
            w.destroy()

        if not registros:
            ctk.CTkLabel(
                self.lista_scroll,
                text="📭 Nenhum memorando encontrado.",
                font=("Segoe UI", 13),
                text_color=AppTheme.TXT_MUTED
            ).pack(pady=60)
            return

        for idx, reg in enumerate(registros):
            self._card(idx, reg)

    def _card(self, idx: int, reg: dict):
        bg = AppTheme.BG_CARD if idx % 2 == 0 else AppTheme.BG_INPUT
        hover_baixar = "#f1f5f9" if bg == AppTheme.BG_CARD else "#ffffff"

        card = ctk.CTkFrame(self.lista_scroll,
                            fg_color=bg, corner_radius=12)
        card.pack(fill="x", pady=(0, 10), padx=2)
        card.grid_columnconfigure(0, weight=1)

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.grid(row=0, column=0, sticky="nsew", padx=20, pady=16)

        linha1 = ctk.CTkFrame(info, fg_color="transparent")
        linha1.pack(fill="x")

        memo_info = ctk.CTkFrame(linha1, fg_color="transparent")
        memo_info.pack(side="left")

        if self.icons.get("file_text"):
            ctk.CTkLabel(
                memo_info,
                text="",
                image=self.icons["file_text"],
                width=20,
                height=20
            ).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            memo_info,
            text=f"Memo Nº {reg.get('numero', '—')}",
            font=("Segoe UI", 15, "bold"),
            text_color=AppTheme.TXT_MAIN,
            anchor="w"
        ).pack(side="left")

        unloc = reg.get("unloc", "—")
        if unloc != "—":
            cor_unloc = get_unloc_color(unloc)
            badge = ctk.CTkFrame(linha1,
                                 fg_color=cor_unloc,
                                 corner_radius=6)
            badge.pack(side="left", padx=(12, 0))
            ctk.CTkLabel(badge,
                         text=unloc,
                         font=("Segoe UI", 11, "bold"),
                         text_color="#ffffff",
                         padx=12, pady=3).pack()

        linha2 = ctk.CTkFrame(info, fg_color="transparent")
        linha2.pack(fill="x", pady=(10, 0))

        meta = [
            ("calendar_days", "Emissão", reg.get("data_emissao", "—")),
            ("clock", "Criado em", reg.get("criado_em", "—")),
            ("user", "Usuário", reg.get("usuario", "—")),
        ]

        for icon_name, titulo, valor in meta:
            bloco = ctk.CTkFrame(linha2, fg_color="transparent")
            bloco.pack(side="left", padx=(0, 32))

            titulo_row = ctk.CTkFrame(bloco, fg_color="transparent")
            titulo_row.pack(anchor="w")

            if self.icons.get(icon_name):
                ctk.CTkLabel(
                    titulo_row,
                    text="",
                    image=self.icons[icon_name],
                    width=16,
                    height=16
                ).pack(side="left", padx=(0, 5))

            ctk.CTkLabel(
                titulo_row,
                text=titulo,
                font=("Segoe UI", 10),
                text_color="#6b7280"
            ).pack(side="left")

            ctk.CTkLabel(
                bloco,
                text=valor,
                font=("Segoe UI", 11),
                text_color=AppTheme.TXT_MUTED
            ).pack(anchor="w")
            
        btns = ctk.CTkFrame(card, fg_color="transparent")
        btns.grid(row=0, column=1, sticky="ns", padx=(0, 20), pady=16)

        if self.on_visualizar:
            btn_visualizar = ctk.CTkButton(
                btns,
                text=" Visualizar",
                image=self.icons.get("eye") if self.icons.get("eye") else None,
                compound="left",
                width=120, height=38,
                corner_radius=10,
                fg_color=AppTheme.BTN_PRIMARY,
                hover_color=AppTheme.BTN_PRIMARY_HOVER,
                font=("Segoe UI", 12, "bold"),
                text_color="#ffffff",
                command=lambda mid=reg.get("id"): self._visualizar_com_tratamento(mid)
            )
            if not self.icons.get("eye"):
                btn_visualizar.configure(text="👁️ Visualizar")
            btn_visualizar.pack(pady=(0, 8))

        if self.on_baixar:
            btn_baixar = ctk.CTkButton(
                btns,
                text=" Baixar",
                image=self.icons.get("download") if self.icons.get("download") else None,
                compound="left",
                width=120,
                height=38,
                corner_radius=10,
                fg_color=bg,
                hover_color=hover_baixar,
                border_width=0,
                font=("Segoe UI", 12),
                text_color=AppTheme.TXT_MAIN,
                command=lambda mid=reg.get("id"), num=reg.get("numero", ""): self._baixar_com_tratamento(mid, num)
            )
            if not self.icons.get("download"):
                btn_baixar.configure(text="⬇️ Baixar")
            btn_baixar.pack()

    def _visualizar_com_tratamento(self, memorando_id):
        if not memorando_id:
            messagebox.showerror("Erro", "ID do memorando não encontrado.")
            return
        
        try:
            if self.on_visualizar:
                self.on_visualizar(memorando_id)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir memorando:\n{str(e)}")

    def _baixar_com_tratamento(self, memorando_id, numero):
        if not memorando_id:
            messagebox.showerror("Erro", "ID do memorando não encontrado.")
            return
        
        try:
            if self.on_baixar:
                self.on_baixar(memorando_id, numero)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao baixar memorando:\n{str(e)}")