# -*- coding: utf-8 -*-
from services.database import get_connection, fetch_one_as_dict


class SefazRepository:

    def obter_credencial(self):
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT TOP 1 usuario, senha
                FROM sefaz_credenciais
                ORDER BY id DESC
            """)
            row = fetch_one_as_dict(cur)
            if not row:
                raise Exception("Nenhuma credencial SEFAZ cadastrada.")
            return row
        finally:
            conn.close()