# -*- coding: utf-8 -*-
"""
Tela Home com Dashboard do Sistema — Design Corporativo com Ícones Pretos
"""

import customtkinter as ctk
from datetime import datetime
import os
from PIL import Image

from app.theme import AppTheme


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
_ICON_COLOR      = "#1e293b"  # Preto suave para os ícones


class IconManager:
    """Gerenciador de ícones para o Dashboard - Ícones Pretos"""
    
    def __init__(self):
        self.icons = {}
        self._find_icons_path()
        
    def _find_icons_path(self):
        """Encontra o caminho correto para a pasta de ícones home"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        possible_paths = [
            # Caminho absoluto
            r"C:\Users\Administrador\Documents\SECTOR AUTOMATION_v14\images\icons\home",
            # Caminhos relativos
            os.path.join(current_dir, "..", "..", "..", "images", "icons", "home"),
            os.path.join(current_dir, "..", "..", "images", "icons", "home"),
            os.path.join(current_dir, "..", "images", "icons", "home"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                self.icons_dir = path
                print(f"[IconManager] ✅ Ícones encontrados em: {self.icons_dir}")
                try:
                    files = os.listdir(path)
                    print(f"[IconManager] Arquivos disponíveis: {files}")
                except:
                    pass
                return
        
        self.icons_dir = None
        print(f"[IconManager] ⚠️ Pasta de ícones não encontrada, usando emojis como fallback")
    
    def load_icon(self, filename, size=(24, 24), colorize_to=None):
        """Carrega um ícone da pasta e aplica cor se necessário"""
        if not self.icons_dir:
            return None
        try:
            path = os.path.join(self.icons_dir, filename)
            if os.path.exists(path):
                img = Image.open(path)
                img = img.resize(size, Image.Resampling.LANCZOS)
                
                # Colorir o ícone se solicitado
                if colorize_to:
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    
                    data = img.getdata()
                    new_data = []
                    
                    # Converter cor hex para RGB
                    if isinstance(colorize_to, tuple):
                        target_r, target_g, target_b = colorize_to
                    else:
                        hex_color = colorize_to.lstrip('#')
                        target_r, target_g, target_b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                    
                    # Processar cada pixel
                    for item in data:
                        r, g, b, a = item
                        if a > 0:  # Pixel não transparente
                            new_data.append((target_r, target_g, target_b, a))
                        else:
                            new_data.append((r, g, b, a))
                    
                    img.putdata(new_data)
                
                return ctk.CTkImage(light_image=img, dark_image=img, size=size)
            else:
                print(f"[IconManager] Arquivo não encontrado: {path}")
        except Exception as e:
            print(f"[IconManager] Erro ao carregar {filename}: {e}")
        return None
    
    def setup_icons(self):
        """Configura todos os ícones com cor preta"""
        icons_config = {
            "dashboard": ("dashboard.png", (36, 36), _ICON_COLOR),
            "online": ("online.png", (28, 28), _ICON_COLOR),
            "offline": ("offline.png", (28, 28), _ICON_COLOR),
            "reports": ("reports.png", (28, 28), _ICON_COLOR),
            "total_reports": ("total_reports.png", (28, 28), _ICON_COLOR),
            "inscricoes": ("inscricoes.png", (24, 24), _ICON_COLOR),
            "devolucoes": ("devolucoes.png", (24, 24), _ICON_COLOR),
            "monthly": ("monthly.png", (24, 24), _ICON_COLOR),
            "last_access": ("access.png", (24, 24), _ICON_COLOR),
            "refresh": ("refresh.png", (22, 22), _ICON_COLOR),
            "users": ("users.png", (20, 20), _ICON_COLOR),
            "activities": ("activities.png", (20, 20), _ICON_COLOR),
            "empty": ("empty.png", (48, 48), _ICON_COLOR),
        }
        
        print("[IconManager] Carregando ícones com cor preta...")
        for name, (filename, size, color) in icons_config.items():
            self.icons[name] = self.load_icon(filename, size, color)
            if self.icons[name]:
                print(f"[IconManager] ✅ {name} carregado com sucesso")
            else:
                print(f"[IconManager] ❌ {name} NÃO carregado")
        
        return self.icons
    
    def get(self, name):
        """Retorna um ícone pelo nome"""
        return self.icons.get(name)


class HomeUI(ctk.CTkFrame):
    """Interface Home com Dashboard"""

    def __init__(self, parent, usuario, conectar_bd):
        super().__init__(parent, fg_color=_CINZA_BG)
        self.usuario     = usuario
        self.conectar_bd = conectar_bd
        
        # Inicializar ícones
        self.icon_manager = IconManager()
        self.icons = self.icon_manager.setup_icons()

        from .services import DashboardService
        self.service = DashboardService()

        self.stats           = None
        self.usuarios_ativos = []
        self.atividades      = []
        self._atualizando    = False

        self._criar_interface()
        self.after(100, self._atualizar_dados)
        self._agendar_atualizacao()

    # =========================================================================
    # Interface
    # =========================================================================
    def _criar_interface(self):
        self.container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=32, pady=24)

        self._criar_header(self.container)
        self._criar_cards_stats(self.container)

        content_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, pady=(24, 0))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)

        self._criar_coluna_esquerda(content_frame)
        self._criar_coluna_direita(content_frame)

        self._criar_loading_overlay()
        self._mostrar_loading()

    def _criar_header(self, parent):
        """Cabeçalho com título e ícone preto"""
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 24))

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left")
        
        # Ícone do dashboard (preto)
        if self.icons.get("dashboard"):
            ctk.CTkLabel(
                left, text="", image=self.icons["dashboard"],
                width=36, height=36
            ).pack(side="left", padx=(0, 12))
        else:
            ctk.CTkLabel(
                left, text="📊", font=("Segoe UI", 32),
                text_color=_CINZA_TEXTO
            ).pack(side="left", padx=(0, 12))
        
        title_frame = ctk.CTkFrame(left, fg_color="transparent")
        title_frame.pack(side="left")
        
        ctk.CTkLabel(
            title_frame,
            text="Dashboard",
            font=("Segoe UI", 28, "bold"),
            text_color=_CINZA_TEXTO,
        ).pack(anchor="w")

        if isinstance(self.usuario, dict):
            nome_usuario = self.usuario.get(
                "nome", self.usuario.get("username", "Usuário"))
        else:
            nome_usuario = self.usuario or "Usuário"

        ctk.CTkLabel(
            title_frame,
            text=f"Bem-vindo, {nome_usuario}!",
            font=("Segoe UI", 13),
            text_color=_MUTED,
        ).pack(anchor="w", pady=(4, 0))

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.pack(side="right")

        self.lbl_data_hora = ctk.CTkLabel(
            right,
            text=datetime.now().strftime("%d/%m/%Y - %H:%M:%S"),
            font=("Segoe UI", 13),
            text_color=_MUTED,
        )
        self.lbl_data_hora.pack()

        # Botão de atualizar com ícone preto
        btn_atualizar = ctk.CTkButton(
            right,
            text="",
            image=self.icons.get("refresh"),
            width=36, height=36,
            fg_color="transparent",
            hover_color=_CINZA_BORDER,
            text_color=_CINZA_TEXTO,
            command=self._atualizar_dados,
        )
        if not self.icons.get("refresh"):
            btn_atualizar.configure(text="🔄", font=("Segoe UI", 16))
        btn_atualizar.pack(pady=(6, 0))

        self._atualizar_hora()

    def _criar_cards_stats(self, parent):
        """Cards de estatísticas principais com ícones pretos"""
        row1 = ctk.CTkFrame(parent, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 12))
        for i in range(4):
            row1.grid_columnconfigure(i, weight=1)

        self.card_online = self._criar_card_stat(
            row1, "Online", "0", _VERDE_STATUS, 0, "online", "🟢")
        self.card_offline = self._criar_card_stat(
            row1, "Offline", "0", _MUTED, 1, "offline", "⚫")
        self.card_relatorios_hoje = self._criar_card_stat(
            row1, "Relatórios Hoje", "0", _AZUL, 2, "reports", "📊")
        self.card_relatorios_total = self._criar_card_stat(
            row1, "Total Relatórios", "0", _AMARELO, 3, "total_reports", "📈")

        row2 = ctk.CTkFrame(parent, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 20))
        for i in range(4):
            row2.grid_columnconfigure(i, weight=1)

        self.card_inscricoes = self._criar_mini_card(
            row2, "Inscrições", "0", _AZUL, 0, "inscricoes", "📝")
        self.card_devolucoes = self._criar_mini_card(
            row2, "Devoluções", "0", _VERMELHO, 1, "devolucoes", "📤")
        self.card_relatorios_mes = self._criar_mini_card(
            row2, "Relatórios / Mês", "0", _VERDE_STATUS, 2, "monthly", "📅")
        self.lbl_ultimo_acesso = self._criar_mini_card(
            row2, "Último Acesso", "-", _MUTED, 3, "last_access", "🕐", valor_pequeno=True)

    def _criar_card_stat(self, parent, titulo, valor, cor, coluna, icon_key, emoji):
        """Cria um card grande de estatística com ícone preto"""
        card = ctk.CTkFrame(
            parent,
            fg_color=_BRANCO,
            corner_radius=12,
            border_width=1,
            border_color=_CINZA_BORDER,
        )
        card.grid(row=0, column=coluna, padx=10, pady=10, sticky="nsew")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=16)

        # Ícone e valor
        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x")
        
        if self.icons.get(icon_key):
            ctk.CTkLabel(
                top, text="", image=self.icons[icon_key],
                width=28, height=28
            ).pack(side="left")
        else:
            ctk.CTkLabel(
                top, text=emoji, font=("Segoe UI", 28),
                text_color=_CINZA_TEXTO
            ).pack(side="left")
        
        lbl_valor = ctk.CTkLabel(
            top, text=valor,
            font=("Segoe UI", 32, "bold"),
            text_color=cor
        )
        lbl_valor.pack(side="right")
        
        # Título
        ctk.CTkLabel(
            inner, text=titulo,
            font=("Segoe UI", 12),
            text_color=_MUTED
        ).pack(anchor="w", pady=(12, 0))
        
        return lbl_valor

    def _criar_mini_card(self, parent, titulo, valor, cor, coluna, icon_key, emoji, valor_pequeno=False):
        """Cria um card pequeno de estatística com ícone preto"""
        card = ctk.CTkFrame(
            parent,
            fg_color=_BRANCO,
            corner_radius=12,
            border_width=1,
            border_color=_CINZA_BORDER,
        )
        card.grid(row=0, column=coluna, padx=8, pady=4, sticky="nsew")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=12)

        # Linha com ícone e valor
        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x")
        
        if self.icons.get(icon_key):
            ctk.CTkLabel(
                top, text="", image=self.icons[icon_key],
                width=24, height=24
            ).pack(side="left")
        else:
            ctk.CTkLabel(
                top, text=emoji, font=("Segoe UI", 20),
                text_color=_CINZA_TEXTO
            ).pack(side="left")
        
        lbl_valor = ctk.CTkLabel(
            top, text=valor,
            font=("Segoe UI", 18 if not valor_pequeno else 13, "bold"),
            text_color=cor
        )
        lbl_valor.pack(side="right")
        
        # Título
        ctk.CTkLabel(
            inner, text=titulo,
            font=("Segoe UI", 11),
            text_color=_MUTED
        ).pack(anchor="w", pady=(8, 0))
        
        return lbl_valor

    def _criar_coluna_esquerda(self, parent):
        """Coluna esquerda - Usuários Ativos"""
        coluna = ctk.CTkFrame(parent, fg_color="transparent")
        coluna.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        card = ctk.CTkFrame(coluna, fg_color=_BRANCO,
                            corner_radius=12, border_width=1,
                            border_color=_CINZA_BORDER)
        card.pack(fill="both", expand=True)

        # Cabeçalho
        titulo_frame = ctk.CTkFrame(card, fg_color="transparent")
        titulo_frame.pack(fill="x", padx=20, pady=(20, 12))
        
        if self.icons.get("users"):
            ctk.CTkLabel(
                titulo_frame, text="", image=self.icons["users"],
                width=20, height=20
            ).pack(side="left", padx=(0, 8))
        else:
            ctk.CTkLabel(
                titulo_frame, text="👥", font=("Segoe UI", 16),
                text_color=_CINZA_TEXTO
            ).pack(side="left", padx=(0, 8))
        
        ctk.CTkLabel(titulo_frame, text="Usuários Ativos",
                     font=("Segoe UI", 16, "bold"),
                     text_color=_CINZA_TEXTO).pack(side="left")

        self.lbl_online_count = ctk.CTkLabel(
            titulo_frame, text="0 online",
            font=("Segoe UI", 11),
            text_color=_VERDE_STATUS)
        self.lbl_online_count.pack(side="right")

        # Separador
        separator = ctk.CTkFrame(card, height=1, fg_color=_CINZA_BORDER)
        separator.pack(fill="x", padx=20, pady=(0, 12))

        # Lista de usuários
        self.frame_usuarios = ctk.CTkScrollableFrame(
            card, fg_color="transparent", height=350)
        self.frame_usuarios.pack(fill="both", expand=True,
                                 padx=12, pady=(0, 16))

    def _criar_coluna_direita(self, parent):
        """Coluna direita - Atividades Recentes"""
        coluna = ctk.CTkFrame(parent, fg_color="transparent")
        coluna.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        card = ctk.CTkFrame(coluna, fg_color=_BRANCO,
                            corner_radius=12, border_width=1,
                            border_color=_CINZA_BORDER)
        card.pack(fill="both", expand=True)

        # Cabeçalho
        titulo_frame = ctk.CTkFrame(card, fg_color="transparent")
        titulo_frame.pack(fill="x", padx=20, pady=(20, 12))
        
        if self.icons.get("activities"):
            ctk.CTkLabel(
                titulo_frame, text="", image=self.icons["activities"],
                width=20, height=20
            ).pack(side="left", padx=(0, 8))
        else:
            ctk.CTkLabel(
                titulo_frame, text="📋", font=("Segoe UI", 16),
                text_color=_CINZA_TEXTO
            ).pack(side="left", padx=(0, 8))
        
        ctk.CTkLabel(titulo_frame, text="Atividades Recentes",
                     font=("Segoe UI", 16, "bold"),
                     text_color=_CINZA_TEXTO).pack(side="left")

        self.lbl_atividades_count = ctk.CTkLabel(
            titulo_frame, text="0 atividades",
            font=("Segoe UI", 11),
            text_color=_MUTED)
        self.lbl_atividades_count.pack(side="right")

        # Separador
        separator = ctk.CTkFrame(card, height=1, fg_color=_CINZA_BORDER)
        separator.pack(fill="x", padx=20, pady=(0, 12))

        # Lista de atividades
        self.frame_atividades = ctk.CTkScrollableFrame(
            card, fg_color="transparent", height=350)
        self.frame_atividades.pack(fill="both", expand=True,
                                   padx=12, pady=(0, 16))

    def _criar_loading_overlay(self):
        """Overlay de loading com ícone preto"""
        self.loading = ctk.CTkFrame(self, fg_color=_CINZA_BG, corner_radius=0)

        content = ctk.CTkFrame(self.loading, fg_color="transparent")
        content.place(relx=0.5, rely=0.5, anchor="center")

        if self.icons.get("empty"):
            ctk.CTkLabel(
                content, text="", image=self.icons["empty"],
                width=48, height=48
            ).pack(pady=(0, 16))
        else:
            ctk.CTkLabel(content, text="⏳",
                         font=("Segoe UI", 48),
                         text_color=_CINZA_TEXTO).pack(pady=(0, 16))

        ctk.CTkLabel(content, text="Carregando dashboard...",
                     font=("Segoe UI", 14),
                     text_color=_CINZA_TEXTO).pack()

    # =========================================================================
    # Loading
    # =========================================================================
    def _mostrar_loading(self):
        try:
            if hasattr(self, "loading") and self.loading.winfo_exists():
                self.loading.place(relx=0, rely=0, relwidth=1, relheight=1)
                self.loading.lift()
                self.update_idletasks()
        except Exception:
            pass

    def _esconder_loading(self):
        try:
            if hasattr(self, "loading") and self.loading.winfo_exists():
                self.loading.place_forget()
        except Exception:
            pass

    # =========================================================================
    # Atualização de dados
    # =========================================================================
    def _atualizar_dados(self):
        if self._atualizando:
            return
        self._atualizando = True
        self._mostrar_loading()

        import threading
        threading.Thread(target=self._worker_atualizar, daemon=True).start()

    def _worker_atualizar(self):
        try:
            stats      = self.service.obter_estatisticas(self.conectar_bd)
            usuarios   = self.service.obter_usuarios_ativos(self.conectar_bd)
            atividades = self.service.obter_atividades_recentes(
                self.conectar_bd, limit=15)
            try:
                dias, valores = self.service.obter_grafico_relatorios_mensal(
                    self.conectar_bd)
            except Exception:
                dias, valores = [], []

            self._after_safe(
                self._aplicar_dados, stats, usuarios, atividades, dias, valores)

        except Exception as e:
            print(f"[Dashboard] Erro ao buscar dados: {e}")
            self._after_safe(self._esconder_loading)
        finally:
            self._atualizando = False

    def _after_safe(self, fn, *args):
        try:
            if self.winfo_exists():
                if args:
                    self.after(0, fn, *args)
                else:
                    self.after(0, fn)
        except Exception:
            pass

    def _aplicar_dados(self, stats, usuarios, atividades, dias, valores):
        try:
            if not self.winfo_exists():
                return

            self.stats           = stats
            self.usuarios_ativos = usuarios
            self.atividades      = atividades

            self._safe_configure(self.card_online, text=str(stats.usuarios_online))
            self._safe_configure(self.card_offline, text=str(stats.usuarios_offline))
            self._safe_configure(self.card_relatorios_hoje, text=str(stats.relatorios_gerados_hoje))
            self._safe_configure(self.card_relatorios_total, text=str(stats.relatorios_gerados_total))

            self._safe_configure(self.lbl_online_count,
                                 text=f"{stats.usuarios_online} online")
            self._safe_configure(self.lbl_atividades_count,
                                 text=f"{len(atividades)} atividades")

            self._safe_configure(self.card_inscricoes, text=str(stats.total_inscricoes))
            self._safe_configure(self.card_devolucoes, text=str(stats.total_devolucoes))
            self._safe_configure(self.card_relatorios_mes, text=str(stats.relatorios_gerados_mes))
            self._safe_configure(self.lbl_ultimo_acesso, text=stats.ultimo_acesso or "-")

            self._atualizar_usuarios_ativos()
            self._atualizar_atividades()

        except Exception as e:
            print(f"[Dashboard] Erro ao aplicar dados: {e}")
        finally:
            self._esconder_loading()

    @staticmethod
    def _safe_configure(widget, **kw):
        try:
            if widget and widget.winfo_exists():
                widget.configure(**kw)
        except Exception:
            pass

    # =========================================================================
    # Listas
    # =========================================================================
    def _atualizar_usuarios_ativos(self):
        try:
            if not self.frame_usuarios.winfo_exists():
                return
            for w in self.frame_usuarios.winfo_children():
                w.destroy()
        except Exception:
            return

        if not self.usuarios_ativos:
            self._mostrar_mensagem_vazia(
                self.frame_usuarios,
                "😴 Nenhum usuário ativo no momento",
                "Os usuários aparecerão aqui quando estiverem online",
            )
            return

        self.usuarios_ativos.sort(key=lambda x: x.ultimo_acesso, reverse=True)
        for usuario in self.usuarios_ativos[:10]:
            self._criar_item_usuario(usuario)

    def _criar_item_usuario(self, usuario):
        item = ctk.CTkFrame(self.frame_usuarios, fg_color="transparent",
                            corner_radius=8)
        item.pack(fill="x", pady=2)

        item.bind("<Enter>", lambda e: item.configure(fg_color=_CINZA_BG))
        item.bind("<Leave>", lambda e: item.configure(fg_color="transparent"))

        inner = ctk.CTkFrame(item, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=10)

        # Status online
        ctk.CTkLabel(inner, text="🟢",
                     font=("Segoe UI", 12),
                     text_color=_VERDE_STATUS).pack(side="left", padx=(0, 12))

        info_frame = ctk.CTkFrame(inner, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(info_frame, text=usuario.nome,
                     font=("Segoe UI", 13, "bold"),
                     text_color=_CINZA_TEXTO,
                     anchor="w").pack(fill="x")

        ctk.CTkLabel(info_frame,
                     text=f"@{usuario.username} · {usuario.perfil}",
                     font=("Segoe UI", 11),
                     text_color=_MUTED,
                     anchor="w").pack(fill="x")

        tempo_color = _VERDE_STATUS if "minutos" in usuario.tempo_online and "1" in usuario.tempo_online.split()[0] else _MUTED

        ctk.CTkLabel(inner, text=usuario.tempo_online,
                     font=("Segoe UI", 11),
                     text_color=tempo_color).pack(side="right", padx=(10, 0))

    def _atualizar_atividades(self):
        try:
            if not self.frame_atividades.winfo_exists():
                return
            for w in self.frame_atividades.winfo_children():
                w.destroy()
        except Exception:
            return

        if not self.atividades:
            self._mostrar_mensagem_vazia(
                self.frame_atividades,
                "📭 Nenhuma atividade recente",
                "As atividades aparecerão aqui quando ocorrerem",
            )
            return

        for atividade in self.atividades[:15]:
            self._criar_item_atividade(atividade)

    def _criar_item_atividade(self, atividade):
        item = ctk.CTkFrame(self.frame_atividades, fg_color="transparent",
                            corner_radius=8)
        item.pack(fill="x", pady=2)

        item.bind("<Enter>", lambda e: item.configure(fg_color=_CINZA_BG))
        item.bind("<Leave>", lambda e: item.configure(fg_color="transparent"))

        inner = ctk.CTkFrame(item, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=12)

        tipo_upper = (atividade.tipo.upper() if hasattr(atividade, "tipo") else "")
        cor_icone = _MUTED
        icone = "📋"
        
        if "LOGIN" in tipo_upper:
            cor_icone = _VERDE_STATUS
            icone = "🔐"
        elif "RELATORIO" in tipo_upper:
            cor_icone = _AZUL
            icone = "📊"
        elif "INSCRICAO" in tipo_upper:
            cor_icone = _AMARELO
            icone = "📝"
        elif "DEVOLUCAO" in tipo_upper:
            cor_icone = _VERMELHO
            icone = "📤"
        elif any(k in tipo_upper for k in ("CADASTRO", "CRIAR")):
            cor_icone = _VERDE_STATUS
            icone = "✓"

        ctk.CTkLabel(inner, text=icone,
                     font=("Segoe UI", 18),
                     text_color=cor_icone).pack(side="left", padx=(0, 12))

        info_frame = ctk.CTkFrame(inner, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)

        descricao = getattr(atividade, "descricao", "Atividade")
        if len(descricao) > 55:
            descricao = descricao[:55] + "..."

        ctk.CTkLabel(info_frame, text=descricao,
                     font=("Segoe UI", 12),
                     text_color=_CINZA_TEXTO,
                     anchor="w").pack(fill="x")

        usuario = getattr(atividade, "usuario", "Sistema")
        data_hora = (atividade.data_hora_formatada()
                     if hasattr(atividade, "data_hora_formatada") else "")

        ctk.CTkLabel(info_frame,
                     text=f"👤 {usuario} · {data_hora}",
                     font=("Segoe UI", 10),
                     text_color=_MUTED,
                     anchor="w").pack(fill="x")

    # =========================================================================
    # Utilitários
    # =========================================================================
    def _mostrar_mensagem_vazia(self, parent, titulo, subtitulo=""):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(expand=True, fill="both", pady=40)

        ctk.CTkLabel(frame, text=titulo,
                     font=("Segoe UI", 14),
                     text_color=_CINZA_TEXTO).pack(pady=(0, 5))

        if subtitulo:
            ctk.CTkLabel(frame, text=subtitulo,
                         font=("Segoe UI", 11),
                         text_color=_MUTED).pack()

    def _atualizar_hora(self):
        try:
            if self.lbl_data_hora.winfo_exists():
                self.lbl_data_hora.configure(
                    text=datetime.now().strftime("%d/%m/%Y - %H:%M:%S"))
                self.after(1000, self._atualizar_hora)
        except Exception:
            pass

    def _agendar_atualizacao(self):
        self.after(30000, self._ciclo_atualizacao)

    def _ciclo_atualizacao(self):
        try:
            if self.winfo_exists():
                self._atualizar_dados()
                self.after(30000, self._ciclo_atualizacao)
        except Exception:
            pass