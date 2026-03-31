# -*- coding: utf-8 -*-
"""
batch_controller.py — Controller de geração em LOTE de carteiras digitais.
Local: app/ui/abas/Carteira/views/batch_controller.py
"""
from __future__ import annotations

import io
import os
import re
import tempfile
import textwrap
import threading
import time
from typing import Callable, Optional

import PyPDF2
from PIL import Image as PILImage, ImageDraw

from ..assets import get_img_frente, get_img_verso, get_pil_font, open_image

# ── SEFAZ ─────────────────────────────────────────────────────────────────────
SEFAZ_URL = "http://sistemas.sefaz.am.gov.br/gcc/entrada.do"

_UNLOC_MAP = {
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

_BASE = "formProdutorRural_produtorRuralTOA_produtorRural_"
_XPATH = {
    "menu_gcc":    '//*[@id="oCMenu___GCC2300"]',
    "menu_cad":    '//*[@id="oCMenu___GCC1008"]',
    "cpf_field":   f'//*[@id="{_BASE}cpfProdutorRuralFormatado"]',
    "pesquisar":   f'//*[@id="formProdutorRural_cadastroProdutorRuralAction!pesquisarProdutorRural"]',
    "th_situacao": '//*[@id="tbProdutorRural"]/thead/tr/th[2]',
    "btn_abrir":   '//*[@id="tbProdutorRural"]/tbody/tr/td[8]/a[2]',
    "nome":        f'//*[@id="{_BASE}cceaPessoaFisica_pfNome"]',
    "rp":          f'//*[@id="{_BASE}ieProdutorRuralFormatado"]',
    "cpf_pg":      f'//*[@id="{_BASE}cpfProdutorRuralFormatado"]',
    "propriedade": f'//*[@id="{_BASE}nmPropriedade"]',
    "endereco":    f'//*[@id="{_BASE}txEnderecoPropriedade"]',
    "unloc":       f'//*[@id="{_BASE}sgDistritoIdam"]',
    "latitude":    f'//*[@id="{_BASE}geoLatitude"]',
    "longitude":   f'//*[@id="{_BASE}geoLongitude"]',
    "atv1":        f'//*[@id="{_BASE}nmCnaePrincipal"]',
    "atv2":        f'//*[@id="{_BASE}nmCnaeSecundario"]',
    "inicioatv":   f'//*[@id="{_BASE}anoInicioAtividade"]',
    "numcontrole": f'//*[@id="{_BASE}nrDeclaracaoUnidLocal"]',
    "cnae1":       f'//*[@id="{_BASE}cnaePrincipalFormatado"]',
    "cnae2":       f'//*[@id="{_BASE}cnaeSecundarioFormatado"]',
    "validade":    f'//*[@id="{_BASE}dtValidadeDeclaracaoFormatado"]',
}


def _normalizar_unloc(unloc: str) -> str:
    return _UNLOC_MAP.get(unloc.strip().upper(), unloc)


def _limitar_texto(texto: str, n: int) -> str:
    if not texto:
        return ""
    return texto[:n - 3] + "..." if len(texto) > n else texto


def _desenhar_texto_quebrado(draw, coordenadas, texto, fonte,
                              largura_max: int, altura_max: int):
    if not texto:
        return
    x, y = coordenadas
    for linha in textwrap.wrap(texto, width=max(1, largura_max // 9)):
        if y >= altura_max:
            break
        if fonte:
            draw.text((x, y), linha, fill=(0, 0, 0), font=fonte)
        else:
            draw.text((x, y), linha, fill=(0, 0, 0))
        y += 40


def _gerar_pdf_bytes(dados: dict) -> bytes:
    """Gera PDF frente+verso. Usa imagem real ou placeholder se não encontrada."""
    fonte          = get_pil_font(41)
    fonte_endereco = get_pil_font(38)
    largura_max    = 540

    nome        = dados.get("nome", "")
    rp          = dados.get("rp", "")
    cpf         = dados.get("cpf", "")
    propriedade = dados.get("propriedade", "")
    unloc       = dados.get("unloc", "")
    inicioatv   = dados.get("inicioatv", "")
    validade    = dados.get("validade", "")
    endereco    = _limitar_texto(dados.get("endereco", ""), 50)
    atv1        = dados.get("atv1", "")
    atv2        = _limitar_texto(dados.get("atv2", ""), 60)
    cnae1       = dados.get("cnae1", "")
    cnae2       = dados.get("cnae2", "") if atv2 else ""
    latitude    = dados.get("latitude", "")
    longitude   = dados.get("longitude", "")

    def _txt(draw, pos, text):
        if not text:
            return
        if fonte:
            draw.text(pos, text, fill=(0, 0, 0), font=fonte)
        else:
            draw.text(pos, text, fill=(0, 0, 0))

    # FRENTE
    modelo  = open_image(get_img_frente(), "FRENTE").copy()
    desenho = ImageDraw.Draw(modelo)
    _txt(desenho, (217, 393),  rp)
    _txt(desenho, (95,  518),  nome)
    _txt(desenho, (864, 392),  cpf)
    _txt(desenho, (100, 660),  propriedade)
    _txt(desenho, (212, 824),  unloc)
    _txt(desenho, (751, 824),  inicioatv)
    _txt(desenho, (1063, 825), validade)

    # VERSO
    modelo_verso  = open_image(get_img_verso(), "VERSO").copy()
    desenho_verso = ImageDraw.Draw(modelo_verso)
    altura_verso  = modelo_verso.size[1]

    coord_end = [89, 285]
    for linha in textwrap.wrap(endereco, largura_max):
        for lq in textwrap.wrap(linha, width=max(1, largura_max // 9)):
            if coord_end[1] < altura_verso:
                if fonte_endereco:
                    desenho_verso.text(tuple(coord_end), lq,
                                       fill=(0, 0, 0), font=fonte_endereco)
                else:
                    desenho_verso.text(tuple(coord_end), lq, fill=(0, 0, 0))
                coord_end[1] += 40

    _desenhar_texto_quebrado(
        desenho_verso, (89, 473),
        f"{cnae1} - {atv1}" if cnae1 else atv1,
        fonte, largura_max, altura_verso)

    if atv2:
        _desenhar_texto_quebrado(
            desenho_verso, (89, 631),
            f"{cnae2} - {atv2}" if cnae2 else atv2,
            fonte, largura_max, altura_verso)

    _desenhar_texto_quebrado(
        desenho_verso, (382, 804),
        f"{latitude}  {longitude}",
        fonte, largura_max, altura_verso)

    path_frente = path_verso = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tf:
            path_frente = tf.name
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tv:
            path_verso = tv.name

        modelo.save(path_frente, format="PDF")
        modelo_verso.save(path_verso, format="PDF")

        merger = PyPDF2.PdfMerger()
        merger.append(PyPDF2.PdfReader(path_frente))
        merger.append(PyPDF2.PdfReader(path_verso))
        buf = io.BytesIO()
        merger.write(buf)
        merger.close()
        return buf.getvalue()
    finally:
        for p in (path_frente, path_verso):
            if p:
                try:
                    os.remove(p)
                except OSError:
                    pass


# BUG CORRIGIDO: _edge_opts e _chrome_opts eram funções de módulo que referenciavam
# `webdriver` sem importá-lo. Selenium só é importado dentro de _abrir_driver.
# Solução: cada helper importa selenium internamente.

def _edge_opts():
    from selenium import webdriver
    opts = webdriver.EdgeOptions()
    opts.add_argument("--start-maximized")
    opts.add_experimental_option("detach", True)
    return opts


def _chrome_opts():
    from selenium import webdriver
    opts = webdriver.ChromeOptions()
    opts.add_argument("--start-maximized")
    opts.add_experimental_option("detach", True)
    return opts


class BatchCarteiraController:

    def __init__(self, usuario: str, repo, sefaz_repo):
        self.usuario     = usuario
        self._repo       = repo
        self._sefaz_repo = sefaz_repo
        self._lock       = threading.Lock()
        self._rodando    = False
        self._parar_flag = False
        self._driver     = None

    @staticmethod
    def cpf_do_arquivo(nome_arquivo: str) -> Optional[str]:
        stem   = os.path.splitext(nome_arquivo)[0]
        digits = re.sub(r"\D", "", stem)
        return digits if len(digits) == 11 else None

    @staticmethod
    def formatar_cpf(cpf_digits: str) -> str:
        d = cpf_digits[:11]
        if len(d) == 11:
            return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"
        return d

    def esta_rodando(self) -> bool:
        with self._lock:
            return self._rodando

    def parar(self) -> None:
        with self._lock:
            self._parar_flag = True

    def executar_lote(self, caminhos_pdf: list, log_cb: Callable,
                      progress_cb: Callable, concluido_cb: Callable) -> None:
        with self._lock:
            if self._rodando:
                return
            self._rodando    = True
            self._parar_flag = False
        threading.Thread(
            target=self._worker,
            args=(caminhos_pdf, log_cb, progress_cb, concluido_cb),
            daemon=True,
        ).start()

    def _worker(self, caminhos_pdf, log_cb, progress_cb, concluido_cb):
        sucesso = erro = ignorado = 0
        total   = len(caminhos_pdf)
        try:
            if self._sefaz_repo is None:
                log_cb("ERRO: repositório SEFAZ não configurado.", "erro")
                concluido_cb(0, total, 0)
                return

            try:
                cred = self._sefaz_repo.obter_credencial()
            except Exception as exc:
                log_cb(f"Erro ao obter credencial SEFAZ: {exc}", "erro")
                concluido_cb(0, total, 0)
                return

            if not cred:
                log_cb("Credenciais SEFAZ não encontradas no banco.", "erro")
                concluido_cb(0, total, 0)
                return

            log_cb("Abrindo navegador...", "info")
            try:
                self._driver = self._abrir_driver(cred["usuario"], cred["senha"])
            except Exception as exc:
                log_cb(f"Erro ao abrir navegador: {exc}", "erro")
                concluido_cb(0, total, 0)
                return

            log_cb("Login realizado. Iniciando processamento...", "sucesso")

            for idx, caminho in enumerate(caminhos_pdf, start=1):
                with self._lock:
                    deve_parar = self._parar_flag
                if deve_parar:
                    log_cb("Processamento interrompido pelo usuário.", "aviso")
                    ignorado += total - idx + 1
                    break

                nome       = os.path.basename(caminho)
                cpf_digits = self.cpf_do_arquivo(nome)

                if not cpf_digits:
                    log_cb(f"[{idx}/{total}] {nome} — CPF não encontrado no nome; ignorado.", "aviso")
                    ignorado += 1
                    continue

                cpf_fmt = self.formatar_cpf(cpf_digits)
                progress_cb(idx, total, nome)
                log_cb(f"[{idx}/{total}] {cpf_fmt} — consultando SEFAZ...", "info")

                try:
                    dados = self._consultar_sefaz(cpf_fmt)
                except Exception as exc:
                    log_cb(f"[{idx}/{total}] {cpf_fmt} — erro na consulta: {exc}", "erro")
                    erro += 1
                    continue

                if not dados:
                    log_cb(f"[{idx}/{total}] {cpf_fmt} — não encontrado.", "aviso")
                    ignorado += 1
                    continue

                try:
                    pdf_bytes = _gerar_pdf_bytes(dados)
                    lat = dados.get("latitude", "")
                    lon = dados.get("longitude", "")
                    georef = f"{lat}  {lon}".strip() if (lat or lon) else ""
                    self._repo.salvar(
                        registro     = dados.get("rp", ""),
                        cpf          = cpf_digits or cpf_fmt,
                        nome         = dados.get("nome", ""),
                        propriedade  = dados.get("propriedade", ""),
                        unloc        = dados.get("unloc", ""),
                        inicio       = dados.get("inicioatv", ""),
                        validade     = dados.get("validade", ""),
                        endereco     = dados.get("endereco", ""),
                        atividade1   = dados.get("atv1", ""),
                        atividade2   = dados.get("atv2", ""),
                        georef       = georef,
                        pdf_conteudo = pdf_bytes,
                        foto1=None, foto2=None, foto3=None,
                        usuario      = self.usuario,
                    )
                    sucesso += 1
                    log_cb(f"[{idx}/{total}] {cpf_fmt} — ✓ salvo.", "sucesso")
                except Exception as exc:
                    log_cb(f"[{idx}/{total}] {cpf_fmt} — erro ao salvar: {exc}", "erro")
                    erro += 1

        except Exception as exc:
            log_cb(f"Erro inesperado: {exc}", "erro")
        finally:
            self._fechar_driver()
            with self._lock:
                self._rodando = False
            concluido_cb(sucesso, erro, ignorado)

    def _abrir_driver(self, usuario: str, senha: str):
        import shutil
        from selenium import webdriver
        from selenium.webdriver.support.ui import WebDriverWait

        driver = None

        for ep in [
            shutil.which("msedgedriver"),
            r"C:\Program Files (x86)\Microsoft\EdgeWebDriver\msedgedriver.exe",
            r"C:\Program Files\Microsoft\EdgeWebDriver\msedgedriver.exe",
            r"C:\Windows\System32\msedgedriver.exe",
        ]:
            if not ep or not os.path.exists(ep):
                continue
            try:
                from selenium.webdriver.edge.service import Service as EdgeService
                driver = webdriver.Edge(service=EdgeService(ep), options=_edge_opts())
                break
            except Exception:
                continue

        if driver is None:
            for try_fn in [
                lambda: webdriver.Edge(options=_edge_opts()),
                lambda: webdriver.Chrome(options=_chrome_opts()),
            ]:
                try:
                    driver = try_fn()
                    break
                except Exception:
                    pass

        if driver is None:
            raise RuntimeError(
                "Nenhum navegador compatível encontrado.\n"
                "Instale Edge WebDriver ou ChromeDriver e adicione ao PATH."
            )

        driver.get(SEFAZ_URL)
        WebDriverWait(driver, 15).until(
            lambda d: d.find_element("id", "username"))
        driver.find_element("id", "username").send_keys(usuario)
        driver.find_element("id", "password").send_keys(senha)
        driver.find_element(
            "xpath",
            '//*[@id="fm1"]/fieldset/div[3]/div/div[4]/input[4]'
        ).click()
        time.sleep(3)
        return driver

    def _consultar_sefaz(self, cpf_fmt: str) -> Optional[dict]:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import NoSuchElementException, TimeoutException

        d    = self._driver
        wait = WebDriverWait(d, 10)
        cpf_limpo = re.sub(r"\D", "", cpf_fmt)

        try:
            wait.until(EC.element_to_be_clickable(
                (By.XPATH, _XPATH["menu_gcc"]))).click()
            time.sleep(0.4)
            wait.until(EC.element_to_be_clickable(
                (By.XPATH, _XPATH["menu_cad"]))).click()
            time.sleep(0.4)
        except (NoSuchElementException, TimeoutException):
            return None

        try:
            campo = wait.until(EC.element_to_be_clickable(
                (By.XPATH, _XPATH["cpf_field"])))
            campo.click()
            time.sleep(0.2)
            campo.clear()
            time.sleep(0.1)

            d.execute_script(f"arguments[0].value = '{cpf_limpo}';", campo)
            d.execute_script(
                "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", campo)
            d.execute_script(
                "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", campo)
            time.sleep(0.3)

            if not campo.get_attribute("value"):
                campo.send_keys(cpf_limpo)
                time.sleep(0.2)

            d.find_element(By.XPATH, _XPATH["pesquisar"]).click()
            time.sleep(1.5)
        except Exception:
            return None

        try:
            wait.until(EC.element_to_be_clickable(
                (By.XPATH, _XPATH["th_situacao"]))).click()
            time.sleep(0.8)
            wait.until(EC.element_to_be_clickable(
                (By.XPATH, _XPATH["btn_abrir"]))).click()
            time.sleep(2)
        except (NoSuchElementException, TimeoutException):
            return None

        def val(key: str) -> str:
            try:
                el = d.find_element(By.XPATH, _XPATH[key])
                return (d.execute_script(
                    "return arguments[0].value;", el) or "").strip()
            except Exception:
                return ""

        nome = val("nome")
        if not nome:
            return None

        unloc_raw   = val("unloc")
        numcontrole = val("numcontrole")
        atv2        = val("atv2")
        cnae2       = val("cnae2") if atv2 else ""

        return {
            "nome":        nome,
            "rp":          val("rp"),
            "cpf":         val("cpf_pg") or cpf_fmt,
            "propriedade": val("propriedade"),
            "endereco":    val("endereco"),
            "unloc":       f"PR-{_normalizar_unloc(unloc_raw)}/{numcontrole}",
            "latitude":    val("latitude").replace(",", "."),
            "longitude":   val("longitude").replace(",", "."),
            "atv1":        val("atv1"),
            "atv2":        atv2,
            "inicioatv":   val("inicioatv"),
            "numcontrole": numcontrole,
            "cnae1":       val("cnae1"),
            "cnae2":       cnae2,
            "validade":    val("validade"),
        }

    def _fechar_driver(self) -> None:
        if self._driver:
            try:
                self._driver.quit()
            except Exception:
                pass
            self._driver = None