# -*- coding: utf-8 -*-
"""
Services para operações de email
"""

import smtplib
import ssl
import re
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Tuple
from .models import EmailConfigModel, EmailLogModel

class EmailService:
    """Serviço para envio de emails"""
    
    @staticmethod
    def validar_email(email: str) -> bool:
        """Valida formato de email"""
        if not email:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def testar_conexao_smtp(
        servidor: str, 
        porta: int, 
        email: str, 
        senha: str
    ) -> Tuple[bool, str]:
        """Testa conexão com servidor SMTP"""
        try:
            context = ssl.create_default_context()
            
            # Conectar ao servidor SMTP
            server = smtplib.SMTP(servidor, porta, timeout=10)
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            
            # Tentar login
            server.login(email, senha)
            
            # Enviar email de teste
            msg = MIMEMultipart()
            msg['From'] = email
            msg['To'] = email
            msg['Subject'] = "Teste de Configuração - Sector Automation"
            
            corpo = f"""Este é um email de teste para verificar a configuração SMTP.
            
            Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
            Servidor: {servidor}:{porta}
            Email: {email}
            
            Se você recebeu esta mensagem, a configuração está funcionando corretamente!"""
            
            msg.attach(MIMEText(corpo, 'plain', 'utf-8'))
            server.send_message(msg)
            server.quit()
            
            return True, "Conexão SMTP testada com sucesso!"
            
        except smtplib.SMTPAuthenticationError:
            return False, "Falha na autenticação. Verifique email e senha."
            
        except smtplib.SMTPConnectError:
            return False, f"Não foi possível conectar ao servidor {servidor}:{porta}"
            
        except Exception as e:
            return False, f"Erro na conexão: {str(e)}"
    
    @classmethod
    def enviar_email_novo_usuario(
        cls, 
        config: EmailConfigModel, 
        usuario_info: dict
    ) -> Tuple[bool, str]:
        """Envia email para novo usuário"""
        
        if not config.habilitado:
            return False, "Notificações por email desabilitadas"
        
        try:
            # Verificar se usuário tem email
            email_destinatario = usuario_info.get('email', '')
            if not email_destinatario:
                return False, "Usuário não possui email cadastrado"
                
            if not cls.validar_email(email_destinatario):
                return False, "Email do destinatário inválido"
            
            # Validar configuração do remetente
            if not all([config.email_remetente, config.senha_remetente, config.smtp_server]):
                return False, "Configuração de email incompleta"
            
            if not cls.validar_email(config.email_remetente):
                return False, "Email do remetente inválido"
            
            # Criar mensagem
            msg = MIMEMultipart()
            msg['From'] = config.email_remetente
            msg['To'] = email_destinatario
            msg['Subject'] = config.assunto_padrao
            
            # Preparar dados para template
            nome = usuario_info.get('nome', usuario_info.get('username', 'Usuário'))
            username = usuario_info.get('username', '')
            perfil = usuario_info.get('perfil', 'Usuário')
            email = usuario_info.get('email', '')
            status = 'Ativo' if usuario_info.get('ativo', True) else 'Inativo'
            
            # Formatar corpo usando template
            corpo = config.template_novo_usuario.format(
                nome=nome,
                username=username,
                perfil=perfil,
                email=email,
                status=status,
                url_sistema=config.url_sistema,
                assinatura=config.assinatura
            )
            
            msg.attach(MIMEText(corpo, 'plain', 'utf-8'))
            
            # Enviar email
            context = ssl.create_default_context()
            
            with smtplib.SMTP(config.smtp_server, config.smtp_port, timeout=10) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(config.email_remetente, config.senha_remetente)
                server.send_message(msg)
            
            # Registrar log de sucesso
            log = EmailLogModel(
                data_hora=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                username=username,
                acao='ENVIO_EMAIL_NOVO_USUARIO',
                destinatario=email_destinatario,
                status='SUCESSO',
                detalhes='Email enviado com sucesso'
            )
            cls._registrar_log(log)
            
            return True, "Email enviado com sucesso"
            
        except smtplib.SMTPAuthenticationError as e:
            log = EmailLogModel(
                data_hora=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                username=usuario_info.get('username', 'Desconhecido'),
                acao='ENVIO_EMAIL_NOVO_USUARIO',
                destinatario=email_destinatario,
                status='FALHA',
                detalhes=f'Erro de autenticação: {str(e)}'
            )
            cls._registrar_log(log)
            return False, "Erro de autenticação. Verifique email e senha."
            
        except smtplib.SMTPException as e:
            log = EmailLogModel(
                data_hora=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                username=usuario_info.get('username', 'Desconhecido'),
                acao='ENVIO_EMAIL_NOVO_USUARIO',
                destinatario=email_destinatario,
                status='FALHA',
                detalhes=f'Erro SMTP: {str(e)}'
            )
            cls._registrar_log(log)
            return False, f"Erro ao enviar email: {str(e)}"
            
        except Exception as e:
            log = EmailLogModel(
                data_hora=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                username=usuario_info.get('username', 'Desconhecido'),
                acao='ENVIO_EMAIL_NOVO_USUARIO',
                destinatario=email_destinatario,
                status='FALHA',
                detalhes=f'Erro inesperado: {str(e)}'
            )
            cls._registrar_log(log)
            return False, f"Erro inesperado: {str(e)}"
    
    @staticmethod
    def _registrar_log(log: EmailLogModel):
        """Registra log de envio de email"""
        try:
            log_dir = "logs"
            os.makedirs(log_dir, exist_ok=True)
            
            log_file = os.path.join(log_dir, "emails.log")
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log.to_log_string() + "\n")
                
        except Exception as e:
            print(f"Erro ao registrar log de email: {e}")