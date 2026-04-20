# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from .components import FormCard, GridLayout, StyledEntry, StyledComboBox, StyledTextbox
from app.theme import AppTheme

MOTIVOS_DEVOLUCAO = [
    "Endereço", "Documentos", "Cadastro",
    "Pesca", "Simples Nacional", "Animais"
]


class InscricaoForm(QFrame):
    """Formulário de Inscrição/Renovação"""
    def __init__(self, parent=None, on_save=None, on_filter_city=None, on_format_cpf=None):
        super().__init__(parent)
        self.on_save = on_save
        self.on_filter_city = on_filter_city
        self.on_format_cpf = on_format_cpf
        
        self.setStyleSheet("background-color: transparent;")
        self._create_widgets()
        
    def _create_widgets(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Card principal
        card = FormCard(self)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(25, 22, 25, 22)
        card_layout.setSpacing(16)
        
        # Grid para os campos
        grid_layout = QVBoxLayout()
        
        # Linha 1: Nome e CPF
        row1 = QHBoxLayout()
        row1.setSpacing(10)
        
        nome_label = QLabel("Nome")
        nome_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        nome_label.setStyleSheet(f"color: {AppTheme.TXT_MAIN};")
        row1.addWidget(nome_label)
        
        self.nome = StyledEntry(self)
        self.nome.setPlaceholderText("Digite nome")
        row1.addWidget(self.nome)
        
        cpf_label = QLabel("CPF")
        cpf_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        cpf_label.setStyleSheet(f"color: {AppTheme.TXT_MAIN};")
        row1.addWidget(cpf_label)
        
        self.cpf = StyledEntry(self)
        self.cpf.setPlaceholderText("000.000.000-00")
        if self.on_format_cpf:
            self.cpf.textChanged.connect(self.on_format_cpf)
        row1.addWidget(self.cpf)
        
        grid_layout.addLayout(row1)
        
        # Linha 2: Município e Memorando
        row2 = QHBoxLayout()
        row2.setSpacing(10)
        
        municipio_label = QLabel("Município")
        municipio_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        municipio_label.setStyleSheet(f"color: {AppTheme.TXT_MAIN};")
        row2.addWidget(municipio_label)
        
        self.unloc = StyledEntry(self)
        self.unloc.setPlaceholderText("Digite município")
        if self.on_filter_city:
            self.unloc.textChanged.connect(lambda: self.on_filter_city(self.unloc))
        row2.addWidget(self.unloc)
        
        memorando_label = QLabel("Memorando")
        memorando_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        memorando_label.setStyleSheet(f"color: {AppTheme.TXT_MAIN};")
        row2.addWidget(memorando_label)
        
        self.memorando = StyledEntry(self)
        self.memorando.setPlaceholderText("Nº do memorando")
        row2.addWidget(self.memorando)
        
        grid_layout.addLayout(row2)
        
        # Linha 3: Tipo
        row3 = QHBoxLayout()
        row3.setSpacing(10)
        
        tipo_label = QLabel("Tipo")
        tipo_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        tipo_label.setStyleSheet(f"color: {AppTheme.TXT_MAIN};")
        row3.addWidget(tipo_label)
        
        self.descricao = StyledComboBox(self, values=["INSC", "RENOV"])
        row3.addWidget(self.descricao)
        
        row3.addStretch()
        grid_layout.addLayout(row3)
        
        card_layout.addLayout(grid_layout)
        layout.addWidget(card)
        
    def get_values(self):
        """Retorna os valores do formulário"""
        return {
            'nome': self.nome.text(),
            'cpf': self.cpf.text(),
            'municipio': self.unloc.text(),
            'memorando': self.memorando.text(),
            'tipo': self.descricao.currentText()
        }
    
    def clear(self):
        """Limpa todos os campos"""
        self.nome.clear()
        self.cpf.clear()
        self.unloc.clear()
        self.memorando.clear()
        self.descricao.setCurrentIndex(0)


class DevolucaoForm(QFrame):
    """Formulário de Devolução"""
    def __init__(self, parent=None, on_save=None, on_format_cpf=None):
        super().__init__(parent)
        self.on_save = on_save
        self.on_format_cpf = on_format_cpf
        
        self.setStyleSheet("background-color: transparent;")
        self._create_widgets()
        
    def _create_widgets(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)
        
        # Primeiro card com campos principais
        card1 = FormCard(self)
        card1_layout = QVBoxLayout(card1)
        card1_layout.setContentsMargins(25, 22, 25, 22)
        card1_layout.setSpacing(16)
        
        # Grid para os campos
        grid_layout = QVBoxLayout()
        
        # Linha 1: Nome e CPF
        row1 = QHBoxLayout()
        row1.setSpacing(10)
        
        nome_label = QLabel("Nome")
        nome_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        nome_label.setStyleSheet(f"color: {AppTheme.TXT_MAIN};")
        row1.addWidget(nome_label)
        
        self.nome = StyledEntry(self)
        self.nome.setPlaceholderText("Digite nome")
        row1.addWidget(self.nome)
        
        cpf_label = QLabel("CPF")
        cpf_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        cpf_label.setStyleSheet(f"color: {AppTheme.TXT_MAIN};")
        row1.addWidget(cpf_label)
        
        self.cpf = StyledEntry(self)
        self.cpf.setPlaceholderText("000.000.000-00")
        if self.on_format_cpf:
            self.cpf.textChanged.connect(self.on_format_cpf)
        row1.addWidget(self.cpf)
        
        grid_layout.addLayout(row1)
        
        # Linha 2: Município e Memorando
        row2 = QHBoxLayout()
        row2.setSpacing(10)
        
        municipio_label = QLabel("Município")
        municipio_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        municipio_label.setStyleSheet(f"color: {AppTheme.TXT_MAIN};")
        row2.addWidget(municipio_label)
        
        self.unloc = StyledEntry(self)
        self.unloc.setPlaceholderText("Digite município")
        row2.addWidget(self.unloc)
        
        memorando_label = QLabel("Memorando")
        memorando_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        memorando_label.setStyleSheet(f"color: {AppTheme.TXT_MAIN};")
        row2.addWidget(memorando_label)
        
        self.memorando = StyledEntry(self)
        self.memorando.setPlaceholderText("Nº do memorando")
        row2.addWidget(self.memorando)
        
        grid_layout.addLayout(row2)
        
        card1_layout.addLayout(grid_layout)
        layout.addWidget(card1)
        
        # Segundo card com motivo
        card2 = FormCard(self)
        card2_layout = QVBoxLayout(card2)
        card2_layout.setContentsMargins(25, 22, 25, 22)
        card2_layout.setSpacing(12)
        
        motivo_label = QLabel("Motivo da Devolução")
        motivo_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        motivo_label.setStyleSheet(f"color: {AppTheme.TXT_MAIN};")
        card2_layout.addWidget(motivo_label)
        
        self.motivo_combo = StyledComboBox(self, values=MOTIVOS_DEVOLUCAO)
        card2_layout.addWidget(self.motivo_combo)
        
        self.motivo_texto = StyledTextbox(self, height=100)
        card2_layout.addWidget(self.motivo_texto)
        
        layout.addWidget(card2)
        
    def get_values(self):
        """Retorna os valores do formulário"""
        return {
            'nome': self.nome.text(),
            'cpf': self.cpf.text(),
            'municipio': self.unloc.text(),
            'memorando': self.memorando.text(),
            'motivo_combo': self.motivo_combo.currentText(),
            'motivo_texto': self.motivo_texto.toPlainText().strip()
        }
    
    def clear(self):
        """Limpa todos os campos"""
        self.nome.clear()
        self.cpf.clear()
        self.unloc.clear()
        self.memorando.clear()
        self.motivo_combo.setCurrentIndex(0)
        self.motivo_texto.clear()