# -*- coding: utf-8 -*-
"""
Repositório para persistência de downloads de emails no SQL Server.
Os bytes do PDF são armazenados diretamente na coluna `pdf` (VARBINARY(MAX)).
Tabela: emails_anexos
"""
from datetime import datetime
from typing import Optional

import pyodbc  # Substituir psycopg2

from services.database import get_connection


class EmailDownloadRepository:
    """Repositório para gerenciar registros de downloads de emails no banco."""

    # ------------------------------------------------------------------
    # Conexão
    # ------------------------------------------------------------------
    @staticmethod
    def _get_conn():
        """Abre conexão com SQL Server."""
        return get_connection()

    # ------------------------------------------------------------------
    # DDL — cria tabela se não existir
    # ------------------------------------------------------------------
    def criar_tabela(self) -> None:
        """
        Garante que a tabela emails_anexos existe com a estrutura correta.
        Este método é idempotente.
        """
        sql = """
        IF NOT EXISTS (SELECT * FROM sys.objects 
                       WHERE object_id = OBJECT_ID(N'[dbo].[emails_anexos]') 
                       AND type in (N'U'))
        BEGIN
            CREATE TABLE [dbo].[emails_anexos] (
                [id]           INT IDENTITY(1,1) PRIMARY KEY,
                [email_id]     NVARCHAR(255) NOT NULL,
                [remetente]    NVARCHAR(500),
                [assunto]      NVARCHAR(500),
                [municipio]    NVARCHAR(100),
                [data_email]   DATETIME,
                [nome_arquivo] NVARCHAR(500) NOT NULL,
                [mime_type]    NVARCHAR(100),
                [pdf]          VARBINARY(MAX) NOT NULL,
                [hash_sha256]  NVARCHAR(100),
                [criado_em]    DATETIME NOT NULL DEFAULT GETDATE()
            );

            CREATE INDEX IX_emails_anexos_criado_em 
                ON [dbo].[emails_anexos]([criado_em] DESC);
        END
        """
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            cursor.close()
            conn.commit()
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # INSERT / UPSERT
    # ------------------------------------------------------------------
    def registrar_download(
        self,
        msg_id: str,
        remetente: str,
        assunto: str,
        municipio: str,
        data_email: Optional[datetime],
        nome_arquivo: str,
        arquivo_bytes: Optional[bytes],
        erro_mensagem: Optional[str] = None,
    ) -> Optional[int]:
        """Insere registro com bytes do PDF."""
        
        # isso aqui e so pra eu saber os erros mesmo ta bom?????
        print(f"[Repositório] Registrando download: msg_id={msg_id}, remetente={remetente}, assunto={assunto}, municipio={municipio}, data_email={data_email}, nome_arquivo={nome_arquivo}, bytes={len(arquivo_bytes) if arquivo_bytes else 0}, erro={erro_mensagem}")
        
        # essa merda aqui gerar um id unico pra evitar duplicidade, pq o msg_id pode ser repetido se o email for reprocessado
        unique_msg_id = f"{msg_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # SQL separado: primeiro INSERT, depois SELECT
        sql_insert = """
        INSERT INTO [dbo].[emails_anexos](
            [email_id], [remetente], [assunto], [municipio],
            [data_email], [nome_arquivo], [mime_type], [pdf],
            [hash_sha256], [criado_em]
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE());
        """
        
        sql_select = """
        SELECT SCOPE_IDENTITY() AS id;
        """
        
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            
            pdf_bytes = pyodbc.Binary(arquivo_bytes) if arquivo_bytes else None
            
            # isso aqui e so pra eu saber se ta chegando os dados certinho, pode tirar depois
            print(f"[Repositório] Executando INSERT com email_id={unique_msg_id}, remetente={remetente}, assunto={assunto}, municipio={municipio}, data_email={data_email}, nome_arquivo={nome_arquivo}, bytes={len(arquivo_bytes) if arquivo_bytes else 0}")
            
            # Executar o INSERT
            cursor.execute(sql_insert, (
                unique_msg_id,
                remetente or "",
                assunto or "",
                municipio or "",
                data_email,
                nome_arquivo,
                "application/pdf" if arquivo_bytes else None,
                pdf_bytes,
                None,  # hash_sha256 pode ser calculado posteriormente
            ))
            
            # Executar o SELECT para pegar o ID
            cursor.execute(sql_select)
            row = cursor.fetchone()
            
            cursor.close()
            conn.commit()
            
            record_id = row[0] if row else None
            print(f"[Repositório] Download registrado com ID {record_id} para email_id {unique_msg_id}")
            return record_id
            
        except Exception as e:
            print(f"[Reposritório] Erro ao registrar download: {e}")
            import traceback
            traceback.print_exc()
            conn.rollback()
            return None
        finally:
            conn.close()
    
    

    # ------------------------------------------------------------------
    # SELECT
    # ------------------------------------------------------------------
    def listar_downloads(self, limit: int = 200) -> list:
        """Retorna metadados sem bytes — leve para preencher a tabela."""
        sql = """
        SELECT TOP (?)
               [id], [email_id], [remetente], [assunto], [municipio],
               [data_email], [nome_arquivo], [criado_em]
        FROM   [dbo].[emails_anexos]
        ORDER  BY [criado_em] DESC;
        """
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (limit,))
            rows = cursor.fetchall()
            cursor.close()
            
            registros = []
            for row in rows:
                registros.append({
                    'id': row[0],
                    'email_id': row[1],
                    'remetente': row[2],
                    'assunto': row[3],
                    'municipio': row[4],
                    'data_email': row[5],
                    'nome_arquivo': row[6],
                    'criado_em': row[7],
                })
            
            return registros
            
        except Exception:
            try:
                conn.rollback()
            except Exception:
                pass
            return []
        finally:
            conn.close()

    def baixar_bytes_por_id(self, record_id: int) -> Optional[tuple]:
        """
        Retorna (nome_arquivo, dados_bytes) para o id informado.
        Busca VARBINARY(MAX) somente quando o usuário clica em Baixar.
        """
        sql = """
        SELECT [nome_arquivo], [pdf]
        FROM   [dbo].[emails_anexos]
        WHERE  [id] = ?;
        """
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (record_id,))
            row = cursor.fetchone()
            cursor.close()
            
            if not row:
                return None
            
            nome = row[0]
            dados = row[1]
            
            # Converter memoryview/bytearray para bytes
            if isinstance(dados, memoryview):
                dados = bytes(dados)
            elif isinstance(dados, bytearray):
                dados = bytes(dados)
            
            return nome, dados
            
        except Exception:
            try:
                conn.rollback()
            except Exception:
                pass
            return None
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Estatísticas
    # ------------------------------------------------------------------
    def estatisticas(self) -> dict:
        sql = """
        SELECT
            COUNT(*)                         AS total,
            MAX([criado_em])                 AS ultima_execucao
        FROM [dbo].[emails_anexos];
        """
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            row = cursor.fetchone()
            cursor.close()
            
            if row:
                return {
                    'total': row[0],
                    'ultima_execucao': row[1]
                }
            return {}
            
        except Exception:
            try:
                conn.rollback()
            except Exception:
                pass
            return {}
        finally:
            conn.close()