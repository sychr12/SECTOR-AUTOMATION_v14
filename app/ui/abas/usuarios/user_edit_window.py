# -*- coding: utf-8 -*-

import customtkinter as ctk
from app.theme import AppTheme


class UserEditWindow(ctk.CTkToplevel):

    def __init__(self, master, user_data, on_confirm):
        super().__init__(master)

        self.title("Alterar Dados do Usuário")
        self.geometry("500x420")
        self.resizable(False, False)

        self.user_data = user_data
        self.on_confirm = on_confirm

        self.grab_set()  # deixa modal (bloqueia tela anterior)
        self._create_widgets()
        self._load_data()

    def _create_widgets(self):

        container = ctk.CTkFrame(self, fg_color=AppTheme.BG_CARD)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            container,
            text="Editar Dados do Usuário",
            font=("Segoe UI", 18, "bold"),
            text_color=AppTheme.TXT_MAIN
        ).pack(pady=(0, 20))

        self.entry_email = self._create_field(container, "Email")
        self.entry_cpf = self._create_field(container, "CPF")
        self.entry_password = self._create_field(container, "Nova Senha", show="*")

        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(
            btn_frame,
            text="Salvar Alterações",
            fg_color=AppTheme.BTN_SUCCESS,
            command=self._confirm
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            fg_color=AppTheme.BG_INPUT,
            command=self.destroy
        ).pack(side="left", padx=10)

    def _create_field(self, parent, label, show=None):

        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            frame,
            text=label,
            font=("Segoe UI", 12, "bold"),
            text_color=AppTheme.TXT_MUTED
        ).pack(anchor="w", pady=(0, 5))

        entry = ctk.CTkEntry(frame, height=40, show=show)
        entry.pack(fill="x")

        return entry

    def _load_data(self):
        self.entry_email.insert(0, self.user_data.get("email") or "")
        self.entry_cpf.insert(0, self.user_data.get("cpf") or "")

    def _confirm(self):

        dados = {
            "email": self.entry_email.get().strip(),
            "cpf": self.entry_cpf.get().strip(),
            "senha": self.entry_password.get().strip()
        }

        if self.on_confirm:
            self.on_confirm(dados)

        self.destroy()