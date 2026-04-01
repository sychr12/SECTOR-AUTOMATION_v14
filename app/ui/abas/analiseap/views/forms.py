# -*- coding: utf-8 -*-
import customtkinter as ctk
from tkinter import END
from .components import FormCard, GridLayout, StyledEntry, StyledComboBox, StyledTextbox
from app.theme import AppTheme

MOTIVOS_DEVOLUCAO = [
    "Endereço", "Documentos", "Cadastro",
    "Pesca", "Simples Nacional", "Animais"
]

class InscricaoForm(ctk.CTkFrame):
    """Formulário de Inscrição/Renovação"""
    def __init__(self, master, on_save=None, on_filter_city=None, on_format_cpf=None):
        super().__init__(master, fg_color="transparent")
        self.on_save = on_save
        self.on_filter_city = on_filter_city
        self.on_format_cpf = on_format_cpf
        
        self._create_widgets()
        
    def _create_widgets(self):
        # Card principal
        card = FormCard(self)
        card.pack()
        
        # Grid para os campos
        grid = GridLayout(card, columns=5)
        grid.pack()
        
        # Campos do formulário
        self.nome = StyledEntry(grid, "Nome")
        self.nome.grid(column=0)
        
        self.cpf = StyledEntry(grid, "CPF")
        self.cpf.grid(column=1)
        if self.on_format_cpf:
            self.cpf.bind("<KeyRelease>", self.on_format_cpf)
        
        self.unloc = StyledEntry(grid, "Município")
        self.unloc.grid(column=2)
        if self.on_filter_city:
            self.unloc.bind("<KeyRelease>", lambda e: self.on_filter_city(self.unloc))
        
        self.memorando = StyledEntry(grid, "Memorando")
        self.memorando.grid(column=3)
        
        self.descricao = StyledComboBox(grid, values=["INSC", "RENOV"])
        self.descricao.grid(column=4)
        
    def get_values(self):
        """Retorna os valores do formulário"""
        return {
            'nome': self.nome.get(),
            'cpf': self.cpf.get(),
            'municipio': self.unloc.get(),
            'memorando': self.memorando.get(),
            'tipo': self.descricao.get()
        }
    
    def clear(self):
        """Limpa todos os campos"""
        self.nome.delete(0, END)
        self.cpf.delete(0, END)
        self.unloc.delete(0, END)
        self.memorando.delete(0, END)
        self.descricao.set("INSC")

class DevolucaoForm(ctk.CTkFrame):
    """Formulário de Devolução"""
    def __init__(self, master, on_save=None, on_format_cpf=None):
        super().__init__(master, fg_color="transparent")
        self.on_save = on_save
        self.on_format_cpf = on_format_cpf
        
        self._create_widgets()
        
    def _create_widgets(self):
        # Primeiro card com campos principais
        card1 = FormCard(self)
        card1.pack()
        
        grid = GridLayout(card1, columns=4)
        grid.pack()
        
        # Campos do formulário
        self.nome = StyledEntry(grid, "Nome")
        self.nome.grid(column=0)
        
        self.cpf = StyledEntry(grid, "CPF")
        self.cpf.grid(column=1)
        if self.on_format_cpf:
            self.cpf.bind("<KeyRelease>", self.on_format_cpf)
        
        self.unloc = StyledEntry(grid, "Município")
        self.unloc.grid(column=2)
        
        self.memorando = StyledEntry(grid, "Memorando")
        self.memorando.grid(column=3)
        
        # Segundo card com motivo
        card2 = FormCard(self)
        card2.pack()
        
        self.motivo_combo = StyledComboBox(card2, values=MOTIVOS_DEVOLUCAO)
        self.motivo_combo.pack()
        
        self.motivo_texto = StyledTextbox(card2, height=100)
        self.motivo_texto.pack()
        
    def get_values(self):
        """Retorna os valores do formulário"""
        return {
            'nome': self.nome.get(),
            'cpf': self.cpf.get(),
            'municipio': self.unloc.get(),
            'memorando': self.memorando.get(),
            'motivo_combo': self.motivo_combo.get(),
            'motivo_texto': self.motivo_texto.get("1.0", END).strip()
        }
    
    def clear(self):
        """Limpa todos os campos"""
        self.nome.delete(0, END)
        self.cpf.delete(0, END)
        self.unloc.delete(0, END)
        self.memorando.delete(0, END)
        self.motivo_combo.set("")
        self.motivo_texto.delete("1.0", END)