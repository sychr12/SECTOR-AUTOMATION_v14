# -*- coding: utf-8 -*-
"""
Formulários para configuração de download de emails
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import *


class AppTheme:
    """Paleta local — espelha app.theme.AppTheme sem depender do caminho absoluto."""
    BG_INPUT         = "#ffffff"
    BG_CARD          = "#f1f5f9"
    TXT_MAIN         = "#0f172a"
    TXT_MUTED        = "#64748b"
    BTN_PRIMARY      = "#2c6e9e"
    BTN_PRIMARY_HOVER = "#1e4a6e"

class ConfiguracaoDownloadForm(ctk.CTkFrame):
    """Formulário para configuração de download"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._criar_widgets()
    
    def _criar_widgets(self):
        # Diretório de salvamento
        ctk.CTkLabel(
            self,
            text="Diretório de Salvamento:",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(0, 5))
        
        dir_frame = ctk.CTkFrame(self, fg_color="transparent")
        dir_frame.pack(fill="x", pady=(0, 15))
        
        self.entry_diretorio = ctk.CTkEntry(
            dir_frame,
            placeholder_text="Caminho para salvar os arquivos...",
            fg_color=AppTheme.BG_INPUT,
            border_color=AppTheme.BTN_PRIMARY,
            text_color=AppTheme.TXT_MAIN,
            font=("Segoe UI", 12),
            height=40
        )
        self.entry_diretorio.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(
            dir_frame,
            text="📁",
            width=40,
            height=40,
            fg_color=AppTheme.BTN_PRIMARY,
            hover_color=AppTheme.BTN_PRIMARY_HOVER,
            command=self._selecionar_diretorio
        ).pack(side="right")
        
        # Filtros
        ctk.CTkLabel(
            self,
            text="Filtros de E-mail:",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(0, 5))
        
        filtros_frame = ctk.CTkFrame(self, fg_color="transparent")
        filtros_frame.pack(fill="x", pady=(0, 20))
        
        # Checkboxes para tipos de anexo
        self.var_pdf = ctk.BooleanVar(value=True)
        self.var_word = ctk.BooleanVar(value=False)
        self.var_excel = ctk.BooleanVar(value=False)
        
        ctk.CTkCheckBox(
            filtros_frame,
            text="PDF",
            variable=self.var_pdf,
            fg_color=AppTheme.BTN_PRIMARY,
            hover_color=AppTheme.BTN_PRIMARY_HOVER,
            font=("Segoe UI", 12)
        ).pack(side="left", padx=(0, 20))
        
        ctk.CTkCheckBox(
            filtros_frame,
            text="Word (.doc, .docx)",
            variable=self.var_word,
            fg_color=AppTheme.BTN_PRIMARY,
            hover_color=AppTheme.BTN_PRIMARY_HOVER,
            font=("Segoe UI", 12)
        ).pack(side="left", padx=(0, 20))
        
        ctk.CTkCheckBox(
            filtros_frame,
            text="Excel (.xls, .xlsx)",
            variable=self.var_excel,
            fg_color=AppTheme.BTN_PRIMARY,
            hover_color=AppTheme.BTN_PRIMARY_HOVER,
            font=("Segoe UI", 12)
        ).pack(side="left")
    
    def _selecionar_diretorio(self):
        """Abre diálogo para selecionar diretório"""
        from PyQt6.QtWidgets import filedialog
        diretorio = filedialog.askdirectory()
        if diretorio:
            self.entry_diretorio.delete(0, "end")
            self.entry_diretorio.insert(0, diretorio)
    
    def obter_diretorio(self):
        """Retorna o diretório configurado"""
        return self.entry_diretorio.get()
    
    def obter_filtros(self):
        """Retorna os tipos de arquivo selecionados"""
        filtros = []
        if self.var_pdf.get():
            filtros.append(".pdf")
        if self.var_word.get():
            filtros.extend([".doc", ".docx"])
        if self.var_excel.get():
            filtros.extend([".xls", ".xlsx"])
        return filtros  # <-- Faltava fechar este método
    
    # Você pode adicionar mais métodos se necessário
    def obter_configuracoes(self):
        """Retorna todas as configurações em um dicionário"""
        return {
            'diretorio': self.obter_diretorio(),
            'filtros': self.obter_filtros(),
            'pdf': self.var_pdf.get(),
            'word': self.var_word.get(),
            'excel': self.var_excel.get()
        }
    
    def definir_diretorio(self, caminho):
        """Define o diretório de salvamento"""
        self.entry_diretorio.delete(0, "end")
        self.entry_diretorio.insert(0, caminho)
