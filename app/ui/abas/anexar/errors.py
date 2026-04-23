# -*- coding: utf-8 -*-
"""
Aba "Erros" — registra todas as falhas durante o processamento.
Versão PyQt6.
"""
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

# ========== CORES ==========
VERM = "#ef4444"
VERM_H = "#b91c1c"
MUTED = "#64748b"
BG_INPUT = "#ffffff"
BG_CARD = "#f1f5f9"
TXT_MAIN = "#0f172a"
VERDE = "#22c55e"
AMBER = "#f59e0b"
INFO = "#60a5fa"


class ErrorsTable:
    """
    Tabela para exibir erros ocorridos durante a anexação.
    """
    
    _lbl_count = None
    
    @classmethod
    def criar(cls, parent):
        """Cria a tabela de erros. Retorna: (table_widget, container_widget)"""
        container = QFrame(parent)
        container.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Cabeçalho
        hdr = QFrame()
        hdr.setStyleSheet("background-color: transparent;")
        hdr_layout = QHBoxLayout(hdr)
        hdr_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl_title = QLabel("❌ Registro de Erros")
        lbl_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl_title.setStyleSheet(f"color: {TXT_MAIN};")
        hdr_layout.addWidget(lbl_title)
        
        cls._lbl_count = QLabel("0 erros")
        cls._lbl_count.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        cls._lbl_count.setStyleSheet(f"color: {VERM};")
        hdr_layout.addWidget(cls._lbl_count, alignment=Qt.AlignmentFlag.AlignRight)
        
        layout.addWidget(hdr)
        
        # Frame da tabela
        table_frame = QFrame()
        table_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_INPUT};
                border-radius: 12px;
                border: 1px solid {BG_CARD};
            }}
        """)
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(4, 4, 4, 4)
        
        # Tabela
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Data/Hora", "CPF", "Status", "Mensagem de Erro"])
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {BG_INPUT};
                color: {TXT_MAIN};
                border: none;
                gridline-color: {BG_CARD};
            }}
            QTableWidget::item {{
                padding: 6px;
            }}
            QHeaderView::section {{
                background-color: {BG_CARD};
                color: {MUTED};
                padding: 8px;
                font-weight: bold;
            }}
        """)
        
        # Configurar larguras das colunas
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        
        table_layout.addWidget(table)
        layout.addWidget(table_frame)
        
        # Botões
        btn_frame = QFrame()
        btn_frame.setStyleSheet("background-color: transparent;")
        btn_layout = QHBoxLayout(btn_frame)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(10)
        
        btn_limpar = QPushButton("🗑️ Limpar Erros")
        btn_limpar.setFixedSize(120, 32)
        btn_limpar.setStyleSheet(f"""
            QPushButton {{
                background-color: {VERM_H};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: #991b1b;
            }}
        """)
        btn_limpar.clicked.connect(lambda: cls.limpar(table))
        btn_layout.addWidget(btn_limpar)
        
        btn_exportar = QPushButton("📋 Exportar")
        btn_exportar.setFixedSize(100, 32)
        btn_exportar.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_INPUT};
                color: {TXT_MAIN};
                border: 1px solid {BG_CARD};
                border-radius: 8px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {BG_CARD};
            }}
        """)
        btn_exportar.clicked.connect(lambda: cls.exportar(table))
        btn_layout.addWidget(btn_exportar)
        
        btn_layout.addStretch()
        layout.addWidget(btn_frame)
        
        return table, container
    
    @classmethod
    def adicionar(cls, table, cpf: str, mensagem: str, tipo: str = "erro"):
        """Adiciona um erro à tabela."""
        ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        icon = {"erro": "✗", "aviso": "⚠", "critico": "💀"}.get(tipo.lower(), "✗")
        
        row = table.rowCount()
        table.insertRow(row)
        
        table.setItem(row, 0, QTableWidgetItem(ts))
        table.setItem(row, 1, QTableWidgetItem(cpf))
        table.setItem(row, 2, QTableWidgetItem(tipo.upper()))
        table.setItem(row, 3, QTableWidgetItem(f"{icon} {mensagem}"))
        
        # Aplicar cor
        color = {"erro": VERM, "aviso": AMBER, "critico": VERM_H}.get(tipo.lower(), VERM)
        for col in range(4):
            item = table.item(row, col)
            if item:
                item.setForeground(QColor(color))
        
        # Atualizar contador
        total = table.rowCount()
        if cls._lbl_count:
            cls._lbl_count.setText(f"{total} erro(s)")
        
        # Scroll para o final
        table.scrollToBottom()
    
    @classmethod
    def limpar(cls, table):
        """Limpa todos os erros da tabela."""
        table.setRowCount(0)
        if cls._lbl_count:
            cls._lbl_count.setText("0 erros")
    
    @classmethod
    def exportar(cls, table):
        """Exporta os erros para um arquivo de texto."""
        destino, _ = QFileDialog.getSaveFileName(
            None,
            "Exportar erros como...",
            f"erros_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Arquivo de Texto (*.txt);;Todos os arquivos (*.*)"
        )
        
        if not destino:
            return
        
        try:
            with open(destino, "w", encoding="utf-8") as f:
                f.write("=" * 80 + "\n")
                f.write("RELATÓRIO DE ERROS - ANEXAÇÃO CARTEIRAS DIGITAIS\n")
                f.write(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                
                for row in range(table.rowCount()):
                    data = table.item(row, 0).text() if table.item(row, 0) else ""
                    cpf = table.item(row, 1).text() if table.item(row, 1) else ""
                    status = table.item(row, 2).text() if table.item(row, 2) else ""
                    mensagem = table.item(row, 3).text() if table.item(row, 3) else ""
                    
                    f.write(f"[{data}] CPF: {cpf} | {status}\n")
                    f.write(f"   {mensagem}\n")
                    f.write("-" * 40 + "\n")
                
                total = table.rowCount()
                f.write(f"\nTotal de erros: {total}\n")
            
            QMessageBox.information(None, "Exportar", f"✅ Erros exportados com sucesso!\n\nArquivo salvo em:\n{destino}")
        except Exception as e:
            QMessageBox.critical(None, "Erro", f"Falha ao exportar:\n{e}")