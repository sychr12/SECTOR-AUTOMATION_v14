# -*- coding: utf-8 -*-
from datetime import datetime
import re
from services.database import get_connection, fetch_all_as_dict, fetch_one_as_dict


class DatabaseService:

    def usuario_existe(self, usuario):
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM usuarios.usuarios WHERE nome = ?", (usuario,))
            return cur.fetchone() is not None
        finally:
            conn.close()

    def salvar_lancamento(self, usuario, dados_texto):
        cpf = self._extrair_cpf(dados_texto)
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO lancamentos.lancamentos (usuario, cpf, dados, data_criacao)
                VALUES (?, ?, ?, ?)
            """, (usuario, cpf, dados_texto or "", datetime.now()))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def listar_lancamentos(self):
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, usuario, cpf, data_criacao
                FROM lancamentos.lancamentos
                ORDER BY id DESC
            """)
            return fetch_all_as_dict(cur)
        finally:
            conn.close()

    def buscar_lancamento_por_id(self, lancamento_id):
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT dados FROM lancamentos.lancamentos WHERE id = ?",
                (lancamento_id,)
            )
            row = fetch_one_as_dict(cur)
            return row["dados"] if row else None
        finally:
            conn.close()

    def excluir_lancamento(self, lancamento_id):
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "DELETE FROM lancamentos.lancamentos WHERE id = ?",
                (lancamento_id,)
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _extrair_cpf(self, texto):
        if not isinstance(texto, str):
            return None
        match = re.search(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b", texto)
        return match.group(0) if match else None