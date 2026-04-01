# -*- coding: utf-8 -*-
"""Controller de relatórios SEFAZ."""
import os
import threading
import traceback
from typing import Callable, Optional

from .services             import SefazService
from .RelatoriosRepository import RelatoriosRepository
from .models               import MunicipioModel, PeriodoModel

# Lista completa de municípios do Amazonas
MUNICIPIOS = {
    "ALVARAES": "2",    "AMATURA": "6",     "ANAMA": "8",    "ANORI": "10",
    "APUI": "14",       "ATALAIA DO NORTE": "20",            "AUTAZES": "30",
    "BARCELOS": "40",   "BARREIRINHA": "50","BENJAMIN CONSTANT": "60",
    "BERURI": "63",     "BOA VISTA DO RAMOS": "68",          "BOCA DO ACRE": "70",
    "BORBA": "80",      "CAAPIRANGA": "83", "CANUTAMA": "90",
    "CARAUARI": "100",  "CAREIRO": "110",   "CAREIRO DA VARZEA": "115",
    "COARI": "120",     "CODAJAS": "130",   "EIRUNEPE": "140",
    "ENVIRA": "150",    "FONTE BOA": "160", "GUAJARA": "165",
    "HUMAITA": "170",   "IPIXUNA": "180",   "IRANDUBA": "185",
    "ITACOATIARA": "190","ITAMARATI": "195","ITAPIRANGA": "200",
    "JAPURA": "210",    "JURUA": "220",     "JUTAI": "230",
    "LABREA": "240",    "MANACAPURU": "250","MANAQUIRI": "255",
    "MANAUS": "260",    "MANICORE": "270",  "MARAA": "280",
    "MAUES": "290",     "NHAMUNDA": "300",  "NOVA OLINDA DO NORTE": "310",
    "NOVO AIRAO": "320","NOVO ARIPUANA": "330",              "PARINTINS": "340",
    "PAUINI": "350",    "PRESIDENTE FIGUEIREDO": "353",
    "RIO PRETO DA EVA": "356",             "SANTA IZABEL DO RIO NEGRO": "360",
    "SANTO ANTONIO DO ICA": "370",         "SAO GABRIEL DA CACHOEIRA": "380",
    "SAO PAULO DE OLIVENCA": "390",        "SAO SEBASTIAO DO UATUMA": "395",
    "SILVES": "400",    "TABATINGA": "406", "TAPAUA": "410",
    "TEFE": "420",      "TONANTINS": "423", "UARINI": "426",
    "URUCARA": "430",   "URUCURITUBA": "440",
}


class RelatoriosController:

    def __init__(self, view, usuario: str):
        self.view     = view
        self.usuario  = usuario
        self._rodando = False

        try:
            self.repo = RelatoriosRepository()
        except Exception as exc:
            print(f"[RelatoriosController] ERRO ao instanciar repositório: {exc}")
            raise

    # ── Municípios ────────────────────────────────────────────────────────────
    def obter_municipios(self) -> list:
        return [MunicipioModel(nome=n, codigo=c) for n, c in MUNICIPIOS.items()]

    def selecionar_todos_municipios(self, selecionar: bool):
        for var in self.view.municipio_vars.values():
            var.set(selecionar)

    def todos_selecionados(self) -> bool:
        if not self.view.municipio_vars:
            return False
        return all(v.get() for v in self.view.municipio_vars.values())

    def atualizar_selecao_municipio(self, nome: str, selecionado: bool):
        pass  # variáveis gerenciadas direto pelo CTkCheckBox

    def definir_periodo(self, ini: str, fim: str):
        self._periodo_ini = ini
        self._periodo_fim = fim

    def validar_configuracao(self) -> tuple:
        if not self._municipios_selecionados():
            return False, "Selecione ao menos um município."
        periodo = PeriodoModel(
            getattr(self, "_periodo_ini", ""),
            getattr(self, "_periodo_fim", ""),
        )
        return periodo.validar()

    def _municipios_selecionados(self) -> list:
        return [
            (n, MUNICIPIOS[n])
            for n, v in self.view.municipio_vars.items()
            if v.get()
        ]

    # ── Gerar relatórios (thread) ─────────────────────────────────────────────
    def gerar_relatorios(self,
                         municipios,
                         data_inicio,
                         data_fim,
                         pasta_download,
                         pasta_relatorios,
                         callback_sucesso: Callable,
                         callback_erro:    Callable,
                         progress_cb:      Optional[Callable] = None,
                         log_cb:           Optional[Callable] = None):

        if self._rodando:
            callback_erro("Já existe uma geração em andamento.")
            return

        def _run():
            self._rodando = True
            try:
                os.makedirs(pasta_download,   exist_ok=True)
                os.makedirs(pasta_relatorios, exist_ok=True)

                svc = SefazService(
                    pasta_download   = pasta_download,
                    pasta_relatorios = pasta_relatorios,
                    usuario          = self.usuario,
                    log_cb           = log_cb,
                )
                svc.gerar_relatorios(
                    municipios  = municipios,
                    data_inicio = data_inicio,
                    data_fim    = data_fim,
                    progress_cb = progress_cb,
                )
                callback_sucesso()
            except Exception as exc:
                traceback.print_exc()
                callback_erro(str(exc))
            finally:
                self._rodando = False

        threading.Thread(target=_run, daemon=True).start()

    # ── Consultas ao banco ────────────────────────────────────────────────────
    def buscar_historico(self, filtro: str = "") -> list:
        try:
            return self.repo.listar(filtro_municipio=filtro)
        except Exception as exc:
            print(f"[RelatoriosController] ERRO buscar_historico: {exc}")
            raise

    def buscar_xls(self, record_id: int):
        try:
            return self.repo.buscar_xls(record_id)
        except Exception as exc:
            print(f"[RelatoriosController] ERRO buscar_xls id={record_id}: {exc}")
            raise

    def estatisticas(self) -> dict:
        try:
            return self.repo.estatisticas()
        except Exception as exc:
            print(f"[RelatoriosController] ERRO estatisticas: {exc}")
            return {}

    def por_hora(self, dias: int = 7) -> list:
        try:
            return self.repo.por_hora(dias)
        except Exception as exc:
            print(f"[RelatoriosController] ERRO por_hora: {exc}")
            return []

    def obter_resumo(self) -> dict:
        """Resumo agregado para exibição nos componentes visuais."""
        try:
            s = self.repo.estatisticas()
            ultima = s.get("ultima")
            if ultima and hasattr(ultima, "strftime"):
                ultima_fmt = ultima.strftime("%d/%m/%Y %H:%M")
            else:
                ultima_fmt = str(ultima) if ultima else "Nunca"
            return {
                "total_arquivos":        s.get("total", 0),
                "total_registros":       (s.get("insc", 0) or 0) + (s.get("renov", 0) or 0),
                "municipios_processados": s.get("municipios", 0),
                "ultima_execucao":       ultima_fmt,
            }
        except Exception as exc:
            print(f"[RelatoriosController] ERRO obter_resumo: {exc}")
            return {
                "total_arquivos": 0,
                "total_registros": 0,
                "municipios_processados": 0,
                "ultima_execucao": "Nunca",
            }
