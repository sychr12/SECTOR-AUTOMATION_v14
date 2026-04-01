# services/credenciais_service.py
# -*- coding: utf-8 -*-
"""
credenciais_service.py — Repositório de credenciais SEFAZ.
"""
from typing import Optional
from services.database import get_connection


class SefazCredentialRepository:
    """Busca credenciais SEFAZ ativas no banco de dados (SQL Server)."""

    def obter_credencial(self) -> Optional[dict]:
        """
        Retorna {'usuario': str, 'senha': str} da primeira credencial ativa,
        ou None se não houver nenhuma cadastrada / ativa.
        """
        sql = """
            SELECT TOP 1 usuario, senha
            FROM sefaz_credenciais
            WHERE ativo = 1
            ORDER BY id DESC;
        """
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(sql)
            row = cursor.fetchone()
            cursor.close()

            if not row:
                print("[SefazCredentialRepository] Nenhuma credencial ativa encontrada na tabela sefaz_credenciais.")
                return None

            print(f"[SefazCredentialRepository] Credencial encontrada: {row[0]}")
            return {"usuario": row[0], "senha": row[1]}

        except Exception as e:
            print(f"[SefazCredentialRepository] Erro ao buscar credencial: {type(e).__name__}: {e}")
            return None
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass