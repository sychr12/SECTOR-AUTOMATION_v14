import os
import re
import sys
import subprocess
import tempfile
import threading
import time
from datetime import datetime
from tkinter import filedialog, messagebox, END

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ✅ URL do SIGED — altere se necessário
SIGED_URL = "https://siged.sefaz.am.gov.br/"


class AnaliseController:
    def __init__(self, usuario, repo, repo_ap, sefaz_repo):
        self.usuario = usuario
        self.repo = repo
        self.repo_ap = repo_ap
        self.sefaz_repo = sefaz_repo
        
        self.driver = None
        self.driver_lock = threading.Lock()
        self.driver_thread = None

    def formatar_cpf(self, cpf_texto):
        """Formata CPF automaticamente"""
        if not cpf_texto:
            return ""
            
        cpf_limpo = re.sub(r"\D", "", cpf_texto)
        cpf_limpo = cpf_limpo[:11]
        
        if len(cpf_limpo) == 11:
            return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
        return cpf_limpo

    def limpar_cpf(self, cpf_texto):
        """Remove formatação do CPF"""
        return re.sub(r"\D", "", cpf_texto)

    def validar_cpf(self, cpf_texto):
        """Valida se CPF tem 11 dígitos"""
        cpf_limpo = self.limpar_cpf(cpf_texto)
        return len(cpf_limpo) == 11

    def visualizar_pdf(self, analise_id):
        """Abre o PDF temporariamente para visualização"""
        if not analise_id:
            return False, "ID da análise não encontrado"
        
        try:
            resultado = self.repo.buscar_pdf_binario(analise_id)
            
            if not resultado or not resultado.get('pdf_conteudo'):
                return False, "PDF não encontrado no banco de dados"
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(resultado['pdf_conteudo'])
                temp_path = temp_file.name
            
            if sys.platform == "win32":
                os.startfile(temp_path)
            elif sys.platform == "darwin":
                subprocess.run(["open", temp_path])
            else:
                subprocess.run(["xdg-open", temp_path])
            
            threading.Timer(30, lambda: os.unlink(temp_path) if os.path.exists(temp_path) else None).start()
            
            return True, "PDF aberto com sucesso"
            
        except Exception as e:
            return False, f"Erro ao visualizar PDF: {str(e)}"

    def baixar_pdf(self, analise_id, nome_sugerido):
        """Baixa o PDF para o disco"""
        try:
            resultado = self.repo.buscar_pdf_binario(analise_id)
            
            if not resultado or not resultado.get('pdf_conteudo'):
                return False, "PDF não encontrado"
            
            caminho = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                initialfile=nome_sugerido.replace('/', '_').replace('\\', '_'),
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )
            
            if caminho:
                with open(caminho, 'wb') as f:
                    f.write(resultado['pdf_conteudo'])
                return True, caminho
            else:
                return False, "Operação cancelada"
                
        except Exception as e:
            return False, f"Erro ao baixar PDF: {str(e)}"

    def salvar_pdfs(self, caminhos, urgencia):
        """Salva múltiplos PDFs no banco"""
        sucesso = 0
        erros = []
        
        for caminho in caminhos:
            nome_pdf = os.path.basename(caminho)
            
            try:
                self.repo.salvar_pdf(
                    nome_pdf=nome_pdf,
                    caminho_pdf=caminho,
                    urgencia=urgencia,
                    usuario=self.usuario
                )
                sucesso += 1
            except Exception as e:
                erros.append(f"{nome_pdf}: {str(e)}")

        return sucesso, erros

    def processar_registros(self, ids, novo_status):
        """Processa registros selecionados"""
        try:
            # Busca o status atual de cada registro antes de alterar
            status_anterior = "PENDENTE"
            try:
                primeiro = self.repo.buscar_por_id(ids[0])
                if primeiro and primeiro.get("status"):
                    status_anterior = primeiro["status"]
            except Exception:
                pass

            self.repo.atualizar_status(ids, novo_status)
            self.repo.salvar_historico(
                ids=ids,
                status_anterior=status_anterior,
                novo_status=novo_status,
                usuario=self.usuario
            )
            return True, f"{len(ids)} PDF(s) movidos para {novo_status}."
        except Exception as e:
            return False, f"Erro ao processar: {str(e)}"

    def processar_devolucao(self, ids, motivo):
        """Processa devolução de registros"""
        try:
            # Busca o status atual de cada registro antes de alterar
            status_anterior = "PENDENTE"
            try:
                primeiro = self.repo.buscar_por_id(ids[0])
                if primeiro and primeiro.get("status"):
                    status_anterior = primeiro["status"]
            except Exception:
                pass

            self.repo.atualizar_status(ids, "DEVOLUCAO", motivo)
            self.repo.salvar_historico(
                ids=ids,
                status_anterior=status_anterior,
                novo_status="DEVOLUCAO",
                usuario=self.usuario,
                motivo=motivo,
            )
            return True, f"{len(ids)} PDF(s) movidos para DEVOLUÇÃO."
        except Exception as e:
            return False, f"Erro ao processar devolução: {str(e)}"

    def abrir_sefaz(self):
        """Abre navegador com SIGED e Google Maps, fazendo login automático."""
        try:
            # ✅ CORRIGIDO: obter_credencial() — método correto do SefazRepository
            credenciais = self.sefaz_repo.obter_credencial()
            
            if not credenciais:
                return False, "Credenciais SIGED não encontradas"

            cpf   = credenciais.get('usuario', '')
            senha = credenciais.get('senha', '')

            with self.driver_lock:
                if self.driver:
                    try:
                        self.driver.quit()
                    except:
                        pass

                options = webdriver.ChromeOptions()
                options.add_experimental_option("detach", True)
                options.add_argument("--start-maximized")
                
                try:
                    self.driver = webdriver.Chrome(
                        service=Service(ChromeDriverManager().install()),
                        options=options
                    )
                except Exception as e:
                    return False, f"Erro ao iniciar Chrome: {str(e)}"

                # ✅ Abre o SIGED
                self.driver.get(SIGED_URL)
                time.sleep(2)

                try:
                    wait = WebDriverWait(self.driver, 15)

                    # ✅ Campo CPF — tenta múltiplos seletores comuns
                    campo_cpf = None
                    for seletor in ["cpf", "username", "login", "usuario", "user"]:
                        try:
                            campo_cpf = wait.until(
                                EC.presence_of_element_located((By.ID, seletor))
                            )
                            break
                        except Exception:
                            pass
                    if not campo_cpf:
                        campo_cpf = self.driver.find_element(
                            By.XPATH,
                            "//input[@type='text'] | //input[@type='email']"
                        )

                    campo_cpf.clear()
                    campo_cpf.send_keys(cpf)

                    # ✅ Campo senha
                    campo_senha = self.driver.find_element(
                        By.XPATH, "//input[@type='password']"
                    )
                    campo_senha.clear()
                    campo_senha.send_keys(senha)

                    # ✅ Botão login — tenta múltiplos padrões
                    try:
                        btn = self.driver.find_element(
                            By.XPATH,
                            "//button[@type='submit'] | //input[@type='submit'] | "
                            "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
                            "'abcdefghijklmnopqrstuvwxyz'),'entrar')] | "
                            "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
                            "'abcdefghijklmnopqrstuvwxyz'),'login')]"
                        )
                    except Exception:
                        btn = self.driver.find_element(By.ID, "btnLogin")

                    btn.click()
                    time.sleep(3)
                    
                except Exception as e:
                    print(f"Login automático SIGED não concluído: {e}")

                self.driver.execute_script("window.open('https://www.google.com/maps', '_blank');")
                self.driver.switch_to.window(self.driver.window_handles[0])

            return True, "SIGED e Google Maps abertos com sucesso"
            
        except Exception as e:
            return False, f"Erro ao abrir SIGED: {str(e)}"

    def fechar_driver(self):
        """Fecha o driver do Selenium"""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
            except:
                pass

    def salvar_registro(self, tipo, dados):
        try:
            memorando = dados["memorando"]

            if tipo == "insc":
                self.repo_ap.salvar_inscricao(
                    nome      = dados["nome"],
                    cpf       = dados["cpf"],
                    municipio = dados["municipio"],
                    memorando = memorando,
                    tipo      = dados["tipo"],
                    usuario   = self.usuario,
                )
                return True, "Inscrição salva com sucesso!"
            else:
                motivo_completo = f"[{dados['categoria']}] {dados['motivo']}"
                self.repo_ap.salvar_devolucao(
                    nome      = dados["nome"],
                    cpf       = dados["cpf"],
                    municipio = dados["municipio"],
                    memorando = memorando,
                    motivo    = motivo_completo,
                    usuario   = self.usuario,
                )
                return True, "Devolução salva com sucesso!"
        except Exception as e:
            return False, f"Erro ao salvar: {e}"

    def carregar_registros_pendentes(self):
        """Carrega registros pendentes do banco"""
        try:
            return self.repo.listar_pendentes()
        except Exception as e:
            raise Exception(f"Erro ao carregar dados: {str(e)}")

    def carregar_historico(self, filtro_status="TODOS", pesquisa=""):
        """Carrega histórico completo do banco; filtragem fica na view."""
        try:
            return self.repo.listar_historico()
        except Exception as e:
            raise Exception(f"Erro ao carregar histórico: {str(e)}")