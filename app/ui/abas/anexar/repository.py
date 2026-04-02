# -*- coding: utf-8 -*-
"""
Repositório SQL Server — tabela carteiras_digitais + sefaz_credenciais.

Estrutura SQL Server:

  carteiras_digitais (
      id INT IDENTITY(1,1) PRIMARY KEY,
      nome NVARCHAR(MAX),
      cpf NVARCHAR(100),
      unloc NVARCHAR(MAX),
      validade DATE,
      pdf VARBINARY(MAX),
      criado_em DATETIME DEFAULT GETDATE(),
      registro NVARCHAR(100),
      propriedade NVARCHAR(255),
      inicio NVARCHAR(50),
      endereco NVARCHAR(MAX),
      atividade1 NVARCHAR(MAX),
      atividade2 NVARCHAR(MAX),
      georef NVARCHAR(MAX),
      pdf_conteudo VARBINARY(MAX),
      foto1 VARBINARY(MAX),
      foto2 VARBINARY(MAX),
      foto3 VARBINARY(MAX),
      usuario NVARCHAR(100),
      anexado_por NVARCHAR(100),
      anexado_em DATETIME
  )

  sefaz_credenciais (
      id INT IDENTITY(1,1) PRIMARY KEY,
      usuario NVARCHAR(20),
      senha NVARCHAR(MAX),
      ativo BIT NOT NULL DEFAULT 1,
      criado_em DATETIME DEFAULT GETDATE()
  )
"""
from typing import Optional

import pyodbc
from services.database import get_connection, fetch_all_as_dict, fetch_one_as_dict


class AnexarRepository:

    def __init__(self):
        self._garantir_colunas_anexacao()

    # ------------------------------------------------------------------
    # Auto-migration: garante colunas anexado_por / anexado_em
    # ------------------------------------------------------------------
    def _garantir_colunas_anexacao(self):
        """Adiciona colunas de rastreio de anexação caso não existam."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            # Verificar se coluna anexado_por existe
            cursor.execute("""
                IF NOT EXISTS (
                    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = 'carteiras_digitais' 
                    AND COLUMN_NAME = 'anexado_por'
                )
                BEGIN
                    ALTER TABLE carteiras_digitais ADD anexado_por NVARCHAR(100);
                END
            """)
            
            # Verificar se coluna anexado_em existe
            cursor.execute("""
                IF NOT EXISTS (
                    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = 'carteiras_digitais' 
                    AND COLUMN_NAME = 'anexado_em'
                )
                BEGIN
                    ALTER TABLE carteiras_digitais ADD anexado_em DATETIME;
                END
            """)
            
            cursor.close()
            conn.commit()
        except Exception as exc:
            conn.rollback()
            print(f"[AnexarRepository] AVISO ao garantir colunas: {exc}")
        finally:
            conn.close()
            
# ------------------------------------------------------------------
# Excluir PDF
# ------------------------------------------------------------------
    def excluir_pdf_por_id(self, record_id: int) -> bool:
        """Exclui apenas o PDF (seta coluna pdf = NULL) e limpa dados de anexação"""
        sql = """
            UPDATE carteiras_digitais
            SET pdf = NULL, 
                anexado_por = NULL, 
                anexado_em = NULL
            WHERE id = ? AND pdf IS NOT NULL
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (record_id,))
            cursor.close()
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Credenciais SEFAZ
    # ------------------------------------------------------------------
    def buscar_credencial_sefaz(self) -> Optional[dict]:
        """Retorna o primeiro usuário ativo da tabela sefaz_credenciais."""
        sql = """
        SELECT TOP 1 usuario, senha
        FROM   sefaz_credenciais
        WHERE  ativo = 1
        ORDER  BY id
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            row = cursor.fetchone()
            cursor.close()
            
            if not row:
                return None
            return {'usuario': row[0], 'senha': row[1]}
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
            cursor = conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            cursor.close()
            
            registros = []
            for row in rows:
                registros.append({
                    'id': row[0],
                    'nome': row[1],
                    'cpf': row[2],
                    'unloc': row[3],
                    'validade': row[4],
                    'criado_em': row[5],
                    'registro': row[6],
                    'propriedade': row[7],
                    'inicio': row[8],
                    'endereco': row[9],
                    'atividade1': row[10],
                    'atividade2': row[11],
                    'georef': row[12],
                    'usuario': row[13],
                })
            return registros
        finally:
            conn.close()

    def buscar_todas_carteiras(self, limit: int = 500) -> list:
        """Retorna todas as carteiras (com e sem PDF), mais recentes primeiro."""
        sql = """
        SELECT TOP (?)
               id, nome, cpf, unloc, validade,
               criado_em, registro, propriedade,
               inicio, endereco, atividade1, atividade2,
               georef, usuario,
               CASE WHEN pdf IS NOT NULL THEN 1 ELSE 0 END AS pdf_gerado
        FROM    carteiras_digitais
        ORDER   BY criado_em DESC
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (limit,))
            rows = cursor.fetchall()
            cursor.close()
            
            registros = []
            for row in rows:
                registros.append({
                    'id': row[0],
                    'nome': row[1],
                    'cpf': row[2],
                    'unloc': row[3],
                    'validade': row[4],
                    'criado_em': row[5],
                    'registro': row[6],
                    'propriedade': row[7],
                    'inicio': row[8],
                    'endereco': row[9],
                    'atividade1': row[10],
                    'atividade2': row[11],
                    'georef': row[12],
                    'usuario': row[13],
                    'pdf_gerado': bool(row[14]),
                })
            return registros
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Buscar PDF salvo
    # ------------------------------------------------------------------
    def buscar_pdf_por_id(self, record_id: int) -> Optional[tuple]:
        """Retorna (nome_arquivo, bytes) do PDF da coluna `pdf`."""
        sql = "SELECT nome, cpf, pdf FROM carteiras_digitais WHERE id = ?"
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (record_id,))
            row = cursor.fetchone()
            cursor.close()
            
            if not row:
                return None
            nome_prod, cpf, dados = row
            if not dados:
                return None
            if isinstance(dados, memoryview):
                dados = bytes(dados)
            if isinstance(dados, bytearray):
                dados = bytes(dados)
            nome_arquivo = f"carteira_{cpf or record_id}.pdf"
            return nome_arquivo, dados
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Salvar PDF gerado
    # ------------------------------------------------------------------
    def salvar_pdf(self, record_id: int, pdf_bytes: bytes,
                   anexado_por: str = "") -> None:
        """Persiste o PDF e registra quem anexou e quando."""
        sql = """
            UPDATE carteiras_digitais
            SET    pdf         = ?,
                   anexado_por = ?,
                   anexado_em  = GETDATE()
            WHERE  id = ?
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (pyodbc.Binary(pdf_bytes), anexado_por, record_id))
            cursor.close()
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Carteiras em análise
    # ------------------------------------------------------------------
    def buscar_em_analise(self) -> list:
        """Retorna processos da tabela analises com status PENDENTE."""
        sql = """
        SELECT  id, nome_pdf, cpf, unloc, memorando,
                usuario, urgencia, tipo, criado_em, atualizado_em
        FROM    analises
        WHERE   status = 'PENDENTE'
        ORDER   BY CASE WHEN urgencia = 1 THEN 0 ELSE 1 END,
                   criado_em ASC
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            cursor.close()
            
            registros = []
            for row in rows:
                registros.append({
                    'id': row[0],
                    'nome_pdf': row[1],
                    'cpf': row[2],
                    'unloc': row[3],
                    'memorando': row[4],
                    'usuario': row[5],
                    'urgencia': row[6],
                    'tipo': row[7],
                    'criado_em': row[8],
                    'atualizado_em': row[9],
                })
            return registros
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Histórico de carteiras anexadas
    # ------------------------------------------------------------------
    def buscar_historico_anexados(self, limit: int = 500) -> list:
        """Retorna carteiras com PDF gerado, mostrando quem anexou e quando."""
        sql = """
        SELECT TOP (?)
               id, nome, cpf, unloc, registro,
               validade, usuario,
               ISNULL(anexado_por, usuario) AS anexado_por,
               ISNULL(anexado_em,  criado_em) AS anexado_em,
               criado_em
        FROM    carteiras_digitais
        WHERE   pdf IS NOT NULL
        ORDER   BY ISNULL(anexado_em, criado_em) DESC
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (limit,))
            rows = cursor.fetchall()
            cursor.close()
            
            registros = []
            for row in rows:
                registros.append({
                    'id': row[0],
                    'nome': row[1],
                    'cpf': row[2],
                    'unloc': row[3],
                    'registro': row[4],
                    'validade': row[5],
                    'usuario': row[6],
                    'anexado_por': row[7],
                    'anexado_em': row[8],
                    'criado_em': row[9],
                })
            return registros
        finally:
            conn.close()

    def buscar_prontos_filtrado(self, usuario: str = "", cpf: str = "",
                                nome: str = "", limit: int = 500) -> list:
        """Busca carteiras prontas com filtros opcionais."""
        clausulas = ["pdf IS NOT NULL"]
        filtro_params = []

        if usuario.strip():
            clausulas.append("LOWER(ISNULL(anexado_por, usuario)) LIKE LOWER(?)")
            filtro_params.append(f"%{usuario.strip()}%")
        if cpf.strip():
            clausulas.append("cpf LIKE ?")
            filtro_params.append(f"%{cpf.strip()}%")
        if nome.strip():
            clausulas.append("LOWER(nome) LIKE LOWER(?)")
            filtro_params.append(f"%{nome.strip()}%")

        where = " AND ".join(clausulas)
        # limit precisa ser o PRIMEIRO parâmetro para coincidir com TOP (?)
        params = [limit] + filtro_params

        sql = f"""
        SELECT TOP (?)
               id, nome, cpf, unloc, registro, validade,
               usuario,
               ISNULL(anexado_por, usuario)      AS anexado_por,
               ISNULL(anexado_em,  criado_em)    AS anexado_em,
               criado_em
        FROM    carteiras_digitais
        WHERE   {where}
        ORDER   BY ISNULL(anexado_em, criado_em) DESC
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            cursor.close()
            
            registros = []
            for row in rows:
                registros.append({
                    'id': row[0],
                    'nome': row[1],
                    'cpf': row[2],
                    'unloc': row[3],
                    'registro': row[4],
                    'validade': row[5],
                    'usuario': row[6],
                    'anexado_por': row[7],
                    'anexado_em': row[8],
                    'criado_em': row[9],
                })
            return registros
        finally:
            conn.close()

    def resumo_por_usuario(self) -> list:
        """Retorna ranking de anexações agrupado por usuário."""
        sql = """
        SELECT
            ISNULL(anexado_por, ISNULL(usuario, '(desconhecido)')) AS usuario,
            COUNT(*)                                                  AS total,
            MAX(ISNULL(anexado_em, criado_em))                       AS ultima_em
        FROM   carteiras_digitais
        WHERE  pdf IS NOT NULL
        GROUP  BY ISNULL(anexado_por, ISNULL(usuario, '(desconhecido)'))
        ORDER  BY COUNT(*) DESC
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            cursor.close()
            
            registros = []
            for row in rows:
                registros.append({
                    'usuario': row[0],
                    'total': row[1],
                    'ultima_em': row[2],
                })
            return registros
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Estatísticas
    # ------------------------------------------------------------------
    def estatisticas(self) -> dict:
        sql = """
        SELECT
            COUNT(*)                                AS total,
            SUM(CASE WHEN pdf IS NULL THEN 1 ELSE 0 END) AS pendentes,
            SUM(CASE WHEN pdf IS NOT NULL THEN 1 ELSE 0 END) AS gerados
        FROM carteiras_digitais
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            row = cursor.fetchone()
            cursor.close()
            
            return {
                "total": row[0] if row else 0,
                "pendentes": row[1] if row else 0,
                "gerados": row[2] if row else 0
            }
        finally:
            conn.close()
    