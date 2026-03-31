# views/historico_view.py
# -*- coding: utf-8 -*-
"""Histórico de Carteiras Digitais."""
import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox, ttk

from app.theme import AppTheme
from ..utils.constants import VERDE, VERDE_HOVER, AZUL, AZUL_HOVER, MUTED, VERMELHO


class HistoricoView(ctk.CTkToplevel):

    def __init__(self, master, usuario, controller):
        super().__init__(master)
        self.usuario    = usuario
        self.controller = controller

        self.title("Histórico de Carteiras Digitais")
        self.geometry("1200x720")
        self.configure(fg_color=AppTheme.BG_APP)
        self.grab_set()
        self._centralizar()
        self._build()
        self._atualizar()

    def _centralizar(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth()  // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    # ... resto do código da classe permanece igual ...