# -*- coding: utf-8 -*-
"""
Serviço para envio de emails
"""

import smtplib
import os
from email.message import EmailMessage
from typing import List
import json


class EmailService:
    """Serviço para envio de emails via SMTP"""
    
    def __init__(self, servidor="smtp.gmail.com", porta=587):
        self.servidor = servidor
        self.porta = porta

        # Carregar credenciais
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cred_path = os.path.join(base_dir, "jsons files", "credentials.json")
        
        with open(cred_path, 'r', encoding='utf-8') as f:
            credenciais = json.load(f)

        self.usuario = credenciais.get("email")
        self.senha = credenciais.get("senha")

        if not self.usuario or not self.senha:
            raise ValueError("Credenciais de email inválidas em credentials.json")

    def enviar_email(
        self,
        assunto: str,
        corpo: str,
        destinatarios: List[str],
        anexos: List[str] = None
    ):
        """
        Envia um email
        
        Args:
            assunto: Assunto do email
            corpo: Corpo do email
            destinatarios: Lista de emails destinatários
            anexos: Lista de caminhos de arquivos anexos (opcional)
        """
        if not destinatarios:
            raise ValueError("Nenhum destinatário informado.")

        msg = EmailMessage()
        msg["From"] = self.usuario
        msg["To"] = ", ".join(destinatarios)
        msg["Subject"] = assunto
        msg.set_content(corpo)

        if anexos:
            for caminho in anexos:
                self._anexar_arquivo(msg, caminho)

        self._enviar(msg)

    def enviar_por_municipio(
        self,
        municipio: str,
        assunto: str,
        corpo: str,
        tipo="dev",
        anexos: List[str] = None
    ):
        """
        Envia email para um município específico
        
        Args:
            municipio: Nome do município
            assunto: Assunto do email
            corpo: Corpo do email
            tipo: Tipo de email ('dev' ou 'recebimento')
            anexos: Lista de arquivos anexos (opcional)
        """
        arquivo = (
            "Emails_Dev.json"
            if tipo == "dev"
            else "Emails_recebimento.json"
        )

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        email_path = os.path.join(base_dir, "jsons files", arquivo)
        
        with open(email_path, 'r', encoding='utf-8') as f:
            emails = json.load(f)

        destinatarios = emails.get(municipio)

        if not destinatarios:
            raise ValueError(f"Nenhum email encontrado para {municipio}")

        self.enviar_email(assunto, corpo, destinatarios, anexos)

    def _enviar(self, msg: EmailMessage):
        """Envia a mensagem via SMTP"""
        with smtplib.SMTP(self.servidor, self.porta) as server:
            server.starttls()
            server.login(self.usuario, self.senha)
            server.send_message(msg)

    def _anexar_arquivo(self, msg: EmailMessage, caminho):
        """Anexa um arquivo à mensagem"""
        if not os.path.exists(caminho):
            raise FileNotFoundError(f"Anexo não encontrado: {caminho}")

        with open(caminho, "rb") as f:
            dados = f.read()

        nome = os.path.basename(caminho)

        msg.add_attachment(
            dados,
            maintype="application",
            subtype="octet-stream",
            filename=nome
        )