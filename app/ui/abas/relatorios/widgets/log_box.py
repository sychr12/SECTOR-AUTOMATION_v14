# -*- coding: utf-8 -*-
"""Caixa de log com cores"""
import customtkinter as ctk
from datetime import datetime


class LogBox(ctk.CTkTextbox):
    """Caixa de texto para exibir logs com cores"""
    
    _LOG_CORES = {
        "sucesso": "#10b981",
        "erro": "#ef4444",
        "info": "#64748b"
    }
    
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color="#f5f7fc",
            text_color="#1e2f3e",
            font=("Consolas", 10),
            state="disabled",
            border_width=1,
            border_color="#e2e8f0",
            corner_radius=10,
            **kwargs
        )
    
    def log(self, msg: str, tipo: str = "info"):
        """Adiciona uma mensagem ao log"""
        self.configure(state="normal")
        tag = f"_t_{tipo}"
        self.tag_config(tag, foreground=self._LOG_CORES.get(tipo, "#64748b"))
        ts = datetime.now().strftime("%H:%M:%S")
        self.insert("end", f"[{ts}] {msg}\n", tag)
        self.see("end")
        self.configure(state="disabled")
    
    def limpar(self):
        """Limpa o log"""
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.configure(state="disabled")