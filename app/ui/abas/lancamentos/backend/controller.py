# -*- coding: utf-8 -*-
"""Controller do módulo Lançamento de Processo."""
import os
import re
import subprocess
import sys
import tempfile
import threading
from typing import Optional

from .error_handler import tratar_erro
from .LancamentoRepository import LancamentoRepository

PASTA_IMPRESSAO = r"Q:\PROCESSOS VIA EMAIL\3°PARA IMPRESSAO"


class LancamentoController:

    def __init__(self, usuario: str):
        self.usuario        = usuario
        self.repo           = LancamentoRepository()
        self._banco_antigo  = None
        self._repo_analiseap = None

    # ------------------------------------------------------------------
    # CPF helpers
    # ------------------------------------------------------------------
    @staticmethod
    def formatar_cpf(texto: str) -> str:
        d = re.sub(r"\D", "", texto or "")[:11]
        if len(d) == 11:
            return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"
        return d

    @staticmethod
    def limpar_cpf(texto: str) -> str:
        return re.sub(r"\D", "", texto or "")

    @staticmethod
    def validar_cpf(texto: str) -> bool:
        return len(re.sub(r"\D", "", texto or "")) == 11

    @staticmethod
    def _cpf_para_banco(cpf_raw) -> str:
        limpo = re.sub(r"\D", "", cpf_raw or "")
        return limpo[:11].ljust(11, "0") if limpo else "00000000000"

    # ------------------------------------------------------------------
    # Ler PDF do disco como bytes
    # ------------------------------------------------------------------
    @staticmethod
    def _ler_pdf(caminho: str) -> Optional[bytes]:
        try:
            if caminho and os.path.exists(caminho):
                with open(caminho, "rb") as f:
                    return f.read()
        except Exception:
            pass
        return None

    @staticmethod
    def _pasta_impressao_acessivel() -> bool:
        try:
            return os.path.exists(PASTA_IMPRESSAO) or os.path.exists(
                os.path.splitdrive(PASTA_IMPRESSAO)[0] + "\\"
            )
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Carregar listas por status
    # ------------------------------------------------------------------
    def carregar_devolucoes(self) -> list:
        return self.repo.listar_devolucoes()

    def carregar_por_tipo(self, tipo: str) -> list:
        """Retorna processos filtrados pelo tipo/status (RENOVACAO ou INSCRICAO)."""
        return self.repo.listar_por_tipo(tipo)

    def carregar_pendentes(self) -> list:
        return self.repo.listar_para_lancamento()

    def carregar_para_revisar(self) -> list:
        todos = self.repo.listar_para_lancamento()
        return [r for r in todos if not r.get("lancado_por")]

    def carregar_prontos(self) -> list:
        todos = self.repo.listar_para_lancamento()
        return [r for r in todos if r.get("lancado_por")]

    # ------------------------------------------------------------------
    # Consulta por CPF
    # ------------------------------------------------------------------
    def consultar_cpf(self, cpf_texto: str) -> dict:
        """Consulta CPF nos bancos SQL Server e MySQL CPP"""
        cpf = self.limpar_cpf(cpf_texto)
        if len(cpf) != 11:
            return {
                "cadastrado": False,
                "analises": [], "lancamentos": [],
                "responsavel": "", "status": "",
                "mensagem": "CPF inválido.",
                "cpp_registros": [], "cpp_encontrado": False,
                "ap_registros": [], "ap_encontrado": False,
            }

        resultado_pg = {}
        resultado_cpp = {}
        resultado_ap = {}

        def _buscar_sqlserver():
            try:
                analises = self.repo.buscar_por_cpf(cpf)
                lancamentos = self.repo.historico_por_cpf(cpf)
                resultado_pg["analises"] = analises
                resultado_pg["lancamentos"] = lancamentos
            except Exception as exc:
                resultado_pg["erro"] = str(exc)
                resultado_pg["analises"] = []
                resultado_pg["lancamentos"] = []

        def _buscar_cpp():
            try:
                from services.lancamento_repository import CPPRepository
                self._banco_antigo = CPPRepository()
                todos = self._banco_antigo.buscar_todos()
                cpf_digits = "".join(c for c in cpf if c.isdigit())
                encontrados = [
                    r for r in todos
                    if "".join(c for c in str(r.get("cpf") or "") if c.isdigit()) == cpf_digits
                ]
                resultado_cpp["registros"] = encontrados
            except Exception as exc:
                resultado_cpp["erro"] = str(exc)
                resultado_cpp["registros"] = []

        def _buscar_analiseap():
            try:
                from services.analiseap_repository import AnaliseapRepository
                self._repo_analiseap = AnaliseapRepository()
                regs = self._repo_analiseap.buscar_por_cpf(cpf)
                resultado_ap["registros"] = regs
            except Exception as exc:
                resultado_ap["erro"] = str(exc)
                resultado_ap["registros"] = []

        # Rodar buscas em paralelo
        t1 = threading.Thread(target=_buscar_sqlserver, daemon=True)
        t2 = threading.Thread(target=_buscar_cpp, daemon=True)
        t3 = threading.Thread(target=_buscar_analiseap, daemon=True)
        t1.start()
        t2.start()
        t3.start()
        t1.join()
        t2.join()
        t3.join()

        analises = resultado_pg.get("analises", [])
        lancamentos = resultado_pg.get("lancamentos", [])
        cpp_regs = resultado_cpp.get("registros", [])
        ap_regs = resultado_ap.get("registros", [])

        cadastrado = bool(analises or lancamentos)
        cpp_encontrado = bool(cpp_regs)
        ap_encontrado = bool(ap_regs)
        responsavel = ""
        status = ""

        if analises:
            responsavel = analises[0].get("analisado_por") or ""
            status = analises[0].get("status") or ""
        if not responsavel and lancamentos:
            responsavel = lancamentos[0].get("analisado_por") or ""

        partes = []
        if analises:
            partes.append(f"{len(analises)} análise(s) no banco principal")
        if lancamentos:
            partes.append(f"{len(lancamentos)} lançamento(s) no banco principal")
        if ap_regs:
            partes.append(f"{len(ap_regs)} registro(s) no banco de inscrições")
        if cpp_regs:
            partes.append(f"{len(cpp_regs)} registro(s) no banco CPP")

        tem_dados = bool(partes)

        if tem_dados:
            mensagem = f"CPF encontrado. {' | '.join(partes)}."
            if responsavel:
                mensagem += f" Responsável: {responsavel}."
        elif resultado_pg.get("erro"):
            mensagem = f"Erro no banco principal: {resultado_pg['erro']}"
        else:
            mensagem = "CPF não encontrado em nenhum banco."

        return {
            "cadastrado": cadastrado or cpp_encontrado or ap_encontrado,
            "analises": analises,
            "lancamentos": lancamentos,
            "responsavel": responsavel,
            "status": status,
            "mensagem": mensagem,
            "cpp_registros": cpp_regs,
            "cpp_encontrado": cpp_encontrado,
            "ap_registros": ap_regs,
            "ap_encontrado": ap_encontrado,
        }

    # ------------------------------------------------------------------
    # Abrir PDF
    # ------------------------------------------------------------------
    def abrir_pdf(self, analise_id: int) -> tuple:
        try:
            dado = self.repo.buscar_pdf(analise_id)
            if not dado:
                return False, "Registro não encontrado."

            caminho = dado.get("caminho_pdf") or ""
            if caminho and os.path.exists(caminho):
                self._open_file(caminho)
                return True, "PDF aberto."

            nome_pdf = dado.get("nome_pdf", "")
            if nome_pdf:
                conteudo = self.repo.buscar_pdf_bytes_lancamento(nome_pdf)
                if conteudo:
                    return self._abrir_bytes_temp(conteudo)

            return False, "PDF não encontrado."
        except Exception as exc:
            return False, tratar_erro(exc)

    def visualizar_pdf_banco(self, lancamento_id: int) -> tuple:
        try:
            conteudo = self.repo.buscar_pdf_bytes_por_id(lancamento_id)
            if not conteudo:
                return False, "PDF não encontrado no banco."
            return self._abrir_bytes_temp(conteudo)
        except Exception as exc:
            return False, tratar_erro(exc)

    def baixar_pdf_banco(self, lancamento_id: int,
                          nome_arquivo: str,
                          caminho_salvar: str) -> tuple:
        try:
            conteudo = self.repo.buscar_pdf_bytes_por_id(lancamento_id)
            if not conteudo:
                return False, "PDF não encontrado no banco."
            with open(caminho_salvar, "wb") as f:
                f.write(conteudo)
            return True, caminho_salvar
        except Exception as exc:
            return False, tratar_erro(exc)

    def abrir_arquivo(self, caminho: str):
        if os.path.exists(caminho):
            self._open_file(caminho)

    def _abrir_bytes_temp(self, conteudo: bytes) -> tuple:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(conteudo)
            tmp_path = tmp.name
        self._open_file(tmp_path)
        threading.Timer(60, lambda p=tmp_path: os.unlink(p) if os.path.exists(p) else None).start()
        return True, "PDF aberto."

    @staticmethod
    def _open_file(path: str):
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.run(["open", path])
        else:
            subprocess.run(["xdg-open", path])

    # ------------------------------------------------------------------
    # Registrar lançamento por CPF
    # ------------------------------------------------------------------
    def registrar_por_cpf(self, cpf_texto: str) -> tuple:
        cpf_limpo = self.limpar_cpf(cpf_texto)
        if len(cpf_limpo) != 11:
            return False, "CPF inválido."

        try:
            pendentes = self.repo.buscar_por_cpf(cpf_limpo)
            if not pendentes:
                return False, f"Nenhum processo pendente para CPF {cpf_texto}."

            afetados = self.repo.marcar_lancado_por_cpf(cpf_limpo, self.usuario)

            for p in pendentes:
                caminho = p.get("caminho_pdf", "") or ""
                pdf_bin = self._ler_pdf(caminho)
                try:
                    self.repo.registrar_lancamento(
                        nome_pdf=p["nome_pdf"],
                        cpf=cpf_limpo,
                        analisado_por=p.get("analisado_por") or "",
                        lancado_por=self.usuario,
                        pdf_conteudo=pdf_bin,
                        caminho_pdf=caminho,
                    )
                except Exception:
                    pass

            return True, f"CPF {cpf_texto}: {afetados} processo(s) marcado(s) como LANÇADO."
        except Exception as exc:
            return False, tratar_erro(exc)

    # ------------------------------------------------------------------
    # Enviar para impressão
    # ------------------------------------------------------------------
    def enviar_para_impressao(self, analise_id: int,
                               nome_pdf: str,
                               pasta_origem: str = "") -> tuple:
        import shutil
        try:
            dado = self.repo.buscar_pdf(analise_id)
            if not dado:
                return False, "Registro não encontrado."

            cpf = self._cpf_para_banco(dado.get("cpf"))
            analisado_por = dado.get("usuario") or ""
            caminho_src = dado.get("caminho_pdf") or ""

            if pasta_origem:
                caminho_src = os.path.join(pasta_origem, nome_pdf)

            pdf_bin = self._ler_pdf(caminho_src)

            caminho_destino = ""
            if caminho_src and os.path.exists(caminho_src):
                if self._pasta_impressao_acessivel():
                    try:
                        nome_pasta = os.path.basename(pasta_origem or os.path.dirname(caminho_src))
                        dest_dir = os.path.join(PASTA_IMPRESSAO, nome_pasta)
                        os.makedirs(dest_dir, exist_ok=True)
                        caminho_destino = os.path.join(dest_dir, nome_pdf)
                        shutil.move(caminho_src, caminho_destino)
                    except Exception:
                        caminho_destino = ""

            self.repo.registrar_lancamento(
                nome_pdf=nome_pdf,
                cpf=cpf,
                analisado_por=analisado_por,
                lancado_por=self.usuario,
                pdf_conteudo=pdf_bin,
                caminho_pdf=caminho_destino or caminho_src,
            )
            self.repo.marcar_como_lancado(analise_id, self.usuario)

            msg = f"{nome_pdf} salvo no banco por {self.usuario}."
            if caminho_destino:
                msg = f"{nome_pdf} enviado para impressão e {msg}"
            return True, msg
        except Exception as exc:
            return False, tratar_erro(exc)

    # ------------------------------------------------------------------
    # Estatísticas
    # ------------------------------------------------------------------
    def estatisticas(self) -> dict:
        try:
            return self.repo.estatisticas()
        except Exception:
            return {}

    # ------------------------------------------------------------------
    # Histórico
    # ------------------------------------------------------------------
    def historico(self) -> list:
        return self.repo.historico()