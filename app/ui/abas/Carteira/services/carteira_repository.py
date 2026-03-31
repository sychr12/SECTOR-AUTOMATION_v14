# -*- coding: utf-8 -*-
"""
Repositório para a tabela carteiras_digitais (SQL Server).

Colunas reais:
    id, nome, cpf, unloc, validade, pdf, criado_em, registro, propriedade,
    inicio, endereco, atividade1, atividade2, georef, pdf_conteudo,
    foto1, foto2, foto3, usuario
"""
import re
from datetime import datetime, timedelta
from typing import Optional, List

import pyodbc
from services.database import get_connection, fetch_all_as_dict, fetch_one_as_dict


class CarteirasRepository:

    # ── Salvar ────────────────────────────────────────────────────────────────
    def salvar(
        self,
        registro:     Optional[str],
        cpf:          str,
        nome:         str,
        propriedade:  Optional[str],
        unloc:        Optional[str],
        inicio:       Optional[str],
        validade:     Optional[str],
        endereco:     Optional[str],
        atividade1:   Optional[str],
        atividade2:   Optional[str],
        georef:       Optional[str],
        pdf_conteudo: Optional[bytes],
        foto1:        Optional[bytes],
        foto2:        Optional[bytes],
        foto3:        Optional[bytes],
        usuario:      Optional[str],
    ) -> Optional[int]:
        sql = """
        INSERT INTO carteiras_digitais
            (nome, cpf, unloc, validade, pdf_conteudo,
             registro, propriedade, inicio, endereco,
             atividade1, atividade2, georef,
             foto1, foto2, foto3, usuario, criado_em)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
        SELECT SCOPE_IDENTITY() AS id;
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            # Verifica tamanho do PDF
            pdf_size = len(pdf_conteudo) if pdf_conteudo else 0
            
            # Limite máximo de 5MB para PDF
            if pdf_size > 5 * 1024 * 1024:
                raise ValueError(f"PDF muito grande ({pdf_size / (1024*1024):.1f}MB). Máximo: 5MB")
            
            cursor.execute(sql, (
                nome, cpf, unloc, validade,
                pyodbc.Binary(pdf_conteudo) if pdf_conteudo else None,
                registro, propriedade, inicio, endereco,
                atividade1, atividade2, georef,
                pyodbc.Binary(foto1) if foto1 else None,
                pyodbc.Binary(foto2) if foto2 else None,
                pyodbc.Binary(foto3) if foto3 else None,
                usuario,
            ))
            row = cursor.fetchone()
            cursor.close()
            conn.commit()
            return row[0] if row else None
        except pyodbc.Error as db_err:
            conn.rollback()
            raise Exception(f"Erro de banco de dados: {db_err}") from db_err
        except Exception as e:
            conn.rollback()
            raise Exception(f"Erro ao salvar carteira: {str(e)}") from e
        finally:
            try:
                conn.close()
            except Exception:
                pass

    # ── Buscar PDF ────────────────────────────────────────────────────────────
    def buscar_pdf_por_id(self, carteira_id: int) -> Optional[dict]:
        sql = """
        SELECT id, nome, cpf, pdf_conteudo
        FROM   carteiras_digitais
        WHERE  id = ?;
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (carteira_id,))
            row = cursor.fetchone()
            cursor.close()
            
            if not row:
                return None
                
            return {
                'id': row[0],
                'nome': row[1],
                'cpf': row[2],
                'pdf_conteudo': row[3] if isinstance(row[3], bytes) else bytes(row[3]) if row[3] else None,
            }
        except Exception:
            raise
        finally:
            conn.close()

    # ── Buscar com filtros ────────────────────────────────────────────────────
    def buscar_com_filtros(
        self,
        termo:    str  = "",
        periodo:  str  = "TODOS",
        usuario:  str  = "TODOS",
        limit:    int  = 300,
    ) -> List[dict]:
        where  = ["1=1"]
        params = []

        if termo:
            where.append(
                "(nome LIKE ? OR cpf LIKE ? OR unloc LIKE ?)")
            like = f"%{termo}%"
            params += [like, like, like]

        if periodo != "TODOS":
            agora = datetime.now()
            if periodo == "HOJE":
                ini = agora.replace(hour=0, minute=0, second=0, microsecond=0)
            elif periodo == "SEMANA":
                ini = agora - timedelta(days=7)
            elif periodo == "MES":
                ini = agora.replace(day=1, hour=0, minute=0,
                                    second=0, microsecond=0)
            elif periodo == "ANO":
                ini = agora.replace(month=1, day=1, hour=0,
                                    minute=0, second=0, microsecond=0)
            else:
                ini = None
            if ini:
                where.append("criado_em >= ?")
                params.append(ini)

        if usuario != "TODOS":
            where.append("usuario = ?")
            params.append(usuario)

        sql = f"""
        SELECT TOP (?)
               id, nome, cpf, unloc, validade,
               usuario, criado_em
        FROM   carteiras_digitais
        WHERE  {' AND '.join(where)}
        ORDER  BY criado_em DESC;
        """
        params.append(limit)

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
                    'validade': row[4],
                    'usuario': row[5],
                    'criado_em': row[6],
                })
            return registros
        except Exception:
            return []
        finally:
            conn.close()

    # ── Contar total ──────────────────────────────────────────────────────────
    def contar_total(self) -> int:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM carteiras_digitais;")
            row = cursor.fetchone()
            cursor.close()
            return row[0] if row else 0
        except Exception:
            return 0
        finally:
            conn.close()

    # ── Usuários únicos ───────────────────────────────────────────────────────
    def buscar_usuarios_unicos(self) -> List[str]:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT usuario
                FROM   carteiras_digitais
                WHERE  usuario IS NOT NULL
                ORDER  BY usuario;
            """)
            rows = cursor.fetchall()
            cursor.close()
            return [row[0] for row in rows]
        except Exception:
            return []
        finally:
            conn.close()

    def buscar_por_cpf(self, cpf: str) -> Optional[dict]:
        """Busca o último registro de carteira por CPF (busca flexível com ou sem máscara)."""
        if not cpf:
            return None

        cpf_limpo = re.sub(r"\D", "", cpf)
        if not cpf_limpo:
            return None

        sql = """
        SELECT TOP 1 id, registro, nome, cpf, propriedade, unloc, inicio, validade,
               endereco, atividade1, atividade2, georef
        FROM   carteiras_digitais
        WHERE  REPLACE(REPLACE(REPLACE(REPLACE(cpf, '.', ''), '-', ''), ' ', ''), '/', '') LIKE ?
        ORDER  BY criado_em DESC;
        """

        like = f"%{cpf_limpo}%"

        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (like,))
            row = cursor.fetchone()
            cursor.close()

            if not row:
                return None

            return {
                'id': row[0],
                'registro': row[1],
                'nome': row[2],
                'cpf': row[3],
                'propriedade': row[4],
                'unloc': row[5],
                'inicio': row[6],
                'validade': row[7],
                'endereco': row[8],
                'atividade1': row[9],
                'atividade2': row[10],
                'georef': row[11],
            }
        except Exception:
            return None
        finally:
            conn.close()