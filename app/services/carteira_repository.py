# -*- coding: utf-8 -*-
from services.database import get_connection, fetch_all_as_dict, fetch_one_as_dict


class CarteirasRepository:

    def salvar(self, registro, cpf, nome, propriedade, unloc, inicio,
               validade, endereco, atividade1, atividade2, georef,
               pdf_conteudo, foto1, foto2, foto3, usuario):
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO carteiras_digitais (
                    registro, cpf, nome, propriedade, unloc,
                    inicio, validade, endereco, atividade1,
                    atividade2, georef, pdf_conteudo,
                    foto1, foto2, foto3, usuario
                )
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (registro, cpf, nome, propriedade, unloc,
                  inicio, validade, endereco, atividade1,
                  atividade2, georef, pdf_conteudo,
                  foto1, foto2, foto3, usuario))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def listar_todos(self, limite=100):
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT TOP (?) id, nome, cpf, unloc, criado_em, usuario
                FROM carteiras_digitais
                ORDER BY criado_em DESC
            """, (limite,))
            return fetch_all_as_dict(cur)
        finally:
            conn.close()

    def buscar_com_filtros(self, termo_pesquisa="", periodo="TODOS", usuario="TODOS", limite=100):
        conn = get_connection()
        try:
            cur = conn.cursor()
            query = """
                SELECT id, nome, cpf, unloc, criado_em, usuario
                FROM carteiras_digitais
                WHERE 1=1
            """
            params = []

            if termo_pesquisa.strip():
                query += " AND (nome LIKE ? OR cpf LIKE ? OR unloc LIKE ?)"
                termo = f"%{termo_pesquisa.strip()}%"
                params.extend([termo, termo, termo])

            if periodo == "HOJE":
                query += " AND CAST(criado_em AS DATE) = CAST(GETDATE() AS DATE)"
            elif periodo == "SEMANA":
                query += " AND criado_em >= DATEADD(day, -7, GETDATE())"
            elif periodo == "MES":
                query += " AND criado_em >= DATEADD(day, -30, GETDATE())"
            elif periodo == "ANO":
                query += " AND criado_em >= DATEADD(day, -365, GETDATE())"

            if usuario != "TODOS":
                query += " AND usuario = ?"
                params.append(usuario)

            query += " ORDER BY criado_em DESC OFFSET 0 ROWS FETCH NEXT ? ROWS ONLY"
            params.append(limite)

            cur.execute(query, params)
            return fetch_all_as_dict(cur)
        finally:
            conn.close()

    def contar_total(self):
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM carteiras_digitais")
            row = cur.fetchone()
            return row[0] if row else 0
        except Exception:
            return 0
        finally:
            conn.close()

    def buscar_usuarios_unicos(self):
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT DISTINCT usuario
                FROM carteiras_digitais
                WHERE usuario IS NOT NULL
                ORDER BY usuario
            """)
            return [row[0] for row in cur.fetchall()]
        except Exception:
            return []
        finally:
            conn.close()

    def buscar_pdf_por_id(self, carteira_id):
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT nome, pdf_conteudo
                FROM carteiras_digitais
                WHERE id = ?
            """, (carteira_id,))
            return fetch_one_as_dict(cur)
        finally:
            conn.close()

    def buscar_por_id(self, carteira_id):
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM carteiras_digitais WHERE id = ?", (carteira_id,))
            return fetch_one_as_dict(cur)
        finally:
            conn.close()

    def deletar(self, carteira_id):
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM carteiras_digitais WHERE id = ?", (carteira_id,))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def atualizar(self, carteira_id, registro, cpf, nome, propriedade, unloc,
                  inicio, validade, endereco, atividade1, atividade2, georef):
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE carteiras_digitais
                SET registro=?, cpf=?, nome=?, propriedade=?, unloc=?,
                    inicio=?, validade=?, endereco=?, atividade1=?,
                    atividade2=?, georef=?
                WHERE id = ?
            """, (registro, cpf, nome, propriedade, unloc,
                  inicio, validade, endereco, atividade1,
                  atividade2, georef, carteira_id))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()