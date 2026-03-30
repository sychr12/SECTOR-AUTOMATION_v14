# -*- coding: utf-8 -*-
"""
Serviço para automação com Selenium
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import os


class SeleniumService:
    """Serviço para automação web com Selenium"""
    
    def __init__(self, download_dir=None):
        """
        Inicializa o serviço Selenium
        
        Args:
            download_dir: Diretório para downloads
        """
        self.driver = None
        self.download_dir = download_dir or self._download_padrao()

    def _download_padrao(self):
        """Define diretório padrão de downloads"""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        pasta = os.path.join(base_dir, "assets", "data", "downloads")
        os.makedirs(pasta, exist_ok=True)
        return pasta

    def _iniciar_driver(self):
        """Inicializa o Chrome WebDriver"""
        if self.driver:
            return

        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-infobars")

        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True
        }
        chrome_options.add_experimental_option("prefs", prefs)

        service = Service()

        self.driver = webdriver.Chrome(
            service=service,
            options=chrome_options
        )

    def _fechar_driver(self):
        """Fecha o WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
            finally:
                self.driver = None

    def consultar_produtor(self, cpf: str) -> dict:
        """
        Consulta dados de um produtor
        
        Args:
            cpf: CPF do produtor
            
        Returns:
            Dicionário com dados do produtor
        """
        try:
            self._iniciar_driver()

            self._abrir_site()
            self._preencher_cpf(cpf)
            self._aguardar_resultado()

            return self._extrair_dados_produtor()

        finally:
            self._fechar_driver()

    def _abrir_site(self):
        """Abre o site de consulta"""
        url = "https://SEU_SITE_AQUI"
        self.driver.get(url)

        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

    def _preencher_cpf(self, cpf):
        """Preenche campo de CPF"""
        campo_cpf = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.ID, "campo_cpf"))
        )
        campo_cpf.clear()
        campo_cpf.send_keys(cpf)

        self.driver.find_element(By.ID, "btn_consultar").click()

    def _aguardar_resultado(self):
        """Aguarda resultado da consulta"""
        time.sleep(2)

    def _extrair_dados_produtor(self) -> dict:
        """Extrai dados do produtor da página"""
        dados = {}

        dados["Nome"] = self._texto_por_xpath("//span[@id='nome']")
        dados["CPF"] = self._texto_por_xpath("//span[@id='cpf']")
        dados["UNLOC"] = self._texto_por_xpath("//span[@id='unloc']")
        dados["CNAE"] = self._texto_por_xpath("//span[@id='cnae']")
        dados["Validade"] = self._texto_por_xpath("//span[@id='validade']")

        return dados

    def _texto_por_xpath(self, xpath):
        """Obtém texto de um elemento por XPath"""
        try:
            elemento = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            return elemento.text.strip()
        except Exception:
            return ""

    def baixar_arquivo(self, xpath_botao):
        """
        Realiza download de arquivo
        
        Args:
            xpath_botao: XPath do botão de download
        """
        botao = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, xpath_botao))
        )
        botao.click()

        time.sleep(5)