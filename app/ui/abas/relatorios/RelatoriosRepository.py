# -*- coding: utf-8 -*-
"""
<<<<<<< HEAD
Repositório PostgreSQL - tabela relatorios_sefaz.

IMPORTANTE: usa importação ABSOLUTA de services.database porque
esse módulo é sempre chamado de dentro do pacote app/, onde o
sys.path já inclui a raiz do projeto.
=======
Repositório SQL Server 2016 - tabela relatorios_sefaz.
Usa pyodbc via services.database (get_connection, fetch_all_as_dict, fetch_one_as_dict).
>>>>>>> f4a3e3b (.)
"""
import traceback
import sys
import io
from typing import Optional

<<<<<<< HEAD
# Garante que prints com Unicode nao quebrem no terminal Windows (cp1252)
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import psycopg2
from psycopg2.extras import RealDictCursor

# Importação absoluta - funciona independente de como o Python é iniciado
from services.database import get_connection
=======
# Garante que prints com Unicode não quebrem no terminal Windows
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from services.database import get_connection, fetch_all_as_dict, fetch_one_as_dict
>>>>>>> f4a3e3b (.)


class RelatoriosRepository:

    def __init__(self):
        self._garantir_tabela()

    # -- Auto-migration --------------------------------------------------------
    def _garantir_tabela(self):
        """Garante que a tabela relatorios_sefaz existe no banco SQL Server."""
        # SQL Server 2016 não tem CREATE TABLE IF NOT EXISTS — usa IF NOT EXISTS padrão
        sql = """
        IF NOT EXISTS (
            SELECT 1 FROM sysobjects
            WHERE name = 'relatorios_sefaz' AND xtype = 'U'
        )
        BEGIN
            CREATE TABLE relatorios_sefaz (
                id          INT           NOT NULL,
                municipio   VARCHAR(255)  NOT NULL,
                periodo_ini DATE          NOT NULL,
                periodo_fim DATE          NOT NULL,
                total_insc  INT           NOT NULL DEFAULT 0,
                total_renov INT           NOT NULL DEFAULT 0,
                usuario     VARCHAR(255)  NOT NULL DEFAULT '',
                xls_insc    VARBINARY(MAX) NULL,
                xls_renov   VARBINARY(MAX) NULL,
                criado_em   DATETIME      NOT NULL DEFAULT GETDATE()
            );
            CREATE INDEX idx_relatorios_sefaz_municipio
                ON relatorios_sefaz (municipio);
            CREATE INDEX idx_relatorios_sefaz_criado_em
                ON relatorios_sefaz (criado_em);
        END
        """
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(sql)
            conn.commit()
            print("[RelatoriosRepository] [OK] Tabela relatorios_sefaz garantida.")
        except Exception as exc:
            conn.rollback()
            print(f"[RelatoriosRepository] ERRO ao garantir tabela: {exc}")
            traceback.print_exc()
            raise
        finally:
            conn.close()

    # -- Salvar ----------------------------------------------------------------
    def salvar(self,
               municipio:   str,
               periodo_ini,
               periodo_fim,
               total_insc:  int,
               total_renov: int,
               usuario:     str,
               xls_insc:    Optional[bytes] = None,
               xls_renov:   Optional[bytes] = None) -> int:
<<<<<<< HEAD
        """Insere um registro de relatório SEFAZ no banco e retorna o id gerado."""
        sql = """
        INSERT INTO public.relatorios_sefaz
            (municipio, periodo_ini, periodo_fim,
             total_insc, total_renov, usuario,
             xls_insc, xls_renov, criado_em)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
        RETURNING id
        """
=======
        """Insere um registro de relatório e retorna o id gerado."""
>>>>>>> f4a3e3b (.)
        print(f"[RelatoriosRepository] Salvando -> {municipio} | "
              f"insc={total_insc} renov={total_renov} usuario='{usuario}'")

        conn = get_connection()
        try:
            cur = conn.cursor()

            # ✅ Gera próximo ID manualmente (sem IDENTITY)
            cur.execute("SELECT ISNULL(MAX(id), 0) + 1 FROM relatorios_sefaz")
            novo_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO relatorios_sefaz
                    (id, municipio, periodo_ini, periodo_fim,
                     total_insc, total_renov, usuario,
                     xls_insc, xls_renov, criado_em)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
            """, (
                novo_id,
                municipio,
                periodo_ini,
                periodo_fim,
                total_insc,
                total_renov,
                usuario,
                xls_insc,
                xls_renov,
            ))
            conn.commit()
<<<<<<< HEAD
            print(f"[RelatoriosRepository] [OK] Salvo com id={rec_id}")
            return rec_id
=======
            print(f"[RelatoriosRepository] [OK] Salvo com id={novo_id}")
            return novo_id
>>>>>>> f4a3e3b (.)
        except Exception as exc:
            conn.rollback()
            print(f"[RelatoriosRepository] ERRO ao salvar '{municipio}': {exc}")
            traceback.print_exc()
            raise
        finally:
            conn.close()

    # -- Listar histórico ------------------------------------------------------
    def listar(self, filtro_municipio: str = "", limit: int = 500) -> list:
        """Lista registros com filtro opcional por município."""
        conn = get_connection()
        try:
            cur = conn.cursor()

            if filtro_municipio.strip():
                # ✅ SQL Server usa LIKE (não ILIKE) e TOP em vez de LIMIT
                cur.execute("""
                    SELECT TOP (?)
                        id, municipio, periodo_ini, periodo_fim,
                        total_insc, total_renov, usuario, criado_em
                    FROM relatorios_sefaz
                    WHERE municipio LIKE ?
                    ORDER BY criado_em DESC
                """, (limit, f"%{filtro_municipio.strip()}%"))
            else:
                cur.execute("""
                    SELECT TOP (?)
                        id, municipio, periodo_ini, periodo_fim,
                        total_insc, total_renov, usuario, criado_em
                    FROM relatorios_sefaz
                    ORDER BY criado_em DESC
                """, (limit,))

            rows = fetch_all_as_dict(cur)

            # Formata datas para exibição
            for d in rows:
                for col in ("periodo_ini", "periodo_fim"):
                    v = d.get(col)
                    if v and hasattr(v, "strftime"):
                        d[col] = v.strftime("%d/%m/%Y")
                v = d.get("criado_em")
                if v and hasattr(v, "strftime"):
                    d["criado_em"] = v.strftime("%d/%m/%Y %H:%M")

<<<<<<< HEAD
            print(f"[RelatoriosRepository] listar() -> {len(resultado)} registro(s)")
            return resultado
=======
            print(f"[RelatoriosRepository] listar() -> {len(rows)} registro(s)")
            return rows
>>>>>>> f4a3e3b (.)

        except Exception as exc:
            print(f"[RelatoriosRepository] ERRO ao listar: {exc}")
            traceback.print_exc()
            raise
        finally:
            conn.close()

    # -- Buscar XLS para download ----------------------------------------------
    def buscar_xls(self, record_id: int) -> Optional[dict]:
        """Busca os blobs XLS de um registro pelo id."""
        print(f"[RelatoriosRepository] buscar_xls id={record_id}")
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT municipio, periodo_ini, periodo_fim,
                       xls_insc, xls_renov
                FROM relatorios_sefaz
                WHERE id = ?
            """, (record_id,))

            row = fetch_one_as_dict(cur)
            if not row:
                print(f"[RelatoriosRepository] Nenhum registro com id={record_id}")
                return None

            # Garante bytes (pyodbc pode retornar bytes ou memoryview)
            for col in ("xls_insc", "xls_renov"):
                v = row.get(col)
                if v is not None:
                    row[col] = bytes(v) if isinstance(v, memoryview) else v

            print(
                f"[RelatoriosRepository] [OK] id={record_id} "
<<<<<<< HEAD
                f"xls_insc={'sim' if d.get('xls_insc') else 'NAO'} "
                f"xls_renov={'sim' if d.get('xls_renov') else 'NAO'}"
=======
                f"xls_insc={'sim' if row.get('xls_insc') else 'NAO'} "
                f"xls_renov={'sim' if row.get('xls_renov') else 'NAO'}"
>>>>>>> f4a3e3b (.)
            )
            return row

        except Exception as exc:
            print(f"[RelatoriosRepository] ERRO buscar_xls id={record_id}: {exc}")
            traceback.print_exc()
            raise
        finally:
            conn.close()

    # -- Estatísticas ----------------------------------------------------------
    def estatisticas(self) -> dict:
        """Retorna totais agregados da tabela relatorios_sefaz."""
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT
                    COUNT(*)                        AS total,
                    COUNT(DISTINCT municipio)       AS municipios,
                    ISNULL(SUM(total_insc),  0)     AS insc,
                    ISNULL(SUM(total_renov), 0)     AS renov,
                    MAX(criado_em)                  AS ultima
                FROM relatorios_sefaz
            """)
            row = fetch_one_as_dict(cur)
            return row if row else {}
        except Exception as exc:
            print(f"[RelatoriosRepository] ERRO estatisticas: {exc}")
            return {}
        finally:
            conn.close()

<<<<<<< HEAD
    # -- Por hora (últimos N dias) ----------------------------------------------
=======
    # ── Por hora (últimos N dias) ─────────────────────────────────────────────
>>>>>>> f4a3e3b (.)
    def por_hora(self, dias: int = 7) -> list:
        """Agrupa geração de relatórios por hora nos últimos N dias."""
        conn = get_connection()
        try:
            cur = conn.cursor()
            # ✅ SQL Server: DATEADD e DATEPART em vez de date_trunc e INTERVAL
            cur.execute("""
                SELECT
                    DATEADD(HOUR, DATEDIFF(HOUR, 0, criado_em), 0) AS hora,
                    COUNT(*)                                        AS quantidade,
                    ISNULL(SUM(total_insc + total_renov), 0)        AS registros
                FROM relatorios_sefaz
                WHERE criado_em >= DATEADD(DAY, ?, GETDATE())
                GROUP BY DATEADD(HOUR, DATEDIFF(HOUR, 0, criado_em), 0)
                ORDER BY hora
            """, (-dias,))
            return fetch_all_as_dict(cur)
        except Exception as exc:
            print(f"[RelatoriosRepository] ERRO por_hora: {exc}")
            return []
        finally:
            conn.close()