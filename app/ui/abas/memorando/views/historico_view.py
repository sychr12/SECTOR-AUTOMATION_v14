# -*- coding: utf-8 -*-
"""Histórico de memorandos — design corporativo com filtros e cores"""

import customtkinter as ctk
from tkinter import messagebox
from app.theme import AppTheme
import hashlib
from datetime import datetime


# ── Paleta de cores para UNLOC ──────────────────────────────────────────────────
UNLOC_CORES = {
    # Cores principais
    "MAO": "#10b981",      # Verde
    "EIR": "#3b82f6",      # Azul
    "TFE": "#8b5cf6",      # Roxo
    "BVB": "#f59e0b",      # Laranja
    "PVH": "#ec489a",      # Rosa
    "RBR": "#14b8a6",      # Turquesa
    "CZS": "#ef4444",      # Vermelho
    "JPR": "#84cc16",      # Verde limão
    "LBR": "#06b6d4",      # Ciano
    "STM": "#a855f7",      # Roxo claro
}

# Cores alternativas para UNLOC não listados
CORES_ALTERNATIVAS = [
    "#10b981", "#3b82f6", "#8b5cf6", "#f59e0b", "#ec489a",
    "#14b8a6", "#ef4444", "#84cc16", "#06b6d4", "#a855f7",
    "#d946ef", "#f43f5e", "#0ea5e9", "#eab308", "#22c55e",
]


# ── MUNICIPIOS ──────────────────────────────────────────────────────────────────
MUNICIPIOS = {
    "ALV": "ALVARÃES",
    "AMT": "AMATURÁ",
    "ANA": "ANAMÃ",
    "ANO": "ANORI",
    "APU": "APUÍ",
    "ATN": "ATALAIA DO NORTE",
    "ATZ": "AUTAZES",
    "BAZ": "BARCELOS",
    "BAR": "BARREIRINHA",
    "BJC": "BENJAMIN CONSTANT",
    "BER": "BERURI",
    "BVR": "BOA VISTA DO RAMOS",
    "BOA": "BOCA DO ACRE",
    "BBA": "BORBA",
    "CAP": "CAAPIRANGA",
    "CAN": "CANUTAMA",
    "CAF": "CARAUARI",
    "CAR": "CAREIRO",
    "CAZ": "CAREIRO DA VÁRZEA",
    "CIZ": "COARI",
    "COD": "CODAJÁS",
    "ERN": "EIRUNEPÉ",
    "ENV": "ENVIRA",
    "FBA": "FONTE BOA",
    "GAJ": "GUAJARÁ",
    "HIA": "HUMAITÁ",
    "IPX": "IPIXUNA",
    "IRB": "IRANDUBA",
    "ITA": "ITAMARATI",
    "ITR": "ITACOATIARA",
    "ITG": "ITAPIRANGA",
    "JPR": "JAPURÁ",
    "JUR": "JURUÁ",
    "JUT": "JUTAÍ",
    "LBR": "LÁBREA",
    "MPU": "MANACAPURU",
    "MQR": "MANAQUIRI",
    "MAO": "MANAUS",
    "MAO-ZL": "MANAUS ZONA LESTE",
    "MNX": "MANICORÉ",
    "MTS-ATZ": "MONTE SINAI",
    "MRA": "MARAÃ",
    "MBZ": "MAUÉS",
    "NMD": "NHAMUNDÁ",
    "ITR-NRO": "NOVO REMANSO",
    "MNX-MTP": "SANTO ANTÔNIO DO MATUPI",
    "LBR-VE": "VILA EXTREMA",
    "VRC": "VILA RICA DE CAVIANA",
    "PRF-BNA": "BALBINA",
    "VLD": "VILA DE LINDÓIA",
    "RLD": "VILA DA REALIDADE",
    "NON": "NOVA OLINDA DO NORTE",
    "NAR": "NOVO AIRÃO",
    "NAP": "NOVO ARIPUANÃ",
    "PAR": "PARINTINS",
    "PUI": "PAUINI",
    "PRF": "PRESIDENTE FIGUEIREDO",
    "RPE": "RIO PRETO DA EVA",
    "SIR": "SANTA ISABEL DO RIO NEGRO",
    "SAI": "SANTO ANTÔNIO DO IÇÁ",
    "SJL": "SÃO GABRIEL DA CACHOEIRA",
    "SPO": "SÃO PAULO DE OLIVENÇA",
    "SSU": "SÃO SEBASTIÃO DO UATUMÃ",
    "SUL-CAN": "SUL DE CANUTAMA",
    "SLV": "SILVES",
    "TBT": "TABATINGA",
    "TPA": "TAPAUÁ",
    "TFF": "TEFÉ",
    "TNT": "TONANTINS",
    "UAN": "UARINI",
    "URC": "URUCARÁ",
    "UCB": "URUCURITUBA",
    "FOZ": "FOZ DE CANUMÃ"
}


def get_unloc_color(unloc: str) -> str:
    """Retorna uma cor consistente para cada UNLOC"""
    if not unloc or unloc == "—":
        return "#64748b"  # Cinza para UNLOC vazio
    
    unloc_upper = unloc.upper()
    
    # Se já tem cor definida
    if unloc_upper in UNLOC_CORES:
        return UNLOC_CORES[unloc_upper]
    
    # Gerar cor baseada no hash do UNLOC
    hash_val = int(hashlib.md5(unloc_upper.encode()).hexdigest()[:8], 16)
    return CORES_ALTERNATIVAS[hash_val % len(CORES_ALTERNATIVAS)]

# ───────────────── Municipios ─────────────────

MUNICIPIOS = {
    "ALV": "ALVARÃES",
    "AMT": "AMATURÁ",
    "ANA": "ANAMÃ",
    "ANO": "ANORI",
    "APU": "APUÍ",
    "ATN": "ATALAIA DO NORTE",
    "ATZ": "AUTAZES",
    "BAZ": "BARCELOS",
    "BAR": "BARREIRINHA",
    "BJC": "BENJAMIN CONSTANT",
    "BER": "BERURI",
    "BVR": "BOA VISTA DO RAMOS",
    "BOA": "BOCA DO ACRE",
    "BBA": "BORBA",
    "CAP": "CAAPIRANGA",
    "CAN": "CANUTAMA",
    "CAF": "CARAUARI",
    "CAR": "CAREIRO",
    "CAZ": "CAREIRO DA VÁRZEA",
    "CIZ": "COARI",
    "COD": "CODAJÁS",
    "ERN": "EIRUNEPÉ",
    "ENV": "ENVIRA",
    "FBA": "FONTE BOA",
    "GAJ": "GUAJARÁ",
    "HIA": "HUMAITÁ",
    "IPX": "IPIXUNA",
    "IRB": "IRANDUBA",
    "ITA": "ITAMARATI",
    "ITR": "ITACOATIARA",
    "ITG": "ITAPIRANGA",
    "JPR": "JAPURÁ",
    "JUR": "JURUÁ",
    "JUT": "JUTAÍ",
    "LBR": "LÁBREA",
    "MPU": "MANACAPURU",
    "MQR": "MANAQUIRI",
    "MAO": "MANAUS",
    "MAO-ZL": "MANAUS ZONA LESTE",
    "MNX": "MANICORÉ",
    "MTS-ATZ": "MONTE SINAI",
    "MRA": "MARAÃ",
    "MBZ": "MAUÉS",
    "NMD": "NHAMUNDÁ",
    "ITR-NRO": "NOVO REMANSO",
    "MNX-MTP": "SANTO ANTÔNIO DO MATUPI",
    "LBR-VE": "VILA EXTREMA",
    "VRC": "VILA RICA DE CAVIANA",
    "PRF-BNA": "BALBINA",
    "VLD": "VILA DE LINDÓIA",
    "RLD": "VILA DA REALIDADE",
    "NON": "NOVA OLINDA DO NORTE",
    "NAR": "NOVO AIRÃO",
    "NAP": "NOVO ARIPUANÃ",
    "PAR": "PARINTINS",
    "PUI": "PAUINI",
    "PRF": "PRESIDENTE FIGUEIREDO",
    "RPE": "RIO PRETO DA EVA",
    "SIR": "SANTA ISABEL DO RIO NEGRO",
    "SAI": "SANTO ANTÔNIO DO IÇÁ",
    "SJL": "SÃO GABRIEL DA CACHOEIRA",
    "SPO": "SÃO PAULO DE OLIVENÇA",
    "SSU": "SÃO SEBASTIÃO DO UATUMÃ",
    "SUL-CAN": "SUL DE CANUTAMA",
    "SLV": "SILVES",
    "TBT": "TABATINGA",
    "TPA": "TAPAUÁ",
    "TFF": "TEFÉ",
    "TNT": "TONANTINS",
    "UAN": "UARINI",
    "URC": "URUCARÁ",
    "UCB": "URUCURITUBA",
    "FOZ": "FOZ DE CANUMÃ"
}

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

    # ── janela ──────────────────────────────────────────────────────
    def _configure_window(self):
        self.title("Histórico de Memorandos")
        self.geometry("1200x750")
        self.configure(fg_color=AppTheme.BG_APP)
        self.grab_set()

        largura = 900
        altura = 600

        self.update_idletasks()
        w, h = 1200, 750
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ── layout ──────────────────────────────────────────────────────
    def _create_widgets(self):
        root = ctk.CTkFrame(self, fg_color="transparent")
        root.pack(fill="both", expand=True, padx=36, pady=32)

        # cabeçalho
        self._build_header(root)
        
        # barra de filtros
        self._build_filters(root)
        
        # linha divisória
        separator = ctk.CTkFrame(root, height=1, fg_color=AppTheme.BG_CARD)
        separator.pack(fill="x", pady=(0, 20))

        # lista scrollável
        self.lista_scroll = ctk.CTkScrollableFrame(
            root,
            fg_color="transparent",
            scrollbar_button_color=AppTheme.BG_CARD,
            scrollbar_button_hover_color=AppTheme.TXT_MUTED,
        )
        self.lista_scroll.pack(fill="both", expand=True)
        
    # ── Limpar tudo dos filtros ────────────────────────────────────────────       
    def _limpar_filtros(self):
        self.pesquisa_var.set("")
        self.municipio_var.set("Todos")
        self.ano_var.set("Todos")
        self.ordem_var.set("Recentes")

        # força atualização da lista após limpar
        if hasattr(self, "on_filtro_change"):
            self.on_filtro_change()
            

    def _build_header(self, parent):
        """Cabeçalho com título e ícone"""
        hdr = ctk.CTkFrame(parent, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 24))

        left = ctk.CTkFrame(hdr, fg_color="transparent")
        left.pack(side="left")
        
        # Ícone do histórico
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

        # Status badge
        status_badge = ctk.CTkLabel(
            hdr, text="📋 Lista de memorandos",
            font=("Segoe UI", 11, "bold"), text_color=AppTheme.TXT_MUTED,
            fg_color=AppTheme.BG_CARD, corner_radius=20, padx=14, pady=6
        )
        status_badge.pack(side="right")

    def _build_filters(self, parent):
        """Barra de filtros completa"""
        bar = ctk.CTkFrame(parent, fg_color=AppTheme.BG_CARD, corner_radius=14)
        bar.pack(fill="x", pady=(0, 20))

        HEIGHT = 38
        PAD_X = 8
        PAD_Y = 10
        FONT = ("Segoe UI", 12)
        FONT_BOLD = ("Segoe UI", 11, "bold")

        # ── Buscar ─────────────────────────────
        ctk.CTkLabel(bar, text="🔍",
                     font=("Segoe UI", 14),
                     text_color=AppTheme.TXT_MUTED).pack(side="left", padx=(16, 4), pady=PAD_Y)
        
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
            corner_radius=10,
            fg_color=AppTheme.BG_INPUT,
            border_color=AppTheme.BG_INPUT,
            font=FONT,
            text_color=AppTheme.TXT_MAIN,
        ).pack(side="left", fill="x", expand=True, padx=(0, PAD_X), pady=PAD_Y)

        # ── Município ─────────────────────────────
        ctk.CTkLabel(bar, text="📍",
                     font=("Segoe UI", 14),
                     text_color=AppTheme.TXT_MUTED).pack(side="left", padx=(12, 4), pady=PAD_Y)
        
        ctk.CTkLabel(bar, text="Município",
                     font=FONT_BOLD,
                     text_color=AppTheme.TXT_MUTED).pack(side="left", padx=(0, 6), pady=PAD_Y)

        self.municipio_var = ctk.StringVar(value="Todos")

        lista_municipios = ["Todos"] + [
            f"{codigo} - {nome}" for codigo, nome in MUNICIPIOS.items()
        ]

        ctk.CTkOptionMenu(
            bar,
            values=lista_municipios,
            variable=self.municipio_var,
            width=200,
            height=HEIGHT,
            fg_color=AppTheme.BG_INPUT,
            button_color=AppTheme.BG_INPUT,
            button_hover_color=AppTheme.BG_CARD,
            text_color=AppTheme.TXT_MAIN,
            dropdown_fg_color=AppTheme.BG_CARD,
            font=FONT,
            command=lambda _: self._carregar_dados()
        ).pack(side="left", padx=(0, PAD_X), pady=PAD_Y)

        # ── Ano ─────────────────────────────
        ctk.CTkLabel(bar, text="📅",
                     font=("Segoe UI", 14),
                     text_color=AppTheme.TXT_MUTED).pack(side="left", padx=(12, 4), pady=PAD_Y)
        
        ctk.CTkLabel(bar, text="Ano",
                     font=FONT_BOLD,
                     text_color=AppTheme.TXT_MUTED).pack(side="left", padx=(0, 6), pady=PAD_Y)

        self.ano_var = ctk.StringVar(value="Todos")

        # Buscar anos disponíveis
        ok, anos = self.controller.listar_anos() if hasattr(self.controller, 'listar_anos') else (False, [])
        lista_anos = ["Todos"] + anos if ok and anos else ["Todos"]

        ctk.CTkOptionMenu(
            bar,
            values=lista_anos,
            variable=self.ano_var,
            width=100,
            height=HEIGHT,
            fg_color=AppTheme.BG_INPUT,
            button_color=AppTheme.BG_INPUT,
            button_hover_color=AppTheme.BG_CARD,
            text_color=AppTheme.TXT_MAIN,
            dropdown_fg_color=AppTheme.BG_CARD,
            font=FONT,
            command=lambda _: self._carregar_dados()
        ).pack(side="left", padx=(0, PAD_X), pady=PAD_Y)

        # ── Ordem ─────────────────────────────
        ctk.CTkLabel(bar, text="🔄",
                     font=("Segoe UI", 14),
                     text_color=AppTheme.TXT_MUTED).pack(side="left", padx=(12, 4), pady=PAD_Y)
        
        ctk.CTkLabel(bar, text="Ordem",
                     font=FONT_BOLD,
                     text_color=AppTheme.TXT_MUTED).pack(side="left", padx=(0, 6), pady=PAD_Y)

        self.ordem_var = ctk.StringVar(value="Recentes")

        ctk.CTkOptionMenu(
            bar,
            values=["Recentes", "Antigos"],
            variable=self.ordem_var,
            width=120,
            height=HEIGHT,
            fg_color=AppTheme.BG_INPUT,
            button_color=AppTheme.BG_INPUT,
            button_hover_color=AppTheme.BG_CARD,
            text_color=AppTheme.TXT_MAIN,
            dropdown_fg_color=AppTheme.BG_CARD,
            font=FONT,
            command=lambda _: self._carregar_dados()
        ).pack(side="left", padx=(0, PAD_X), pady=PAD_Y)

        # ── Botão Limpar ─────────────────────────────
        ctk.CTkButton(
            bar,
            text=" Limpar Filtros",
            image=self.icons.get("delete") if self.icons.get("delete") else None,
            compound="left",
            width=120,
            height=HEIGHT,
            corner_radius=10,
            fg_color=AppTheme.BG_INPUT,
            hover_color=AppTheme.BG_APP,
            text_color=AppTheme.TXT_MUTED,
            font=("Segoe UI", 11),
            command=self._limpar_filtros
        ).pack(side="right", padx=14, pady=PAD_Y)

    def _limpar_filtros(self):
        """Limpa todos os filtros e recarrega os dados."""
        self.pesquisa_var.set("")
        self.municipio_var.set("Todos")
        self.ano_var.set("Todos")
        self.ordem_var.set("Recentes")
        self._carregar_dados()

    def _carregar_dados(self):
        """Carrega os dados com todos os filtros aplicados."""
        termo = self.pesquisa_var.get().strip()
        municipio = self.municipio_var.get()
        ano = self.ano_var.get()
        ordem = self.ordem_var.get()
        
        # Extrair código do município se não for "Todos"
        codigo_municipio = None
        if municipio != "Todos" and " - " in municipio:
            codigo_municipio = municipio.split(" - ")[0]
        
        # Mostrar loading
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
            # Buscar histórico com filtros
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
        """Mostra mensagem de erro na lista."""
        ctk.CTkLabel(
            self.lista_scroll,
            text=f"❌ Erro: {mensagem}",
            font=("Segoe UI", 13),
            text_color="#ef4444"
        ).pack(pady=60)

    # ── renderizar lista ────────────────────────────────────────────
    def atualizar_lista(self, registros):
        """Atualiza a lista com os registros fornecidos."""
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
        """Cria um card para cada memorando."""
        # fundo alternado suave
        bg = AppTheme.BG_CARD if idx % 2 == 0 else AppTheme.BG_INPUT

        card = ctk.CTkFrame(self.lista_scroll,
                            fg_color=bg, corner_radius=12)
        card.pack(fill="x", pady=(0, 10), padx=2)
        card.grid_columnconfigure(0, weight=1)

        # ── lado esquerdo — informações ─────────────────────────────
        info = ctk.CTkFrame(card, fg_color="transparent")
        info.grid(row=0, column=0, sticky="nsew", padx=20, pady=16)

        # linha 1 — número em destaque + badge UNLOC colorido
        linha1 = ctk.CTkFrame(info, fg_color="transparent")
        linha1.pack(fill="x")

        ctk.CTkLabel(linha1,
                     text=f"📄 Memo Nº {reg.get('numero', '—')}",
                     font=("Segoe UI", 15, "bold"),
                     text_color=AppTheme.TXT_MAIN,
                     anchor="w").pack(side="left")

        # badge UNLOC com cor personalizada
        unloc = reg.get("unloc", "—")
        if unloc != "—":
            cor_unloc = get_unloc_color(unloc)
            badge = ctk.CTkFrame(linha1,
                                 fg_color=cor_unloc,
                                 corner_radius=6)
            badge.pack(side="left", padx=(12, 0))
            ctk.CTkLabel(badge,
                         text=f"📍 {unloc}",
                         font=("Segoe UI", 11, "bold"),
                         text_color="#ffffff",
                         padx=12, pady=3).pack()

        # linha 2 — metadados
        linha2 = ctk.CTkFrame(info, fg_color="transparent")
        linha2.pack(fill="x", pady=(10, 0))

        meta = [
            ("📅 Emissão",   reg.get("data_emissao", "—")),
            ("🕐 Criado em", reg.get("criado_em", "—")),
            ("👤 Usuário",   reg.get("usuario", "—")),
        ]
        for titulo, valor in meta:
            bloco = ctk.CTkFrame(linha2, fg_color="transparent")
            bloco.pack(side="left", padx=(0, 32))
            ctk.CTkLabel(bloco, text=titulo,
                         font=("Segoe UI", 10),
                         text_color="#6b7280").pack(anchor="w")
            ctk.CTkLabel(bloco, text=valor,
                         font=("Segoe UI", 11),
                         text_color=AppTheme.TXT_MUTED).pack(anchor="w")

        # ── lado direito — botões ───────────────────────────────────
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
                width=120, height=38,
                corner_radius=10,
                fg_color=AppTheme.BG_INPUT,
                hover_color=AppTheme.BG_APP,
                font=("Segoe UI", 12),
                text_color=AppTheme.TXT_MAIN,
                command=lambda mid=reg.get("id"), num=reg.get("numero", ""): self._baixar_com_tratamento(mid, num)
            )
            if not self.icons.get("download"):
                btn_baixar.configure(text="⬇️ Baixar")
            btn_baixar.pack()

    def _visualizar_com_tratamento(self, memorando_id):
        """Visualiza o memorando com tratamento de erro."""
        if not memorando_id:
            messagebox.showerror("Erro", "ID do memorando não encontrado.")
            return
        
        try:
            if self.on_visualizar:
                self.on_visualizar(memorando_id)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir memorando:\n{str(e)}")

    def _baixar_com_tratamento(self, memorando_id, numero):
        """Baixa o memorando com tratamento de erro."""
        if not memorando_id:
            messagebox.showerror("Erro", "ID do memorando não encontrado.")
            return
        
        try:
            if self.on_baixar:
                self.on_baixar(memorando_id, numero)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao baixar memorando:\n{str(e)}")