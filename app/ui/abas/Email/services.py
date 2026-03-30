# -*- coding: utf-8 -*-
"""
Services para autenticação e operações do Gmail
"""

import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

class EmailDownloadService:
    """Service para autenticação e operações do Gmail"""
    
    SCOPES = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.modify",
    ]
    
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.creds = None
        self.service = None
    
    def autenticar(self):
        """Autentica com a API do Google"""
        token_path = os.path.join(self.base_dir, "token.json")
        
        try:
            # Tentar carregar credenciais existentes
            if os.path.exists(token_path):
                self.creds = Credentials.from_authorized_user_file(
                    token_path, self.SCOPES
                )
            
            # Verificar se as credenciais são válidas
            if self.creds and self.creds.valid:
                self.service = build("gmail", "v1", credentials=self.creds)
                return True, "Autenticado com credenciais existentes"
            
            # Tentar renovar credenciais expiradas
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
                self.service = build("gmail", "v1", credentials=self.creds)
                
                # Salvar credenciais atualizadas
                with open(token_path, "w") as token:
                    token.write(self.creds.to_json())
                
                return True, "Credenciais renovadas com sucesso"
            
            # Criar novas credenciais
            credentials_path = os.path.join(self.base_dir, "jsons files", "credentials.json")
            if not os.path.exists(credentials_path):
                return False, "Arquivo credentials.json não encontrado"
            
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path,
                self.SCOPES
            )
            self.creds = flow.run_local_server(port=0)
            self.service = build("gmail", "v1", credentials=self.creds)
            
            # Salvar credenciais para uso futuro
            with open(token_path, "w") as token:
                token.write(self.creds.to_json())
            
            return True, "Autenticação realizada com sucesso"
            
        except Exception as e:
            return False, f"Erro na autenticação: {str(e)}"
    
    def obter_service(self):
        """Retorna o serviço do Gmail"""
        return self.service
    
    def buscar_emails_nao_lidos_com_anexos(self):
        """Busca emails não lidos com anexos"""
        try:
            if not self.service:
                return [], "Serviço não inicializado"
            
            result = self.service.users().messages().list(
                userId="me",
                q="has:attachment is:unread"
            ).execute()
            
            messages = result.get("messages", [])
            emails = []
            
            for msg in messages:
                email = self.service.users().messages().get(
                    userId="me",
                    id=msg["id"],
                    format="full"
                ).execute()
                emails.append(email)
            
            return emails, f"Encontrados {len(emails)} emails"
            
        except Exception as e:
            return [], f"Erro ao buscar emails: {str(e)}"
    
    def extrair_cabecalho_email(self, email, nome_cabecalho, padrao="Desconhecido"):
        """Extrai um cabeçalho específico do email"""
        try:
            headers = email["payload"]["headers"]
            for header in headers:
                if header["name"] == nome_cabecalho:
                    return header["value"]
        except:
            pass
        
        return padrao