# -*- coding: utf-8 -*-
"""
GerenciarUsuariosUI — gerenciamento de usuários com popup modal.

Criar/editar abre UserFormPopup em vez de formulário inline.
"""
import threading
import os
import sys
from PIL import Image

import customtkinter as ctk
from tkinter import messagebox

from ui.base_ui import BaseUI
from app.theme  import AppTheme

from .controller       import UsuarioController
from .services         import ConfiguracaoUsuariosService, HistoricoUsuariosService
from .views import (
    SearchFilterCard,
    UserListCard,
    UserFormPopup,
    ConfirmationDialog,
)

# ── Paleta Corporativa ──────────────────────────────────────────────────────────
_PRIMARY_DARK    = "#0a2540"
_PRIMARY         = "#1a4b6e"
_ACCENT          = "#2c6e9e"
_ACCENT_DARK     = "#1e4a6e"
_ACCENT_LIGHT    = "#e8f0f8"
_BRANCO          = "#ffffff"
_CINZA_BG        = "#f5f7fc"
_CINZA_BORDER    = "#e2e8f0"
_CINZA_MEDIO     = "#5a6e8a"
_CINZA_TEXTO     = "#1e2f3e"
_VERDE_STATUS    = "#10b981"
_VERDE_HOVER     = "#d1fae5"
_VERMELHO        = "#ef4444"
_VERMELHO_DARK   = "#dc2626"
_AZUL_INFO       = "#3b82f6"
_AZUL_INFO_DARK  = "#2563eb"
_PURPLE          = "#8b5cf6"
_MUTED           = "#64748b"
_ICON_COLOR      = "#1e293b"

class IconManager:
    """Gerenciador de ícones para a interface de usuários"""
    
    def __init__(self):
        self.icons = {}
        
        # Tentar encontrar o caminho correto da pasta de ícones
        self._find_icons_path()
        
    def _find_icons_path(self):
        """Encontra o caminho correto para a pasta de ícones"""
        # Caminhos possíveis
        possible_paths = []
        
        # 1. Caminho relativo a partir deste arquivo
        current_dir = os.path.dirname(os.path.abspath(__file__))
        possible_paths.append(os.path.join(current_dir, "..", "..", "..", "..", "images", "icons", "usuarios"))
        possible_paths.append(os.path.join(current_dir, "..", "..", "..", "images", "icons", "usuarios"))
        
        # 2. Caminho absoluto
        possible_paths.append(r"C:\Users\Administrador\Documents\SECTOR AUTOMATION_v14\images\icons\usuarios")
        
        # 3. Caminho base do projeto
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
        possible_paths.append(os.path.join(base_dir, "images", "icons", "usuarios"))
        
        # Procurar o caminho que existe
        for path in possible_paths:
            if os.path.exists(path):
                self.icons_dir = path
                # Listar arquivos encontrados
                try:
                    files = os.listdir(path)
                except:
                    pass
                return
        
        # Se não encontrou, usar o caminho padrão
        self.icons_dir = possible_paths[0]
        
    def load_icon(self, filename, size=(32, 32), colorize_to=None):
        """Carrega um ícone e opcionalmente aplica cor"""
        try:
            path = os.path.join(self.icons_dir, filename)
            
            if os.path.exists(path):
                img = Image.open(path)
                img = img.resize(size, Image.Resampling.LANCZOS)
                
                # Se for para colorir o ícone
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
            else:
                return None
        except Exception as e:
            return None
    
    def setup_icons(self):
        """Configura todos os ícones necessários"""
        icons_config = {
            # Ícones para o header
            "user": ("user.png", (28, 28), _ICON_COLOR),
            "users": ("uses.png", (32, 32), _ICON_COLOR),
            
            # Ícones para os cards de estatísticas
            "total": ("uses.png", (32, 32), _PURPLE),      # Total de usuários
            "ativos": ("ativo.png", (32, 32), _VERDE_STATUS),  # Usuários ativos
            "inativos": ("inativos.png", (32, 32), _VERMELHO),  # Usuários inativos
            "perfis": ("user.png", (32, 32), _ACCENT),      # Perfis disponíveis
        }
        
        for name, (filename, size, color) in icons_config.items():
            self.icons[name] = self.load_icon(filename, size, color)
            pass  # icon loaded
        
        return self.icons

class GerenciarUsuariosUI(BaseUI):

    def __init__(self, parent, usuario_logado, conectar_bd=None):
        super().__init__(parent)
        self.configure(fg_color=_CINZA_BG)

        self.usuario_logado = usuario_logado
        self.conectar_bd    = conectar_bd

        # Inicializar gerenciador de ícones
        self.icon_manager = IconManager()
        self.icons = self.icon_manager.setup_icons()

        self.controller        = UsuarioController(conectar_bd, usuario_logado)
        self.historico_service = HistoricoUsuariosService()

        self._usuarios: list      = []
        self._current_index: int  = 0
        self._pending_users: list = []

        self._criar_interface()
        self._carregar_usuarios()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _criar_interface(self):
        # Container principal com padding
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=32, pady=32)

        self._build_header(main_container)
        self._build_stats_cards(main_container)

        # Card de busca e filtros
        self.search_card = SearchFilterCard(
            main_container,
            on_search=self._filtrar_usuarios,
            on_new_user=self._abrir_popup_novo,
        )
        self.search_card.pack(fill="x", pady=(20, 16))

        # Lista de usuários
        self.user_list_card = UserListCard(main_container)
        self.user_list_card.pack(fill="both", expand=True)

    def _build_header(self, parent):
        """Cria o cabeçalho da tela"""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 24))
        
        # Título e subtítulo
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left")
        
        # Ícone do título
        if self.icons.get("users"):
            icon_label = ctk.CTkLabel(
                title_frame,
                text="",
                image=self.icons["users"],
                width=36,
                height=36
            )
            icon_label.pack(side="left", padx=(0, 12))
        else:
            pass
        
        title_text_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        title_text_frame.pack(side="left")
        
        ctk.CTkLabel(
            title_text_frame,
            text="Gerenciamento de Usuários",
            font=("Segoe UI", 28, "bold"),
            text_color=_CINZA_TEXTO
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_text_frame,
            text="Crie, edite e gerencie os usuários do sistema com segurança",
            font=("Segoe UI", 12),
            text_color=_MUTED
        ).pack(anchor="w", pady=(4, 0))
        
        # Card do usuário logado
        user_card = ctk.CTkFrame(
            header_frame,
            fg_color=_BRANCO,
            corner_radius=12,
            border_width=1,
            border_color=_CINZA_BORDER
        )
        user_card.pack(side="right")
        
        inner = ctk.CTkFrame(user_card, fg_color="transparent")
        inner.pack(padx=20, pady=12)
        
        # Ícone do usuário
        if self.icons.get("user"):
            ctk.CTkLabel(
                inner,
                text="",
                image=self.icons["user"],
                width=28,
                height=28
            ).pack(side="left")
        
        info = ctk.CTkFrame(inner, fg_color="transparent")
        info.pack(side="left", padx=(12, 0))
        
        ctk.CTkLabel(
            info,
            text=self.usuario_logado,
            font=("Segoe UI", 13, "bold"),
            text_color=_CINZA_TEXTO
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            info,
            text="Logado no sistema",
            font=("Segoe UI", 10),
            text_color=_MUTED
        ).pack(anchor="w")
        
        ctk.CTkButton(
            inner,
            text=" Alterar Senha",
            image=self.icons.get("user"),
            compound="left",
            height=36,
            corner_radius=8,
            font=("Segoe UI", 11, "bold"),
            fg_color=_ACCENT,
            hover_color=_ACCENT_DARK,
            text_color=_BRANCO,
            command=self._abrir_editar_proprio_usuario,
        ).pack(side="right", padx=(15, 0))

    def _build_stats_cards(self, parent):
        """Cria os cards de estatísticas com ícones"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(0, 20))
        
        # Configurar grid para 4 colunas
        for i in range(4):
            frame.columnconfigure(i, weight=1)

        specs = [
            ("total", "Total de Usuários", "0", _PURPLE),
            ("ativos", "Usuários Ativos", "0", _VERDE_STATUS),
            ("inativos", "Usuários Inativos", "0", _VERMELHO),
            ("perfis", "Perfis Disponíveis", "3", _ACCENT),
        ]
        
        self._stats_labels: dict[str, ctk.CTkLabel] = {}

        for i, (key, label, value, color) in enumerate(specs):
            card = ctk.CTkFrame(
                frame,
                fg_color=_BRANCO,
                corner_radius=12,
                border_width=1,
                border_color=_CINZA_BORDER
            )
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 12, 0))
            
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=20, pady=16)
            
            # Linha superior com ícone e valor
            row_top = ctk.CTkFrame(inner, fg_color="transparent")
            row_top.pack(fill="x")
            
            # Ícone do card
            icon = self.icons.get(key)
            if icon:
                ctk.CTkLabel(
                    row_top,
                    text="",
                    image=icon,
                    width=32,
                    height=32
                ).pack(side="left")
            else:
                # Fallback visual temporário (apenas para debug)
                ctk.CTkLabel(
                    row_top,
                    text="📊",
                    font=("Segoe UI", 24),
                    text_color=color
                ).pack(side="left")
            
            # Valor
            lbl_valor = ctk.CTkLabel(
                row_top,
                text=value,
                font=("Segoe UI", 28, "bold"),
                text_color=color
            )
            lbl_valor.pack(side="right")
            self._stats_labels[key] = lbl_valor
            
            # Label
            ctk.CTkLabel(
                inner,
                text=label,
                font=("Segoe UI", 12),
                text_color=_MUTED
            ).pack(anchor="w", pady=(12, 0))

    def _update_stats(self):
        """Atualiza os valores dos cards de estatísticas"""
        total    = len(self._usuarios)
        ativos   = sum(1 for u in self._usuarios if u.get("ativo"))
        inativos = total - ativos
        
        self._stats_labels["total"].configure(text=str(total))
        self._stats_labels["ativos"].configure(text=str(ativos))
        self._stats_labels["inativos"].configure(text=str(inativos))

    # ── Carregamento ──────────────────────────────────────────────────────────

    def _carregar_usuarios(self):
        self.user_list_card.show_loading()
        threading.Thread(target=self._worker_carregar, daemon=True).start()

    def _worker_carregar(self):
        try:
            usuarios = self.controller.carregar_usuarios()
            self.after(0, self._on_usuarios_carregados, usuarios)
        except Exception as exc:
            self.after(0, self.user_list_card.show_error, str(exc))

    def _on_usuarios_carregados(self, usuarios: list):
        self._usuarios = usuarios
        self._update_stats()
        self._exibir_usuarios(usuarios)

    def _exibir_usuarios(self, usuarios: list):
        self.user_list_card.clear_users()
        if not usuarios:
            self.user_list_card.show_no_users_message()
            return
        self._current_index = 0
        self._pending_users = usuarios
        self._animate_user_list()

    def _animate_user_list(self):
        if self._current_index < len(self._pending_users):
            u = self._pending_users[self._current_index]
            self.user_list_card.add_user_card(
                u,
                on_select=self._abrir_popup_editar,
                on_delete=self._confirmar_exclusao,
            )
            self._current_index += 1
            self.after(40, self._animate_user_list)

    # ── Filtros ───────────────────────────────────────────────────────────────

    def _filtrar_usuarios(self):
        busca  = self.search_card.get_search_text().lower()
        perfil = self.search_card.get_selected_profile()
        status = self.search_card.get_selected_status()

        filtrados = [
            u for u in self._usuarios
            if (not busca
                or busca in u["username"].lower()
                or busca in (u.get("email") or "").lower())
            and (perfil == "Todos" or u["perfil"] == perfil.lower())
            and (status == "Todos"
                 or (status == "Ativo"   and     u["ativo"])
                 or (status == "Inativo" and not u["ativo"]))
        ]

        if not filtrados:
            self.user_list_card.show_no_users_message(
                "Nenhum usuário encontrado com os filtros aplicados.")
        else:
            self._exibir_usuarios(filtrados)

    # ── Popups ────────────────────────────────────────────────────────────────

    def _abrir_popup_novo(self):
        UserFormPopup(
            self,
            on_save   = self._on_popup_save,
            on_delete = None,
            user_data = None,
        )

    def _abrir_popup_editar(self, usuario: dict):
        self.historico_service.registrar_operacao(
            self.usuario_logado, "visualizar",
            f"Visualizou usuário: {usuario['username']}")
        UserFormPopup(
            self,
            on_save   = self._on_popup_save,
            on_delete = self._on_popup_delete,
            user_data = usuario,
        )

    # ── Callbacks do popup ────────────────────────────────────────────────────

    def _on_popup_save(self, form_data: dict, is_new_user: bool,
                       user_data, popup: UserFormPopup):
        # Validar
        erros = self.controller.validar_usuario(form_data, is_new_user)
        if erros:
            messagebox.showerror("Erro de Validação", "\n".join(erros))
            return

        if form_data.get("cpf"):
            ok, cpf_limpo = self.controller.validar_cpf(form_data["cpf"])
            if not ok:
                messagebox.showerror("Erro", "CPF inválido")
                return
            form_data["cpf"] = cpf_limpo

        popup.show_saving_state()

        def _worker():
            sucesso, msg = self.controller.salvar_usuario(form_data, user_data)
            self.after(0, self._on_save_result,
                       sucesso, msg, is_new_user, form_data, popup)

        threading.Thread(target=_worker, daemon=True).start()

    def _on_save_result(self, sucesso: bool, msg: str,
                        is_new_user: bool, form_data: dict,
                        popup: UserFormPopup):
        popup.hide_saving_state()
        if sucesso:
            tipo = "criar" if is_new_user else "editar"
            self.historico_service.registrar_operacao(
                self.usuario_logado, tipo,
                f"{'Criou' if is_new_user else 'Editou'} usuário: "
                f"{form_data['username']}")
            messagebox.showinfo("Sucesso", f"✅ {msg}")
            popup.destroy()
            self._carregar_usuarios()
        else:
            messagebox.showerror("Erro", f"❌ {msg}")

    def _on_popup_delete(self, usuario: dict, popup: UserFormPopup):
        if usuario["username"] == self.usuario_logado:
            messagebox.showerror(
                "Erro",
                "❌ Você não pode excluir seu próprio usuário!\n\n"
                "Esta ação está bloqueada por segurança.")
            return

        dlg = ConfirmationDialog(
            self,
            "⚠️ Confirmar Exclusão",
            f"Tem certeza que deseja excluir o usuário\n\n"
            f"👤 {usuario['username']}\n\n"
            f"Esta ação é irreversível.",
            type="warning",
        )
        if not dlg.show():
            return

        self.user_list_card.disable_user_actions(usuario["username"])

        def _worker():
            sucesso, msg = self.controller.excluir_usuario(usuario["username"])
            self.after(0, self._on_delete_result, sucesso, msg, usuario, popup)

        threading.Thread(target=_worker, daemon=True).start()

    def _on_delete_result(self, sucesso: bool, msg: str,
                          usuario: dict, popup: UserFormPopup):
        if sucesso:
            self.historico_service.registrar_operacao(
                self.usuario_logado, "excluir",
                f"Excluiu usuário: {usuario['username']}")
            messagebox.showinfo("Sucesso", f"✅ {msg}")
            popup.destroy()
            self._carregar_usuarios()
        else:
            messagebox.showerror("Erro", f"❌ {msg}")
            self.user_list_card.enable_user_actions(usuario["username"])

    # ── Confirmar exclusão direto do card ─────────────────────────────────────

    def _confirmar_exclusao(self, usuario: dict):
        """Acionado pelo botão 🗑️ direto no card — pede confirmação e exclui."""
        if usuario["username"] == self.usuario_logado:
            messagebox.showerror(
                "Erro",
                "❌ Você não pode excluir seu próprio usuário!\n\nEsta ação está bloqueada por segurança.")
            return

        dlg = ConfirmationDialog(
            self,
            "⚠️ Confirmar Exclusão",
            f"Tem certeza que deseja excluir o usuário\n\n👤 {usuario['username']}\n\nEsta ação é irreversível.",
            type="warning",
        )
        if not dlg.show():
            return

        self.user_list_card.disable_user_actions(usuario["username"])

        def _worker():
            sucesso, msg = self.controller.excluir_usuario(usuario["username"])
            self.after(0, self._on_delete_card_result, sucesso, msg, usuario)

        threading.Thread(target=_worker, daemon=True).start()

    def _on_delete_card_result(self, sucesso: bool, msg: str, usuario: dict):
        if sucesso:
            self.historico_service.registrar_operacao(
                self.usuario_logado, "excluir",
                f"Excluiu usuário: {usuario['username']}")
            messagebox.showinfo("Sucesso", f"✅ {msg}")
            self._carregar_usuarios()
        else:
            messagebox.showerror("Erro", f"❌ {msg}")
            self.user_list_card.enable_user_actions(usuario["username"])

    # ── Editar próprio usuário ────────────────────────────────────────────────

    def _abrir_editar_proprio_usuario(self):
        usuario_atual = next(
            (u for u in self._usuarios
             if u["username"] == self.usuario_logado),
            {"username": self.usuario_logado},
        )
        UserFormPopup(
            self,
            on_save=self._on_popup_save,
            on_delete=None,
            user_data=usuario_atual,
        )