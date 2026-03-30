# -*- coding: utf-8 -*-
"""
Aba "Erros" — registra todas as falhas durante o processamento.
"""
from tkinter import ttk, filedialog, messagebox
from datetime import datetime

import customtkinter as ctk

# ========== CORES DIRETAMENTE NO ARQUIVO (sem import do theme) ==========
VERM = "#ef4444"
VERM_H = "#b91c1c"
MUTED = "#64748b"
BG_INPUT = "#ffffff"
BG_CARD = "#f1f5f9"
TXT_MAIN = "#0f172a"


class ErrorsTable:
    """
    Tabela para exibir erros ocorridos durante a anexação.
    """
    
    # Cores para cada tipo de erro
    _TAGS = {
        "erro": (VERM, "#3f0a0a"),
        "aviso": ("#f59e0b", "#2d2a0a"),
        "critico": ("#b91c1c", "#ffffff"),
    }
    
    # Ícones para cada tipo
    _ICONS = {
        "erro": "✗",
        "aviso": "⚠",
        "critico": "💀",
    }
    
    _lbl_count = None  # Contador de erros
    
    @classmethod
    def criar(cls, parent):
        """
        Cria a tabela de erros.
        Retorna: (treeview, container_frame)
        """
        # Estilo da tabela
        s = ttk.Style()
        s.configure("Errors.Treeview",
                    background=BG_INPUT,
                    fieldbackground=BG_INPUT,
                    foreground=TXT_MAIN,
                    rowheight=34,
                    font=("Segoe UI", 10),
                    borderwidth=0)
        s.configure("Errors.Treeview.Heading",
                    background=BG_CARD,
                    foreground=MUTED,
                    font=("Segoe UI", 10, "bold"),
                    relief="flat")
        s.map("Errors.Treeview",
              background=[("selected", "#1e3a5f")])
        
        container = ctk.CTkFrame(parent, fg_color="transparent")
        
        # ========== CABEÇALHO ==========
        hdr = ctk.CTkFrame(container, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 12))
        
        cls._section_header(hdr, "❌ Registro de Erros")
        
        # Contador de erros
        cls._lbl_count = ctk.CTkLabel(
            hdr, text="0 erros",
            font=("Segoe UI", 11, "bold"),
            text_color=VERM
        )
        cls._lbl_count.pack(side="right")
        
        # ========== TABELA ==========
        frame = cls._tree_frame(container)
        
        tree = ttk.Treeview(
            frame,
            columns=("data", "cpf", "status", "mensagem"),
            show="headings",
            style="Errors.Treeview",
            selectmode="browse"
        )
        
        # Configurar colunas
        tree.heading("data", text="Data/Hora")
        tree.heading("cpf", text="CPF")
        tree.heading("status", text="Status")
        tree.heading("mensagem", text="Mensagem de Erro")
        
        tree.column("data", width=140, minwidth=120)
        tree.column("cpf", width=120, minwidth=100)
        tree.column("status", width=100, minwidth=80)
        tree.column("mensagem", width=500, stretch=True, minwidth=200)
        
        # Scrollbar
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True, padx=4, pady=4)
        
        # Configurar cores por tipo
        for tag, (bg, fg) in cls._TAGS.items():
            tree.tag_configure(tag, background=bg, foreground=fg)
        
        # ========== BOTÕES ==========
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(12, 0))
        
        ctk.CTkButton(
            btn_frame,
            text="🗑️ Limpar Erros",
            width=120, height=32,
            corner_radius=8,
            fg_color=VERM_H,
            hover_color="#991b1b",
            text_color="white",
            font=("Segoe UI", 11),
            command=lambda: cls.limpar(tree)
        ).pack(side="left")
        
        ctk.CTkButton(
            btn_frame,
            text="📋 Exportar",
            width=100, height=32,
            corner_radius=8,
            fg_color=BG_INPUT,
            hover_color=BG_CARD,
            text_color=TXT_MAIN,
            font=("Segoe UI", 11),
            command=lambda: cls.exportar(tree)
        ).pack(side="left", padx=(10, 0))
        
        return tree, container
    
    @staticmethod
    def _section_header(parent, texto: str):
        """Cria um cabeçalho de seção"""
        ctk.CTkLabel(
            parent, text=texto,
            font=("Segoe UI", 13, "bold"),
            text_color=TXT_MAIN
        ).pack(side="left")
    
    @staticmethod
    def _tree_frame(parent):
        """Cria um frame estilizado para a tabela"""
        frame = ctk.CTkFrame(
            parent,
            fg_color=BG_INPUT,
            corner_radius=12,
            border_width=1,
            border_color=BG_CARD
        )
        frame.pack(fill="both", expand=True)
        return frame
    
    # ========== MÉTODOS PRINCIPAIS ==========
    
    @classmethod
    def adicionar(cls, tree, cpf: str, mensagem: str, tipo: str = "erro"):
        """
        Adiciona um erro à tabela.
        
        Args:
            tree: Treeview onde adicionar
            cpf: CPF do processo que deu erro
            mensagem: Descrição do erro
            tipo: "erro", "aviso", ou "critico"
        """
        ts = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        icon = cls._ICONS.get(tipo.lower(), "✗")
        
        tree.insert(
            "", "end",
            values=(ts, cpf, tipo.upper(), f"{icon} {mensagem}"),
            tags=(tipo.lower(),)
        )
        
        # Atualizar contador
        if cls._lbl_count:
            total = len(tree.get_children())
            cls._lbl_count.configure(text=f"{total} erro(s)")
        
        # Rolar para o final
        kids = tree.get_children()
        if kids:
            tree.see(kids[-1])
    
    @classmethod
    def limpar(cls, tree):
        """Limpa todos os erros da tabela"""
        for item in tree.get_children():
            tree.delete(item)
        if cls._lbl_count:
            cls._lbl_count.configure(text="0 erros")
    
    @classmethod
    def exportar(cls, tree):
        """Exporta os erros para um arquivo de texto"""
        destino = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivo de Texto", "*.txt"), ("Todos", "*.*")],
            initialfile=f"erros_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            title="Exportar erros como..."
        )
        
        if not destino:
            return
        
        try:
            with open(destino, "w", encoding="utf-8") as f:
                f.write("=" * 80 + "\n")
                f.write("RELATÓRIO DE ERROS - ANEXAÇÃO CARTEIRAS DIGITAIS\n")
                f.write(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                
                for item in tree.get_children():
                    valores = tree.item(item, "values")
                    if valores:
                        f.write(f"[{valores[0]}] CPF: {valores[1]} | {valores[2]}\n")
                        f.write(f"   {valores[3]}\n")
                        f.write("-" * 40 + "\n")
                
                total = len(tree.get_children())
                f.write(f"\nTotal de erros: {total}\n")
            
            messagebox.showinfo("Exportar", f"✅ Erros exportados com sucesso!\n\nArquivo salvo em:\n{destino}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao exportar:\n{e}")