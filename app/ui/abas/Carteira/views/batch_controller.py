# -*- coding: utf-8 -*-
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
from PIL import Image as PILImage, ImageDraw, ImageFont

# ──────────────────────────────────────────────────────────────────────────────
# PATHS DOS ASSETS
# ──────────────────────────────────────────────────────────────────────────────
IMG_FRENTE = r"Q:\ARQUIVOS CPCPR\SECTOR AUTOMATION\images\frente.png"
IMG_VERSO  = r"Q:\ARQUIVOS CPCPR\SECTOR AUTOMATION\images\verso.png"
FONTE_PATH = r"Q:\ARQUIVOS CPCPR\fabio jr\CARTAO-DIGITAL\Roboto-Regular.ttf"
SEFAZ_URL  = "http://sistemas.sefaz.am.gov.br/gcc/entrada.do"

# ──────────────────────────────────────────────────────────────────────────────
# MAPEAMENTO UNLOC
# ──────────────────────────────────────────────────────────────────────────────
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

<<<<<<< HEAD
# ── XPaths SEFAZ (base) ───────────────────────────────────────────────────────
_BASE = "formProdutorRural_produtorRuralTOA_produtorRural_"

_XPATH = {
    "menu_gcc":     '//*[@id="oCMenu___GCC2300"]',
    "menu_cad":     '//*[@id="oCMenu___GCC1008"]',
    "cpf_field":    f'//*[@id="{_BASE}cpfProdutorRuralFormatado"]',
    "pesquisar":    '//*[@id="formProdutorRural_cadastroProdutorRuralAction!pesquisarProdutorRural"]',
    "th_situacao":  '//*[@id="tbProdutorRural"]/thead/tr/th[2]',
    "btn_abrir":    '//*[@id="tbProdutorRural"]/tbody/tr/td[8]/a[2]',
    # dados do produtor
    "nome":         f'//*[@id="{_BASE}cceaPessoaFisica_pfNome"]',
    "rp":           f'//*[@id="{_BASE}ieProdutorRuralFormatado"]',
    "cpf_pg":       f'//*[@id="{_BASE}cpfProdutorRuralFormatado"]',
    "propriedade":  f'//*[@id="{_BASE}nmPropriedade"]',
    "endereco":     f'//*[@id="{_BASE}txEnderecoPropriedade"]',
    "unloc":        f'//*[@id="{_BASE}sgDistritoIdam"]',
    "latitude":     f'//*[@id="{_BASE}geoLatitude"]',
    "longitude":    f'//*[@id="{_BASE}geoLongitude"]',
    "atv1":         f'//*[@id="{_BASE}nmCnaePrincipal"]',
    "atv2":         f'//*[@id="{_BASE}nmCnaeSecundario"]',
    "inicioatv":    f'//*[@id="{_BASE}anoInicioAtividade"]',
    "numcontrole":  f'//*[@id="{_BASE}nrDeclaracaoUnidLocal"]',
    "cnae1":        f'//*[@id="{_BASE}cnaePrincipalFormatado"]',
    "cnae2":        f'//*[@id="{_BASE}cnaeSecundarioFormatado"]',
    "validade":     f'//*[@id="{_BASE}dtValidadeDeclaracaoFormatado"]',
}


# ── Helpers de geração de PDF ─────────────────────────────────────────────────
=======
# ──────────────────────────────────────────────────────────────────────────────
# XPATHS SEFAZ
# ──────────────────────────────────────────────────────────────────────────────
_BASE = "formProdutorRural_produtorRuralTOA_produtorRural_"
>>>>>>> f4a3e3b (.)

_XPATH = {
    "menu_gcc":     '//*[@id="oCMenu___GCC2300"]',
    "menu_cad":     '//*[@id="oCMenu___GCC1008"]',
    "cpf_field":    f'//*[@id="{_BASE}cpfProdutorRuralFormatado"]',
    "pesquisar":    '//*[@id="formProdutorRural_cadastroProdutorRuralAction!pesquisarProdutorRural"]',
    "th_situacao":  '//*[@id="tbProdutorRural"]/thead/tr/th[2]',
    "btn_abrir":    '//*[@id="tbProdutorRural"]/tbody/tr/td[8]/a[2]',
    "nome":         f'//*[@id="{_BASE}cceaPessoaFisica_pfNome"]',
    "rp":           f'//*[@id="{_BASE}ieProdutorRuralFormatado"]',
    "cpf_pg":       f'//*[@id="{_BASE}cpfProdutorRuralFormatado"]',
    "propriedade":  f'//*[@id="{_BASE}nmPropriedade"]',
    "endereco":     f'//*[@id="{_BASE}txEnderecoPropriedade"]',
    "unloc":        f'//*[@id="{_BASE}sgDistritoIdam"]',
    "latitude":     f'//*[@id="{_BASE}geoLatitude"]',
    "longitude":    f'//*[@id="{_BASE}geoLongitude"]',
    "atv1":         f'//*[@id="{_BASE}nmCnaePrincipal"]',
    "atv2":         f'//*[@id="{_BASE}nmCnaeSecundario"]',
    "inicioatv":    f'//*[@id="{_BASE}anoInicioAtividade"]',
    "numcontrole":  f'//*[@id="{_BASE}nrDeclaracaoUnidLocal"]',
    "cnae1":        f'//*[@id="{_BASE}cnaePrincipalFormatado"]',
    "cnae2":        f'//*[@id="{_BASE}cnaeSecundarioFormatado"]',
    "validade":     f'//*[@id="{_BASE}dtValidadeDeclaracaoFormatado"]',
}

# ──────────────────────────────────────────────────────────────────────────────
# HELPERS DE GERAÇÃO DE PDF
# ──────────────────────────────────────────────────────────────────────────────
def _normalizar_unloc(unloc: str) -> str:
    return _UNLOC_MAP.get(unloc, unloc)

def _limitar_texto(texto: str, n: int) -> str:
    return texto[:n - 3] + "..." if len(texto) > n else texto

def _desenhar_texto_quebrado(draw, coordenadas, texto, fonte, largura_max, altura_max):
    x, y = coordenadas
    for linha in textwrap.wrap(texto or "", width=largura_max // 9):
        if y >= altura_max:
            break
        draw.text((x, y), linha, fill=(0, 0, 0), font=fonte)
        y += 40

def _gerar_pdf_bytes(dados: dict) -> bytes:
<<<<<<< HEAD
    """
    Desenha frente + verso com Pillow, mescla com PyPDF2 e retorna
    os bytes do PDF final — idêntico ao APP_SETOR / ui.py.
    """
=======
>>>>>>> f4a3e3b (.)
    largura_max    = 540
    fonte          = ImageFont.truetype(FONTE_PATH, 41)
    fonte_endereco = ImageFont.truetype(FONTE_PATH, 38)

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

<<<<<<< HEAD
    # ── FRENTE ────────────────────────────────────────────────────────────────
=======
>>>>>>> f4a3e3b (.)
    modelo  = PILImage.open(IMG_FRENTE)
    desenho = ImageDraw.Draw(modelo)
    desenho.text((217, 393),  rp,          fill=(0, 0, 0), font=fonte)
    desenho.text((95,  518),  nome,        fill=(0, 0, 0), font=fonte)
    desenho.text((864, 392),  cpf,         fill=(0, 0, 0), font=fonte)
    desenho.text((100, 660),  propriedade, fill=(0, 0, 0), font=fonte)
    desenho.text((212, 824),  unloc,       fill=(0, 0, 0), font=fonte)
    desenho.text((751, 824),  inicioatv,   fill=(0, 0, 0), font=fonte)
    desenho.text((1063, 825), validade,    fill=(0, 0, 0), font=fonte)

<<<<<<< HEAD
    # ── VERSO ─────────────────────────────────────────────────────────────────
=======
>>>>>>> f4a3e3b (.)
    modelo_verso  = PILImage.open(IMG_VERSO)
    desenho_verso = ImageDraw.Draw(modelo_verso)
    altura_verso  = modelo_verso.size[1]

    # Endereço com quebra de linha (igual ao APP_SETOR)
    linhas_endereco = textwrap.wrap(endereco, largura_max)
    coord_end = [89, 285]
    for linha in linhas_endereco:
        for lq in textwrap.wrap(linha, width=largura_max // 9):
            if coord_end[1] < altura_verso:
                desenho_verso.text(tuple(coord_end), lq,
                                   fill=(0, 0, 0), font=fonte_endereco)
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

<<<<<<< HEAD
    # ── Salvar como PDF e mesclar ─────────────────────────────────────────────
=======
>>>>>>> f4a3e3b (.)
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tf:
        path_frente = tf.name
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tv:
        path_verso = tv.name

    try:
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
            try:
                os.remove(p)
            except OSError:
                pass

<<<<<<< HEAD

# ── Controller ────────────────────────────────────────────────────────────────

class BatchCarteiraController:
    """
    Controller de lote — usado exclusivamente por BatchCarteiraView.

    Parâmetros
    ----------
    usuario    : str  — nome do usuário logado
    repo       : objeto com método .salvar(...)      — CarteirasRepository
    sefaz_repo : objeto com método .obter_credencial() → dict | None
    """
=======
# ──────────────────────────────────────────────────────────────────────────────
# CONTROLLER
# ──────────────────────────────────────────────────────────────────────────────
class BatchCarteiraController:
>>>>>>> f4a3e3b (.)

    def __init__(self, usuario: str, repo, sefaz_repo):
        self.usuario      = usuario
        self._repo        = repo
        self._sefaz_repo  = sefaz_repo
<<<<<<< HEAD

        self._rodando     = False
        self._parar_flag  = False
        self._driver      = None

    # ── Helpers estáticos ────────────────────────────────────────────────────

    @staticmethod
    def cpf_do_arquivo(nome_arquivo: str) -> Optional[str]:
        """Extrai CPF (11 dígitos) do nome do arquivo. None se inválido."""
=======
        self._rodando     = False
        self._parar_flag  = False
        self._driver      = None

    @staticmethod
    def cpf_do_arquivo(nome_arquivo: str) -> Optional[str]:
>>>>>>> f4a3e3b (.)
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
        return self._rodando

    def parar(self) -> None:
        self._parar_flag = True

<<<<<<< HEAD
    # ── Ponto de entrada ─────────────────────────────────────────────────────

    def executar_lote(
        self,
        caminhos_pdf: list,
        log_cb:       Callable,
        progress_cb:  Callable,
        concluido_cb: Callable,
    ) -> None:
        """
        Dispara processamento em lote em thread daemon.

        Callbacks:
          log_cb(msg, tipo)              tipo ∈ {info, sucesso, erro, aviso}
          progress_cb(atual, total, nome)
          concluido_cb(sucesso, erro, ignorado)
        """
        if self._rodando:
            return
        self._parar_flag = False
        threading.Thread(
            target=self._worker,
            args=(caminhos_pdf, log_cb, progress_cb, concluido_cb),
            daemon=True,
        ).start()

    # ── Worker ───────────────────────────────────────────────────────────────

=======
    def executar_lote(self, caminhos_pdf: list, log_cb: Callable, progress_cb: Callable, concluido_cb: Callable) -> None:
        if self._rodando:
            return
        self._parar_flag = False
        threading.Thread(target=self._worker, args=(caminhos_pdf, log_cb, progress_cb, concluido_cb), daemon=True).start()

>>>>>>> f4a3e3b (.)
    def _worker(self, caminhos_pdf, log_cb, progress_cb, concluido_cb):
        self._rodando = True
        sucesso = erro = ignorado = 0
        total   = len(caminhos_pdf)

        try:
<<<<<<< HEAD
            # 1. Credenciais SEFAZ
            cred = None
            if self._sefaz_repo:
                try:
                    cred = self._sefaz_repo.obter_credencial()
                except Exception as exc:
                    log_cb(f"Aviso: não foi possível obter credenciais — {exc}", "aviso")

            if not cred:
                log_cb("Credenciais SEFAZ não encontradas no banco. Abortando.", "erro")
                concluido_cb(0, total, 0)
                return

            # 2. Abrir Chrome + login
            log_cb("Abrindo Chrome e fazendo login no SEFAZ...", "info")
=======
            cred = None
            if self._sefaz_repo is None:
                log_cb("ERRO: sefaz_repo é None", "erro")
                concluido_cb(0, total, 0)
                return
            try:
                cred = self._sefaz_repo.obter_credencial()
            except Exception as exc:
                log_cb(f"Erro ao obter credencial: {exc}", "erro")
                concluido_cb(0, total, 0)
                return

            if not cred:
                log_cb("Credenciais SEFAZ não encontradas no banco.", "erro")
                concluido_cb(0, total, 0)
                return

            log_cb("Abrindo navegador...", "info")
>>>>>>> f4a3e3b (.)
            try:
                self._driver = self._abrir_driver(cred["usuario"], cred["senha"])
                time.sleep(2)  # Aguarda carregamento
            except Exception as exc:
                log_cb(f"Erro ao abrir navegador: {exc}", "erro")
                concluido_cb(0, total, 0)
                return

            log_cb("Login realizado. Iniciando processamento...", "sucesso")
            time.sleep(1)

            # 3. Processar cada PDF
            for idx, caminho in enumerate(caminhos_pdf, start=1):
                if self._parar_flag:
                    log_cb("Processamento interrompido.", "aviso")
                    ignorado += total - idx + 1
                    break

                nome       = os.path.basename(caminho)
                cpf_digits = self.cpf_do_arquivo(nome)
                cpf_fmt    = self.formatar_cpf(cpf_digits) if cpf_digits else nome

                progress_cb(idx, total, nome)
                log_cb(f"[{idx}/{total}] {cpf_fmt} — consultando SEFAZ...", "info")

                # Consulta SEFAZ
                try:
                    dados = self._consultar_sefaz(cpf_fmt)
                except Exception as exc:
<<<<<<< HEAD
                    log_cb(f"[{idx}/{total}] {cpf_fmt} — erro na consulta: {exc}", "erro")
=======
                    log_cb(f"[{idx}/{total}] {cpf_fmt} — erro: {exc}", "erro")
>>>>>>> f4a3e3b (.)
                    erro += 1
                    continue

                if not dados:
<<<<<<< HEAD
                    log_cb(f"[{idx}/{total}] {cpf_fmt} — não encontrado no SEFAZ.", "aviso")
=======
                    log_cb(f"[{idx}/{total}] {cpf_fmt} — não encontrado.", "aviso")
>>>>>>> f4a3e3b (.)
                    ignorado += 1
                    continue

                # Gerar PDF + salvar banco
                try:
                    pdf_bytes = _gerar_pdf_bytes(dados)

                    self._repo.salvar(
                        registro     = dados.get("rp", ""),
                        cpf          = cpf_digits or "",
                        nome         = dados.get("nome", ""),
                        propriedade  = dados.get("propriedade", ""),
                        unloc        = dados.get("unloc", ""),
                        inicio       = dados.get("inicioatv", ""),
                        validade     = dados.get("validade", ""),
                        endereco     = dados.get("endereco", ""),
                        atividade1   = dados.get("atv1", ""),
                        atividade2   = dados.get("atv2", ""),
<<<<<<< HEAD
                        georef       = (f"{dados.get('latitude', '')}  "
                                        f"{dados.get('longitude', '')}"),
=======
                        georef       = f"{dados.get('latitude', '')}  {dados.get('longitude', '')}",
>>>>>>> f4a3e3b (.)
                        pdf_conteudo = pdf_bytes,
                        foto1=None, foto2=None, foto3=None,
                        usuario      = self.usuario,
                    )

                    sucesso += 1
                    log_cb(f"[{idx}/{total}] {cpf_fmt} — ✓ salvo com sucesso.", "sucesso")

                except Exception as exc:
                    log_cb(f"[{idx}/{total}] {cpf_fmt} — erro ao salvar: {exc}", "erro")
                    erro += 1

        except Exception as exc:
            log_cb(f"Erro inesperado: {exc}", "erro")
        finally:
            self._fechar_driver()
            self._rodando = False
            concluido_cb(sucesso, erro, ignorado)

    def _abrir_driver(self, usuario: str, senha: str):
        import shutil
        from selenium import webdriver

        driver = None

        edge_driver_paths = [
            r"C:\Program Files (x86)\Microsoft\EdgeWebDriver\msedgedriver.exe",
            r"C:\Program Files\Microsoft\EdgeWebDriver\msedgedriver.exe",
            r"C:\Windows\System32\msedgedriver.exe",
        ]
        which = shutil.which("msedgedriver")
        if which:
            edge_driver_paths.insert(0, which)

        for edge_driver in edge_driver_paths:
            if not edge_driver or not os.path.exists(edge_driver):
                continue
            try:
                from selenium.webdriver.edge.service import Service as EdgeService
                options = webdriver.EdgeOptions()
                options.add_argument("--start-maximized")
                options.add_experimental_option("detach", True)
                driver = webdriver.Edge(service=EdgeService(edge_driver), options=options)
                break
            except Exception:
                continue

        if driver is None:
            try:
                options = webdriver.EdgeOptions()
                options.add_argument("--start-maximized")
                options.add_experimental_option("detach", True)
                driver = webdriver.Edge(options=options)
            except Exception:
                pass

        if driver is None:
            try:
                options = webdriver.ChromeOptions()
                options.add_argument("--start-maximized")
                options.add_experimental_option("detach", True)
                driver = webdriver.Chrome(options=options)
            except Exception:
                pass

        if driver is None:
            raise RuntimeError("Nenhum navegador encontrado.")

        driver.get(SEFAZ_URL)
        time.sleep(2)

        driver.find_element("id", "username").send_keys(usuario)
        driver.find_element("id", "password").send_keys(senha)
        driver.find_element("xpath", '//*[@id="fm1"]/fieldset/div[3]/div/div[4]/input[4]').click()
        time.sleep(3)
        return driver

    def _consultar_sefaz(self, cpf_fmt: str) -> Optional[dict]:
        from selenium.webdriver.common.by import By
        from selenium.common.exceptions import NoSuchElementException

        d = self._driver

<<<<<<< HEAD
        # Navegar no menu SEFAZ (idêntico ao APP_SETOR)
        d.find_element(By.XPATH, _XPATH["menu_gcc"]).click()
        time.sleep(1)
        d.find_element(By.XPATH, _XPATH["menu_cad"]).click()
        time.sleep(1)

        # Preencher CPF e pesquisar
        campo = d.find_element(By.XPATH, _XPATH["cpf_field"])
        campo.click()
        campo.send_keys(cpf_fmt)
        d.find_element(By.XPATH, _XPATH["pesquisar"]).click()
        time.sleep(1)
=======
        try:
            d.find_element(By.XPATH, _XPATH["menu_gcc"]).click()
            time.sleep(0.8)
            d.find_element(By.XPATH, _XPATH["menu_cad"]).click()
            time.sleep(0.8)
        except Exception:
            return None
>>>>>>> f4a3e3b (.)

        # Ordenar por situação e abrir declaração mais recente
        try:
<<<<<<< HEAD
            d.find_element(By.XPATH, _XPATH["th_situacao"]).click()
            time.sleep(2)
            d.find_element(By.XPATH, _XPATH["btn_abrir"]).click()
            time.sleep(3)
=======
            campo = d.find_element(By.XPATH, _XPATH["cpf_field"])
            campo.click()
            campo.clear()
            campo.send_keys(cpf_fmt)
            d.find_element(By.XPATH, _XPATH["pesquisar"]).click()
            time.sleep(1.5)
        except Exception:
            return None

        try:
            d.find_element(By.XPATH, _XPATH["th_situacao"]).click()
            time.sleep(1.5)
            d.find_element(By.XPATH, _XPATH["btn_abrir"]).click()
            time.sleep(2.5)
>>>>>>> f4a3e3b (.)
        except NoSuchElementException:
            return None

        def val(key: str) -> str:
            try:
                el = d.find_element(By.XPATH, _XPATH[key])
                return d.execute_script("return arguments[0].value;", el) or ""
            except Exception:
                return ""

        nome = val("nome")
        if not nome:
            return None

        rp          = val("rp")
        cpf_pg      = val("cpf_pg")
        propriedade = val("propriedade")
        endereco    = val("endereco")
        unloc_raw   = val("unloc")
        latitude    = val("latitude").replace(",", ".")
        longitude   = val("longitude").replace(",", ".")
        atv1        = val("atv1")
        atv2        = val("atv2")
        inicioatv   = val("inicioatv")
        numcontrole = val("numcontrole")
        cnae1       = val("cnae1")
        cnae2       = val("cnae2")
        validade    = val("validade")

        if not atv2:
            cnae2 = ""

        # Mapeamento UNLOC (idêntico ao APP_SETOR)
        unloc_da_pagina = _normalizar_unloc(unloc_raw)
        unloc_completo  = f"PR-{unloc_da_pagina}/{numcontrole}"

        return {
            "nome":            nome,
            "rp":              rp,
            "cpf":             cpf_pg or cpf_fmt,
            "propriedade":     propriedade,
            "endereco":        endereco,
            "unloc_da_pagina": unloc_da_pagina,
            "unloc":           unloc_completo,
            "latitude":        latitude,
            "longitude":       longitude,
            "atv1":            atv1,
            "atv2":            atv2,
            "inicioatv":       inicioatv,
            "numcontrole":     numcontrole,
            "cnae1":           cnae1,
            "cnae2":           cnae2,
            "validade":        validade,
        }

<<<<<<< HEAD
    # ── Fechar driver ─────────────────────────────────────────────────────────

=======
>>>>>>> f4a3e3b (.)
    def _fechar_driver(self) -> None:
        if self._driver:
            try:
                self._driver.quit()
            except Exception:
                pass
            self._driver = None