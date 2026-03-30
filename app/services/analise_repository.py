# -*- coding: utf-8 -*-
import os
from typing import Optional
from services.database import get_connection, fetch_all_as_dict, fetch_one_as_dict


class AnaliseRepository:

    # ------------------------------------------------------------------
    # Salvar PDF
    # ------------------------------------------------------------------
    def salvar_pdf(self, nome_pdf, caminho_pdf, urgencia,
                   usuario=None, cpf=None):
        if not os.path.exists(caminho_pdf):
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho_pdf}")

        conn = get_connection()
        try:
            cur = conn.cursor()
            # ✅ Gera próximo ID manualmente — coluna 'id' não tem IDENTITY
            cur.execute("SELECT ISNULL(MAX(id), 0) + 1 FROM analises")
            novo_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO analises
                    (id, nome_pdf, cpf, usuario, urgencia, caminho_pdf, status, criado_em)
                VALUES
                    (?, ?, ?, ?, ?, ?, 'PENDENTE', GETDATE())
            """, (novo_id, nome_pdf, cpf, usuario, urgencia, caminho_pdf))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Listar pendentes
    # ------------------------------------------------------------------
    def listar_pendentes(self):
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT
                    id, nome_pdf, cpf, usuario, urgencia,
                    status, caminho_pdf, criado_em, atualizado_em
                FROM analises
                WHERE CAST(status AS VARCHAR(50)) = 'PENDENTE'
                ORDER BY urgencia DESC, criado_em DESC
            """)
            return fetch_all_as_dict(cur)
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Buscar por ID
    # ------------------------------------------------------------------
    def buscar_por_id(self, analise_id):
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT
                    id, nome_pdf, cpf, usuario, urgencia,
                    status, caminho_pdf, criado_em, atualizado_em
                FROM analises
                WHERE id = ?
            """, (analise_id,))
            return fetch_one_as_dict(cur)
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Buscar caminho do PDF
    # ------------------------------------------------------------------
    def buscar_caminho_pdf(self, analise_id):
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT caminho_pdf FROM analises WHERE id = ?",
                (analise_id,)
            )
            row = cur.fetchone()
            return row[0] if row else None
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Atualizar status
    # ------------------------------------------------------------------
    def atualizar_status(self, ids, novo_status, motivo=None):
        if not ids:
            return
        conn = get_connection()
        try:
            cur = conn.cursor()
            placeholders = ",".join(["?" for _ in ids])
            cur.execute(f"""
                UPDATE analises
                SET
                    status        = ?,
                    atualizado_em = GETDATE()
                WHERE id IN ({placeholders})
            """, [novo_status] + list(ids))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Salvar histórico
    # ------------------------------------------------------------------
    def salvar_historico(self, ids, status_anterior, novo_status,
                         usuario, motivo=None):
        if not ids:
            return
        conn = get_connection()
        try:
            cur = conn.cursor()
            for analise_id in ids:
                # ✅ Sem coluna 'motivo' — não existe na tabela
                cur.execute("""
                    INSERT INTO analises_historico
                        (analise_id, status_anterior, novo_status, usuario)
                    VALUES (?, ?, ?, ?)
                """, (analise_id, status_anterior, novo_status, usuario))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Listar histórico
    # ------------------------------------------------------------------
    def listar_historico(self):
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT
                    h.id,
                    h.analise_id,
                    h.status_anterior,
                    h.novo_status,
                    h.usuario,
                    h.data_acao,
                    a.nome_pdf,
                    a.cpf,
                    a.urgencia
                FROM analises_historico h
                JOIN analises a ON a.id = h.analise_id
                ORDER BY h.data_acao DESC
            """)
            return fetch_all_as_dict(cur)
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Listar todos
    # ------------------------------------------------------------------
    def listar_todos(self):
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT
                    id, nome_pdf, cpf, usuario, urgencia,
                    status, caminho_pdf, criado_em, atualizado_em
                FROM analises
                ORDER BY criado_em DESC
            """)
            return fetch_all_as_dict(cur)
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Buscar PDF binário (via tabela lancamentos pelo nome_pdf)
    # ------------------------------------------------------------------
    def buscar_pdf_binario(self, analise_id):
        """
        Busca o conteúdo binário do PDF na tabela lancamentos
        usando o nome_pdf da análise como chave de ligação.
        """
        conn = get_connection()
        try:
            cur = conn.cursor()
            # Primeiro busca o nome_pdf da análise
            cur.execute(
                "SELECT nome_pdf FROM analises WHERE id = ?",
                (analise_id,)
            )
            row = cur.fetchone()
            if not row:
                return None
            nome_pdf = row[0]

            # Depois busca o binário na tabela lancamentos
            cur.execute("""
                SELECT TOP 1 nome_pdf, pdf_conteudo
                FROM lancamentos
                WHERE CAST(nome_pdf AS VARCHAR(500)) = ?
                ORDER BY criado_em DESC
            """, (nome_pdf,))
            return fetch_one_as_dict(cur)
        finally:
            conn.close()