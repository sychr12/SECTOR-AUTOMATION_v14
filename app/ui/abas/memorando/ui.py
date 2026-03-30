# -*- coding: utf-8 -*-
"""Interface principal para memorando de saída — design corporativo premium"""

import customtkinter as ctk
from tkinter import messagebox
import os
from PIL import Image
from datetime import datetime

from app.theme import AppTheme
from ui.base_ui import BaseUI
from .controller import MemorandoController
from .views import MemorandoFormView, HistoricoMemorandoView


# ── Lista de MUNICÍPIOS com códigos UNLOC ─────────────────────────────────────────
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

# ── Criar lista formatada para o ComboBox ────────────────────────────────────────
UNLOC_LIST_FORMATADO = [f"{codigo} - {nome}" for codigo, nome in MUNICIPIOS.items()]

# ── Dicionário para converter de volta ───────────────────────────────────────────
UNLOC_CODIGOS = {f"{codigo} - {nome}": codigo for codigo, nome in MUNICIPIOS.items()}

_ICON_COLOR = "#1e293b"

# ── Paleta de Cores Premium ──────────────────────────────────────────────────────
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


class IconManager:
    """Gerenciador de ícones para a interface de memorando"""

    def __init__(self):
        self.icons = {}
        self._find_icons_path()

    def _find_icons_path(self):
        """Encontra o caminho correto para a pasta de ícones"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        possible_paths = [
            os.path.join(current_dir, "..", "..", "..", "images", "icons", "memorando"),
            os.path.join(current_dir, "..", "..", "..", "..", "images", "icons", "memorando"),
            r"C:\Users\Administrador\Documents\SECTOR AUTOMATION_v14\images\icons\memorando",
        ]

        for path in possible_paths:
            if os.path.exists(path):
                self.icons_dir = path
                print(f"[IconManager] ✅ Ícones encontrados em: {self.icons_dir}")
                return

        self.icons_dir = possible_paths[0]
        print(f"[IconManager] ⚠️ Pasta de ícones não encontrada: {self.icons_dir}")

    def load_icon(self, filename, size=(24, 24), colorize_to=None):
        """Carrega um ícone da pasta e aplica cor se necessário"""
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
                        target_r, target_g, target_b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

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
            "document": ("document.png", (36, 36), _ICON_COLOR),
            "history":  ("history.png",  (26, 26), _ICON_COLOR),
            "save":     ("save.png",     (22, 22), _ICON_COLOR),
            "search":   ("search.png",   (20, 20), _ICON_COLOR),
            "delete":   ("delete.png",   (20, 20), _ICON_COLOR),
            "download": ("download.png", (22, 22), _ICON_COLOR),
            "eye":      ("eye.png",      (22, 22), _ICON_COLOR),
        }

        for name, (filename, size, color) in icons_config.items():
            self.icons[name] = self.load_icon(filename, size, color)

        return self.icons

    def get(self, name):
        """Retorna um ícone pelo nome"""
        return self.icons.get(name)


class MemorandoUI(BaseUI):

    def __init__(self, parent, usuario=None):
        super().__init__(parent)
        self.usuario = usuario or "sistema"
<<<<<<< HEAD
        self.controller = MemorandoController(self.usuario)  
        self.configure(fg_color=AppTheme.BG_APP)
=======
        self.controller = MemorandoController(self.usuario)

        # Inicializar ícones
        self.icon_manager = IconManager()
        self.icons = self.icon_manager.setup_icons()

        self.configure(fg_color=_CINZA_BG)
>>>>>>> f4a3e3b (.)
        self._layout()

    def _layout(self):
        # ── container principal ──────────────────────────────────────────
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=32, pady=28)

        # ── cabeçalho ───────────────────────────────────────────────
        self._build_header(main_container)

        # ── formulário em card ──────────────────────────────────────────
        form_card = ctk.CTkFrame(main_container, fg_color=_BRANCO, corner_radius=16,
                                  border_width=1, border_color=_CINZA_BORDER)
        form_card.pack(fill="x", pady=(0, 24))

        self.form_view = MemorandoFormView(
            form_card, self.controller,
            on_gerar=self.gerar_memorando,
            on_historico=self.abrir_historico,
            icons=self.icons,
            unloc_list=UNLOC_LIST_FORMATADO,
            unloc_dict=UNLOC_CODIGOS
        )
        self.form_view.pack(fill="x", padx=24, pady=24)

        # ── log ─────────────────────────────────────────────────────
        self._build_log(main_container)

    def _build_header(self, parent):
        """Cabeçalho com título e ícone"""
        hdr = ctk.CTkFrame(parent, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 24))

        left = ctk.CTkFrame(hdr, fg_color="transparent")
        left.pack(side="left")

        # Ícone do documento
        if self.icons.get("document"):
            icon_label = ctk.CTkLabel(
                left, text="", image=self.icons["document"],
                width=40, height=40
            )
            icon_label.pack(side="left", padx=(0, 16))

        title_frame = ctk.CTkFrame(left, fg_color="transparent")
        title_frame.pack(side="left")

        ctk.CTkLabel(title_frame, text="Memorando de Saída",
                     font=("Segoe UI", 28, "bold"),
                     text_color=_CINZA_TEXTO,
                     anchor="w").pack(anchor="w")

        ctk.CTkLabel(title_frame,
                     text="Geração e controle de memorandos",
                     font=("Segoe UI", 13),
                     text_color=_MUTED,
                     anchor="w").pack(anchor="w", pady=(4, 0))

        # Data e hora atual
        right = ctk.CTkFrame(hdr, fg_color="transparent")
        right.pack(side="right")

        self.lbl_data = ctk.CTkLabel(
            right,
            text=datetime.now().strftime("%d/%m/%Y"),
            font=("Segoe UI", 13, "bold"),
            text_color=_ACCENT
        )
        self.lbl_data.pack(anchor="e")

        self.lbl_hora = ctk.CTkLabel(
            right,
            text=datetime.now().strftime("%H:%M"),
            font=("Segoe UI", 12),
            text_color=_MUTED
        )
        self.lbl_hora.pack(anchor="e", pady=(2, 0))

        # Atualizar hora
        self._atualizar_hora()

    def _atualizar_hora(self):
        try:
            if self.lbl_data and self.lbl_data.winfo_exists():
                now = datetime.now()
                self.lbl_data.configure(text=now.strftime("%d/%m/%Y"))
                self.lbl_hora.configure(text=now.strftime("%H:%M"))
                self.after(1000, self._atualizar_hora)
        except Exception:
            pass

    def _build_log(self, parent):
        """Seção de log de atividades"""
        log_card = ctk.CTkFrame(parent, fg_color=_BRANCO, corner_radius=16,
                                 border_width=1, border_color=_CINZA_BORDER)
        log_card.pack(fill="both", expand=True)

        log_hdr = ctk.CTkFrame(log_card, fg_color="transparent")
        log_hdr.pack(fill="x", padx=24, pady=(20, 12))

        # Ícone do log
        ctk.CTkLabel(
            log_hdr, text="📋", font=("Segoe UI", 20),
            text_color=_ACCENT
        ).pack(side="left", padx=(0, 12))

        ctk.CTkLabel(log_hdr, text="Registro de Atividade",
                     font=("Segoe UI", 16, "bold"),
                     text_color=_CINZA_TEXTO).pack(side="left")

        # Botão limpar
        btn_limpar = ctk.CTkButton(
            log_hdr, text=" Limpar",
            image=self.icons.get("delete"), compound="left",
            width=100, height=34,
            font=("Segoe UI", 12),
            fg_color=_CINZA_BG, hover_color=_CINZA_BORDER,
            text_color=_MUTED, corner_radius=8,
            command=self._limpar_log
        )
        btn_limpar.pack(side="right")

        # Separador
        separator = ctk.CTkFrame(log_card, height=1, fg_color=_CINZA_BORDER)
        separator.pack(fill="x", padx=24, pady=(0, 16))

        # Área de log
        self.confirmacao = ctk.CTkTextbox(
            log_card,
            fg_color=_CINZA_BG,
            text_color=_CINZA_TEXTO,
            height=180,
            state="disabled",
            font=("Consolas", 11),
            corner_radius=8,
        )
        self.confirmacao.pack(fill="both", expand=True,
                              padx=24, pady=(0, 20))

    # ── ações ──────────────────────────────────────────────────────
    def gerar_memorando(self, dados_form):
        numero       = dados_form["numero"]
        data         = dados_form["data"]
        unloc_raw    = dados_form["unloc"]
        memo_entrada = dados_form["memo_entrada"]

        # Extrair apenas o código do UNLOC (ex: "MAO - MANAUS" -> "MAO")
        if " - " in unloc_raw:
            unloc = unloc_raw.split(" - ")[0]
        else:
            unloc = unloc_raw

        self._limpar_log()
        self._log("▶  Iniciando geração do memorando...", "muted")
        self._log(f"   Nº: {numero}  |  Município: {unloc_raw}", "muted")

        try:
            sucesso, mensagem, resultado = self.controller.gerar_memorando(
                numero=numero, data_str=data,
                unloc=unloc, memo_entrada=memo_entrada
            )

            if sucesso:
                self._log(f"✓  {mensagem}", "ok")
                self._log("   Memorando gerado com sucesso!", "ok")
                self.form_view.clear_form()
                if messagebox.askyesno("Memorando criado",
                                       f"{mensagem}\n\nDeseja abrir agora?"):
                    if resultado:
                        self.visualizar_memorando(resultado["id"])
            else:
                self._log(f"✕  {mensagem}", "err")
                messagebox.showerror("Erro", mensagem)
        except Exception as e:
            self._log(f"✕  Erro: {str(e)}", "err")
            messagebox.showerror("Erro", f"Erro ao gerar memorando:\n{str(e)}")

    def abrir_historico(self):
        """Abre a janela de histórico. Os filtros e carregamento são
        gerenciados internamente pelo próprio HistoricoMemorandoView."""
        self.historico_view = HistoricoMemorandoView(
            self, self.controller,
            on_visualizar=self.visualizar_memorando,
            on_baixar=self.baixar_memorando,
            icons=self.icons,
        )
<<<<<<< HEAD

        self._carregar_historico()

        # função de pesquisa com município
        def pesquisar(*_):
            municipio_raw = self.historico_view.municipio_var.get()
            ano = self.historico_view.ano_var.get()
            ordem = self.historico_view.ordem_var.get()
            
            if municipio_raw == "Todos":
                municipio = "Todos"
            else:
                municipio = municipio_raw.split(" - ")[0]

            self._carregar_historico(
                termo=self.historico_view.pesquisa_var.get(),
                municipio=municipio,
                ano=ano,
                ordem = ordem
            )
            
        self.historico_view.on_filtro_change = pesquisar

        self.historico_view.pesquisa_var.trace("w", pesquisar)

        self.historico_view.municipio_var.trace("w", pesquisar)
        
        self.historico_view.ano_var.trace("w", pesquisar)
        
        self.historico_view.ordem_var.trace("w", pesquisar)

    def _carregar_historico(self, termo="", municipio="Todos", ano="Todos", ordem="Recentes"):
        if hasattr(self, "historico_view") and self.historico_view.winfo_exists():
            ok, msg, registros = self.controller.buscar_historico(
                termo, 
                municipio,
                ano,
                ordem
                )
            if ok:
                self.historico_view.atualizar_lista(registros)
            else:
                messagebox.showerror("Erro", msg)
=======
        # O _carregar_dados() já é chamado no __init__ de HistoricoMemorandoView
>>>>>>> f4a3e3b (.)

    def visualizar_memorando(self, mid):
        ok, msg = self.controller.visualizar_memorando(mid)
        if ok:
            self._log(f"✓  {msg}", "ok")
        else:
            messagebox.showerror("Erro", msg)

    def baixar_memorando(self, mid, numero):
        ok, msg = self.controller.baixar_memorando(mid, numero)
        if ok:
            self._log(f"✓  {msg}", "ok")
            if "salvo em:" in msg and messagebox.askyesno("Abrir?", "Abrir o arquivo agora?"):
                self.controller.visualizar_memorando(mid)
        else:
            if "cancelada" not in msg.lower():
                messagebox.showerror("Erro", msg)

    # ── log helpers ─────────────────────────────────────────────────
    _CORES = {"ok": _VERDE_STATUS, "err": _VERMELHO, "muted": _MUTED}

    def _log(self, texto, tipo="muted"):
<<<<<<< HEAD
        self.confirmacao.configure(state="normal")
        tag = f"tag_{tipo}"
        self.confirmacao.tag_config(tag, foreground=self._CORES.get(tipo, "#e2e8f0"))
        self.confirmacao.insert("end", texto + "\n", tag)
        self.confirmacao.see("end")
        self.confirmacao.configure(state="disabled")
=======
        try:
            self.confirmacao.configure(state="normal")
            tag = f"tag_{tipo}"
            self.confirmacao.tag_config(tag, foreground=self._CORES.get(tipo, _CINZA_MEDIO))
            ts = datetime.now().strftime("%H:%M:%S")
            self.confirmacao.insert("end", f"[{ts}] {texto}\n", tag)
            self.confirmacao.see("end")
            self.confirmacao.configure(state="disabled")
        except Exception:
            pass
>>>>>>> f4a3e3b (.)

    def _limpar_log(self):
        try:
            self.confirmacao.configure(state="normal")
            self.confirmacao.delete("1.0", "end")
            self.confirmacao.configure(state="disabled")
        except Exception:
            pass