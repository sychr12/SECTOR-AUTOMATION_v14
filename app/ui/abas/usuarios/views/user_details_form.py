# -*- coding: utf-8 -*-
"""UserDetailsForm — formulário inline de criação e edição de usuário."""

import customtkinter as ctk
from app.theme import AppTheme

_VERDE  = "#22c55e"
_VERDE_H = "#16a34a"
_VERM   = "#ef4444"
_VERM_H = "#dc2626"
_MUTED  = "#64748b"

# Perfis atualizados
PERFIS = ["administrador", "chefe", "usuario"]


class UserDetailsForm(ctk.CTkFrame):
    """
    Callbacks:
        on_save(form_data, is_new_user, user_data)
        on_cancel()
        on_delete(user_data)
    """

    def __init__(self, master, on_save, on_cancel, on_delete, **kwargs):
        super().__init__(master,
                         fg_color=AppTheme.BG_CARD,
                         corner_radius=16, **kwargs)
        self._on_save   = on_save
        self._on_cancel = on_cancel
        self._on_delete = on_delete
        self._user_data = None
        self._is_new    = True
        self._build()

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self):
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=24, pady=20)

        self._lbl_titulo = ctk.CTkLabel(
            wrap, text="Novo Usuário",
            font=("Segoe UI", 18, "bold"),
            text_color=AppTheme.TXT_MAIN)
        self._lbl_titulo.pack(anchor="w", pady=(0, 16))

        # Grid 2 colunas
        grid = ctk.CTkFrame(wrap, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 12))
        grid.columnconfigure((0, 1), weight=1)

        def _lbl(txt, row, col):
            ctk.CTkLabel(grid, text=txt,
                         font=("Segoe UI", 11, "bold"),
                         text_color=_MUTED, anchor="w",
                         ).grid(row=row * 2, column=col,
                                padx=(0, 12) if col == 0 else (12, 0),
                                pady=(8, 2), sticky="w")

        def _entry(ph, row, col, show=""):
            e = ctk.CTkEntry(
                grid, placeholder_text=ph,
                height=40, corner_radius=10,
                font=("Segoe UI", 12),
                fg_color=AppTheme.BG_INPUT,
                border_color=AppTheme.BG_INPUT,
                text_color=AppTheme.TXT_MAIN,
                show=show)
            e.grid(row=row * 2 + 1, column=col,
                   padx=(0, 12) if col == 0 else (12, 0),
                   sticky="ew")
            return e

        _lbl("Usuário *",   0, 0); self._e_user  = _entry("nome.sobrenome",            0, 0)
        _lbl("Perfil *",    0, 1)
        self._combo_perfil = ctk.CTkComboBox(
            grid, values=PERFIS,
            height=40, corner_radius=10,
            font=("Segoe UI", 12),
            fg_color=AppTheme.BG_INPUT, border_color=AppTheme.BG_INPUT,
            button_color=_VERDE, button_hover_color=_VERDE_H,
            text_color=AppTheme.TXT_MAIN,
            dropdown_fg_color=AppTheme.BG_CARD,
            dropdown_text_color=AppTheme.TXT_MAIN)
        self._combo_perfil.grid(row=1, column=1, padx=(12, 0), sticky="ew")
        self._combo_perfil.set("usuario")  # padrão agora é "usuario"

        _lbl("CPF",         1, 0); self._e_cpf   = _entry("000.000.000-00",            1, 0)
        _lbl("E-mail",      1, 1); self._e_email = _entry("usuario@dominio.com",        1, 1)
        _lbl("Senha",       2, 0); self._e_senha = _entry("Deixe em branco p/ manter", 2, 0, show="*")
        _lbl("Observações", 2, 1); self._e_obs   = _entry("Observações opcionais",      2, 1)

        # Status ativo
        self._var_ativo = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            wrap, text="Usuário ativo",
            variable=self._var_ativo,
            fg_color=_VERDE, hover_color=_VERDE_H,
            font=("Segoe UI", 12),
            text_color=AppTheme.TXT_MAIN,
        ).pack(anchor="w", pady=(0, 14))

        # Botões
        btns = ctk.CTkFrame(wrap, fg_color="transparent")
        btns.pack(fill="x")

        self._btn_salvar = ctk.CTkButton(
            btns, text="💾 Salvar",
            height=42, corner_radius=10,
            fg_color=_VERDE, hover_color=_VERDE_H,
            font=("Segoe UI", 13, "bold"), text_color="#fff",
            command=self._salvar)
        self._btn_salvar.pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btns, text="Cancelar",
            height=42, corner_radius=10,
            fg_color=AppTheme.BG_INPUT, hover_color=AppTheme.BG_APP,
            font=("Segoe UI", 13), text_color=AppTheme.TXT_MAIN,
            command=self._on_cancel,
        ).pack(side="left", padx=(0, 8))

        self._btn_excluir = ctk.CTkButton(
            btns, text="🗑 Excluir Usuário",
            height=42, corner_radius=10,
            fg_color=_VERM, hover_color=_VERM_H,
            font=("Segoe UI", 13), text_color="#fff",
            command=self._excluir)
        # Visível só em modo edição

    # ── API pública ───────────────────────────────────────────────────────────

    def load_user(self, user_data: dict):
        """Carrega dados de um usuário existente no formulário."""
        self._user_data = user_data
        self._is_new    = False
        self._lbl_titulo.configure(
            text=f"✏️ Editando: {user_data.get('username', '')}")
        self._clear()
        self._e_user.configure(state="normal")
        self._e_user.insert(0, user_data.get("username", "") or "")
        self._e_user.configure(state="disabled")
        self._combo_perfil.set(user_data.get("perfil", "usuario"))
        self._e_cpf.insert(0,   user_data.get("cpf",          "") or "")
        self._e_email.insert(0, user_data.get("email",         "") or "")
        self._e_obs.insert(0,   user_data.get("observacoes",   "") or "")
        self._var_ativo.set(bool(user_data.get("ativo", True)))
        self._btn_excluir.pack(side="right")

    def new_user(self):
        """Prepara o formulário para criação de novo usuário."""
        self._user_data = None
        self._is_new    = True
        self._lbl_titulo.configure(text="➕ Novo Usuário")
        self._clear()
        self._e_user.configure(state="normal")
        self._combo_perfil.set("usuario")
        self._var_ativo.set(True)
        self._btn_excluir.pack_forget()

    def clear_form(self):
        self.new_user()

    def show_saving_state(self):
        """Desabilita o botão Salvar e mostra indicador de carregamento."""
        self._btn_salvar.configure(
            state="disabled", text="⏳ Salvando...")

    def hide_saving_state(self):
        """Restaura o botão Salvar ao estado normal."""
        self._btn_salvar.configure(
            state="normal", text="💾 Salvar")

    # ── Internos ──────────────────────────────────────────────────────────────

    def _clear(self):
        for e in (self._e_user, self._e_cpf,
                  self._e_email, self._e_senha, self._e_obs):
            e.configure(state="normal")
            e.delete(0, "end")

    def _salvar(self):
        form = {
            "username":    self._e_user.get().strip(),
            "perfil":      self._combo_perfil.get().strip(),
            "cpf":         self._e_cpf.get().strip(),
            "email":       self._e_email.get().strip(),
            "senha":       self._e_senha.get().strip(),
            "observacoes": self._e_obs.get().strip(),
            "ativo":       self._var_ativo.get(),
        }
        self._on_save(form, self._is_new, self._user_data)

    def _excluir(self):
        if self._user_data:
            self._on_delete(self._user_data)