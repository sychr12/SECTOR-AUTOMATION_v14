# -*- coding: utf-8 -*-
from services.database import get_connection


class AnaliseapRepository:

    def salvar_inscricao(self, nome, cpf, municipio, memorando, tipo, usuario):
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO analise_ap (nome, cpf, municipio, memorando, tipo, usuario)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (nome, cpf, municipio, memorando, tipo, usuario))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def salvar_devolucao(self, nome, cpf, municipio, memorando, motivo, usuario):
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO analise_ap (nome, cpf, municipio, memorando, tipo, motivo, usuario)
                VALUES (?, ?, ?, ?, 'DEVOLUÇÃO', ?, ?)
            """, (nome, cpf, municipio, memorando, motivo, usuario))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def consultar_analises(self, conexoes, filtros, params):
        todos_dados = []
        where = f"WHERE {' AND '.join(filtros)}" if filtros else ""

        sql = f"""
            SELECT nome, cpf, municipio, memorando, tipo,
                   CAST(motivo AS VARCHAR(MAX)) AS motivo,
                   usuario, criado_em
            FROM analise_ap
            {where}
            ORDER BY criado_em DESC
        """

        for conectar in conexoes:
            conn = conectar()
            cur = conn.cursor()
            cur.execute(sql, params)
            for row in cur.fetchall():
                todos_dados.append(tuple(row))
            cur.close()
            conn.close()

        return todos_dados