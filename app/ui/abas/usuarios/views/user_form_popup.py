# -*- coding: utf-8 -*-
"""UserFormPopup — popup modal para criar ou editar usuário."""

import customtkinter as ctk
from app.theme import AppTheme

def _aplicar_mascara_cpf(entry):
    """Aplica máscara CPF (000.000.000-00) em tempo real ao entry."""
    def _on_key(event=None):
        texto = entry.get()
        apenas_numeros = ''.join(c for c in texto if c.isdigit())[:11]
        mascara = ''
        for i, d in enumerate(apenas_numeros):
            if i == 3 or i == 6:
                mascara += '.'
            elif i == 9:
                mascara += '-'
            mascara += d
        entry.delete(0, 'end')
        entry.insert(0, mascara)
    entry.bind('<KeyRelease>', _on_key)


_VERDE  = "#22c55e"
_VERDE_H = "#16a34a"
_VERM   = "#ef4444"
_VERM_H = "#dc2626"
_MUTED  = "#64748b"

# Perfis atualizados
PERFIS = ["administrador", "chefe", "usuario"]


class UserFormPopup(ctk.CTkToplevel):

    def __init__(self, master, on_save, on_delete=None,
                 user_data: dict = None):
        super().__init__(master)
        self._on_save   = on_save
        self._on_delete = on_delete
        self._user_data = user_data
        self._is_new    = user_data is None

        titulo = ("➕ Novo Usuário" if self._is_new
                  else f"✏️ Editando: {user_data.get('username', '')}")
        self.title(titulo)
        self.geometry("560x500")
        self.resizable(False, False)
        self.configure(fg_color=AppTheme.BG_APP)
        self.grab_set()
        self.after(0, self._centralizar)
        self._build()
        if not self._is_new:
            self._carregar_dados()

    def _centralizar(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = self.winfo_screenwidth()  // 2 - w // 2
        y = self.winfo_screenheight() // 2 - h // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build(self):
        wrap = ctk.CTkFrame(self, fg_color=AppTheme.BG_CARD, corner_radius=16)
        wrap.pack(fill="both", expand=True, padx=20, pady=20)

        inner = ctk.CTkFrame(wrap, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        titulo = ("➕ Novo Usuário" if self._is_new
                  else f"✏️ Editando: {self._user_data.get('username', '')}")
        ctk.CTkLabel(inner, text=titulo,
                     font=("Segoe UI", 18, "bold"),
                     text_color=AppTheme.TXT_MAIN,
                     ).pack(anchor="w", pady=(0, 18))

        grid = ctk.CTkFrame(inner, fg_color="transparent")
        grid.pack(fill="x")
        grid.columnconfigure((0, 1), weight=1)

        def _lbl(txt, row, col):
            ctk.CTkLabel(grid, text=txt,
                         font=("Segoe UI", 11, "bold"),
                         text_color=_MUTED, anchor="w",
                         ).grid(row=row * 2, column=col,
                                padx=(0, 8) if col == 0 else (8, 0),
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
                   padx=(0, 8) if col == 0 else (8, 0),
                   sticky="ew")
            return e

        _lbl("Usuário *", 0, 0); self._e_user = _entry("nome.sobrenome", 0, 0)
        _lbl("Perfil *",  0, 1)
        self._combo = ctk.CTkComboBox(
            grid, values=PERFIS,
            height=40, corner_radius=10,
            font=("Segoe UI", 12),
            fg_color=AppTheme.BG_INPUT, border_color=AppTheme.BG_INPUT,
            button_color=_VERDE, button_hover_color=_VERDE_H,
            text_color=AppTheme.TXT_MAIN,
            dropdown_fg_color=AppTheme.BG_CARD,
            dropdown_text_color=AppTheme.TXT_MAIN)
        self._combo.grid(row=1, column=1, padx=(8, 0), sticky="ew")
        self._combo.set("usuario")   # padrão é "usuario"

        _lbl("CPF",         1, 0); self._e_cpf   = _entry("000.000.000-00",              1, 0)
        _aplicar_mascara_cpf(self._e_cpf)
        _lbl("E-mail",      1, 1); self._e_email = _entry("usuario@dominio.com",          1, 1)
        _lbl("Senha",       2, 0)
        self._e_senha = _entry(
            "Senha obrigatória" if self._is_new else "Deixe em branco p/ manter",
            2, 0, show="*")
        _lbl("Observações", 2, 1); self._e_obs = _entry("Observações opcionais", 2, 1)

        self._var_ativo = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            inner, text="Usuário ativo",
            variable=self._var_ativo,
            fg_color=_VERDE, hover_color=_VERDE_H,
            font=("Segoe UI", 12),
            text_color=AppTheme.TXT_MAIN,
        ).pack(anchor="w", pady=(12, 16))

        btns = ctk.CTkFrame(inner, fg_color="transparent")
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
            command=self.destroy,
        ).pack(side="left")

        if not self._is_new and self._on_delete:
            ctk.CTkButton(
                btns, text="🗑 Excluir",
                height=42, corner_radius=10,
                fg_color=_VERM, hover_color=_VERM_H,
                font=("Segoe UI", 13), text_color="#fff",
                command=self._excluir,
            ).pack(side="right")

    def _carregar_dados(self):
        u = self._user_data
        self._e_user.insert(0,  u.get("username",   "") or "")
        self._e_user.configure(state="disabled")
        self._combo.set(u.get("perfil", "usuario"))
        self._e_cpf.insert(0,   u.get("cpf",        "") or "")
        self._e_email.insert(0, u.get("email",       "") or "")
        self._e_obs.insert(0,   u.get("observacoes", "") or "")
        self._var_ativo.set(bool(u.get("ativo", True)))

    def show_saving_state(self):
        self._btn_salvar.configure(state="disabled", text="⏳ Salvando...")

    def hide_saving_state(self):
        self._btn_salvar.configure(state="normal", text="💾 Salvar")

    def _salvar(self):
        form = {
            "username":    self._e_user.get().strip(),
            "perfil":      self._combo.get().strip(),
            "cpf":         self._e_cpf.get().strip(),
            "email":       self._e_email.get().strip(),
            "senha":       self._e_senha.get().strip(),
            "observacoes": self._e_obs.get().strip(),
            "ativo":       self._var_ativo.get(),
        }
        self._on_save(form, self._is_new, self._user_data, self)

    def _excluir(self):
        if self._on_delete:
            self._on_delete(self._user_data, self)