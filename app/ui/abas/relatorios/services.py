# -*- coding: utf-8 -*-
"""
SefazService — acessa o sistema SEFAZ via Selenium,
baixa os XLS de inscrição e renovação e salva no banco.
"""
import io
import os
import time
import traceback
from datetime import datetime
from typing import Callable, Optional

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

from services.credenciais_service import SefazRepository

# ── Importação RELATIVA do repositório ───────────────────────────────────────
# Garante que o mesmo RelatoriosRepository.py deste pacote é usado,
# independente de como o Python resolve o sys.path.
from .RelatoriosRepository import RelatoriosRepository


class SefazService:

    def __init__(self,
                 pasta_download:   str,
                 pasta_relatorios: str,
                 usuario:          str = "sistema",
                 log_cb:           Optional[Callable] = None):

        self.pasta_download   = pasta_download
        self.pasta_relatorios = pasta_relatorios
        self.usuario          = usuario
        self.log              = log_cb or (lambda msg, t="info": print(f"[{t.upper()}] {msg}"))

        # Conecta ao banco logo na inicialização — erro aqui é visível imediatamente
        try:
            self.repo = RelatoriosRepository()
            self.log("✓ Banco conectado (relatorios_sefaz pronta).", "sucesso")
        except Exception as exc:
            self.log(f"ERRO CRÍTICO: falha ao conectar ao banco — {exc}", "erro")
            raise

    # ── Método principal ──────────────────────────────────────────────────────
    def gerar_relatorios(self,
                         municipios:  list,
                         data_inicio: str,
                         data_fim:    str,
                         progress_cb: Optional[Callable] = None):
        """
        Para cada município da lista:
          1. Navega no SEFAZ via Selenium
          2. Baixa XLS de inscrição e renovação
          3. Salva no banco (relatorios_sefaz)
        """
        os.makedirs(self.pasta_download, exist_ok=True)

        options = webdriver.EdgeOptions()
        options.add_argument("--start-maximized")
        options.add_experimental_option(
            "prefs", {"download.default_directory": self.pasta_download}
        )
        driver = webdriver.Edge(options=options)

        try:
            # ── Login ─────────────────────────────────────────────────────────
            self.log("Buscando credenciais SEFAZ...", "info")
            try:
                cred = SefazRepository().obter_credencial()
                self.log(f"Credencial: {cred['usuario']}", "info")
            except Exception as exc:
                self.log(f"ERRO credencial: {exc}", "erro")
                raise

            self.log("Abrindo sistema SEFAZ...", "info")
            driver.get("http://sistemas.sefaz.am.gov.br/gcc/entrada.do")
            time.sleep(3)

            try:
                driver.find_element(By.ID, "username").send_keys(cred["usuario"])
                driver.find_element(By.ID, "password").send_keys(cred["senha"])
                driver.find_element(By.NAME, "submit").click()
                time.sleep(4)
                self.log("Login realizado.", "sucesso")
            except Exception as exc:
                self.log(f"ERRO login: {exc}", "erro")
                raise

            # ── Loop municípios ───────────────────────────────────────────────
            total  = len(municipios)
            salvos = 0
            erros  = 0

            for idx, (nome, codigo) in enumerate(municipios, 1):
                if progress_cb:
                    progress_cb(idx, total, nome)

                self.log(f"[{idx}/{total}] {nome}", "info")

                try:
                    self._abrir_menu(driver)
                    self._selecionar_municipio(driver, codigo)

                    # Inscrição
                    self.log(f"  → XLS INSCRICAO...", "info")
                    self._set_datas(driver, data_inicio, data_fim, "inscricao")
                    xls_insc = self._baixar_xls(driver, nome, "INSCRICAO")
                    self.log(f"  ✓ INSCRICAO {len(xls_insc):,} bytes", "info")

                    # Renovação
                    self.log(f"  → XLS RENOVACAO...", "info")
                    self._set_datas(driver, data_inicio, data_fim, "renovacao")
                    xls_renov = self._baixar_xls(driver, nome, "RENOVACAO")
                    self.log(f"  ✓ RENOVACAO {len(xls_renov):,} bytes", "info")

                    # Contagem de linhas
                    total_insc  = self._contar_linhas(xls_insc)
                    total_renov = self._contar_linhas(xls_renov)
                    self.log(f"  Insc={total_insc}  Renov={total_renov}", "info")

                    # ── Gravar no banco ───────────────────────────────────────
                    self.log("  Gravando no banco...", "info")
                    try:
                        rec_id = self.repo.salvar(
                            municipio   = nome,
                            periodo_ini = datetime.strptime(data_inicio, "%d/%m/%Y").date(),
                            periodo_fim = datetime.strptime(data_fim,    "%d/%m/%Y").date(),
                            total_insc  = total_insc,
                            total_renov = total_renov,
                            usuario     = self.usuario,
                            xls_insc    = xls_insc,
                            xls_renov   = xls_renov,
                        )
                        self.log(
                            f"  ✓ Salvo no banco id={rec_id} "
                            f"(Insc={total_insc} Renov={total_renov})",
                            "sucesso",
                        )
                        salvos += 1
                    except Exception as exc_db:
                        self.log(f"  ✕ ERRO AO SALVAR NO BANCO: {exc_db}", "erro")
                        self.log(traceback.format_exc(), "erro")
                        erros += 1
                        # continua para o próximo município

                except Exception as exc:
                    self.log(f"  ✕ ERRO em {nome}: {exc}", "erro")
                    self.log(traceback.format_exc(), "erro")
                    erros += 1

            # ── Resumo ────────────────────────────────────────────────────────
            tipo_log = "sucesso" if erros == 0 else "info"
            self.log(
                f"Concluído — {salvos} salvo(s) no banco | {erros} erro(s)",
                tipo_log,
            )

        finally:
            driver.quit()

    # ── Helpers Selenium ──────────────────────────────────────────────────────
    def _abrir_menu(self, driver):
        driver.find_element(By.ID, "oCMenu___GCC2300").click()
        time.sleep(1)
        driver.find_element(By.ID, "oCMenu___GCC1003").click()
        time.sleep(1)
        driver.find_element(
            By.XPATH, '//*[@id="produtorRuralTOA.csTipoImpressao"]/option[2]'
        ).click()

    def _selecionar_municipio(self, driver, codigo: str):
        driver.find_element(
            By.XPATH, f'//*[@id="idMunicipio"]/option[@value="{codigo}"]'
        ).click()

    def _set_datas(self, driver, ini: str, fim: str, tipo: str):
        mapa = {
            "inscricao": (
                "formProdutorRural_produtorRuralTOA_dtInicialInscricao",
                "formProdutorRural_produtorRuralTOA_dtFinalInscricao",
            ),
            "renovacao": (
                "formProdutorRural_produtorRuralTOA_dtInicialRenovacao",
                "formProdutorRural_produtorRuralTOA_dtFinalRenovacao",
            ),
        }
        id_ini, id_fim = mapa[tipo]
        for field_id, valor in ((id_ini, ini), (id_fim, fim)):
            campo = driver.find_element(By.ID, field_id)
            campo.clear()
            campo.send_keys(valor)
            time.sleep(0.3)
        driver.find_element(By.TAG_NAME, "body").click()
        time.sleep(0.3)

    def _baixar_xls(self, driver, municipio: str, tipo: str) -> bytes:
        """Clica em imprimir e aguarda o XLS aparecer na pasta de download."""
        # Limpa XLS anteriores
        for f in os.listdir(self.pasta_download):
            if f.endswith(".xls"):
                os.remove(os.path.join(self.pasta_download, f))

        driver.find_element(By.ID, "imprimir").click()

        deadline = time.time() + 60
        while time.time() < deadline:
            arquivos = [f for f in os.listdir(self.pasta_download)
                        if f.endswith(".xls")]
            if arquivos:
                caminho = os.path.join(self.pasta_download, arquivos[0])
                time.sleep(1)          # aguarda escrita completa
                with open(caminho, "rb") as fh:
                    dados = fh.read()
                os.remove(caminho)
                return dados
            time.sleep(1)

        raise TimeoutError(
            f"Timeout: download {tipo} de {municipio} não concluído em 60s.")

    @staticmethod
    def _contar_linhas(xls_bytes: bytes) -> int:
        try:
            df = pd.read_excel(io.BytesIO(xls_bytes), skiprows=6)
            return max(0, len(df) - 1)
        except Exception:
            return 0


class RelatorioAnaliseService:
    @staticmethod
    def gerar_totais(pasta_relatorios: str):
        dados = []
        for arq in os.listdir(pasta_relatorios):
            if arq.endswith(".xls"):
                caminho = os.path.join(pasta_relatorios, arq)
                try:
                    df = pd.read_excel(caminho, skiprows=6)
                    dados.append({"ARQUIVO": arq.replace(".xls", ""),
                                  "TOTAL":   len(df)})
                except Exception:
                    pass
        if dados:
            pd.DataFrame(dados).to_excel(
                os.path.join(pasta_relatorios, "totais_relatorios.xlsx"),
                index=False,
            )