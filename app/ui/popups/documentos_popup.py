# -*- coding: utf-8 -*-
"""
Popup para adicionar documentos do produtor
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
from app.theme import AppTheme


class DocumentosPopup(ctk.CTkToplevel):
    """Janela popup para upload de documentos"""

    def __init__(self, parent, on_confirmar):
        super().__init__(parent)

        self.on_confirmar = on_confirmar
        self.docs = {
            "foto_produtor": None,
            "doc_frente": None,
            "doc_verso": None
        }

        self.title("Adicionar documentos")
        self.geometry("420x450")
        self.resizable(False, False)
        self.grab_set()
        self.focus_force()

        self._criar_layout()

    def _criar_layout(self):
        """Cria o layout do popup"""
        
        # Container principal
        container = ctk.CTkFrame(self, corner_radius=0)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        ctk.CTkLabel(
            container,
            text="Documentos do Produtor",
            font=("Segoe UI", 20, "bold"),
            text_color=AppTheme.TXT_MAIN
        ).pack(pady=(10, 30))

        # Instruções
        ctk.CTkLabel(
            container,
            text="Selecione os documentos necessários:",
            font=("Segoe UI", 12),
            text_color=AppTheme.TXT_MUTED
        ).pack(pady=(0, 20))

        # Botões de upload
        self._botao_upload("📷 Foto do produtor", "foto_produtor")
        self._botao_upload("🆔 Documento (frente)", "doc_frente")
        self._botao_upload("🆔 Documento (verso)", "doc_verso")

        # Status
        self.status_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.status_frame.pack(pady=20, fill="x")

        self.status_labels = {
            "foto_produtor": ctk.CTkLabel(
                self.status_frame,
                text="❌ Foto não selecionada",
                font=("Segoe UI", 10),
                text_color="red"
            ),
            "doc_frente": ctk.CTkLabel(
                self.status_frame,
                text="❌ Frente não selecionada",
                font=("Segoe UI", 10),
                text_color="red"
            ),
            "doc_verso": ctk.CTkLabel(
                self.status_frame,
                text="❌ Verso não selecionado",
                font=("Segoe UI", 10),
                text_color="red"
            )
        }

        for label in self.status_labels.values():
            label.pack(pady=2)

        # Botão confirmar
        ctk.CTkButton(
            container,
            text="✅ Confirmar",
            fg_color=AppTheme.BTN_SUCCESS,
            hover_color=AppTheme.BTN_SUCCESS_HOVER,
            height=45,
            font=("Segoe UI", 13, "bold"),
            corner_radius=10,
            command=self._confirmar
        ).pack(pady=(20, 10), fill="x")

    def _botao_upload(self, texto, chave):
        """Cria um botão de upload"""
        ctk.CTkButton(
            self.master.winfo_children()[0],  # container
            text=texto,
            height=45,
            font=("Segoe UI", 12),
            fg_color=AppTheme.BTN_PRIMARY,
            hover_color=AppTheme.BTN_PRIMARY_HOVER,
            corner_radius=10,
            command=lambda: self._selecionar(chave)
        ).pack(fill="x", padx=20, pady=6)

    def _selecionar(self, chave):
        """Abre dialog para selecionar arquivo"""
        path = filedialog.askopenfilename(
            title="Selecione o arquivo",
            filetypes=[
                ("Imagens", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("Todos os arquivos", "*.*")
            ]
        )
        
        if path:
            self.docs[chave] = path
            
            # Atualiza status
            nome_arquivo = path.split("/")[-1]
            self.status_labels[chave].configure(
                text=f"✅ {nome_arquivo[:30]}...",
                text_color="green"
            )
            
            messagebox.showinfo("Sucesso", f"Arquivo carregado:\n{nome_arquivo}")

    def _confirmar(self):
        """Confirma os documentos selecionados"""
        # Verifica se todos foram selecionados
        faltando = [k for k, v in self.docs.items() if v is None]
        
        if faltando:
            messagebox.showwarning(
                "Documentos Faltando",
                "Selecione todos os documentos antes de confirmar."
            )
            return
        
        self.on_confirmar(self.docs)
        self.destroy()