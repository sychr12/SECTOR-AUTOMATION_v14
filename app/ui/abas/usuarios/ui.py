# -*- coding: utf-8 -*-
"""
GerenciarUsuariosUI — gerenciamento de usuários com popup modal.
Versão PyQt6.
"""

import threading
import os
from PyQt6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QComboBox, QMessageBox,
    QScrollArea, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPixmap

from app.theme import AppTheme

from .controller import UsuarioController
from .services import ConfiguracaoUsuariosService, HistoricoUsuariosService
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


class GerenciarUsuariosUI(QWidget):
    """Interface de gerenciamento de usuários."""

    def __init__(self, parent=None, usuario_logado=None, conectar_bd=None):
        super().__init__(parent)
        
        self.usuario_logado = usuario_logado
        self.conectar_bd = conectar_bd

        # Configurar estilo base
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {_CINZA_BG};
            }}
        """)

        self.controller = UsuarioController(conectar_bd, usuario_logado)
        self.historico_service = HistoricoUsuariosService()

        self._usuarios: list = []
        self._current_index: int = 0
        self._pending_users: list = []

        self._criar_interface()
        self._carregar_usuarios()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _criar_interface(self):
        # Container principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 32, 32, 32)
        main_layout.setSpacing(20)

        self._build_header(main_layout)
        self._build_stats_cards(main_layout)

        # Card de busca e filtros
        self.search_card = SearchFilterCard(
            on_search=self._filtrar_usuarios,
            on_new_user=self._abrir_popup_novo,
        )
        main_layout.addWidget(self.search_card)

        # Lista de usuários
        self.user_list_card = UserListCard()
        main_layout.addWidget(self.user_list_card, 1)

    def _build_header(self, parent_layout):
        """Cria o cabeçalho da tela"""
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 24)
        
        # Título e subtítulo
        title_frame = QWidget()
        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Gerenciamento de Usuários")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {_CINZA_TEXTO};")
        title_layout.addWidget(title)
        
        subtitle = QLabel("Crie, edite e gerencie os usuários do sistema com segurança")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setStyleSheet(f"color: {_MUTED};")
        title_layout.addWidget(subtitle)
        
        header_layout.addWidget(title_frame, 1)
        
        # Card do usuário logado
        user_card = QFrame()
        user_card.setStyleSheet(f"""
            QFrame {{
                background-color: {_BRANCO};
                border-radius: 12px;
                border: 1px solid {_CINZA_BORDER};
            }}
        """)
        user_card.setFixedWidth(200)
        
        user_inner = QVBoxLayout(user_card)
        user_inner.setContentsMargins(20, 12, 20, 12)
        
        user_name = QLabel(self.usuario_logado or "Usuário")
        user_name.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        user_inner.addWidget(user_name)
        
        user_status = QLabel("Logado no sistema")
        user_status.setFont(QFont("Segoe UI", 10))
        user_status.setStyleSheet(f"color: {_MUTED};")
        user_inner.addWidget(user_status)
        
        btn_alterar = QPushButton("🔑 Alterar Senha")
        btn_alterar.setStyleSheet(f"""
            QPushButton {{
                background-color: {_ACCENT};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                margin-top: 8px;
            }}
            QPushButton:hover {{
                background-color: {_ACCENT_DARK};
            }}
        """)
        btn_alterar.clicked.connect(self._abrir_editar_proprio_usuario)
        user_inner.addWidget(btn_alterar)
        
        header_layout.addWidget(user_card)
        parent_layout.addWidget(header_widget)

    def _build_stats_cards(self, parent_layout):
        """Cria os cards de estatísticas"""
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(12)
        
        specs = [
            ("total", "Total de Usuários", _PURPLE),
            ("ativos", "Usuários Ativos", _VERDE_STATUS),
            ("inativos", "Usuários Inativos", _VERMELHO),
            ("perfis", "Perfis Disponíveis", _ACCENT),
        ]
        
        self._stats_labels = {}
        
        for key, label, color in specs:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {_BRANCO};
                    border-radius: 12px;
                    border: 1px solid {_CINZA_BORDER};
                }}
            """)
            
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(20, 16, 20, 16)
            
            lbl_valor = QLabel("0")
            lbl_valor.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
            lbl_valor.setStyleSheet(f"color: {color};")
            card_layout.addWidget(lbl_valor)
            
            lbl_desc = QLabel(label)
            lbl_desc.setFont(QFont("Segoe UI", 11))
            lbl_desc.setStyleSheet(f"color: {_MUTED};")
            card_layout.addWidget(lbl_desc)
            
            self._stats_labels[key] = lbl_valor
            stats_layout.addWidget(card)
        
        parent_layout.addLayout(stats_layout)

    def _update_stats(self):
        """Atualiza os valores dos cards de estatísticas"""
        total = len(self._usuarios)
        ativos = sum(1 for u in self._usuarios if u.get("ativo", False))
        inativos = total - ativos
        
        self._stats_labels["total"].setText(str(total))
        self._stats_labels["ativos"].setText(str(ativos))
        self._stats_labels["inativos"].setText(str(inativos))
        self._stats_labels["perfis"].setText("3")

    # ── Carregamento ──────────────────────────────────────────────────────────

    def _carregar_usuarios(self):
        """Carrega usuários em background"""
        self.user_list_card.show_loading()
        threading.Thread(target=self._worker_carregar, daemon=True).start()

    def _worker_carregar(self):
        try:
            usuarios = self.controller.carregar_usuarios()
            QTimer.singleShot(0, lambda: self._on_usuarios_carregados(usuarios))
        except Exception as exc:
            QTimer.singleShot(0, lambda: self.user_list_card.show_error(str(exc)))

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
            QTimer.singleShot(40, self._animate_user_list)

    # ── Filtros ───────────────────────────────────────────────────────────────

    def _filtrar_usuarios(self):
        busca = self.search_card.get_search_text().lower()
        perfil = self.search_card.get_selected_profile()
        status = self.search_card.get_selected_status()

        filtrados = [
            u for u in self._usuarios
            if (not busca
                or busca in u.get("username", "").lower()
                or busca in (u.get("email") or "").lower())
            and (perfil == "Todos" or u.get("perfil", "").lower() == perfil.lower())
            and (status == "Todos"
                 or (status == "Ativo" and u.get("ativo", False))
                 or (status == "Inativo" and not u.get("ativo", False)))
        ]

        if not filtrados:
            self.user_list_card.show_no_users_message(
                "Nenhum usuário encontrado com os filtros aplicados.")
        else:
            self._exibir_usuarios(filtrados)

    # ── Popups ────────────────────────────────────────────────────────────────

    def _abrir_popup_novo(self):
        popup = UserFormPopup(
            self,
            on_save=self._on_popup_save,
            on_delete=None,
            user_data=None,
        )
        popup.show()

    def _abrir_popup_editar(self, usuario: dict):
        if self.historico_service:
            self.historico_service.registrar_operacao(
                self.usuario_logado, "visualizar",
                f"Visualizou usuário: {usuario.get('username', '')}")
        popup = UserFormPopup(
            self,
            on_save=self._on_popup_save,
            on_delete=self._on_popup_delete,
            user_data=usuario,
        )
        popup.show()

    # ── Callbacks do popup ────────────────────────────────────────────────────

    def _on_popup_save(self, form_data: dict, is_new_user: bool,
                       user_data, popup):
        # Validar
        erros = self.controller.validar_usuario(form_data, is_new_user)
        if erros:
            QMessageBox.critical(self, "Erro de Validação", "\n".join(erros))
            return

        if form_data.get("cpf"):
            ok, cpf_limpo = self.controller.validar_cpf(form_data["cpf"])
            if not ok:
                QMessageBox.critical(self, "Erro", "CPF inválido")
                return
            form_data["cpf"] = cpf_limpo

        popup.show_saving_state()

        def _worker():
            sucesso, msg = self.controller.salvar_usuario(form_data, user_data)
            QTimer.singleShot(0, lambda: self._on_save_result(
                sucesso, msg, is_new_user, form_data, popup))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_save_result(self, sucesso: bool, msg: str,
                        is_new_user: bool, form_data: dict,
                        popup):
        popup.hide_saving_state()
        if sucesso:
            tipo = "criar" if is_new_user else "editar"
            if self.historico_service:
                self.historico_service.registrar_operacao(
                    self.usuario_logado, tipo,
                    f"{'Criou' if is_new_user else 'Editou'} usuário: "
                    f"{form_data.get('username', '')}")
            QMessageBox.information(self, "Sucesso", f"✅ {msg}")
            popup.close()
            self._carregar_usuarios()
        else:
            QMessageBox.critical(self, "Erro", f"❌ {msg}")

    def _on_popup_delete(self, usuario: dict, popup):
        if usuario.get("username") == self.usuario_logado:
            QMessageBox.critical(
                self,
                "Erro",
                "❌ Você não pode excluir seu próprio usuário!\n\n"
                "Esta ação está bloqueada por segurança.")
            return

        dlg = ConfirmationDialog(
            self,
            "⚠️ Confirmar Exclusão",
            f"Tem certeza que deseja excluir o usuário\n\n"
            f"👤 {usuario.get('username', '')}\n\n"
            f"Esta ação é irreversível.",
            type="warning",
        )
        if not dlg.show():
            return

        self.user_list_card.disable_user_actions(usuario.get("username", ""))

        def _worker():
            sucesso, msg = self.controller.excluir_usuario(usuario.get("username", ""))
            QTimer.singleShot(0, lambda: self._on_delete_result(sucesso, msg, usuario, popup))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_delete_result(self, sucesso: bool, msg: str,
                          usuario: dict, popup):
        if sucesso:
            if self.historico_service:
                self.historico_service.registrar_operacao(
                    self.usuario_logado, "excluir",
                    f"Excluiu usuário: {usuario.get('username', '')}")
            QMessageBox.information(self, "Sucesso", f"✅ {msg}")
            popup.close()
            self._carregar_usuarios()
        else:
            QMessageBox.critical(self, "Erro", f"❌ {msg}")
            self.user_list_card.enable_user_actions(usuario.get("username", ""))

    # ── Confirmar exclusão direto do card ─────────────────────────────────────

    def _confirmar_exclusao(self, usuario: dict):
        """Acionado pelo botão 🗑️ direto no card — pede confirmação e exclui."""
        if usuario.get("username") == self.usuario_logado:
            QMessageBox.critical(
                self,
                "Erro",
                "❌ Você não pode excluir seu próprio usuário!\n\nEsta ação está bloqueada por segurança.")
            return

        dlg = ConfirmationDialog(
            self,
            "⚠️ Confirmar Exclusão",
            f"Tem certeza que deseja excluir o usuário\n\n👤 {usuario.get('username', '')}\n\nEsta ação é irreversível.",
            type="warning",
        )
        if not dlg.show():
            return

        self.user_list_card.disable_user_actions(usuario.get("username", ""))

        def _worker():
            sucesso, msg = self.controller.excluir_usuario(usuario.get("username", ""))
            QTimer.singleShot(0, lambda: self._on_delete_card_result(sucesso, msg, usuario))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_delete_card_result(self, sucesso: bool, msg: str, usuario: dict):
        if sucesso:
            if self.historico_service:
                self.historico_service.registrar_operacao(
                    self.usuario_logado, "excluir",
                    f"Excluiu usuário: {usuario.get('username', '')}")
            QMessageBox.information(self, "Sucesso", f"✅ {msg}")
            self._carregar_usuarios()
        else:
            QMessageBox.critical(self, "Erro", f"❌ {msg}")
            self.user_list_card.enable_user_actions(usuario.get("username", ""))

    # ── Editar próprio usuário ────────────────────────────────────────────────

    def _abrir_editar_proprio_usuario(self):
        usuario_atual = next(
            (u for u in self._usuarios if u.get("username") == self.usuario_logado),
            {"username": self.usuario_logado},
        )
        popup = UserFormPopup(
            self,
            on_save=self._on_popup_save,
            on_delete=None,
            user_data=usuario_atual,
        )
        popup.show()