# -*- coding: utf-8 -*-
import os
from tkinter import messagebox, END
import customtkinter as ctk

from ui.base_ui import BaseUI
from services.analiseap_repository import AnaliseapRepository
from app.theme import AppTheme
from .controller import AnaliseapController
from .services import AnaliseapServices

# ================== MOTIVOS DE DEVOLUÇÃO ==================
MOTIVOS_DEVOLUCAO = [
    "Endereço", "Documentos", "Cadastro",
    "Pesca", "Simples Nacional", "Animais"
]

class AnaliseapUI(BaseUI):
    def __init__(self, master, usuario):
        super().__init__(master)

        self.usuario = usuario
        self.repo = AnaliseapRepository()
        self.lista_municipios = {}
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

        # Inicializar controller e services
        self.controller = AnaliseapController(usuario, self.repo)
        self.services = AnaliseapServices(self.BASE_DIR)

        self.configure(fg_color=AppTheme.BG_APP)

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(expand=True, fill="both", padx=40, pady=35)

        self._header()
        self._selector()
        self._content()

        self.radio_var.set("insc")
        self._show_screen()

    # ================= HEADER =================
    def _header(self):
        ctk.CTkLabel(
            self.container,
            text="Adicionar Dados",
            font=("Segoe UI", 28, "bold"),
            text_color=AppTheme.TXT_MAIN
        ).pack(anchor="w")

        ctk.CTkLabel(
            self.container,
            text="Gestão de Inscrição, Renovação e Devolução",
            font=("Segoe UI", 14),
            text_color=AppTheme.TXT_MUTED
        ).pack(anchor="w", pady=(6, 28))

    # ================= SELECTOR =================
    def _selector(self):
        card = ctk.CTkFrame(self.container, fg_color=AppTheme.BG_CARD, corner_radius=22)
        card.pack(fill="x", pady=(0, 28))

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(padx=25, pady=20)

        self.radio_var = ctk.StringVar(value="insc")

        ctk.CTkRadioButton(
            row, 
            text="Inscrição / Renovação",
            variable=self.radio_var, 
            value="insc",
            command=self._show_screen,
            fg_color=AppTheme.BTN_PRIMARY,
            hover_color=AppTheme.BTN_PRIMARY_HOVER,
            border_color=AppTheme.BTN_PRIMARY,
            text_color=AppTheme.TXT_MAIN,
            font=("Segoe UI", 12)
        ).pack(side="left", padx=40)

        ctk.CTkRadioButton(
            row, 
            text="Devolução",
            variable=self.radio_var, 
            value="dev",
            command=self._show_screen,
            fg_color=AppTheme.BTN_PRIMARY,
            hover_color=AppTheme.BTN_PRIMARY_HOVER,
            border_color=AppTheme.BTN_PRIMARY,
            text_color=AppTheme.TXT_MAIN,
            font=("Segoe UI", 12)
        ).pack(side="left", padx=40)

    # ================= CONTENT =================
    def _content(self):
        self.body = ctk.CTkFrame(self.container, fg_color="transparent")
        self.body.pack(expand=True, fill="both")

        self.frame_insc = ctk.CTkFrame(self.body, fg_color="transparent")
        self.frame_dev = ctk.CTkFrame(self.body, fg_color="transparent")

        self._form_inscricao(self.frame_insc)
        self._form_devolucao(self.frame_dev)

    def _show_screen(self):
        self.frame_insc.pack_forget()
        self.frame_dev.pack_forget()

        if self.radio_var.get() == "insc":
            self.frame_insc.pack(fill="both", expand=True)
        else:
            self.frame_dev.pack(fill="both", expand=True)

    # ================= FORM INSCRIÇÃO =================
    def _form_inscricao(self, parent):
        self.services.carregar_municipios()
        card = self._card(parent)
        grid = self._grid(card)

        self.nome = self._entry(grid, "Nome", 0)
        self.cpf = self._entry(grid, "CPF", 1)
        self.cpf.bind("<KeyRelease>", self._format_cpf)

        self.unloc = self._entry(grid, "Município", 2)
        self.unloc.bind("<KeyRelease>", lambda e: self._filter_city())

        self.memorando = self._entry(grid, "Memorando", 3)

        self.descricao = ctk.CTkComboBox(
            grid, 
            values=["INSC", "RENOV"], 
            fg_color=AppTheme.BG_INPUT,
            border_color=AppTheme.BTN_PRIMARY,
            button_color=AppTheme.BTN_PRIMARY,
            button_hover_color=AppTheme.BTN_PRIMARY_HOVER,
            text_color=AppTheme.TXT_MAIN,
            dropdown_fg_color=AppTheme.BG_INPUT,
            dropdown_text_color=AppTheme.TXT_MAIN,
            dropdown_hover_color=AppTheme.BG_CARD
        )
        self.descricao.grid(row=0, column=4, padx=10, sticky="ew")

        self._action_button(parent, self._add_insc)

    # ================= FORM DEVOLUÇÃO =================
    def _form_devolucao(self, parent):
        card = self._card(parent)
        grid = self._grid(card)

        self.nome_dev = self._entry(grid, "Nome", 0)
        self.cpf_dev = self._entry(grid, "CPF", 1)
        self.cpf_dev.bind("<KeyRelease>", self._format_cpf)

        self.unloc_dev = self._entry(grid, "Município", 2)
        self.memo_dev = self._entry(grid, "Memorando", 3)

        motivo_card = self._card(parent)

        self.motivo_combo = ctk.CTkComboBox(
            motivo_card, 
            values=MOTIVOS_DEVOLUCAO, 
            fg_color=AppTheme.BG_INPUT,
            border_color=AppTheme.BTN_PRIMARY,
            button_color=AppTheme.BTN_PRIMARY,
            button_hover_color=AppTheme.BTN_PRIMARY_HOVER,
            text_color=AppTheme.TXT_MAIN,
            dropdown_fg_color=AppTheme.BG_INPUT,
            dropdown_text_color=AppTheme.TXT_MAIN,
            dropdown_hover_color=AppTheme.BG_CARD
        )
        self.motivo_combo.pack(padx=20, pady=(12, 6), fill="x")

        self.motivo_texto = ctk.CTkTextbox(
            motivo_card, 
            height=100,
            fg_color=AppTheme.BG_INPUT,
            text_color=AppTheme.TXT_MAIN,
            border_color=AppTheme.BTN_PRIMARY
        )
        self.motivo_texto.pack(fill="x", padx=20, pady=(0, 18))

        self._action_button(parent, self._add_dev)

    # ================= ACTIONS =================
    def _add_insc(self):
        # Validar campos obrigatórios
        campos = [
            self.nome.get(),
            self.cpf.get(),
            self.unloc.get(),
            self.memorando.get(),
            self.descricao.get()
        ]
        
        if not self.controller.validar_campos_obrigatorios(campos):
            messagebox.showwarning("Aviso", "Preencha todos os campos.")
            return

        # Salvar usando o controller
        sucesso, mensagem = self.controller.salvar_inscricao(
            nome=self.nome.get(),
            cpf=self.cpf.get(),
            municipio=self.unloc.get(),
            memorando=self.memorando.get(),
            tipo=self.descricao.get()
        )
        
        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            # Limpar campos após salvar
            self._limpar_campos_inscricao()
        else:
            messagebox.showerror("Erro", mensagem)

    def _add_dev(self):
        # Validar campos obrigatórios
        campos = [
            self.nome_dev.get(),
            self.cpf_dev.get(),
            self.unloc_dev.get(),
            self.memo_dev.get(),
            self.motivo_combo.get(),
            self.motivo_texto.get("1.0", END).strip()
        ]
        
        if not self.controller.validar_campos_obrigatorios(campos):
            messagebox.showwarning("Aviso", "Preencha todos os campos.")
            return

        # Salvar usando o controller
        sucesso, mensagem = self.controller.salvar_devolucao(
            nome=self.nome_dev.get(),
            cpf=self.cpf_dev.get(),
            municipio=self.unloc_dev.get(),
            memorando=self.memo_dev.get(),
            motivo_combo=self.motivo_combo.get(),
            motivo_texto=self.motivo_texto.get("1.0", END).strip()
        )
        
        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            # Limpar campos após salvar
            self._limpar_campos_devolucao()
        else:
            messagebox.showerror("Erro", mensagem)

    # ================= HELPERS =================
    def _card(self, parent):
        card = ctk.CTkFrame(parent, fg_color=AppTheme.BG_CARD, corner_radius=22)
        card.pack(fill="x", pady=(0, 24))
        return card

    def _grid(self, parent):
        grid = ctk.CTkFrame(parent, fg_color="transparent")
        grid.pack(padx=25, pady=22, fill="x")
        for i in range(5):
            grid.columnconfigure(i, weight=1)
        return grid

    def _entry(self, parent, placeholder, col):
        entry = ctk.CTkEntry(
            parent, 
            placeholder_text=placeholder,
            fg_color=AppTheme.BG_INPUT,
            border_color=AppTheme.BTN_PRIMARY,
            text_color=AppTheme.TXT_MAIN,
            placeholder_text_color=AppTheme.TXT_MUTED,
            font=("Segoe UI", 12),
            height=40
        )
        entry.grid(row=0, column=col, padx=10, sticky="ew")
        return entry

    def _action_button(self, parent, command):
        ctk.CTkButton(
            parent, 
            text="Salvar", 
            command=command,
            fg_color=AppTheme.BTN_PRIMARY,
            hover_color=AppTheme.BTN_PRIMARY_HOVER,
            text_color=AppTheme.TXT_MAIN,
            font=("Segoe UI", 12, "bold"),
            height=40,
            corner_radius=10
        ).pack(anchor="e", padx=20, pady=10)

    def _format_cpf(self, event):
        entry = event.widget
        texto_formatado = self.controller.formatar_cpf(entry.get())
        entry.delete(0, END)
        entry.insert(0, texto_formatado)

    def _filter_city(self):
        texto = self.unloc.get()
        cidade = self.services.filtrar_cidade(texto)
        if cidade:
            self.unloc.delete(0, END)
            self.unloc.insert(0, cidade)

    def _limpar_campos_inscricao(self):
        """Limpa campos do formulário de inscrição"""
        self.nome.delete(0, END)
        self.cpf.delete(0, END)
        self.unloc.delete(0, END)
        self.memorando.delete(0, END)
        self.descricao.set("INSC")

    def _limpar_campos_devolucao(self):
        """Limpa campos do formulário de devolução"""
        self.nome_dev.delete(0, END)
        self.cpf_dev.delete(0, END)
        self.unloc_dev.delete(0, END)
        self.memo_dev.delete(0, END)
        self.motivo_combo.set("")
        self.motivo_texto.delete("1.0", END)