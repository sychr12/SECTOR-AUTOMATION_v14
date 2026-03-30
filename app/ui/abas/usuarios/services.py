# -*- coding: utf-8 -*-
from datetime import datetime
from typing import List


class ConfiguracaoUsuariosService:
    def get_perfis(self) -> List[str]:
        return ["Todos", "administrador", "chefe", "usuario"]


class HistoricoUsuariosService:
    def registrar_operacao(self, usuario: str, tipo: str, descricao: str):
        print(
            f"[HISTORICO] {datetime.utcnow().isoformat()} | "
            f"{usuario} | {tipo.upper()} | {descricao}"
        )