# -*- coding: utf-8 -*-
"""Popup de devolução — design refinado."""
import customtkinter as ctk
from app.theme import AppTheme

_VERDE   = "#22c55e"
_VERDE_H = "#16a34a"
_VERM    = "#ef4444"
_VERM_H  = "#dc2626"
_MUTED   = "#64748b"

MOTIVOS = ["Endereço", "Documentos", "Cadastro",
           "Pesca", "Simples Nacional", "Animais", "Outros"]


class DevolucaoPopup(ctk.CTkToplevel):

    def __init__(self, master, callback):
        super().__init__(master)
        self.callback = callback

        self.title("Devolução de Processos")
        self.geometry("520x460")
        self.resizable(False, False)
        self.configure(fg_color=AppTheme.BG_APP)
        self.grab_set()
        self._build()
        # Centralizar após a janela ser desenhada
        self.after(0, self._centralizar)

    def _centralizar(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth()  // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build(self):
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=28, pady=24)

        # Título
        ctk.CTkLabel(wrap, text="Devolução de Processos",
                     font=("Segoe UI", 20, "bold"),
                     text_color=AppTheme.TXT_MAIN).pack(anchor="w",
                                                         pady=(0, 20))

        # Card de motivos
        card = ctk.CTkFrame(wrap, fg_color=AppTheme.BG_CARD,
                            corner_radius=14)
        card.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(card, text="Motivo da devolução:",
                     font=("Segoe UI", 12, "bold"),
                     text_color=_MUTED).pack(anchor="w",
                                             padx=20, pady=(18, 10))

        self.motivo_var = ctk.StringVar(value="Endereço")

        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(padx=20, pady=(0, 16))

        for i, m in enumerate(MOTIVOS):
            ctk.CTkRadioButton(
                grid, text=m,
                variable=self.motivo_var, value=m,
                fg_color=_VERDE, hover_color=_VERDE_H,
                text_color=AppTheme.TXT_MAIN,
                font=("Segoe UI", 12),
            ).grid(row=i // 2, column=i % 2,
                   padx=16, pady=5, sticky="w")

        # Detalhes
        ctk.CTkLabel(wrap, text="Detalhes adicionais (opcional):",
                     font=("Segoe UI", 11, "bold"),
                     text_color=_MUTED).pack(anchor="w",
                                              pady=(0, 6))

        self.detalhes = ctk.CTkTextbox(
            wrap, height=80, corner_radius=12,
            font=("Segoe UI", 12),
            fg_color=AppTheme.BG_INPUT,
            border_width=0,
            text_color=AppTheme.TXT_MAIN,
        )
        self.detalhes.pack(fill="x", pady=(0, 20))

        # Botões
        btns = ctk.CTkFrame(wrap, fg_color="transparent")
        btns.pack(fill="x")
        btns.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btns, text="Confirmar Devolução",
            height=46, corner_radius=12,
            fg_color=_VERDE, hover_color=_VERDE_H,
            font=("Segoe UI", 13, "bold"), text_color="#fff",
            command=self._confirmar
        ).grid(row=0, column=0, padx=(0, 6), sticky="ew")

        ctk.CTkButton(
            btns, text="Cancelar",
            height=46, corner_radius=12,
            fg_color=AppTheme.BG_INPUT,
            hover_color=AppTheme.BG_APP,
            font=("Segoe UI", 13),
            text_color=AppTheme.TXT_MAIN,
            command=self.destroy
        ).grid(row=0, column=1, padx=(6, 0), sticky="ew")

    def _confirmar(self):
        motivo   = self.motivo_var.get()
        detalhes = self.detalhes.get("1.0", "end-1c").strip()
        resultado = f"[{motivo}] {detalhes}" if detalhes else f"[{motivo}]"
        self.callback(resultado)
        self.destroy()