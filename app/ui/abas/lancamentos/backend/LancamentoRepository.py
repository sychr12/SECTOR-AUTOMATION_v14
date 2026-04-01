# -*- coding: utf-8 -*-
"""
Repositório SQL Server — módulo Lançamento de Processo.

Tabela analises:
  id, nome_pdf, cpf, unloc, memorando, usuario, urgencia, tipo,
  caminho_pdf, criado_em, status, atualizado_em, motivo
  *** NÃO tem pdf_conteudo ***

Tabela lancamentos:
  id, nome_pdf, cpf, analisado_por, lancado_por,
  criado_em, caminho_pdf, pdf_conteudo, caminho_word
"""
from typing import Optional

import pyodbc  # Substituir psycopg2

from services.database import get_connection


def _b(v) -> bytes:
    """Converte dados binários para bytes"""
    if v is None:
        return b""
    if isinstance(v, memoryview):
        return bytes(v)
    if isinstance(v, bytearray):
        return bytes(v)
    return v if isinstance(v, bytes) else b""


class LancamentoRepository:

    # ------------------------------------------------------------------
    # Listar devoluções (status DEVOLUCAO)
    # ------------------------------------------------------------------
    def listar_devolucoes(self) -> list:
        sql = """
        SELECT
            a.id,
            a.nome_pdf,
            a.cpf,
            a.usuario          AS analisado_por,
            a.status,
            a.urgencia,
            a.caminho_pdf,
            a.criado_em,
            a.memorando,
            COALESCE(a.motivo, '') AS motivo,
            l.lancado_por
        FROM  analises a
        LEFT  JOIN lancamentos l ON l.nome_pdf = a.nome_pdf
        WHERE a.status = 'DEVOLUCAO'
        ORDER BY CASE WHEN a.urgencia = 1 THEN 0 ELSE 1 END,
                 a.criado_em ASC
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
                    'analisado_por': row[3],
                    'status': row[4],
                    'urgencia': row[5],
                    'caminho_pdf': row[6],
                    'criado_em': row[7],
                    'memorando': row[8],
                    'motivo': row[9],
                    'lancado_por': row[10],
                })
            return registros
        except Exception:
            conn.rollback()
            return []
        finally:
            conn.close()

    def listar_para_lancamento(self) -> list:
        sql = """
        SELECT
            a.id,
            a.nome_pdf,
            a.cpf,
            a.usuario          AS analisado_por,
            a.status,
            a.urgencia,
            a.caminho_pdf,
            a.criado_em,
            l.lancado_por
        FROM  analises a
        LEFT  JOIN lancamentos l ON l.nome_pdf = a.nome_pdf
        WHERE a.status IN ('RENOVACAO', 'INSCRICAO')
        ORDER BY CASE WHEN a.urgencia = 1 THEN 0 ELSE 1 END,
                 a.criado_em ASC
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
                    'analisado_por': row[3],
                    'status': row[4],
                    'urgencia': row[5],
                    'caminho_pdf': row[6],
                    'criado_em': row[7],
                    'lancado_por': row[8],
                })
            return registros
        except Exception:
            conn.rollback()
            return []
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Buscar analise para abrir PDF
    # ------------------------------------------------------------------
    def buscar_pdf(self, analise_id: int) -> Optional[dict]:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, nome_pdf, cpf, caminho_pdf, usuario
                FROM   analises
                WHERE  id = ?
            """, (analise_id,))
            row = cursor.fetchone()
            cursor.close()
            
            if not row:
                return None
            return {
                'id': row[0],
                'nome_pdf': row[1],
                'cpf': row[2],
                'caminho_pdf': row[3],
                'usuario': row[4],
            }
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Buscar bytes do PDF
    # ------------------------------------------------------------------
    def buscar_pdf_bytes_lancamento(self, nome_pdf: str) -> Optional[bytes]:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT TOP 1 pdf_conteudo
                FROM   lancamentos
                WHERE  nome_pdf = ?
                ORDER  BY criado_em DESC
            """, (nome_pdf,))
            row = cursor.fetchone()
            cursor.close()
            return _b(row[0]) if (row and row[0]) else None
        finally:
            conn.close()

    def buscar_pdf_bytes_por_id(self, lancamento_id: int) -> Optional[bytes]:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT pdf_conteudo
                FROM   lancamentos
                WHERE  id = ?
            """, (lancamento_id,))
            row = cursor.fetchone()
            cursor.close()
            return _b(row[0]) if (row and row[0]) else None
        finally:
            conn.close()

    def buscar_pdf_binario(self, lancamento_id: int) -> Optional[dict]:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT nome_pdf, pdf_conteudo
                FROM   lancamentos
                WHERE  id = ?
            """, (lancamento_id,))
            row = cursor.fetchone()
            cursor.close()
            
            if not row:
                return None
            return {
                'nome_pdf': row[0],
                'pdf_conteudo': _b(row[1]),
            }
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Registrar lançamento
    # ------------------------------------------------------------------
    def registrar_lancamento(self, nome_pdf: str, cpf: str,
                              analisado_por: str, lancado_por: str,
                              pdf_conteudo: Optional[bytes] = None,
                              caminho_pdf: str = "") -> Optional[int]:
        sql = """
        INSERT INTO lancamentos
            (nome_pdf, cpf, analisado_por, lancado_por,
             pdf_conteudo, caminho_pdf, criado_em)
        VALUES (?, ?, ?, ?, ?, ?, GETDATE())
        SELECT SCOPE_IDENTITY() AS id
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (
                nome_pdf, cpf, analisado_por, lancado_por,
                pyodbc.Binary(pdf_conteudo) if pdf_conteudo else None,
                caminho_pdf,
            ))
            row = cursor.fetchone()
            cursor.close()
            conn.commit()
            return row[0] if row else None
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def salvar(self, nome_pdf: str, cpf: str, analisado_por: str,
               lancado_por: str,
               pdf_conteudo: Optional[bytes] = None) -> Optional[int]:
        return self.registrar_lancamento(
            nome_pdf=nome_pdf, cpf=cpf,
            analisado_por=analisado_por, lancado_por=lancado_por,
            pdf_conteudo=pdf_conteudo,
        )

    # ------------------------------------------------------------------
    # Marcar como LANCADO
    # ------------------------------------------------------------------
    def marcar_como_lancado(self, analise_id: int, lancado_por: str) -> None:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE analises
                SET    status        = 'LANCADO',
                       atualizado_em = GETDATE()
                WHERE  id = ?
            """, (analise_id,))
            cursor.close()
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Buscar por CPF (analises pendentes)
    # ------------------------------------------------------------------
    def buscar_por_cpf(self, cpf: str) -> list:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.id, a.nome_pdf, a.caminho_pdf,
                       a.usuario AS analisado_por,
                       a.status, l.lancado_por
                FROM   analises a
                LEFT   JOIN lancamentos l ON l.nome_pdf = a.nome_pdf
                WHERE  a.cpf = ?
                  AND  a.status IN ('RENOVACAO','INSCRICAO')
                ORDER  BY a.criado_em DESC
            """, (cpf,))
            rows = cursor.fetchall()
            cursor.close()
            
            registros = []
            for row in rows:
                registros.append({
                    'id': row[0],
                    'nome_pdf': row[1],
                    'caminho_pdf': row[2],
                    'analisado_por': row[3],
                    'status': row[4],
                    'lancado_por': row[5],
                })
            return registros
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Histórico de lancamentos por CPF (consulta)
    # ------------------------------------------------------------------
    def historico_por_cpf(self, cpf: str) -> list:
        """Retorna todos os lançamentos já feitos para esse CPF."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, nome_pdf, cpf, analisado_por,
                       lancado_por, criado_em
                FROM   lancamentos
                WHERE  cpf = ?
                ORDER  BY criado_em DESC
            """, (cpf,))
            rows = cursor.fetchall()
            cursor.close()
            
            result = []
            for row in rows:
                d = {
                    'id': row[0],
                    'nome_pdf': row[1],
                    'cpf': row[2],
                    'analisado_por': row[3],
                    'lancado_por': row[4],
                    'criado_em': row[5],
                }
                if d.get("criado_em") and hasattr(d["criado_em"], "strftime"):
                    d["criado_em"] = d["criado_em"].strftime("%d/%m/%Y %H:%M")
                result.append(d)
            return result
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Marcar lançado por CPF
    # ------------------------------------------------------------------
    def marcar_lancado_por_cpf(self, cpf: str, lancado_por: str) -> int:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE analises
                SET    status        = 'LANCADO',
                       atualizado_em = GETDATE()
                WHERE  cpf    = ?
                  AND  status IN ('RENOVACAO','INSCRICAO')
            """, (cpf,))
            affected = cursor.rowcount
            cursor.close()
            conn.commit()
            return affected
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Histórico geral
    # ------------------------------------------------------------------
    def historico(self, limit: int = 200) -> list:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT TOP (?)
                       id, nome_pdf, cpf, analisado_por,
                       lancado_por, criado_em
                FROM   lancamentos
                ORDER  BY criado_em DESC
            """, (limit,))
            rows = cursor.fetchall()
            cursor.close()
            
            result = []
            for row in rows:
                d = {
                    'id': row[0],
                    'nome_pdf': row[1],
                    'cpf': row[2],
                    'analisado_por': row[3],
                    'lancado_por': row[4],
                    'criado_em': row[5],
                }
                if d.get("criado_em") and hasattr(d["criado_em"], "strftime"):
                    d["criado_em"] = d["criado_em"].strftime("%d/%m/%Y %H:%M")
                result.append(d)
            return result
        finally:
            conn.close()

    def listar_ultimos(self, limite: int = 50) -> list:
        return self.historico(limit=limite)

    # ------------------------------------------------------------------
    # Estatísticas
    # ------------------------------------------------------------------
    def estatisticas(self) -> dict:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            # Pendentes: status RENOVACAO/INSCRICAO mas não lançados
            cursor.execute("""
                SELECT COUNT(*) FROM analises a
                WHERE a.status IN ('RENOVACAO','INSCRICAO')
                  AND NOT EXISTS (
                      SELECT 1 FROM lancamentos l 
                      WHERE l.nome_pdf = a.nome_pdf
                  )
            """)
            pendentes = cursor.fetchone()[0]
            
            # Prontos: status RENOVACAO/INSCRICAO E já lançados
            cursor.execute("""
                SELECT COUNT(*) FROM analises a
                WHERE a.status IN ('RENOVACAO','INSCRICAO')
                  AND EXISTS (
                      SELECT 1 FROM lancamentos l 
                      WHERE l.nome_pdf = a.nome_pdf
                  )
            """)
            prontos = cursor.fetchone()[0]
            
            # Lançados
            cursor.execute("SELECT COUNT(*) FROM analises WHERE status = 'LANCADO'")
            lancados = cursor.fetchone()[0]
            
            # Devoluções
            cursor.execute("SELECT COUNT(*) FROM analises WHERE status = 'DEVOLUCAO'")
            devolucoes = cursor.fetchone()[0]
            
            # Urgentes
            cursor.execute("""
                SELECT COUNT(*) FROM analises 
                WHERE urgencia = 1 
                  AND status IN ('RENOVACAO','INSCRICAO')
            """)
            urgentes = cursor.fetchone()[0]
            
            cursor.close()
            
            return {
                'pendentes': pendentes,
                'prontos': prontos,
                'lancados': lancados,
                'devolucoes': devolucoes,
                'urgentes': urgentes,
            }
        finally:
            conn.close()