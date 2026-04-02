# -*- coding: utf-8 -*-
"""
Services para autenticação e operações do Gmail.
Todas as credenciais OAuth (ClientId, ClientSecret, AccessToken, RefreshToken…)
são lidas e gravadas exclusivamente na tabela bancocpp.dbo.Credenciais.
Nenhum arquivo local (token.json / credentials.json) é necessário.
"""

from datetime import datetime, timezone

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from services.database import get_connection


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
_TIPO = "credentials"
_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]

# URI padrão de token do Google — usado como fallback se a coluna vier nula
_TOKEN_URI_PADRAO = "https://oauth2.googleapis.com/token"
# URI de autorização do Google — necessária para montar o flow interativo
_AUTH_URI_PADRAO  = "https://accounts.google.com/o/oauth2/auth"


# ---------------------------------------------------------------------------
# Helpers de banco
# ---------------------------------------------------------------------------

def _carregar_linha_do_banco() -> dict | None:
    """
    Retorna um dicionário com TODAS as colunas da linha google_gmail,
    ou None se não existir registro.
    """
    sql = """
    SELECT [ClientId], [ClientSecret], [AuthUri], [TokenUri],
           [RedirectUris], [AccessToken], [RefreshToken], [Scopes], [Expiry]
    FROM   [bancocpp].[dbo].[Credenciais]
    WHERE  [Tipo] = ?;
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (_TIPO,))
        row = cursor.fetchone()
        cursor.close()
    finally:
        conn.close()

    if not row:
        return None

    return {
        "client_id":     row[0],
        "client_secret": row[1],
        "auth_uri":      row[2] or _AUTH_URI_PADRAO,
        "token_uri":     row[3] or _TOKEN_URI_PADRAO,
        "redirect_uris": [r.strip() for r in (row[4] or "").split(",") if r.strip()]
                         or ["http://localhost"],
        "access_token":  row[5],
        "refresh_token": row[6],
        "scopes":        [s.strip() for s in (row[7] or "").replace(",", " ").split() if s.strip()]
                         or _SCOPES,
        "expiry":        row[8],
    }


def _montar_credentials(dados: dict) -> Credentials | None:
    """Reconstrói um objeto Credentials a partir do dicionário do banco.
    O expiry NAO e setado para evitar o erro offset-naive vs offset-aware.
    Com RefreshToken presente o google-auth renova o token automaticamente.
    """
    if not dados.get("access_token"):
        return None

    return Credentials(
        token=dados["access_token"],
        refresh_token=dados.get("refresh_token"),
        token_uri=dados["token_uri"],
        client_id=dados["client_id"],
        client_secret=dados["client_secret"],
        scopes=dados["scopes"],
    )


def _salvar_tokens_no_banco(creds: Credentials) -> None:
    """
    Atualiza apenas as colunas de token na linha existente.
    (ClientId, ClientSecret, AuthUri etc. já estão no banco — não sobrescrevemos.)
    """
    scopes_str = " ".join(creds.scopes) if creds.scopes else " ".join(_SCOPES)

    expiry_val = None
    if creds.expiry:
        exp = creds.expiry
        expiry_val = exp.replace(tzinfo=None) if exp.tzinfo is not None else exp

    sql = """
    UPDATE [bancocpp].[dbo].[Credenciais]
    SET    [AccessToken]     = ?,
           [RefreshToken]    = ?,
           [Expiry]          = ?,
           [Scopes]          = ?,
           [DataAtualizacao] = GETDATE()
    WHERE  [Tipo] = ?;
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (
            creds.token,
            creds.refresh_token,
            expiry_val,
            scopes_str,
            _TIPO,
        ))
        cursor.close()
        conn.commit()
    except Exception as e:
        print(f"[Service] Erro ao salvar tokens no banco: {e}")
        conn.rollback()
    finally:
        conn.close()


def _montar_flow_do_banco(dados: dict) -> InstalledAppFlow:
    """
    Constrói um InstalledAppFlow usando os dados do banco,
    sem precisar de nenhum arquivo credentials.json.
    """
    client_config = {
        "installed": {
            "client_id":     dados["client_id"],
            "client_secret": dados["client_secret"],
            "auth_uri":      dados["auth_uri"],
            "token_uri":     dados["token_uri"],
            "redirect_uris": dados["redirect_uris"],
        }
    }
    return InstalledAppFlow.from_client_config(client_config, _SCOPES)


# ---------------------------------------------------------------------------
# Service principal
# ---------------------------------------------------------------------------

class EmailDownloadService:
    """Service para autenticação e operações do Gmail.

    Todas as credenciais vêm exclusivamente do banco (bancocpp.dbo.Credenciais).
    Nenhum arquivo local é lido ou escrito.

    Fluxo de autenticação:
      1. Carrega ClientId/Secret + AccessToken/RefreshToken do banco.
      2. Se o AccessToken for válido → usa direto.
      3. Se estiver expirado e houver RefreshToken → renova e salva de volta.
      4. Se não houver token válido → abre navegador para consentimento OAuth
         usando os dados do banco e salva o novo token.
    """

    SCOPES = _SCOPES

    def __init__(self, base_dir: str = ""):
        # base_dir mantido por compatibilidade com o restante do código
        self.base_dir = base_dir
        self.creds: Credentials | None = None
        self.service = None

    # ------------------------------------------------------------------
    # Autenticação
    # ------------------------------------------------------------------

    def autenticar(self) -> tuple[bool, str]:
        """Autentica com a API do Google usando credenciais do banco."""

        # 1 — carregar todos os dados do banco
        dados = _carregar_linha_do_banco()
        if not dados:
            return False, (
                "Nenhuma credencial encontrada no banco para Tipo='google_gmail'. "
                "Cadastre o registro na tabela bancocpp.dbo.Credenciais."
            )
        if not dados["client_id"] or not dados["client_secret"]:
            return False, "ClientId ou ClientSecret ausentes na tabela Credenciais."

        # 2 — montar objeto Credentials a partir dos tokens salvos
        self.creds = _montar_credentials(dados)

        # 3 — token válido → pronto
        if self.creds and self.creds.valid:
            self.service = build("gmail", "v1", credentials=self.creds)
            return True, "Autenticado com credenciais do banco"

        # 4 — token expirado + refresh_token → renovar automaticamente
        if self.creds and self.creds.expired and self.creds.refresh_token:
            try:
                self.creds.refresh(Request())
                _salvar_tokens_no_banco(self.creds)
                self.service = build("gmail", "v1", credentials=self.creds)
                return True, "Token renovado automaticamente e salvo no banco"
            except Exception as e:
                print(f"[Service] Falha ao renovar token: {e}")
                # Cai para o fluxo interativo

        # 5 — sem token válido → erro direto, sem abrir navegador
        return False, (
            "Nenhum token válido encontrado no banco. "
            "Preencha AccessToken e RefreshToken na tabela bancocpp.dbo.Credenciais."
        )

    # ------------------------------------------------------------------
    # Operações do Gmail
    # ------------------------------------------------------------------

    def obter_service(self):
        """Retorna o serviço do Gmail."""
        return self.service

    def buscar_emails_nao_lidos_com_anexos(self) -> tuple[list, str]:
        """Busca emails não lidos com anexos PDF, Word ou ZIP."""
        if not self.service:
            return [], "Serviço não inicializado"

        try:
            result = self.service.users().messages().list(
                userId="me",
                q="has:attachment is:unread (filename:pdf OR filename:doc OR filename:docx OR filename:zip)",
            ).execute()

            messages = result.get("messages", [])
            emails = []
            for msg in messages:
                email = self.service.users().messages().get(
                    userId="me",
                    id=msg["id"],
                    format="full",
                ).execute()
                emails.append(email)

            return emails, f"Encontrados {len(emails)} emails"

        except Exception as e:
            return [], f"Erro ao buscar emails: {e}"

    def extrair_cabecalho_email(
        self, email: dict, nome_cabecalho: str, padrao: str = "Desconhecido"
    ) -> str:
        """Extrai um cabeçalho específico do email."""
        try:
            for header in email["payload"]["headers"]:
                if header["name"] == nome_cabecalho:
                    return header["value"]
        except Exception:
            pass
        return padrao