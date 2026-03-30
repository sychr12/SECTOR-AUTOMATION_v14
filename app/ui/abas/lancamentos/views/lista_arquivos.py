# -*- coding: utf-8 -*-
import customtkinter as ctk
from app.theme import AppTheme   # ← CORRIGIDO (era: from theme import AppTheme)


class ListaArquivosView(ctk.CTkToplevel):

    def __init__(self, master, usuario, controller):
        super().__init__(master)
        self.usuario    = usuario
        self.controller = controller

        self.title("Lista de Arquivos")
        self.geometry("800x600")
        self.configure(fg_color=AppTheme.BG_APP)
        self.grab_set()

        self._centralizar()
        self._build()

    def _centralizar(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth()  // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build(self):
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=24, pady=24)

        ctk.CTkLabel(wrap, text="Lista de Arquivos",
                     font=("Segoe UI", 22, "bold"),
                     text_color=AppTheme.TXT_MAIN
                     ).pack(anchor="w", pady=(0, 16))

        ctk.CTkLabel(wrap,
                     text="Esta funcionalidade está em desenvolvimento.",
                     text_color="#64748b",
                     font=("Segoe UI", 14)).pack(pady=50)