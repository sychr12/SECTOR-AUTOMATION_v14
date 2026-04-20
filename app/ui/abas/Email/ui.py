# -*- coding: utf-8 -*-
"""
Interface para baixar emails com anexos PDF do Gmail
Com persistência em SQL Server — PDFs armazenados como VARBINARY(MAX)
Versão PyQt6
"""
import threading
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar,
    QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor
import os

from .controller import EmailDownloadController
from .services import EmailDownloadService
from .repository import EmailDownloadRepository

# ── Paleta Corporativa ──────────────────────────────────────────────────────────
_PRIMARY_DARK = "#0a2540"
_PRIMARY = "#1a4b6e"
_ACCENT = "#2c6e9e"
_ACCENT_DARK = "#1e4a6e"
_ACCENT_LIGHT = "#e8f0f8"
_BRANCO = "#ffffff"
_CINZA_BG = "#f5f7fc"
_CINZA_BORDER = "#e2e8f0"
_CINZA_MEDIO = "#5a6e8a"
_CINZA_TEXTO = "#1e2f3e"
_VERDE_STATUS = "#10b981"
_AMARELO = "#f59e0b"
_VERMELHO = "#ef4444"
_AZUL_INFO = "#3b82f6"
_ICON_COLOR = "#1e293b"


def _safe_print(msg: str) -> None:
    """Print seguro para terminais Windows."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", errors="replace").decode("ascii"))


class ProgressoDownload(QWidget):
    """Barra de progresso com status"""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 8px;
                background-color: {_CINZA_BORDER};
                height: 8px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {_VERDE_STATUS};
                border-radius: 8px;
            }}
        """)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Pronto")
        self.status_label.setFont(QFont("Segoe UI", 10))
        self.status_label.setStyleSheet(f"color: {_CINZA_MEDIO};")
        layout.addWidget(self.status_label)

    def atualizar(self, valor, status=""):
        self.progress_bar.setValue(valor)
        if status:
            self.status_label.setText(status)

    def reset(self):
        self.progress_bar.setValue(0)
        self.status_label.setText("Pronto")


class EstatisticasDownload(QWidget):
    """Painel de estatísticas"""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        self.lbl_emails = self._create_stat_card("E-mails", "0")
        self.lbl_arquivos = self._create_stat_card("Anexos", "0")
        self.lbl_sucessos = self._create_stat_card("Sucessos", "0")
        self.lbl_erros = self._create_stat_card("Erros", "0")
        self.lbl_ultimo = self._create_stat_card("Ultima execucao", "---")

        layout.addWidget(self.lbl_emails)
        layout.addWidget(self.lbl_arquivos)
        layout.addWidget(self.lbl_sucessos)
        layout.addWidget(self.lbl_erros)
        layout.addWidget(self.lbl_ultimo, 1)

    def _create_stat_card(self, title, value):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {_BRANCO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 12px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)

        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Segoe UI", 10))
        lbl_title.setStyleSheet(f"color: {_CINZA_MEDIO};")
        layout.addWidget(lbl_title)

        lbl_value = QLabel(value)
        lbl_value.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        lbl_value.setStyleSheet(f"color: {_CINZA_TEXTO};")
        layout.addWidget(lbl_value)

        return card

    def atualizar(self, emails, anexos, sucessos, erros):
        self._set_value(self.lbl_emails, str(emails))
        self._set_value(self.lbl_arquivos, str(anexos))
        self._set_value(self.lbl_sucessos, str(sucessos))
        self._set_value(self.lbl_erros, str(erros))

    def atualizar_ultima_execucao(self, data):
        self._set_value(self.lbl_ultimo, data)

    def _set_value(self, card, value):
        for child in card.findChildren(QLabel):
            if child.font().pointSize() == 18:
                child.setText(value)

    def reset(self):
        self.atualizar(0, 0, 0, 0)
        self.atualizar_ultima_execucao("---")


class LogTableView(QWidget):
    """Tabela de histórico com coluna de ação de download."""

    COLUNAS = ["status", "remetente", "assunto", "arquivo", "criado_em", "acao"]
    CABECALHOS = {
        "status": "Status",
        "remetente": "Remetente",
        "assunto": "Assunto",
        "arquivo": "Arquivo",
        "criado_em": "Data/Hora",
        "acao": "Acao",
    }

    def __init__(self, parent=None, on_download_click=None):
        super().__init__(parent)
        self.on_download_click = on_download_click
        self._create_table()

    def _create_table(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        lbl_title = QLabel("Historico de Downloads")
        lbl_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(lbl_title)

        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {_BRANCO};
                border-radius: 12px;
                border: 1px solid {_CINZA_BORDER};
            }}
        """)
        frame_layout = QVBoxLayout(frame)

        self.table = QTableWidget()
        self.table.setColumnCount(len(self.COLUNAS))
        self.table.setHorizontalHeaderLabels([self.CABECALHOS[col] for col in self.COLUNAS])
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {_BRANCO};
                border: none;
                gridline-color: {_CINZA_BORDER};
            }}
            QTableWidget::item {{
                padding: 8px;
            }}
            QHeaderView::section {{
                background-color: {_ACCENT_LIGHT};
                color: {_ACCENT};
                padding: 8px;
                font-weight: bold;
            }}
        """)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        self.table.itemDoubleClicked.connect(self._on_double_click)

        frame_layout.addWidget(self.table)
        layout.addWidget(frame)

    def _on_double_click(self, item):
        row = item.row()
        record_id_item = self.table.item(row, 0)
        if record_id_item:
            record_id = record_id_item.data(Qt.ItemDataRole.UserRole)
            if record_id and self.on_download_click:
                self.on_download_click(record_id)

    def adicionar_linha(self, record_id: int, status: str, remetente: str,
                        assunto: str, arquivo: str, criado_em: str):
        row = self.table.rowCount()
        self.table.insertRow(row)

        status_colors = {
            "sucesso": _VERDE_STATUS,
            "erro": _VERMELHO,
            "info": _AZUL_INFO,
            "ok": _VERDE_STATUS,
            "iniciando": _AMARELO,
        }
        color = status_colors.get(status.lower(), _CINZA_MEDIO)

        status_item = QTableWidgetItem(status.upper())
        status_item.setForeground(QColor(color))
        status_item.setData(Qt.ItemDataRole.UserRole, record_id)

        self.table.setItem(row, 0, status_item)
        self.table.setItem(row, 1, QTableWidgetItem(remetente))
        self.table.setItem(row, 2, QTableWidgetItem(assunto))
        self.table.setItem(row, 3, QTableWidgetItem(arquivo))
        self.table.setItem(row, 4, QTableWidgetItem(criado_em))
        self.table.setItem(row, 5, QTableWidgetItem("Baixar"))

    def carregar_do_banco(self, registros: list):
        self.limpar()
        for r in registros:
            data_fmt = ""
            if r.get("criado_em"):
                try:
                    if isinstance(r["criado_em"], datetime):
                        data_fmt = r["criado_em"].strftime("%d/%m/%Y %H:%M")
                    else:
                        data_fmt = str(r["criado_em"])
                except Exception:
                    data_fmt = str(r["criado_em"])
            self.adicionar_linha(
                record_id=r["id"],
                status="sucesso",
                remetente=r.get("remetente", ""),
                assunto=r.get("assunto", ""),
                arquivo=r.get("nome_arquivo", ""),
                criado_em=data_fmt,
            )

    def limpar(self):
        self.table.setRowCount(0)


class BaixarEmailUI(QWidget):
    """Interface para download de emails com anexos PDF."""

    def __init__(self, parent=None, usuario=None, conectar_bd=None):
        super().__init__(parent)
        self.usuario = usuario
        self.conectar_bd = conectar_bd

        self.BASE_DIR = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
        )

        self.controller = EmailDownloadController(
            base_dir=self.BASE_DIR,
            save_directory="",
            usuario=usuario,
        )
        self.service = EmailDownloadService(self.BASE_DIR)
        self.repository = EmailDownloadRepository()

        self.emails_processados = 0
        self.arquivos_baixados = 0
        self.sucessos = 0
        self.erros = 0
        self.log_table = None

        self.setStyleSheet(f"background-color: {_CINZA_BG};")
        self._criar_interface()

        threading.Thread(target=self._init_banco, daemon=True).start()

    def _init_banco(self):
        try:
            if self.conectar_bd:
                conn = self.conectar_bd()
                conn.close()
            _safe_print("[EmailDownloadUI] Conexao com banco estabelecida.")
            self.repository.criar_tabela()
        except Exception as e:
            _safe_print(f"[EmailDownloadUI] Erro: {e}")
        self._carregar_historico()

    def _criar_interface(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        self._criar_header(layout)
        self._criar_painel_controle(layout)
        self._criar_cards_informativos(layout)
        self._criar_tabela(layout)
        self._criar_estatisticas(layout)

    def _criar_header(self, parent_layout):
        title = QLabel("Download de E-mails")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {_CINZA_TEXTO};")
        parent_layout.addWidget(title)

        subtitle = QLabel("Anexos PDF recebidos no Gmail — armazenados no banco de dados")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setStyleSheet(f"color: {_CINZA_MEDIO};")
        parent_layout.addWidget(subtitle)

    def _criar_painel_controle(self, parent_layout):
        panel_layout = QHBoxLayout()
        panel_layout.setSpacing(12)

        self.btn_baixar = QPushButton("Iniciar Download")
        self.btn_baixar.setFixedHeight(48)
        self.btn_baixar.setStyleSheet(f"""
            QPushButton {{
                background-color: {_ACCENT};
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
                padding: 0 24px;
            }}
            QPushButton:hover {{
                background-color: {_ACCENT_DARK};
            }}
        """)
        self.btn_baixar.clicked.connect(self.iniciar_download)
        panel_layout.addWidget(self.btn_baixar)

        btn_recarregar = QPushButton("Recarregar")
        btn_recarregar.setFixedHeight(48)
        btn_recarregar.setStyleSheet(f"""
            QPushButton {{
                background-color: {_CINZA_BG};
                color: {_CINZA_TEXTO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 10px;
                font-size: 13px;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background-color: {_ACCENT_LIGHT};
            }}
        """)
        btn_recarregar.clicked.connect(self._carregar_historico)
        panel_layout.addWidget(btn_recarregar)

        self.btn_baixar_todos = QPushButton("Baixar Todos")
        self.btn_baixar_todos.setFixedHeight(48)
        self.btn_baixar_todos.setStyleSheet(f"""
            QPushButton {{
                background-color: {_VERDE_STATUS};
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 13px;
                font-weight: bold;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background-color: #059669;
            }}
        """)
        self.btn_baixar_todos.clicked.connect(self._baixar_todos_pdfs)
        panel_layout.addWidget(self.btn_baixar_todos)

        btn_limpar = QPushButton("Limpar Logs")
        btn_limpar.setFixedHeight(48)
        btn_limpar.setStyleSheet(f"""
            QPushButton {{
                background-color: {_CINZA_BG};
                color: {_CINZA_TEXTO};
                border: 1px solid {_CINZA_BORDER};
                border-radius: 10px;
                font-size: 13px;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background-color: {_VERMELHO};
                color: white;
            }}
        """)
        btn_limpar.clicked.connect(self._limpar_logs)
        panel_layout.addWidget(btn_limpar)

        self.progresso = ProgressoDownload()
        panel_layout.addWidget(self.progresso, 1)

        parent_layout.addLayout(panel_layout)

    def _criar_cards_informativos(self, parent_layout):
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)

        card_storage = self._create_info_card("Armazenamento", "PDFs salvos diretamente no banco de dados (SQL Server)")
        cards_layout.addWidget(card_storage, 1)

        card_api = self._create_info_card("Status da API Google", "Pronto para autenticar")
        self.lbl_status_api = self._find_status_label(card_api)
        cards_layout.addWidget(card_api, 1)

        parent_layout.addLayout(cards_layout)

    def _create_info_card(self, title, content):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {_ACCENT_LIGHT};
                border-radius: 12px;
                border: 1px solid {_CINZA_BORDER};
            }}
        """)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)

        text_layout = QVBoxLayout()
        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        text_layout.addWidget(lbl_title)

        lbl_content = QLabel(content)
        lbl_content.setObjectName("status")
        lbl_content.setFont(QFont("Segoe UI", 11))
        lbl_content.setStyleSheet(f"color: {_CINZA_MEDIO};")
        text_layout.addWidget(lbl_content)

        layout.addLayout(text_layout, 1)
        return card

    def _find_status_label(self, card):
        for child in card.findChildren(QLabel):
            if child.objectName() == "status":
                return child
        return None

    def _criar_tabela(self, parent_layout):
        self.log_table = LogTableView(self, on_download_click=self._baixar_pdf_do_banco)
        parent_layout.addWidget(self.log_table)

    def _criar_estatisticas(self, parent_layout):
        self.estatisticas = EstatisticasDownload()
        parent_layout.addWidget(self.estatisticas)

    def _carregar_historico(self):
        threading.Thread(target=self._worker_historico, daemon=True).start()

    def _worker_historico(self):
        try:
            registros = self.repository.listar_downloads(limit=200)
            QTimer.singleShot(0, lambda: self._aplicar_historico(registros))
        except Exception as exc:
            _safe_print(f"[EmailDownloadUI] Erro ao carregar historico: {exc}")

    def _aplicar_historico(self, registros: list):
        if self.log_table:
            self.log_table.carregar_do_banco(registros)

    def _baixar_pdf_do_banco(self, record_id: int):
        try:
            resultado = self.repository.baixar_bytes_por_id(record_id)
            if not resultado:
                QMessageBox.warning(self, "Aviso", "Registro nao encontrado no banco.")
                return

            nome_arquivo, dados = resultado

            if not dados:
                QMessageBox.critical(self, "Erro", "Nenhum dado encontrado para este registro.")
                return

            destino, _ = QFileDialog.getSaveFileName(
                self,
                "Salvar PDF como...",
                nome_arquivo or "anexo.pdf",
                "PDF Files (*.pdf)"
            )
            if not destino:
                return

            with open(destino, "wb") as f:
                f.write(dados)

            QMessageBox.information(self, "Sucesso", f"PDF salvo em:\n{destino}")

        except Exception as exc:
            QMessageBox.critical(self, "Erro", f"Falha ao baixar PDF:\n{exc}")

    def _baixar_todos_pdfs(self):
        pasta_destino = QFileDialog.getExistingDirectory(
            self,
            "Selecione a pasta para salvar todos os PDFs"
        )

        if not pasta_destino:
            return

        try:
            registros = self.repository.listar_downloads(limit=1000)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao buscar registros: {e}")
            return

        if not registros:
            QMessageBox.information(self, "Info", "Nenhum PDF encontrado no historico")
            return

        resposta = QMessageBox.question(
            self,
            "Confirmar",
            f"Voce esta prestes a baixar {len(registros)} arquivos PDF.\n\n"
            f"Pasta de destino: {pasta_destino}\n\n"
            "Deseja continuar?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if resposta != QMessageBox.StandardButton.Yes:
            return

        self.btn_baixar.setEnabled(False)
        self.btn_baixar_todos.setEnabled(False)

        threading.Thread(
            target=self._executar_download_todos,
            args=(registros, pasta_destino),
            daemon=True
        ).start()

    def _executar_download_todos(self, registros, pasta_destino):
        total = len(registros)
        sucessos = 0
        erros = 0

        for i, registro in enumerate(registros):
            try:
                record_id = registro["id"]
                nome_arquivo = registro["nome_arquivo"]

                resultado = self.repository.baixar_bytes_por_id(record_id)
                if not resultado:
                    erros += 1
                    continue

                nome, dados = resultado

                nome_limpo = "".join(c for c in nome if c.isalnum() or c in ".-_ ").strip()
                if not nome_limpo:
                    nome_limpo = f"anexo_{record_id}.pdf"

                municipio_raw = registro.get("municipio") or "Desconhecido"
                municipio_dir = "".join(c for c in municipio_raw if c.isalnum() or c in " _-").strip() or "Desconhecido"

                data_email = registro.get("data_email")
                if data_email and hasattr(data_email, "year"):
                    ano = data_email.year
                else:
                    ano = datetime.now().year

                subpasta = os.path.join(pasta_destino, f"email {ano}", municipio_dir)
                os.makedirs(subpasta, exist_ok=True)

                caminho = os.path.join(subpasta, nome_limpo)

                contador = 1
                while os.path.exists(caminho):
                    nome_sem_ext = os.path.splitext(nome_limpo)[0]
                    ext = os.path.splitext(nome_limpo)[1]
                    caminho = os.path.join(subpasta, f"{nome_sem_ext}_{contador}{ext}")
                    contador += 1

                with open(caminho, "wb") as f:
                    f.write(dados)

                sucessos += 1

                percentual = int((i + 1) / total * 100)
                QTimer.singleShot(0, lambda p=percentual, t=f"{i+1}/{total}: {nome_limpo}":
                                  self.progresso.atualizar(p, t))

            except Exception:
                erros += 1

        QTimer.singleShot(0, lambda: self.progresso.atualizar(100, f"Download concluido! {sucessos} sucessos, {erros} erros"))
        QTimer.singleShot(0, lambda: self.btn_baixar.setEnabled(True))
        QTimer.singleShot(0, lambda: self.btn_baixar_todos.setEnabled(True))

        QTimer.singleShot(0, lambda: QMessageBox.information(
            self,
            "Download Concluido",
            f"Download finalizado!\n\n"
            f"Pasta: {pasta_destino}\n"
            f"Sucessos: {sucessos}\n"
            f"Erros: {erros}\n"
            f"Total: {total}"
        ))

    def iniciar_download(self):
        self.btn_baixar.setEnabled(False)
        self.progresso.reset()
        self._resetar_estatisticas()
        threading.Thread(target=self._executar_fluxo_download, daemon=True).start()

    def _executar_fluxo_download(self):
        try:
            self._atualizar_progresso(0, "Autenticando no Google...")
            self._log("Iniciando", "Autenticando no Google...")

            sucesso, mensagem = self.service.autenticar()
            if not sucesso:
                self._log("Erro", mensagem)
                self._atualizar_status_api("Falha: " + mensagem, _VERMELHO)
                self._finalizar_fluxo(False)
                return

            self._log("OK", "Autenticacao bem-sucedida.")
            self._atualizar_status_api("Autenticado com sucesso", _VERDE_STATUS)
            self._atualizar_progresso(10, "Buscando e-mails...")

            emails, mensagem = self.service.buscar_emails_nao_lidos_com_anexos()
            self._log("Info", mensagem)

            if not emails:
                self._log("Info", "Nenhum e-mail encontrado.")
                self._finalizar_fluxo(True)
                return

            total = len(emails)
            self._atualizar_progresso(20, f"Processando {total} e-mails...")

            for i, email in enumerate(emails, start=1):
                try:
                    self._processar_email(email)
                    self.emails_processados += 1
                    self._log("OK", f"E-mail {i}/{total} processado.")
                    self._atualizar_progresso(
                        int(20 + (i / total) * 70),
                        f"Processando e-mail {i} de {total}",
                    )
                except Exception as exc:
                    self.erros += 1
                    self._log("Erro", f"E-mail {i}: {exc}")

            self._atualizar_estatisticas()
            self._atualizar_progresso(100, "Download concluido!")
            self._carregar_historico()
            self._finalizar_fluxo(True)

        except Exception as exc:
            self._log("Erro Critico", str(exc))
            self._finalizar_fluxo(False)

    def _processar_email(self, email):
        service = self.service.obter_service()
        if not service:
            raise Exception("Servico do Gmail nao disponivel")

        msg_id = email["id"]
        remetente = self.service.extrair_cabecalho_email(email, "From", "Desconhecido")
        assunto = self.service.extrair_cabecalho_email(email, "Subject", "Sem assunto")
        municipio = self.controller.obter_municipio_por_email(remetente)
        data = self.controller.formatar_data(email["internalDate"])

        try:
            data_email = datetime.strptime(data, "%d-%m-%Y")
        except Exception:
            data_email = None

        parts = email["payload"].get("parts", [])
        for part in self.controller.extrair_parts_pdf(parts):
            nome, dados, erro = self.controller.obter_bytes_anexo_pdf(service, msg_id, part)

            record_id = self.repository.registrar_download(
                msg_id=f"{msg_id}_{nome or 'erro'}",
                remetente=remetente,
                assunto=assunto,
                municipio=municipio,
                data_email=data_email,
                nome_arquivo=nome or "Error.pdf",
                arquivo_bytes=dados,
                erro_mensagem=erro if erro else None,
            )

            if dados:
                self.arquivos_baixados += 1
                self.sucessos += 1
                self._log("OK", f"Salvo no banco: {nome}")
                QTimer.singleShot(0, lambda rid=record_id, r=remetente, a=assunto, n=nome:
                                  self._adicionar_linha_safe(rid, r, a, n))
            else:
                self.erros += 1
                self._log("Erro", f"Falha: {erro}")

        self.controller.marcar_email_como_processado(service, msg_id, "salvo")

    def _adicionar_linha_safe(self, record_id, remetente, assunto, nome):
        if self.log_table:
            self.log_table.adicionar_linha(
                record_id, "sucesso",
                remetente, assunto, nome,
                datetime.now().strftime("%d/%m/%Y %H:%M"),
            )

    def _log(self, status, mensagem):
        _safe_print(f"[{status}] {mensagem}")

    def _atualizar_progresso(self, valor, status=""):
        QTimer.singleShot(0, lambda: self.progresso.atualizar(valor, status))

    def _atualizar_status_api(self, texto, cor):
        if self.lbl_status_api:
            QTimer.singleShot(0, lambda: self.lbl_status_api.setText(texto))

    def _atualizar_estatisticas(self):
        QTimer.singleShot(0, lambda: self.estatisticas.atualizar(
            self.emails_processados,
            self.arquivos_baixados,
            self.sucessos,
            self.erros,
        ))
        QTimer.singleShot(0, lambda: self.estatisticas.atualizar_ultima_execucao(
            datetime.now().strftime("%d/%m/%Y %H:%M")
        ))

    def _resetar_estatisticas(self):
        self.emails_processados = 0
        self.arquivos_baixados = 0
        self.sucessos = 0
        self.erros = 0
        QTimer.singleShot(0, lambda: self.estatisticas.reset())

    def _finalizar_fluxo(self, sucesso: bool):
        def apply():
            if sucesso:
                self.progresso.atualizar(100, "Download concluido com sucesso!")
                QMessageBox.information(self, "Sucesso", "Download concluido!")
            else:
                self.progresso.atualizar(0, "Falha no download")
            self.btn_baixar.setEnabled(True)
        QTimer.singleShot(0, apply)

    def _limpar_logs(self):
        if self.log_table:
            self.log_table.limpar()
        self._resetar_estatisticas()
        self.progresso.reset()