# -*- coding: utf-8 -*-
"""
Controller do módulo Anexar.

Fluxo:
  1. Busca credenciais SEFAZ na tabela sefaz_credenciais (ativo=TRUE)
  2. Busca carteiras pendentes (pdf IS NULL) de carteiras_digitais
  3. Para cada carteira:
     a. Gera PDF (frente + verso) em memória com Pillow + PyPDF2
     b. Salva em arquivo temporário
     c. Abre SIGED, busca pelo CPF, faz o upload
     d. Se sucesso → persiste PDF na coluna `pdf` do banco
  4. Loga resultado em tempo real na UI

Salvar em: app/ui/abas/Anexar/controller.py
"""
import io
import os
import sys
import tempfile
import textwrap
import time
from typing import Callable, Optional, List, Dict, Any

import PyPDF2
from PIL import Image as PILImage, ImageDraw, ImageFont
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    UnexpectedAlertPresentException,
    WebDriverException,
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.edge.options import Options

from .repository import AnexarRepository

# ---------------------------------------------------------------------------
# Configuração de paths - versão flexível
# ---------------------------------------------------------------------------
def _get_asset_path(relative_path: str) -> str:
    """Encontra o caminho correto para assets, tentando múltiplas possibilidades."""
    base_paths = [
        os.path.dirname(os.path.abspath(__file__)),  # pasta atual
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."),  # app root
        os.path.join(os.path.expanduser("~"), "Documents", "fabio jr", "SECTOR AUTOMATION"),
        os.path.join(os.path.expanduser("~"), "Documents", "SECTOR AUTOMATION_v14"),
        r"Q:\ARQUIVOS CPCPR\SECTOR AUTOMATION",
    ]
    
    for base in base_paths:
        full_path = os.path.join(base, relative_path)
        if os.path.exists(full_path):
            return full_path
    return relative_path  # fallback


ASSETS = {
    "frente": _get_asset_path(r"images\frente.png"),
    "verso":  _get_asset_path(r"images\verso.png"),
    "fonte":  _get_asset_path(r"fabio jr\CARTAO-DIGITAL\Roboto-Regular.ttf"),
}

# Fallback para fonte caso não exista
if not os.path.exists(ASSETS["fonte"]):
    # Tentar fontes comuns do sistema
    system_fonts = [
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\segoeui.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for font in system_fonts:
        if os.path.exists(font):
            ASSETS["fonte"] = font
            break

SIGED_URL = ("https://online.sefaz.am.gov.br/cas/login"
             "?service=https://sistemas.sefaz.am.gov.br/siged/cas")

# Normalização de UNLOC (igual ao APP_SETOR)
UNLOC_MAP = {
    "BAE":     "BAR",
    "MTS-ATZ": "ATZ-MTS", "MTS": "ATZ-MTS",
    "NRO-ITR": "ITR-NRO", "NRO": "ITR-NRO",
    "MTP-MNX": "MNX-MTP", "MTP": "MNX-MTP",
    "VE-LBR":  "LBR-VE",  "VE":  "LBR-VE",
    "VRC-MPU": "MPU-VRC", "VRC": "MPU-VRC",
    "BNA-PRF": "PRF-BNA", "BNA": "PRF-BNA",
    "VDL-ITR": "ITR-VDL", "VDL": "ITR-VDL",
    "RLD-HIA": "HIA-RLD", "RLD": "HIA-RLD",
    "CAN-SUL": "SUL-CAN",
    "ZL-MAO":  "MAO-ZL",  "ZL":  "MAO-ZL",
}


# ---------------------------------------------------------------------------
# Gerador de PDF
# ---------------------------------------------------------------------------
class _GeradorPDF:
    """
    Gera o PDF da carteira (frente + verso) em memória a partir
    dos dados da tabela carteiras_digitais.

    Campos usados:
      nome, cpf, registro, propriedade, unloc,
      inicio, validade, endereco,
      atividade1, atividade2, georef
    """

    LG = 540  # largura máxima para quebra de texto

    @staticmethod
    def _limitar(texto: str, n: int) -> str:
        if not texto:
            return ""
        return texto[:n - 3] + "..." if len(texto) > n else texto

    @staticmethod
    def _fmt_validade(val) -> str:
        if not val:
            return ""
        if hasattr(val, "strftime"):
            return val.strftime("%d/%m/%Y")
        return str(val)

    @staticmethod
    def _desenhar_quebrado(draw, xy, texto, fonte, largura, altura_max):
        x, y = xy
        if not texto:
            return
        for linha in textwrap.wrap(str(texto), width=largura // 9):
            if y >= altura_max:
                break
            try:
                draw.text((x, y), linha, fill=(0, 0, 0), font=fonte)
            except Exception:
                # Fallback sem fonte específica
                draw.text((x, y), linha, fill=(0, 0, 0))
            y += 40

    def gerar(self, dados: Dict[str, Any]) -> bytes:
        nome        = str(dados.get("nome", "") or "")
        cpf         = str(dados.get("cpf", "") or "")
        registro    = str(dados.get("registro", "") or "")
        propriedade = str(dados.get("propriedade", "") or "")
        unloc_raw   = str(dados.get("unloc", "") or "")
        inicio      = str(dados.get("inicio", "") or "")
        validade    = self._fmt_validade(dados.get("validade"))
        endereco    = self._limitar(str(dados.get("endereco", "") or ""), 50)
        atividade1  = str(dados.get("atividade1", "") or "")
        atividade2  = self._limitar(str(dados.get("atividade2", "") or ""), 60)
        georef      = str(dados.get("georef", "") or "")

        unloc = UNLOC_MAP.get(unloc_raw, unloc_raw)
        
        # O registro já vem formatado (ex: "PR-MAO-ZL/000123")
        unloc_label = registro if registro else f"PR-{unloc}"

        # Carregar fonte
        try:
            fonte = ImageFont.truetype(ASSETS["fonte"], 41)
            fonte_endereco = ImageFont.truetype(ASSETS["fonte"], 38)
        except Exception:
            fonte = ImageFont.load_default()
            fonte_endereco = ImageFont.load_default()

        # --- FRENTE ---
        try:
            modelo = PILImage.open(ASSETS["frente"])
        except Exception:
            # Criar imagem em branco se arquivo não existir
            modelo = PILImage.new("RGB", (1200, 900), color="white")
        
        draw = ImageDraw.Draw(modelo)

        try:
            draw.text((217, 393), registro, fill=(0, 0, 0), font=fonte)  # RP
            draw.text((95,  518), nome, fill=(0, 0, 0), font=fonte)  # Nome
            draw.text((864, 392), cpf, fill=(0, 0, 0), font=fonte)  # CPF
            draw.text((100, 660), propriedade, fill=(0, 0, 0), font=fonte)  # Propriedade
            draw.text((212, 824), unloc_label, fill=(0, 0, 0), font=fonte)  # UNLOC
            draw.text((751, 824), inicio, fill=(0, 0, 0), font=fonte)  # Início ativ.
            draw.text((1063, 825), validade, fill=(0, 0, 0), font=fonte)  # Validade
        except Exception as e:
            # Ignora erros de posicionamento
            pass

        # --- VERSO ---
        try:
            modelo_v = PILImage.open(ASSETS["verso"])
        except Exception:
            modelo_v = PILImage.new("RGB", (1200, 900), color="white")
        
        draw_v = ImageDraw.Draw(modelo_v)
        h = modelo_v.size[1]

        self._desenhar_quebrado(draw_v, (89,  285), endereco, fonte_endereco, self.LG, h)
        self._desenhar_quebrado(draw_v, (89,  473), atividade1, fonte, self.LG, h)
        if atividade2:
            self._desenhar_quebrado(draw_v, (89, 631), atividade2, fonte, self.LG, h)
        self._desenhar_quebrado(draw_v, (382, 804), georef, fonte, self.LG, h)

        # --- Mesclar frente + verso em memória ---
        pf = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        pv = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        pf.close()
        pv.close()
        try:
            modelo.save(pf.name)
            modelo_v.save(pv.name)
            merger = PyPDF2.PdfMerger()
            merger.append(PyPDF2.PdfReader(pf.name))
            merger.append(PyPDF2.PdfReader(pv.name))
            buf = io.BytesIO()
            merger.write(buf)
            merger.close()
            return buf.getvalue()
        finally:
            for p in (pf.name, pv.name):
                try:
                    os.remove(p)
                except OSError:
                    pass


# ---------------------------------------------------------------------------
# Controller
# ---------------------------------------------------------------------------
class AnexarController:

    def __init__(self, usuario: Optional[str] = None):
        self.usuario      = usuario
        self.repository   = AnexarRepository()
        self._gerador     = _GeradorPDF()
        self._parar       = False
        self._processando = False
        self._log_cb:     Optional[Callable] = None
        self._status_cb:  Optional[Callable] = None
        self._buttons_cb: Optional[Callable] = None

    def set_callbacks(self, log_callback=None,
                      status_callback=None,
                      update_buttons_callback=None):
        self._log_cb     = log_callback
        self._status_cb  = status_callback
        self._buttons_cb = update_buttons_callback

    def _log(self, status: str, msg: str, tag: str = "info"):
        if self._log_cb:
            self._log_cb(status, msg, tag)

    def _status(self, texto: str, tipo: str = "info"):
        if self._status_cb:
            self._status_cb(texto, tipo)

    def _botoes(self, iniciar: bool, parar: bool):
        if self._buttons_cb:
            self._buttons_cb(iniciar, parar)

    def verificar_processando(self) -> bool:
        return self._processando

    def iniciar_processamento(self) -> bool:
        if self._processando:
            return False
        self._parar       = False
        self._processando = True
        self._botoes(False, True)
        self._status("Iniciando...", "primary")
        return True

    def parar_processamento(self):
        self._parar = True
        self._status("Parando...", "warning")

    # ------------------------------------------------------------------
    # Execução principal (roda em thread separada)
    # ------------------------------------------------------------------
    def executar_processamento(self):
        driver = None
        try:
            # 1. Credenciais do banco
            cred = self.repository.buscar_credencial_sefaz()
            if not cred:
                self._log("Erro",
                          "Nenhuma credencial ativa encontrada em sefaz_credenciais.",
                          "erro")
                return

            login_usuario = cred["usuario"]
            login_senha   = cred["senha"]

            # 2. Carteiras pendentes
            carteiras = self.repository.buscar_carteiras_pendentes()
            if not carteiras:
                self._log("Aviso", "Nenhuma carteira pendente (pdf IS NULL).", "aviso")
                self._status("Nenhuma carteira pendente.", "warning")
                return

            total   = len(carteiras)
            sucesso = erro = n_enc = 0
            self._log("Info", f"{total} carteira(s) pendente(s) encontrada(s).", "info")
            self._status(f"0/{total} processadas", "primary")

            # 3. Iniciar Selenium Edge
            try:
                options = Options()
                options.add_argument("--start-maximized")
                options.add_experimental_option("excludeSwitches", ["enable-logging"])
                driver = webdriver.Edge(options=options)
            except Exception as e:
                self._log("Erro", f"Falha ao iniciar navegador: {e}", "erro")
                return

            try:
                self._fazer_login(driver, login_usuario, login_senha)

                for i, carteira in enumerate(carteiras, 1):
                    if self._parar:
                        self._log("Aviso", "Interrompido pelo usuario.", "aviso")
                        break

                    cpf    = str(carteira.get("cpf", "") or "").strip()
                    nome   = str(carteira.get("nome", "") or cpf)
                    rec_id = carteira["id"]

                    self._log("Info",
                              f"[{i}/{total}] {nome} — CPF: {cpf}", "info")
                    self._status(f"{i}/{total} — {nome}", "primary")

                    # Gerar PDF
                    try:
                        pdf_bytes = self._gerador.gerar(carteira)
                    except Exception as exc:
                        self._log("Erro", f"Falha ao gerar PDF ({cpf}): {exc}", "erro")
                        erro += 1
                        continue

                    # Arquivo temporário para upload
                    tmp = tempfile.NamedTemporaryFile(
                        suffix=".pdf", prefix=f"{cpf}_", delete=False)
                    tmp.write(pdf_bytes)
                    tmp.close()

                    try:
                        resultado = self._anexar_siged(driver, cpf, tmp.name)
                    except Exception as exc:
                        self._log("Erro", f"Erro SIGED ({cpf}): {exc}", "erro")
                        erro += 1
                        continue
                    finally:
                        try:
                            os.remove(tmp.name)
                        except OSError:
                            pass

                    if resultado == "sucesso":
                        try:
                            self.repository.salvar_pdf(rec_id, pdf_bytes,
                                                       anexado_por=self.usuario or "")
                        except Exception as exc:
                            self._log("Aviso",
                                      f"Anexado mas falhou ao salvar no banco ({cpf}): {exc}",
                                      "aviso")
                        self._log("Sucesso",
                                  f"{nome} (CPF {cpf}) anexado com sucesso.", "sucesso")
                        sucesso += 1

                    elif resultado == "nao_encontrado":
                        self._log("Nao encontrado",
                                  f"CPF {cpf} nao encontrado no SIGED.", "aviso")
                        n_enc += 1

                    elif resultado == "arquivado":
                        self._log("Erro",
                                  f"CPF {cpf} — processo arquivado no SIGED.", "erro")
                        erro += 1

            finally:
                if driver:
                    try:
                        driver.quit()
                    except Exception:
                        pass

            resumo = (f"Concluido — Sucesso: {sucesso} | "
                      f"Nao encontrado: {n_enc} | Erros: {erro}")
            self._log("Info", resumo, "info")
            self._status(resumo, "success" if erro == 0 else "warning")

        except Exception as exc:
            self._log("Erro", f"Erro critico: {exc}", "erro")
            self._status(f"Erro: {exc}", "error")

        finally:
            self._processando = False
            self._botoes(True, False)

    # ------------------------------------------------------------------
    # Login SIGED
    # ------------------------------------------------------------------
    def _fazer_login(self, driver, usuario: str, senha: str):
        driver.get(SIGED_URL)
        
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, "username")))
        except TimeoutException:
            raise RuntimeError("Timeout ao carregar página de login")
        
        driver.find_element(By.ID, "username").clear()
        driver.find_element(By.ID, "username").send_keys(usuario)
        driver.find_element(By.ID, "password").clear()
        driver.find_element(By.ID, "password").send_keys(senha)
        
        try:
            driver.find_element(
                By.XPATH,
                '//*[@id="fm1"]/fieldset/div[3]/div/div[4]/input[4]').click()
        except NoSuchElementException:
            # Tentar botão alternativo
            driver.find_element(
                By.XPATH,
                '//input[@type="submit" and @value="Entrar"]').click()
        
        # Aguardar e selecionar filtro "Interessado"
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="sCmbFiltroBusca2"]/option[2]')))
            driver.find_element(
                By.XPATH, '//*[@id="sCmbFiltroBusca2"]/option[2]').click()
        except (TimeoutException, NoSuchElementException):
            # Se não encontrar o filtro, tenta prosseguir
            pass
        
        self._log("Info", "Login no SIGED realizado.", "info")

    # ------------------------------------------------------------------
    # Anexar no SIGED
    # Retorna: "sucesso" | "nao_encontrado" | "arquivado"
    # ------------------------------------------------------------------
    def _anexar_siged(self, driver, cpf: str, caminho_pdf: str) -> str:
        try:
            # Pesquisar CPF
            try:
                campo = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="txt-buscar-todos"]')))
            except TimeoutException:
                return "nao_encontrado"
            
            campo.clear()
            campo.send_keys(cpf)
            campo.send_keys(Keys.RETURN)
            time.sleep(3)

            # Ordenar por origem (2 cliques — igual APP_SETOR)
            try:
                th5 = driver.find_element(
                    By.XPATH, '//*[@id="list-inbox"]/thead/tr/th[5]')
                th5.click()
                time.sleep(2)
                th5.click()
                time.sleep(2)
            except NoSuchElementException:
                pass

            # Verificar se há resultado
            linhas = driver.find_elements(
                By.XPATH, '//*[@id="list-inbox"]/tbody/tr/td[3]')
            if not linhas:
                return "nao_encontrado"

            # Entrar no processo
            linhas[0].click()
            time.sleep(3)

            # Adicionar documento temporário
            try:
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '//*[@id="add-tmp-file"]'))).click()
            except (TimeoutException, NoSuchElementException):
                # Tentar alternativo
                driver.find_element(By.XPATH, '//*[@id="add-tmp-file"]').click()
            time.sleep(2)

            # Abrir lista de tipos de documento
            try:
                driver.find_element(
                    By.XPATH,
                    '//*[@id="s2id_cmb-tipo-doc"]/a/span[2]/b').click()
                time.sleep(4)
                ActionChains(driver).send_keys(Keys.ENTER).perform()
            except NoSuchElementException:
                pass

            # Upload do PDF
            try:
                file_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="input-tmp2"]')))
                file_input.send_keys(caminho_pdf)
                time.sleep(3)
            except (TimeoutException, NoSuchElementException):
                pass

            # Enviar
            try:
                driver.find_element(
                    By.XPATH, '//*[@id="btn-anexar-tmp"]').click()
            except NoSuchElementException:
                pass

            # Aguardar botão assinar varios
            try:
                WebDriverWait(driver, 25).until(
                    EC.visibility_of_element_located(
                        (By.XPATH, '//*[@id="spn-ass-varios-tmp"]/a'))).click()
                time.sleep(2)
            except (TimeoutException, NoSuchElementException):
                pass

            # Marcar todos e assinar mais tarde
            try:
                driver.find_element(
                    By.XPATH, '//*[@id="chk-ass-all"]').click()
                time.sleep(2)
                driver.find_element(
                    By.XPATH, '//*[@id="ass-varios-tmp"]/td[3]/a[2]').click()
                time.sleep(2)
            except NoSuchElementException:
                pass

            # Fechar popup
            try:
                driver.find_element(
                    By.XPATH, '//*[@id="popup-close"]').click()
            except NoSuchElementException:
                pass
            time.sleep(2)

            return "sucesso"

        except UnexpectedAlertPresentException:
            try:
                driver.switch_to.alert.dismiss()
            except Exception:
                pass
            return "arquivado"

        except (TimeoutException, NoSuchElementException, WebDriverException) as exc:
            raise RuntimeError(f"Falha na navegacao: {exc}") from exc