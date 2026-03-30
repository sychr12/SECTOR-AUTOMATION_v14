# -*- coding: utf-8 -*-
"""
Services — conexão e consultas aos dois bancos (somente leitura).

  • MySQL      → tabela dev      (banco CPP / legado)
  • PostgreSQL → tabela analises (banco novo)
"""

import threading
import time
import socket

import mysql.connector
from mysql.connector import errorcode
from psycopg2.extras import RealDictCursor

from app.services.database import get_connection

# ── Configuração MySQL ────────────────────────────────────────────────────────
_MYSQL_CONFIG = {
    "host":            "10.46.1.25",
    "user":            "cpp",
    "password":        "@cppbanco01",
    "database":        "bancocpp",
    "charset":         "utf8mb4",
    "use_unicode":     True,
    "connect_timeout": 15,          # Aumentado de 8 para 15 segundos
    "autocommit":      True,
    "raise_on_warnings": False,
}


class ConsultaBancoService:
    """
    Gerencia consultas somente leitura nos dois bancos em paralelo.
    """

    # ── MySQL ─────────────────────────────────────────────────────────────────

    def _conectar_mysql(self):
        """
        Tenta conectar ao MySQL com retry automático.
        """
        max_retries = 2
        retry_delay = 2
        
        for attempt in range(max_retries + 1):
            try:
                return mysql.connector.connect(**_MYSQL_CONFIG)
            except mysql.connector.Error as err:
                if attempt == max_retries:
                    # Última tentativa, relança o erro
                    raise
                print(f"Tentativa {attempt + 1} falhou: {err}. Tentando novamente em {retry_delay}s...")
                time.sleep(retry_delay)
        
        raise Exception("Não foi possível conectar ao MySQL após múltiplas tentativas")

    def buscar_todos(self) -> list:
        """
        Retorna todos os registros da tabela dev (MySQL/CPP),
        do mais recente ao mais antigo.
        """
        conn = None
        cur = None
        try:
            conn = self._conectar_mysql()
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT
                    id, nome, cpf, unloc, memorando,
                    datas, analise, motivo, envio, lancou
                FROM dev
                ORDER BY id DESC
            """)
            return cur.fetchall()
        except mysql.connector.Error as err:
            if err.errno == errorcode.CR_CONN_HOST_ERROR:
                raise Exception(
                    f"Não foi possível conectar ao servidor MySQL ({_MYSQL_CONFIG['host']}). "
                    f"Verifique se o servidor está online e o firewall permite acesso à porta 3306."
                )
            elif err.errno == errorcode.CR_SERVER_LOST:
                raise Exception(
                    f"Conexão perdida com o servidor MySQL. "
                    f"Verifique a rede e se o servidor está respondendo."
                )
            else:
                raise Exception(f"Erro MySQL: {err}")
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def buscar_municipios(self) -> list:
        """Retorna lista ordenada de municípios distintos presentes no MySQL."""
        conn = None
        cur = None
        try:
            conn = self._conectar_mysql()
            cur = conn.cursor()
            cur.execute("""
                SELECT DISTINCT unloc
                FROM   dev
                WHERE  unloc IS NOT NULL AND unloc != ''
                ORDER  BY unloc
            """)
            return [row[0] for row in cur.fetchall()]
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    # ── PostgreSQL ────────────────────────────────────────────────────────────

    def buscar_todos_pg(self) -> list:
        """
        Retorna todos os registros do PostgreSQL (banco novo),
        com colunas normalizadas para as mesmas chaves do MySQL.
        """
        conn = None
        try:
            conn = get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT
                        a.id,
                        a.nome_pdf       AS nome,
                        a.cpf,
                        a.unloc,
                        a.memorando,
                        a.criado_em      AS datas,
                        a.status         AS analise,
                        a.urgencia       AS motivo,
                        l.lancado_por    AS lancou,
                        a.usuario        AS envio,
                        a.status,
                        a.caminho_pdf
                    FROM  analises a
                    LEFT  JOIN lancamentos l ON l.nome_pdf = a.nome_pdf
                    ORDER BY a.criado_em DESC
                """)
                rows = cur.fetchall()
            result = []
            for r in rows:
                d = dict(r)
                if d.get("datas") and hasattr(d["datas"], "strftime"):
                    d["datas"] = d["datas"].strftime("%d/%m/%Y %H:%M")
                d["_origem"] = "pg"
                result.append(d)
            return result
        except Exception as e:
            # Não relança erro PostgreSQL para não quebrar a consulta MySQL
            # O erro será capturado no método buscar_todos_ambos
            raise
        finally:
            if conn:
                conn.close()

    # ── Ambos em paralelo ─────────────────────────────────────────────────────

    def buscar_todos_ambos(self) -> dict:
        """
        Consulta MySQL e PostgreSQL em paralelo.

        Retorna:
            {
                "cpp": [ ...registros MySQL... ],
                "pg":  [ ...registros PostgreSQL... ],
                "erros": {
                    "cpp": "mensagem ou None",
                    "pg":  "mensagem ou None",
                }
            }
        """
        resultado = {"cpp": [], "pg": [], "erros": {"cpp": None, "pg": None}}

        def _buscar_cpp():
            try:
                resultado["cpp"] = self.buscar_todos()
            except Exception as exc:
                resultado["erros"]["cpp"] = str(exc)
                print(f"Erro MySQL: {exc}")

        def _buscar_pg():
            try:
                resultado["pg"] = self.buscar_todos_pg()
            except Exception as exc:
                resultado["erros"]["pg"] = str(exc)
                print(f"Erro PostgreSQL: {exc}")

        t1 = threading.Thread(target=_buscar_cpp, daemon=True)
        t2 = threading.Thread(target=_buscar_pg,  daemon=True)
        t1.start()
        t2.start()
        t1.join(timeout=30)  # Timeout de 30 segundos
        t2.join(timeout=30)

        return resultado

    def buscar_por_cpf(self, cpf: str) -> dict:
        """
        Busca um CPF específico nos dois bancos em paralelo.

        Aceita CPF formatado (000.000.000-00) ou só dígitos.

        Retorna o mesmo formato de buscar_todos_ambos(),
        filtrado pelo CPF informado.
        """
        cpf_digits = "".join(c for c in (cpf or "") if c.isdigit())

        resultado = {"cpp": [], "pg": [], "erros": {"cpp": None, "pg": None}}

        def _buscar_cpp():
            try:
                todos = self.buscar_todos()
                resultado["cpp"] = [
                    r for r in todos
                    if "".join(
                        c for c in str(r.get("cpf") or "") if c.isdigit()
                    ) == cpf_digits
                ]
            except Exception as exc:
                resultado["erros"]["cpp"] = str(exc)
                print(f"Erro MySQL: {exc}")

        def _buscar_pg():
            try:
                conn = get_connection()
                try:
                    with conn.cursor(cursor_factory=RealDictCursor) as cur:
                        cur.execute("""
                            SELECT
                                a.id,
                                a.nome_pdf       AS nome,
                                a.cpf,
                                a.unloc,
                                a.memorando,
                                a.criado_em      AS datas,
                                a.status         AS analise,
                                a.urgencia       AS motivo,
                                l.lancado_por    AS lancou,
                                a.usuario        AS envio,
                                a.status,
                                a.caminho_pdf
                            FROM  analises a
                            LEFT  JOIN lancamentos l ON l.nome_pdf = a.nome_pdf
                            WHERE a.cpf = %s
                            ORDER BY a.criado_em DESC
                        """, (cpf_digits,))
                        rows = cur.fetchall()
                    pg_result = []
                    for r in rows:
                        d = dict(r)
                        if d.get("datas") and hasattr(d["datas"], "strftime"):
                            d["datas"] = d["datas"].strftime("%d/%m/%Y %H:%M")
                        d["_origem"] = "pg"
                        pg_result.append(d)
                    resultado["pg"] = pg_result
                finally:
                    conn.close()
            except Exception as exc:
                resultado["erros"]["pg"] = str(exc)
                print(f"Erro PostgreSQL: {exc}")

        t1 = threading.Thread(target=_buscar_cpp, daemon=True)
        t2 = threading.Thread(target=_buscar_pg,  daemon=True)
        t1.start()
        t2.start()
        t1.join(timeout=30)
        t2.join(timeout=30)

        return resultado