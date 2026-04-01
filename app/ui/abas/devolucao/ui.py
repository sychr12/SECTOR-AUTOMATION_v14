# -*- coding: utf-8 -*-
"""
Interface para devolução de documentos
"""

import threading
from tkinter import messagebox
import customtkinter as ctk

from ui.base_ui import BaseUI
from app.theme import AppTheme
from services.pdf_service import PDFService
from services.email_service import EmailService
from .controller import DevolucaoController
from .services import ConfiguracaoService, HistoricoService
from .views import HeaderCard, ConteudoCard, BotoesAcao, StatusBar, ContadorCaracteres, FormularioDestinatarios

class DevolucaoUI(BaseUI):
    """Interface para devolução de documentos"""

    def __init__(self, master, usuario):
        super().__init__(master)
        self.usuario = usuario
        
        # Inicializar services
        self.pdf_service = PDFService()
        self.email_service = EmailService()
        self.config_service = ConfiguracaoService()
        self.historico_service = HistoricoService()
        
        # Inicializar controller
        self.controller = DevolucaoController(
            usuario=usuario,
            pdf_service=self.pdf_service,
            email_service=self.email_service
        )
        
        # Criar interface
        self._criar_interface()
    
    def _criar_interface(self):
        """Cria a interface do usuário"""
        self.configure(fg_color=AppTheme.BG_APP)
        
        # Container principal
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=40, pady=40)
        
        # Cabeçalho
        self.header = HeaderCard(
            container,
            title="Devolução",
            subtitle="Gerar PDF e enviar email de devolução"
        )
        self.header.pack()
        
        # Barra de status
        self.status_bar = StatusBar(container)
        
        # Card de conteúdo
        self.conteudo_card = ConteudoCard(
            container,
            on_content_change=self._atualizar_status_conteudo
        )
        self.conteudo_card.pack(fill="both", expand=True, pady=(0, 20))
        
        # Contador de caracteres
        self.contador = ContadorCaracteres(
            container,
            text_widget=self.conteudo_card.text_widget,
            max_caracteres=2000
        )
        self.contador.pack(anchor="e", pady=(0, 10))
        
        # Botões de ação
        self.botoes_acao = BotoesAcao(
            container,
            on_gerar_pdf=self.gerar_pdf,
            on_enviar_email=self.enviar_email
        )
        self.botoes_acao.pack(pady=10)
        
        # Botões adicionais
        botoes_adicionais = ctk.CTkFrame(container, fg_color="transparent")
        botoes_adicionais.pack(pady=(5, 0))
        
        ctk.CTkButton(
            botoes_adicionais,
            text="⚙️ Configurar Destinatários",
            width=200,
            height=35,
            font=("Segoe UI", 12),
            fg_color=AppTheme.BG_INPUT,
            hover_color=AppTheme.TXT_MUTED,
            text_color=AppTheme.TXT_MAIN,
            command=self._configurar_destinatarios
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            botoes_adicionais,
            text="📋 Limpar",
            width=100,
            height=35,
            font=("Segoe UI", 12),
            fg_color=AppTheme.BG_INPUT,
            hover_color=AppTheme.TXT_MUTED,
            text_color=AppTheme.TXT_MAIN,
            command=self._limpar_conteudo
        ).pack(side="left", padx=5)
    
    def _atualizar_status_conteudo(self):
        """Atualiza o status baseado no conteúdo"""
        conteudo = self.conteudo_card.obter_conteudo()
        if conteudo:
            self.status_bar.hide()
    
    def _limpar_conteudo(self):
        """Limpa o conteúdo do textbox"""
        self.conteudo_card.limpar_conteudo()
        self.status_bar.hide()
    
    def _configurar_destinatarios(self):
        """Abre formulário para configurar destinatários"""
        destinatarios_atual = self.config_service.obter_destinatarios()
        
        formulario = FormularioDestinatarios(
            self,
            destinatarios_iniciais=destinatarios_atual,
            on_salvar=self._salvar_destinatarios
        )
        
        formulario.show()
    
    def _salvar_destinatarios(self, destinatarios):
        """Salva a lista de destinatários"""
        for email in destinatarios:
            self.config_service.adicionar_destinatario(email)
        
        messagebox.showinfo("Sucesso", "Destinatários atualizados com sucesso.")
    
    def gerar_pdf(self):
        """Gera PDF com o conteúdo"""
        conteudo = self.conteudo_card.obter_conteudo()
        
        # Validar limite de caracteres
        if not self.contador.esta_dentro_limite():
            self.status_bar.mostrar_aviso("O conteúdo excede o limite de caracteres.")
            return
        
        # Desabilitar botões durante operação
        self.botoes_acao.desabilitar_botoes()
        
        # Executar em thread
        threading.Thread(
            target=self._executar_gerar_pdf,
            args=(conteudo,),
            daemon=True
        ).start()
    
    def _executar_gerar_pdf(self, conteudo):
        """Executa a geração de PDF em thread"""
        try:
            sucesso, resultado = self.controller.gerar_pdf_devolucao(conteudo)
            
            # Registrar no histórico
            self.historico_service.registrar_devolucao(
                usuario=self.usuario,
                tipo="pdf",
                conteudo=conteudo,
                sucesso=sucesso,
                detalhes=resultado if sucesso else f"Erro: {resultado}"
            )
            
            # Atualizar interface
            self.after(0, self._finalizar_gerar_pdf, sucesso, resultado)
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Erro", f"Erro inesperado: {str(e)}"))
            self.after(0, self.botoes_acao.habilitar_botoes)
    
    def _finalizar_gerar_pdf(self, sucesso, resultado):
        """Finaliza a geração de PDF"""
        self.botoes_acao.habilitar_botoes()
        
        if sucesso:
            self.status_bar.mostrar_sucesso(f"PDF gerado: {resultado}")
            messagebox.showinfo("Sucesso", f"PDF gerado com sucesso:\n{resultado}")
        else:
            self.status_bar.mostrar_erro(resultado)
            messagebox.showerror("Erro", resultado)
    
    def enviar_email(self):
        """Envia email com o conteúdo"""
        conteudo = self.conteudo_card.obter_conteudo()
        
        # Validar limite de caracteres
        if not self.contador.esta_dentro_limite():
            self.status_bar.mostrar_aviso("O conteúdo excede o limite de caracteres.")
            return
        
        # Obter destinatários
        destinatarios = self.config_service.obter_destinatarios()
        
        if not destinatarios:
            messagebox.showwarning(
                "Atenção",
                "Nenhum destinatário configurado. Configure os destinatários primeiro."
            )
            return
        
        # Desabilitar botões durante operação
        self.botoes_acao.desabilitar_botoes()
        
        # Executar em thread
        threading.Thread(
            target=self._executar_enviar_email,
            args=(conteudo, destinatarios),
            daemon=True
        ).start()
    
    def _executar_enviar_email(self, conteudo, destinatarios):
        """Executa o envio de email em thread"""
        try:
            sucesso, resultado = self.controller.enviar_email_devolucao(conteudo, destinatarios)
            
            # Registrar no histórico
            self.historico_service.registrar_devolucao(
                usuario=self.usuario,
                tipo="email",
                conteudo=conteudo,
                sucesso=sucesso,
                detalhes=resultado if sucesso else f"Erro: {resultado}"
            )
            
            # Atualizar interface
            self.after(0, self._finalizar_enviar_email, sucesso, resultado)
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Erro", f"Erro inesperado: {str(e)}"))
            self.after(0, self.botoes_acao.habilitar_botoes)
    
    def _finalizar_enviar_email(self, sucesso, resultado):
        """Finaliza o envio de email"""
        self.botoes_acao.habilitar_botoes()
        
        if sucesso:
            self.status_bar.mostrar_sucesso(resultado)
            messagebox.showinfo("Sucesso", resultado)
        else:
            self.status_bar.mostrar_erro(resultado)
            messagebox.showerror("Erro", resultado)