# -*- coding: utf-8 -*-
"""Utilitários para datas"""
from datetime import datetime
import calendar


class DateUtils:
    """Utilitários para manipulação de datas"""
    
    @staticmethod
    def aplicar_mascara(var, entry, aplicando_flag):
        """Aplica máscara de data DD/MM/AAAA"""
        if aplicando_flag[0]:
            return
        aplicando_flag[0] = True
        try:
            t = var.get()
            d = "".join(c for c in t if c.isdigit())[:8]
            r = (d if len(d) <= 2
                 else d[:2] + "/" + d[2:] if len(d) <= 4
                 else d[:2] + "/" + d[2:4] + "/" + d[4:])
            if r != t:
                var.set(r)
                entry.after(0, lambda: entry.icursor("end"))
        finally:
            aplicando_flag[0] = False
    
    @staticmethod
    def periodo_mes_atual():
        """Retorna primeiro e último dia do mês atual"""
        hoje = datetime.today()
        return (
            hoje.replace(day=1).strftime("%d/%m/%Y"),
            hoje.strftime("%d/%m/%Y")
        )
    
    @staticmethod
    def periodo_mes_anterior():
        """Retorna primeiro e último dia do mês anterior"""
        hoje = datetime.today()
        primeiro = hoje.replace(day=1)
        mes = primeiro.month - 1 or 12
        ano = primeiro.year if primeiro.month > 1 else primeiro.year - 1
        ultimo = calendar.monthrange(ano, mes)[1]
        return (
            f"01/{mes:02d}/{ano}",
            f"{ultimo:02d}/{mes:02d}/{ano}"
        )
    
    @staticmethod
    def periodo_ano_atual():
        """Retorna primeiro e último dia do ano atual"""
        ano = datetime.today().year
        return f"01/01/{ano}", f"31/12/{ano}"