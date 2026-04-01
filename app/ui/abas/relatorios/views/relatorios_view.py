# -*- coding: utf-8 -*-
"""
View para interface de relatórios SEFAZ
"""
# Essa é a parte mais "visual" da aplicação, então tem bastante código relacionado à criação de widgets e layout.
import customtkinter as ctk
from tkinter import messagebox
from typing import Callable
from app.theme import AppTheme


class RelatoriosView(ctk.CTkFrame):
    """View principal para geração de relatórios"""

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.on_gerar_relatorios: Callable | None = None

        self.municipio_vars: dict[str, ctk.BooleanVar] = {}

        self._create_widgets()
        self._load_municipios()

    # ======================================================
    # CRIAÇÃO DA INTERFACE
    # ======================================================

    def _create_widgets(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(expand=True, fill="both")

        ctk.CTkLabel(
            container,
            text="📊 Relatórios SEFAZ",
            font=("Segoe UI", 28, "bold"),
            text_color=AppTheme.TXT_MAIN,
        ).pack(anchor="w", pady=(0, 30))

        self.card = ctk.CTkFrame(
            container,
            fg_color=AppTheme.BG_CARD,
            corner_radius=20
        )
        self.card.pack(fill="both", expand=True)

        self._create_date_frame()
        self._create_municipios_frame()
        self._create_action_button()

    def _create_date_frame(self):
        datas_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        datas_frame.pack(anchor="w", padx=30, pady=(30, 20))

        # Data Inicial
        ctk.CTkLabel(
            datas_frame,
            text="Data Inicial (dd/mm/aaaa)",
            font=("Segoe UI", 12, "bold"),
            text_color=AppTheme.TXT_MAIN
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.data_inicio_entry = ctk.CTkEntry(
            datas_frame,
            width=200,
            height=40,
            placeholder_text="01/01/2024",
            fg_color=AppTheme.BG_INPUT,
            border_color=AppTheme.BORDER
        )
        self.data_inicio_entry.grid(row=1, column=0, sticky="w")

        # Data Final
        ctk.CTkLabel(
            datas_frame,
            text="Data Final (dd/mm/aaaa)",
            font=("Segoe UI", 12, "bold"),
            text_color=AppTheme.TXT_MAIN
        ).grid(row=0, column=1, sticky="w", padx=(30, 0), pady=(0, 5))

        self.data_fim_entry = ctk.CTkEntry(
            datas_frame,
            width=200,
            height=40,
            placeholder_text="31/12/2024",
            fg_color=AppTheme.BG_INPUT,
            border_color=AppTheme.BORDER
        )
        self.data_fim_entry.grid(row=1, column=1, sticky="w", padx=(30, 0))

    def _create_municipios_frame(self):
        municipios_container = ctk.CTkFrame(self.card, fg_color="transparent")
        municipios_container.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        ctk.CTkLabel(
            municipios_container,
            text="Municípios",
            font=("Segoe UI", 14, "bold"),
            text_color=AppTheme.TXT_MAIN
        ).pack(anchor="w", pady=(0, 10))

        self.municipios_scroll_frame = ctk.CTkScrollableFrame(
            municipios_container,
            height=350,
            fg_color=AppTheme.BG_INPUT,
            border_color=AppTheme.BORDER,
            border_width=1
        )
        self.municipios_scroll_frame.pack(fill="both", expand=True)

        self.var_todos = ctk.BooleanVar()

        self.checkbox_todos = ctk.CTkCheckBox(
            self.municipios_scroll_frame,
            text="✅ TODOS",
            variable=self.var_todos,
            command=self._on_todos_changed,
            font=("Segoe UI", 12, "bold"),
            fg_color=AppTheme.BTN_SUCCESS,
            hover_color=AppTheme.BTN_SUCCESS_HOVER
        )
        self.checkbox_todos.pack(anchor="w", padx=10, pady=6)

        self.municipios_frame = ctk.CTkFrame(
            self.municipios_scroll_frame,
            fg_color="transparent"
        )
        self.municipios_frame.pack(fill="both", expand=True, padx=10)

    # ======================================================
    # MUNICÍPIOS
    # ======================================================

    def _load_municipios(self):
        municipios = self.controller.obter_municipios()

        for municipio in municipios:
            nome = str(municipio.nome)

            var = ctk.BooleanVar(value=bool(municipio.selecionado))

            checkbox = ctk.CTkCheckBox(
                self.municipios_frame,
                text=nome,
                variable=var,
                command=lambda m=nome, v=var: self._on_municipio_changed(m, v),
                fg_color=AppTheme.BTN_PRIMARY,
                hover_color=AppTheme.BTN_PRIMARY_HOVER
            )
            checkbox.pack(anchor="w", pady=2)

            self.municipio_vars[nome] = var

    # ======================================================
    # AÇÕES
    # ======================================================

    def _create_action_button(self):
        ctk.CTkButton(
            self.card,
            text="🚀 Gerar Relatórios",
            width=300,
            height=50,
            fg_color=AppTheme.BTN_SUCCESS,
            hover_color=AppTheme.BTN_SUCCESS_HOVER,
            text_color=AppTheme.TXT_MAIN,
            font=("Segoe UI", 16, "bold"),
            corner_radius=12,
            command=self._on_gerar_relatorios_click
        ).pack(pady=(0, 30))

    def _on_todos_changed(self):
        selecionar = self.var_todos.get()
        self.controller.selecionar_todos_municipios(selecionar)

        for var in self.municipio_vars.values():
            var.set(selecionar)

    def _on_municipio_changed(self, nome_municipio: str, var: ctk.BooleanVar):
        selecionado = var.get()
        self.controller.atualizar_selecao_municipio(nome_municipio, selecionado)

        self.var_todos.set(self.controller.todos_selecionados())

    def _on_gerar_relatorios_click(self):
        data_inicio = self.data_inicio_entry.get().strip()
        data_fim = self.data_fim_entry.get().strip()
    
        self.controller.definir_periodo(data_inicio, data_fim)
    
        valido, mensagem = self.controller.validar_configuracao()
    
        if not valido:
            messagebox.showwarning("Aviso", mensagem)
            return
    
        if self.on_gerar_relatorios:
            self.on_gerar_relatorios()
    

    # ======================================================
    # API EXTERNA
    # ======================================================

    def set_on_gerar_relatorios_callback(self, callback: Callable):
        self.on_gerar_relatorios = callback

    def get_form_data(self) -> dict:
        return {
            "data_inicio": self.data_inicio_entry.get().strip(),
            "data_fim": self.data_fim_entry.get().strip(),
            "municipios_selecionados": [
                nome for nome, var in self.municipio_vars.items()
                if var.get()
            ]
        }
