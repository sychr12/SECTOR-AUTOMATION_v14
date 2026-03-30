# -*- coding: utf-8 -*-
"""
Popup para recuperação de senha
"""
import customtkinter as ctk
from tkinter import messagebox
import pyperclip


class PopupRecuperarSenha(ctk.CTkToplevel):
    """Janela popup para recuperar senha"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.parent = parent

        self.title("Recuperar Senha")
        self.geometry("450x300")
        
        self.transient(parent)
        self.grab_set()

        self.centralizar_janela()
        self.protocol("WM_DELETE_WINDOW", self.fechar)

        self._criar_layout()

    def _criar_layout(self):
        """Cria o layout do popup"""
        
        # Container principal
        container = ctk.CTkFrame(self, corner_radius=0)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        ctk.CTkLabel(
            container,
            text="Recuperar Senha",
            font=("Segoe UI", 20, "bold")
        ).pack(pady=(10, 20))

        # Instruções
        ctk.CTkLabel(
            container,
            text="Digite seu email para receber\ninstruções de recuperação:",
            font=("Segoe UI", 12),
            justify="center"
        ).pack(pady=(0, 15))

        # Campo de email
        self.email_entry = ctk.CTkEntry(
            container,
            placeholder_text="seu@email.com",
            width=300,
            height=40,
            font=("Segoe UI", 12)
        )
        self.email_entry.pack(pady=(0, 20))

        # Botões
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(pady=(10, 10))

        ctk.CTkButton(
            btn_frame,
            text="Enviar",
            width=120,
            height=35,
            command=self.enviar_recuperacao
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            width=120,
            height=35,
            fg_color="gray",
            command=self.fechar
        ).pack(side="left", padx=5)

    def centralizar_janela(self):
        """Centraliza a janela na tela"""
        self.update_idletasks()
        
        largura = self.winfo_width()
        altura = self.winfo_height()
        
        x = (self.winfo_screenwidth() // 2) - (largura // 2)
        y = (self.winfo_screenheight() // 2) - (altura // 2)
        
        self.geometry(f'{largura}x{altura}+{x}+{y}')

    def enviar_recuperacao(self):
        """Envia email de recuperação"""
        email = self.email_entry.get().strip()
        
        if not email:
            messagebox.showwarning("Aviso", "Digite um email válido.")
            return
        
        if "@" not in email:
            messagebox.showwarning("Aviso", "Email inválido.")
            return
        
        # Aqui você implementaria a lógica real de envio de email
        messagebox.showinfo(
            "Sucesso", 
            f"Instruções de recuperação enviadas para:\n{email}"
        )
        
        self.fechar()

    def fechar(self):
        """Fecha o popup"""
        self.grab_release()
        self.destroy()