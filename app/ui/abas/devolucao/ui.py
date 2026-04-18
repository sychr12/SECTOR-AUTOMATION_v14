# -*- coding: utf-8 -*-
"""
Interface para devolução de documentos (PyQt6)
"""

import threading
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton,
    QTextEdit, QMessageBox, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from app.theme import AppTheme
from services.pdf_service import PDFService
from services.email_service import EmailService
from .controller import DevolucaoController
from .services import ConfiguracaoService, HistoricoService
from .views import HeaderCard, ConteudoCard, BotoesAcao, StatusBar, ContadorCaracteres, FormularioDestinatarios


class DevolucaoUI(QWidget):
    """Interface para devolução de documentos"""

    def __init__(self, parent=None, usuario=None):
        super().__init__(parent)
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
        
        self.setStyleSheet(f"background-color: {AppTheme.BG_APP};")
        
        # Criar interface
        self._criar_interface()
    
    def _criar_interface(self):
        """Cria a interface do usuário"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Cabeçalho
        self.header = HeaderCard(title="Devolução", subtitle="Gerar PDF e enviar email de devolução")
        layout.addWidget(self.header)
        
        # Card de conteúdo
        self.conteudo_card = ConteudoCard(on_content_change=self._atualizar_status_conteudo)
        layout.addWidget(self.conteudo_card, 1)
        
        # Contador de caracteres
        self.contador = ContadorCaracteres(
            text_widget=self.conteudo_card.text_widget,
            max_caracteres=2000
        )
        layout.addWidget(self.contador, alignment=Qt.AlignmentFlag.AlignRight)
        
        # Botões de ação
        self.botoes_acao = BotoesAcao(
            on_gerar_pdf=self.gerar_pdf,
            on_enviar_email=self.enviar_email
        )
        layout.addWidget(self.botoes_acao)
        
        # Botões adicionais
        botoes_adicionais = QWidget()
        botoes_adicionais_layout = QHBoxLayout(botoes_adicionais)
        botoes_adicionais_layout.setContentsMargins(0, 0, 0, 0)
        botoes_adicionais_layout.setSpacing(10)
        
        btn_config = QPushButton("⚙️ Configurar Destinatários")
        btn_config.setFixedSize(200, 35)
        btn_config.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppTheme.BG_INPUT};
                color: {AppTheme.TXT_MAIN};
                border: 1px solid {AppTheme.BORDER};
                border-radius: 8px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {AppTheme.TXT_MUTED};
            }}
        """)
        btn_config.clicked.connect(self._configurar_destinatarios)
        botoes_adicionais_layout.addWidget(btn_config)
        
        btn_limpar = QPushButton("📋 Limpar")
        btn_limpar.setFixedSize(100, 35)
        btn_limpar.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppTheme.BG_INPUT};
                color: {AppTheme.TXT_MAIN};
                border: 1px solid {AppTheme.BORDER};
                border-radius: 8px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {AppTheme.TXT_MUTED};
            }}
        """)
        btn_limpar.clicked.connect(self._limpar_conteudo)
        botoes_adicionais_layout.addWidget(btn_limpar)
        
        botoes_adicionais_layout.addStretch()
        layout.addWidget(botoes_adicionais)
        
        # Barra de status
        self.status_bar = StatusBar()
        layout.addWidget(self.status_bar)
        self.status_bar.hide()
    
    def _atualizar_status_conteudo(self):
        """Atualiza o status baseado no conteúdo"""
        pass
    
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
        formulario.exec()
    
    def _salvar_destinatarios(self, destinatarios):
        """Salva a lista de destinatários"""
        self.config_service.config['destinatarios_padrao'] = destinatarios
        self.config_service.salvar_config()
        QMessageBox.information(self, "Sucesso", "Destinatários atualizados com sucesso.")
    
    def gerar_pdf(self):
        """Gera PDF com o conteúdo"""
        conteudo = self.conteudo_card.obter_conteudo()
        
        # Validar limite de caracteres
        if not self.contador.esta_dentro_limite():
            self.status_bar.mostrar_aviso("O conteúdo excede o limite de caracteres.")
            self.status_bar.show()
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
            QTimer.singleShot(0, lambda: self._finalizar_gerar_pdf(sucesso, resultado))
            
        except Exception as e:
            QTimer.singleShot(0, lambda: QMessageBox.critical(self, "Erro", f"Erro inesperado: {str(e)}"))
            QTimer.singleShot(0, self.botoes_acao.habilitar_botoes)
    
    def _finalizar_gerar_pdf(self, sucesso, resultado):
        """Finaliza a geração de PDF"""
        self.botoes_acao.habilitar_botoes()
        
        if sucesso:
            self.status_bar.mostrar_sucesso(f"PDF gerado: {resultado}")
            self.status_bar.show()
            QMessageBox.information(self, "Sucesso", f"PDF gerado com sucesso:\n{resultado}")
        else:
            self.status_bar.mostrar_erro(resultado)
            self.status_bar.show()
            QMessageBox.critical(self, "Erro", resultado)
    
    def enviar_email(self):
        """Envia email com o conteúdo"""
        conteudo = self.conteudo_card.obter_conteudo()
        
        # Validar limite de caracteres
        if not self.contador.esta_dentro_limite():
            self.status_bar.mostrar_aviso("O conteúdo excede o limite de caracteres.")
            self.status_bar.show()
            return
        
        # Obter destinatários
        destinatarios = self.config_service.obter_destinatarios()
        
        if not destinatarios:
            QMessageBox.warning(
                self,
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
            QTimer.singleShot(0, lambda: self._finalizar_enviar_email(sucesso, resultado))
            
        except Exception as e:
            QTimer.singleShot(0, lambda: QMessageBox.critical(self, "Erro", f"Erro inesperado: {str(e)}"))
            QTimer.singleShot(0, self.botoes_acao.habilitar_botoes)
    
    def _finalizar_enviar_email(self, sucesso, resultado):
        """Finaliza o envio de email"""
        self.botoes_acao.habilitar_botoes()
        
        if sucesso:
            self.status_bar.mostrar_sucesso(resultado)
            self.status_bar.show()
            QMessageBox.information(self, "Sucesso", resultado)
        else:
            self.status_bar.mostrar_erro(resultado)
            self.status_bar.show()
            QMessageBox.critical(self, "Erro", resultado)