# -*- coding: utf-8 -*-
"""
Controller — filtragem, ordenação e paginação dos dados de consulta.
Pertence ao módulo bancoantigo (app/ui/abas/bancoantigo/controller.py).
"""

from datetime import datetime, date, timedelta
from typing import Optional

from .services import ConsultaBancoService

REGISTROS_POR_PAGINA = 100


def _parse_data(texto: str) -> Optional[date]:
    try:
        return datetime.strptime(texto.strip(), "%d/%m/%Y").date()
    except Exception:
        return None


def _extrair_data(val) -> Optional[date]:
    if not val:
        return None
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, date):
        return val
    s = str(val).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt).date()
        except Exception:
            pass
    return None


class ConsultaBancoController:

    def __init__(self):
        self.service = ConsultaBancoService()
        self._dados_completos: list = []
        self._dados_filtrados: list = []
        self._pagina_atual: int = 0
        self._total_paginas: int = 1
        self._sort_col: str = ""
        self._sort_rev: bool = False

    # ── Carregamento ──────────────────────────────────────────────────────────
    def carregar(self) -> list:
        self._dados_completos = self.service.buscar_todos()
        self._aplicar_filtros({})
        return self._dados_completos

    def carregar_municipios(self) -> list:
        return self.service.buscar_municipios()

    # ── Filtros ───────────────────────────────────────────────────────────────
    def filtrar(self, filtros: dict) -> dict:
        if not isinstance(filtros, dict):
            filtros = {}
        self._aplicar_filtros(filtros)
        return self._pagina_info()

    def _aplicar_filtros(self, f: dict):
        dados = self._dados_completos

        cpf = "".join(c for c in f.get("cpf", "") if c.isdigit())
        if cpf:
            dados = [
                r for r in dados
                if cpf in "".join(c for c in str(r.get("cpf") or "") if c.isdigit())
            ]

        analise = f.get("analise", "TODOS")
        if analise and analise != "TODOS":
            dados = [
                r for r in dados
                if str(r.get("analise") or "").upper() == analise.upper()
            ]

        municipio = f.get("municipio", "TODOS")
        if municipio and municipio != "TODOS":
            dados = [
                r for r in dados
                if str(r.get("unloc") or "").strip() == municipio
            ]

        lancou = f.get("lancou", "")
        if lancou:
            bl = lancou.lower()
            dados = [r for r in dados if bl in str(r.get("lancou") or "").lower()]

        envio = f.get("envio", "TODOS")
        if envio == "Com envio":
            dados = [
                r for r in dados
                if r.get("envio")
                and str(r["envio"]).strip() not in ("", "0", "0000-00-00", "None")
            ]
        elif envio == "Sem envio":
            dados = [
                r for r in dados
                if not r.get("envio")
                or str(r["envio"]).strip() in ("", "0", "0000-00-00", "None")
            ]

        lancado = f.get("lancado", "TODOS")
        if lancado == "Sim":
            dados = [r for r in dados if r.get("lancou") and str(r["lancou"]).strip() != ""]
        elif lancado == "Não":
            dados = [r for r in dados if not r.get("lancou") or str(r["lancou"]).strip() == ""]

        periodo  = f.get("periodo", "TODOS")
        data_ini = None
        data_fim = None
        hoje     = date.today()

        if periodo == "Hoje":
            data_ini = data_fim = hoje
        elif periodo == "Esta semana":
            data_ini = hoje - timedelta(days=hoje.weekday())
            data_fim = hoje
        elif periodo == "Este mês":
            data_ini = hoje.replace(day=1)
            data_fim = hoje
        elif periodo == "Este ano":
            data_ini = hoje.replace(month=1, day=1)
            data_fim = hoje
        elif periodo == "Personalizado":
            data_ini = _parse_data(f.get("data_ini", ""))
            data_fim = _parse_data(f.get("data_fim", ""))

        if data_ini or data_fim:
            filtrados = []
            for r in dados:
                d = _extrair_data(r.get("datas"))
                if d is None:
                    continue
                if data_ini and d < data_ini:
                    continue
                if data_fim and d > data_fim:
                    continue
                filtrados.append(r)
            dados = filtrados

        busca = f.get("busca", "")
        if busca:
            bl     = busca.lower()
            campos = ("nome", "cpf", "unloc", "memorando", "motivo", "lancou")
            dados  = [r for r in dados if any(bl in str(r.get(c) or "").lower() for c in campos)]

        if self._sort_col:
            dados = sorted(
                dados,
                key=lambda r: self._sort_key(r, self._sort_col),
                reverse=self._sort_rev,
            )

        self._dados_filtrados = dados
        self._pagina_atual    = 0
        self._total_paginas   = max(
            1, (len(dados) + REGISTROS_POR_PAGINA - 1) // REGISTROS_POR_PAGINA
        )

    def _sort_key(self, r, col):
        val = r.get(col)
        if val is None:
            return ""
        d = _extrair_data(val)
        if d:
            return d
        try:
            return float(val)
        except Exception:
            pass
        return str(val).lower()

    # ── Ordenação ─────────────────────────────────────────────────────────────
    def ordenar(self, coluna: str) -> dict:
        if self._sort_col == coluna:
            self._sort_rev = not self._sort_rev
        else:
            self._sort_col = coluna
            self._sort_rev = False
        self._dados_filtrados.sort(
            key=lambda r: self._sort_key(r, coluna),
            reverse=self._sort_rev,
        )
        self._pagina_atual = 0
        return self._pagina_info()

    # ── Paginação ─────────────────────────────────────────────────────────────
    def primeira_pagina(self) -> dict:
        self._pagina_atual = 0
        return self._pagina_info()

    def ultima_pagina(self) -> dict:
        self._pagina_atual = self._total_paginas - 1
        return self._pagina_info()

    def pagina_anterior(self) -> dict:
        if self._pagina_atual > 0:
            self._pagina_atual -= 1
        return self._pagina_info()

    def proxima_pagina(self) -> dict:
        if self._pagina_atual < self._total_paginas - 1:
            self._pagina_atual += 1
        return self._pagina_info()

    def _pagina_info(self) -> dict:
        inicio = self._pagina_atual * REGISTROS_POR_PAGINA
        fim    = inicio + REGISTROS_POR_PAGINA
        total  = len(self._dados_filtrados)
        return {
            "pagina":         self._dados_filtrados[inicio:fim],
            "pagina_atual":   self._pagina_atual,
            "total_paginas":  self._total_paginas,
            "total_filtrado": total,
            "total_banco":    len(self._dados_completos),
            "inicio":         inicio,
            "fim":            min(fim, total),
        }

    def total_banco(self) -> int:
        return len(self._dados_completos)