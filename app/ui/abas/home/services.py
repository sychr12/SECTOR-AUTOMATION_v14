# -*- coding: utf-8 -*-
"""
Serviços para Dashboard — busca dados reais do banco SQL Server.

Adaptado para SQL Server:
  - TRUE → 1
  - LIMIT → TOP
  - DATE() → CAST() ou CONVERT()
  - %s → ?
"""

import os
from datetime import datetime, timedelta
from typing import List, Tuple

from .models import DashboardStats, UsuarioAtivo, AtividadeRecente


def _query_one(conectar_bd, sql: str, params=None):
    """
    Executa uma query que retorna uma única linha.
    Usa cursor padrão para acessar por índice.
    """
    conn = None
    try:
        conn = conectar_bd()
        cur = conn.cursor()
        cur.execute(sql, params or ())
        row = cur.fetchone()
        cur.close()
        # Se vier como dict, converter para tupla
        if isinstance(row, dict):
            row = tuple(row.values())
        return row, None
    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        return None, str(e)
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def _query_all(conectar_bd, sql: str, params=None):
    """
    Executa uma query que retorna várias linhas.
    Usa cursor padrão para acessar por índice.
    """
    conn = None
    try:
        conn = conectar_bd()
        cur = conn.cursor()
        cur.execute(sql, params or ())
        rows = cur.fetchall()
        cur.close()
        # Se vier como lista de dicts, converter para tuplas
        if rows and isinstance(rows[0], dict):
            rows = [tuple(r.values()) for r in rows]
        return rows, None
    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        return [], str(e)
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


class DashboardService:
    """Serviço para buscar dados do dashboard."""

    # ── Estatísticas ─────────────────────────────────────────────────────────
    @staticmethod
    def obter_estatisticas(conectar_bd) -> DashboardStats:
        """Obtém estatísticas gerais usando conexões isoladas por query."""
        stats = DashboardStats()

        # 1. Total de usuários ativos
        row, err = _query_one(
            conectar_bd,
            "SELECT COUNT(*) FROM requerentes WHERE ativo = 1"
        )
        if err:
            row, _ = _query_one(conectar_bd,
                                "SELECT COUNT(*) FROM requerentes")
        stats.total_usuarios = row[0] if row else 0

        # 2. Usuários online (últimos 5 min)
        cinco_min = datetime.now() - timedelta(minutes=5)
        row, err = _query_one(
            conectar_bd,
            "SELECT COUNT(*) FROM requerentes "
            "WHERE ultimo_acesso >= ? AND ativo = 1",
            (cinco_min,)
        )
        if err:
            print(f"[Dashboard] usuários online: {err}")
        stats.usuarios_online  = row[0] if row else 0
        stats.usuarios_offline = stats.total_usuarios - stats.usuarios_online

        # 3. Relatórios gerados hoje
        hoje = datetime.now().date()
        row, err = _query_one(
            conectar_bd,
            "SELECT COUNT(*) FROM memorandos WHERE CAST(criado_em AS DATE) = ?",
            (hoje,)
        )
        if err:
            print(f"[Dashboard] relatórios hoje: {err}")
        stats.relatorios_gerados_hoje = row[0] if row else 0

        # 4. Relatórios gerados este mês
        inicio_mes = datetime.now().replace(day=1).date()
        row, err = _query_one(
            conectar_bd,
            "SELECT COUNT(*) FROM memorandos WHERE CAST(criado_em AS DATE) >= ?",
            (inicio_mes,)
        )
        if err:
            print(f"[Dashboard] relatórios mês: {err}")
        stats.relatorios_gerados_mes = row[0] if row else 0

        # 5. Total de relatórios
        row, err = _query_one(conectar_bd, "SELECT COUNT(*) FROM memorandos")
        if err:
            print(f"[Dashboard] total memorandos: {err}")
        stats.relatorios_gerados_total = row[0] if row else 0

        # 6. Total de inscrições — tabela inscricoes
        row, err = _query_one(conectar_bd, "SELECT COUNT(*) FROM inscricoes")
        if err:
            print(f"[Dashboard] inscricoes: {err}")
        stats.total_inscricoes = row[0] if row else 0

        # 7. Total de devoluções — tabela devolucoes
        row, err = _query_one(conectar_bd, "SELECT COUNT(*) FROM devolucoes")
        if err:
            print(f"[Dashboard] devolucoes: {err}")
        stats.total_devolucoes = row[0] if row else 0

        # 8. Último acesso
        row, err = _query_one(
            conectar_bd,
            "SELECT MAX(ultimo_acesso) FROM requerentes"
        )
        if err:
            print(f"[Dashboard] ultimo acesso: {err}")
        if row and row[0]:
            val = row[0]
            stats.ultimo_acesso = (
                val.strftime("%d/%m/%Y %H:%M:%S")
                if isinstance(val, datetime)
                else str(val)
            )
        else:
            stats.ultimo_acesso = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        return stats

    # ── Usuários ativos ───────────────────────────────────────────────────────
    @staticmethod
    def obter_usuarios_ativos(conectar_bd) -> List[UsuarioAtivo]:
        """Usuários que acessaram nos últimos 5 minutos."""
        cinco_min = datetime.now() - timedelta(minutes=5)

        rows, err = _query_all(
            conectar_bd,
            """
            SELECT TOP 20
                   username,
                   COALESCE(nome_completo, username) AS nome,
                   perfil,
                   ultimo_acesso
            FROM   requerentes
            WHERE  ultimo_acesso >= ? AND ativo = 1
            ORDER  BY ultimo_acesso DESC
            """,
            (cinco_min,)
        )
        if err:
            print(f"[Dashboard] usuarios ativos: {err}")
            return []

        usuarios = []
        for row in rows:
            username      = row[0] or "usuario"
            nome          = row[1] or username
            perfil        = row[2] or "usuario"
            ultimo_acesso = row[3]

            if ultimo_acesso:
                if isinstance(ultimo_acesso, str):
                    try:
                        ultimo = datetime.fromisoformat(
                            ultimo_acesso.replace("Z", "+00:00"))
                    except Exception:
                        ultimo = datetime.now()
                else:
                    ultimo = ultimo_acesso

                delta   = datetime.now() - ultimo
                minutos = int(delta.total_seconds() / 60)
                tempo   = ("Agora" if minutos < 1
                           else f"{minutos} minuto{'s' if minutos > 1 else ''}")
            else:
                ultimo = datetime.now()
                tempo  = "Agora"

            usuarios.append(UsuarioAtivo(
                username=username,
                nome=nome,
                perfil=perfil,
                ultimo_acesso=ultimo,
                tempo_online=tempo,
            ))

        return usuarios

    # ── Atividades recentes ───────────────────────────────────────────────────
    @staticmethod
    def obter_atividades_recentes(conectar_bd,
                                  limit: int = 10) -> List[AtividadeRecente]:
        """Atividades recentes das tabelas de operações."""
        atividades = []

        # 1. Memorandos
        rows, err = _query_all(
            conectar_bd,
            """
            SELECT TOP 5
                   'RELATORIO' AS tipo,
                   usuario,
                   CONCAT('Memorando ', numero, ' gerado') AS descricao,
                   criado_em
            FROM   memorandos
            WHERE  criado_em IS NOT NULL
            ORDER  BY criado_em DESC
            """
        )
        if err:
            print(f"[Dashboard] memorandos: {err}")
        for row in rows:
            a = DashboardService._criar_atividade(row, "RELATORIO", "📊")
            if a:
                atividades.append(a)

        # 2. Inscrições
        rows, err = _query_all(
            conectar_bd,
            """
            SELECT TOP 5
                   'INSCRICAO' AS tipo,
                   usuario,
                   CONCAT('Inscrição para ', unloc, ' realizada') AS descricao,
                   data_registro
            FROM   inscricoes
            WHERE  data_registro IS NOT NULL
            ORDER  BY data_registro DESC
            """
        )
        if err:
            print(f"[Dashboard] inscricoes: {err}")
        for row in rows:
            a = DashboardService._criar_atividade(row, "INSCRICAO", "📝")
            if a:
                atividades.append(a)

        # 3. Devoluções
        rows, err = _query_all(
            conectar_bd,
            """
            SELECT TOP 5
                   'DEVOLUCAO' AS tipo,
                   usuario,
                   CONCAT('Devolução - ', COALESCE(motivo, '')) AS descricao,
                   data_registro
            FROM   devolucoes
            WHERE  data_registro IS NOT NULL
            ORDER  BY data_registro DESC
            """
        )
        if err:
            print(f"[Dashboard] devolucoes: {err}")
        for row in rows:
            a = DashboardService._criar_atividade(row, "DEVOLUCAO", "📤")
            if a:
                atividades.append(a)

        # 4. Novos cadastros
        rows, err = _query_all(
            conectar_bd,
            """
            SELECT TOP 5
                   'CADASTRO' AS tipo,
                   username   AS usuario,
                   CONCAT('Usuário ', username, ' cadastrado') AS descricao,
                   data_criacao
            FROM   requerentes
            WHERE  data_criacao IS NOT NULL
            ORDER  BY data_criacao DESC
            """
        )
        if err:
            print(f"[Dashboard] cadastros: {err}")
        for row in rows:
            a = DashboardService._criar_atividade(row, "CADASTRO", "➕")
            if a:
                atividades.append(a)

        atividades.sort(key=lambda x: x.data_hora, reverse=True)
        return atividades[:limit]

    # ── Gráfico mensal ────────────────────────────────────────────────────────
    @staticmethod
    def obter_grafico_relatorios_mensal(
            conectar_bd) -> Tuple[List[str], List[int]]:
        """Dados do gráfico de relatórios dos últimos 30 dias."""
        dias   = []
        valores = []

        for i in range(29, -1, -1):
            dia = datetime.now().date() - timedelta(days=i)
            dias.append(dia.strftime("%d/%m"))

            row, err = _query_one(
                conectar_bd,
                "SELECT COUNT(*) FROM memorandos WHERE CAST(criado_em AS DATE) = ?",
                (dia,)
            )
            if err:
                print(f"[Dashboard] gráfico dia {dia}: {err}")
            valores.append(row[0] if row else 0)

        return dias, valores

    # ── Helper ────────────────────────────────────────────────────────────────
    @staticmethod
    def _criar_atividade(row, tipo_padrao: str,
                         icone_padrao: str):
        """Cria AtividadeRecente a partir de uma linha do banco."""
        try:
            if len(row) < 4:
                return None

            tipo      = str(row[0]) if row[0] else tipo_padrao
            usuario   = str(row[1]) if row[1] else "Sistema"
            descricao = str(row[2]) if row[2] else f"Operação {tipo}"
            data_hora = row[3]

            if isinstance(data_hora, str):
                try:
                    data_hora = datetime.fromisoformat(
                        data_hora.replace("Z", "+00:00"))
                except Exception:
                    data_hora = datetime.now()
            elif not isinstance(data_hora, datetime):
                data_hora = datetime.now()

            icones = {
                "RELATORIO": "📊", "INSCRICAO": "📝",
                "RENOVACAO": "🔄", "DEVOLUCAO": "📤",
                "CADASTRO":  "➕", "LOGIN":     "🔓",
                "LOGOUT":    "🔒",
            }

            return AtividadeRecente(
                tipo=tipo,
                usuario=usuario,
                descricao=descricao,
                data_hora=data_hora,
                icone=icones.get(tipo.upper(), icone_padrao),
            )

        except Exception as e:
            print(f"[Dashboard] _criar_atividade: {e}")
            return None