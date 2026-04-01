# -*- coding: utf-8 -*-
"""Utilitários para tabela de histórico"""
from datetime import datetime


class TableUtils:
    """Utilitários para manipulação da tabela de histórico"""
    
    @staticmethod
    def filtrar_rows(rows: list, ano: str, de: str, ate: str) -> list:
        """Filtra registros por ano e período"""
        resultado = []
        for r in rows:
            criado = r.get("criado_em", "")
            
            if ano and ano != "Todos":
                try:
                    ano_reg = criado.split("/")[2].split(" ")[0].strip()
                    if ano_reg != ano:
                        continue
                except Exception:
                    continue
                    
            if de and len(de) == 10:
                try:
                    d, m, a = de.split("/")
                    dt_de = datetime(int(a), int(m), int(d))
                    d2, m2, resto = criado.split("/")
                    dt_reg = datetime(int(resto[:4]), int(m2), int(d2))
                    if dt_reg < dt_de:
                        continue
                except Exception:
                    pass
                    
            if ate and len(ate) == 10:
                try:
                    d, m, a = ate.split("/")
                    dt_ate = datetime(int(a), int(m), int(d))
                    d2, m2, resto = criado.split("/")
                    dt_reg = datetime(int(resto[:4]), int(m2), int(d2))
                    if dt_reg > dt_ate:
                        continue
                except Exception:
                    pass
                    
            resultado.append(r)
        return resultado
    
    @staticmethod
    def formatar_registro(r):
        """Formata um registro para exibição na tabela"""
        criado = r.get("criado_em", "—")
        partes = criado.split(" ") if " " in criado else [criado, "—"]
        data_str = partes[0]
        hora_str = partes[1] if len(partes) > 1 else "—"
        
        try:
            ano_str = data_str.split("/")[2]
        except Exception:
            ano_str = "—"
        
        periodo = (
            f"{r.get('periodo_ini', '—').strip()}  →  "
            f"{r.get('periodo_fim', '—').strip()}"
        )
        
        return {
            "municipio": r.get("municipio", "—"),
            "ano": ano_str,
            "periodo": periodo,
            "insc": r.get("total_insc", 0),
            "renov": r.get("total_renov", 0),
            "usuario": r.get("usuario", "—"),
            "data": data_str,
            "hora": hora_str
        }