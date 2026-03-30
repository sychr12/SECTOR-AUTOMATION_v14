# -*- coding: utf-8 -*-
"""
Repositório PostgreSQL — tabela carteiras_digitais + sefaz_credenciais.
Schema real (sistemadocumentos.sql):

  carteiras_digitais (
      id SERIAL PK, nome TEXT, cpf VARCHAR(100),
      unloc TEXT, validade DATE, pdf BYTEA,
      criado_em TIMESTAMP, registro VARCHAR(100),
      propriedade VARCHAR(255), inicio VARCHAR(50),
      endereco TEXT, atividade1 TEXT, atividade2 TEXT,
      georef TEXT, pdf_conteudo BYTEA,
      foto1 BYTEA, foto2 BYTEA, foto3 BYTEA, usuario VARCHAR(100)
  )

  sefaz_credenciais (
      id SERIAL PK, usuario VARCHAR(20),
      senha TEXT, ativo BOOLEAN, criado_em TIMESTAMP
  )
"""
from typing import Optional

import psycopg2
from psycopg2.extras import RealDictCursor

from app.services.database import get_connection   # ← caminho corrigido


class AnexarRepository:

    # ------------------------------------------------------------------
    # Credenciais SEFAZ
    # ------------------------------------------------------------------
    def buscar_credencial_sefaz(self) -> Optional[dict]:
        """Retorna o primeiro usuário ativo da tabela sefaz_credenciais."""
        sql = """
        SELECT usuario, senha
        FROM   sefaz_credenciais
        WHERE  ativo = TRUE
        ORDER  BY id
        LIMIT  1
        """
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql)
                row = cur.fetchone()
                return dict(row) if row else None
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Carteiras pendentes
    # ------------------------------------------------------------------
    def buscar_carteiras_pendentes(self) -> list:
        """Retorna carteiras onde pdf IS NULL, sem colunas BYTEA pesadas."""
        sql = """
        SELECT  id, nome, cpf, unloc, validade,
                criado_em, registro, propriedade,
                inicio, endereco, atividade1, atividade2,
                georef, usuario
        FROM    carteiras_digitais
        WHERE   pdf IS NULL
        ORDER   BY criado_em DESC
        """
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql)
                return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

    def buscar_todas_carteiras(self, limit: int = 500) -> list:
        """Retorna todas as carteiras (com e sem PDF), mais recentes primeiro."""
        sql = """
        SELECT  id, nome, cpf, unloc, validade,
                criado_em, registro, propriedade,
                inicio, endereco, atividade1, atividade2,
                georef, usuario,
                (pdf IS NOT NULL) AS pdf_gerado
        FROM    carteiras_digitais
        ORDER   BY criado_em DESC
        LIMIT   %s
        """
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, (limit,))
                return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Buscar PDF salvo
    # ------------------------------------------------------------------
    def buscar_pdf_por_id(self, record_id: int) -> Optional[tuple]:
        """Retorna (nome_arquivo, bytes) do PDF da coluna `pdf`."""
        sql = "SELECT nome, cpf, pdf FROM carteiras_digitais WHERE id = %s"
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (record_id,))
                row = cur.fetchone()
            if not row:
                return None
            nome_prod, cpf, dados = row
            if not dados:
                return None
            if isinstance(dados, memoryview):
                dados = bytes(dados)
            nome_arquivo = f"carteira_{cpf or record_id}.pdf"
            return nome_arquivo, dados
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Salvar PDF gerado
    # ------------------------------------------------------------------
    def salvar_pdf(self, record_id: int, pdf_bytes: bytes) -> None:
        """Persiste o PDF gerado na coluna `pdf` da carteira."""
        sql = "UPDATE carteiras_digitais SET pdf = %s WHERE id = %s"
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (psycopg2.Binary(pdf_bytes), record_id))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Estatísticas
    # ------------------------------------------------------------------
    def estatisticas(self) -> dict:
        sql = """
        SELECT
            COUNT(*)                                AS total,
            COUNT(*) FILTER (WHERE pdf IS NULL)     AS pendentes,
            COUNT(*) FILTER (WHERE pdf IS NOT NULL) AS gerados
        FROM carteiras_digitais
        """
        conn = get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql)
                row = cur.fetchone()
                return dict(row) if row else {"total": 0, "pendentes": 0, "gerados": 0}
        finally:
            conn.close()