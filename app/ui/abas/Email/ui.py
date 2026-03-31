# -*- coding: utf-8 -*-
"""
Interface para baixar emails com anexos PDF do Gmail
Com persistência em SQL Server — PDFs armazenados como VARBINARY(MAX)
"""
import threading
from datetime import datetime
from tkinter import messagebox, filedialog
import customtkinter as ctk
from tkinter import ttk
from PIL import Image, ImageOps
import os

from .controller import EmailDownloadController
from .services import EmailDownloadService
from .views import ProgressoDownload, EstatisticasDownload
from .repository import EmailDownloadRepository


# ── Paleta Corporativa ──────────────────────────────────────────────────────────
_PRIMARY_DARK    = "#0a2540"
_PRIMARY         = "#1a4b6e"
_ACCENT          = "#2c6e9e"
_ACCENT_DARK     = "#1e4a6e"
_ACCENT_LIGHT    = "#e8f0f8"
_BRANCO          = "#ffffff"
_CINZA_BG        = "#f5f7fc"
_CINZA_BORDER    = "#e2e8f0"
_CINZA_MEDIO     = "#5a6e8a"
_CINZA_TEXTO     = "#1e2f3e"
_VERDE_STATUS    = "#10b981"
_VERDE_HOVER     = "#d1fae5"
_AMARELO         = "#f59e0b"
_VERMELHO        = "#ef4444"
_AZUL_INFO       = "#3b82f6"
_ICON_COLOR      = "#1e293b"  # Preto suave para os ícones


def _safe_print(msg: str) -> None:
    """Print seguro para terminais Windows que não suportam UTF-8."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", errors="replace").decode("ascii"))


# ---------------------------------------------------------------------------
# Classe para gerenciar ícones dos cards
# ---------------------------------------------------------------------------
class IconManager:
    """Gerenciador de ícones para os cards"""
    
    def __init__(self):
        self.icons = {}
        # Caminho base do projeto
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
        # Caminho para a pasta de ícones de email
        self.icons_dir = os.path.join(self.base_dir, "images", "icons", "email")
        
    def load_icon(self, filename, size=(32, 32), colorize_to=None):
        """Carrega um ícone da pasta images/icons/email e opcionalmente aplica cor"""
        try:
            path = os.path.join(self.icons_dir, filename)
            if os.path.exists(path):
                img = Image.open(path)
                img = img.resize(size, Image.Resampling.LANCZOS)
                
                # Se for para colorir o ícone
                if colorize_to:
                    # Converte para RGBA se necessário
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    
                    # Obtém os dados da imagem
                    data = img.getdata()
                    new_data = []
                    
                    # Define a cor de destino (RGB)
                    if isinstance(colorize_to, tuple):
                        target_r, target_g, target_b = colorize_to
                    else:
                        # Se for string hex, converte para RGB
                        hex_color = colorize_to.lstrip('#')
                        target_r, target_g, target_b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                    
                    # Processa cada pixel
                    for item in data:
                        r, g, b, a = item
                        # Mantém a transparência e aplica a nova cor nos pixels não transparentes
                        if a > 0:
                            new_data.append((target_r, target_g, target_b, a))
                        else:
                            new_data.append((r, g, b, a))
                    
                    img.putdata(new_data)
                
                return ctk.CTkImage(light_image=img, dark_image=img, size=size)
            else:
                _safe_print(f"Ícone não encontrado: {path}")
        except Exception as e:
            _safe_print(f"Erro ao carregar ícone {filename}: {e}")
        return None
    
    def setup_icons(self):
        """Configura os ícones dos cards com cor preta"""
        icons_config = {
            "database": ("hard_drive.png", (32, 32), _ICON_COLOR),  # Ícone com cor preta
            "google": ("api.png", (32, 32), _ICON_COLOR),           # Ícone com cor preta
        }
        
        for name, (filename, size, color) in icons_config.items():
            self.icons[name] = self.load_icon(filename, size, color)
            
        # Verificar se os ícones foram carregados
        if self.icons.get("database"):
            _safe_print("✅ Ícone hard_drive.png carregado com sucesso (cor preta aplicada)")
        else:
            _safe_print("⚠️ Ícone hard_drive.png NÃO encontrado em: " + self.icons_dir)
            
        if self.icons.get("google"):
            _safe_print("✅ Ícone api.png carregado com sucesso (cor preta aplicada)")
        else:
            _safe_print("⚠️ Ícone api.png NÃO encontrado em: " + self.icons_dir)
        
        return self.icons


# ---------------------------------------------------------------------------
# Tabela de histórico
# ---------------------------------------------------------------------------
class LogTableView:
    """Tabela de histórico com coluna de ação de download."""

    COLUNAS    = ("status", "remetente", "assunto", "arquivo", "criado_em", "acao")
    CABECALHOS = {
        "status":    ("Status",     100),
        "remetente": ("Remetente", 220),
        "assunto":   ("Assunto",   280),
        "arquivo":   ("Arquivo",   250),
        "criado_em": ("Data/Hora", 150),
        "acao":      ("Ação",      90),
    }
    TAG_CORES = {
        "sucesso":   (_VERDE_STATUS, "#052e16"),
        "erro":      (_VERMELHO, "#450a0a"),
        "info":      (_AZUL_INFO, "#172554"),
        "ok":        (_VERDE_STATUS, "#052e16"),
        "iniciando": (_AMARELO, "#451a03"),
    }

    def __init__(self, parent, on_download_click):
        self.parent = parent
        self.on_download_click = on_download_click
        self.tree = None
        self.container = None
        self._criar()

    def _criar(self):
        """Cria a tabela com design moderno"""
        self.container = ctk.CTkFrame(self.parent, fg_color="transparent")
        
        # Header
        header_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        header_frame.pack(anchor="w", pady=(0, 12))
        
        ctk.CTkLabel(
            header_frame,
            text="Histórico de Downloads",
            font=("Segoe UI", 14, "bold"),
            text_color=_CINZA_TEXTO
        ).pack(side="left")

        # Container da tabela
        frame_tree = ctk.CTkFrame(
            self.container, 
            fg_color=_BRANCO, 
            corner_radius=12,
            border_width=1,
            border_color=_CINZA_BORDER
        )
        frame_tree.pack(fill="both", expand=True)

        # Estilo da Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "EmailDL.Treeview",
            background=_BRANCO,
            fieldbackground=_BRANCO,
            foreground=_CINZA_TEXTO,
            rowheight=40,
            font=("Segoe UI", 11),
            borderwidth=0,
        )
        style.configure(
            "EmailDL.Treeview.Heading",
            background=_ACCENT_LIGHT,
            foreground=_ACCENT,
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            borderwidth=0,
        )
        style.map("EmailDL.Treeview", 
                  background=[("selected", _ACCENT_LIGHT)],
                  foreground=[("selected", _ACCENT)])

        # Treeview
        self.tree = ttk.Treeview(
            frame_tree,
            columns=self.COLUNAS,
            show="headings",
            style="EmailDL.Treeview",
            selectmode="browse",
            height=10
        )
        
        for col in self.COLUNAS:
            titulo, largura = self.CABECALHOS[col]
            self.tree.heading(col, text=titulo)
            self.tree.column(col, width=largura, minwidth=50, stretch=(col == "assunto"))

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_tree, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.tree.pack(side="left", fill="both", expand=True, padx=12, pady=12)
        scrollbar.pack(side="right", fill="y", pady=12)
        
        # Configurar tags de cor
        for tag, (bg, fg) in self.TAG_CORES.items():
            self.tree.tag_configure(tag, background=bg, foreground=fg)
        
        # Bind duplo clique
        self.tree.bind("<Double-1>", self._on_double_click)

    def _on_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if not item:
            return
        tags = self.tree.item(item, "tags")
        if len(tags) >= 2:
            try:
                self.on_download_click(int(tags[1]))
            except (ValueError, TypeError):
                pass

    def adicionar_linha(self, record_id: int, status: str, remetente: str,
                        assunto: str, arquivo: str, criado_em: str):
        tag_cor = status.lower() if status.lower() in self.TAG_CORES else "info"
        self.tree.insert(
            "", 0,
            values=(status, remetente, assunto, arquivo, criado_em, "📥 Baixar"),
            tags=(tag_cor, str(record_id)),
        )

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
        for item in self.tree.get_children():
            self.tree.delete(item)

    def pack(self, **kwargs):
        self.container.pack(**kwargs)


# ---------------------------------------------------------------------------
# UI principal
# ---------------------------------------------------------------------------
class BaixarEmailUI(ctk.CTkFrame):
    """Interface para download de emails com anexos PDF."""

    def __init__(self, master, usuario=None):
        super().__init__(master)
        self.usuario = usuario
        
        # Inicializar gerenciador de ícones
        self.icon_manager = IconManager()
        self.icons = self.icon_manager.setup_icons()

        self.BASE_DIR = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
        )

        self.controller  = EmailDownloadController(
            base_dir=self.BASE_DIR,
            save_directory="",
            usuario=usuario,
        )
        self.service    = EmailDownloadService(self.BASE_DIR)
        self.repository = EmailDownloadRepository()

        self.emails_processados = 0
        self.arquivos_baixados  = 0
        self.sucessos           = 0
        self.erros              = 0
        self.log_table = None

        self._criar_interface()

        # Inicialização em background
        threading.Thread(target=self._init_banco, daemon=True).start()

    # ------------------------------------------------------------------
    # Inicialização do banco em background
    # ------------------------------------------------------------------
    def _init_banco(self):
        try:
            self.repository.criar_tabela()
        except Exception as exc:
            _safe_print(f"[EmailDownloadUI] Aviso: nao foi possivel criar tabela: {exc}")
        self._carregar_historico()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def _criar_interface(self):
        self.configure(fg_color=_CINZA_BG)

        # Container principal
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=32, pady=32)

        # Card principal
        card = ctk.CTkFrame(
            main_container, 
            corner_radius=16, 
            fg_color=_BRANCO,
            border_width=1,
            border_color=_CINZA_BORDER
        )
        card.pack(fill="both", expand=True)

        # Header
        self._criar_header(card)
        self._criar_painel_controle(card)
        self._criar_cards_informativos(card)  # Cards com ícones pretos
        self._criar_tabela(card)
        self._criar_estatisticas(card)

    def _criar_header(self, parent):
        """Cria o cabeçalho com título"""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", padx=32, pady=(32, 24))
        
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left")
        
        ctk.CTkLabel(
            title_frame,
            text="Download de E-mails",
            font=("Segoe UI", 24, "bold"),
            text_color=_CINZA_TEXTO
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_frame,
            text="Anexos PDF recebidos no Gmail — armazenados no banco de dados",
            font=("Segoe UI", 12),
            text_color=_CINZA_MEDIO
        ).pack(anchor="w", pady=(4, 0))

    def _criar_painel_controle(self, parent):
        """Cria o painel de botões de controle"""
        painel = ctk.CTkFrame(parent, fg_color="transparent")
        painel.pack(fill="x", padx=32, pady=(0, 24))

        # Botão de download
        self.btn_baixar = ctk.CTkButton(
            painel,
            text="Iniciar Download",
            command=self.iniciar_download,
            height=48,
            corner_radius=10,
            fg_color=_ACCENT,
            hover_color=_ACCENT_DARK,
            text_color=_BRANCO,
            font=("Segoe UI", 14, "bold")
        )
        self.btn_baixar.pack(side="left", padx=(0, 12))

        # Botão de recarregar
        ctk.CTkButton(
            painel,
            text="Recarregar",
            height=48,
            width=140,
            corner_radius=10,
            fg_color=_CINZA_BG,
            hover_color=_ACCENT_LIGHT,
            text_color=_CINZA_TEXTO,
            font=("Segoe UI", 13),
            command=self._carregar_historico,
        ).pack(side="left", padx=(0, 12))

        # Botão de limpar logs
        ctk.CTkButton(
            painel,
            text="Limpar Logs",
            height=48,
            width=140,
            corner_radius=10,
            fg_color=_CINZA_BG,
            hover_color=_VERMELHO,
            text_color=_CINZA_TEXTO,
            font=("Segoe UI", 13),
            command=self._limpar_logs,
        ).pack(side="left")

        # Barra de progresso
        self.progresso = ProgressoDownload(painel)
        self.progresso.pack(side="left", fill="x", expand=True, padx=(20, 0))

    def _criar_cards_informativos(self, parent):
        """Cria os cards informativos COM ÍCONES PRETOS"""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=32, pady=(0, 24))
        
        # Configurar grid
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)
        
        # ==================== CARD 1: Armazenamento ====================
        card_storage = ctk.CTkFrame(
            container,
            fg_color=_ACCENT_LIGHT,
            corner_radius=12,
            border_width=1,
            border_color=_CINZA_BORDER
        )
        card_storage.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=5)
        
        storage_inner = ctk.CTkFrame(card_storage, fg_color="transparent")
        storage_inner.pack(fill="x", padx=20, pady=16)
        
        # Ícone do card de armazenamento (hard_drive.png) com cor preta
        if self.icons.get("database"):
            icon_label = ctk.CTkLabel(
                storage_inner,
                text="",
                image=self.icons["database"],
                width=32,
                height=32
            )
            icon_label.pack(side="left", padx=(0, 12))
        else:
            # Fallback se o ícone não for encontrado
            ctk.CTkLabel(
                storage_inner,
                text="",
                font=("Segoe UI", 24),
                text_color=_ICON_COLOR  # Usa a cor preta também no fallback
            ).pack(side="left", padx=(0, 12))
        
        # Texto do card
        storage_text_frame = ctk.CTkFrame(storage_inner, fg_color="transparent")
        storage_text_frame.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(
            storage_text_frame,
            text="Armazenamento",
            font=("Segoe UI", 13, "bold"),
            text_color=_CINZA_TEXTO
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            storage_text_frame,
            text="PDFs salvos diretamente no banco de dados (SQL Server)",
            font=("Segoe UI", 11),
            text_color=_CINZA_MEDIO,
            wraplength=300
        ).pack(anchor="w", pady=(4, 0))
        
        # ==================== CARD 2: Status da API Google ====================
        card_api = ctk.CTkFrame(
            container,
            fg_color=_ACCENT_LIGHT,
            corner_radius=12,
            border_width=1,
            border_color=_CINZA_BORDER
        )
        card_api.grid(row=0, column=1, sticky="nsew", padx=(12, 0), pady=5)
        
        api_inner = ctk.CTkFrame(card_api, fg_color="transparent")
        api_inner.pack(fill="x", padx=20, pady=16)
        
        # Ícone do card da API Google (api.png) com cor preta
        if self.icons.get("google"):
            icon_label = ctk.CTkLabel(
                api_inner,
                text="",
                image=self.icons["google"],
                width=32,
                height=32
            )
            icon_label.pack(side="left", padx=(0, 12))
        else:
            # Fallback se o ícone não for encontrado
            ctk.CTkLabel(
                api_inner,
                text="",
                font=("Segoe UI", 24),
                text_color=_ICON_COLOR  # Usa a cor preta também no fallback
            ).pack(side="left", padx=(0, 12))
        
        # Texto do card
        api_text_frame = ctk.CTkFrame(api_inner, fg_color="transparent")
        api_text_frame.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(
            api_text_frame,
            text="Status da API Google",
            font=("Segoe UI", 13, "bold"),
            text_color=_CINZA_TEXTO
        ).pack(anchor="w")
        
        self.lbl_status_api = ctk.CTkLabel(
            api_text_frame,
            text="✅ Pronto para autenticar",
            font=("Segoe UI", 11),
            text_color=_VERDE_STATUS
        )
        self.lbl_status_api.pack(anchor="w", pady=(4, 0))

    def _criar_tabela(self, parent):
        """Cria a tabela de histórico"""
        self.log_table = LogTableView(
            parent, 
            on_download_click=self._baixar_pdf_do_banco
        )
        self.log_table.pack(fill="both", expand=True, padx=32, pady=(0, 24))

    def _criar_estatisticas(self, parent):
        """Cria o rodapé com estatísticas"""
        self.estatisticas = EstatisticasDownload(parent)
        self.estatisticas.pack(fill="x", padx=32, pady=(0, 32))

    # ------------------------------------------------------------------
    # Histórico
    # ------------------------------------------------------------------
    def _carregar_historico(self):
        """Carrega histórico em thread separada"""
        threading.Thread(target=self._worker_historico, daemon=True).start()

    def _worker_historico(self):
        try:
            registros = self.repository.listar_downloads(limit=200)
            self.after(0, self._aplicar_historico, registros)
        except Exception as exc:
            _safe_print(f"[EmailDownloadUI] Erro ao carregar historico: {exc}")

    def _aplicar_historico(self, registros: list):
        """Aplica o histórico na UI"""
        if not self.winfo_exists():
            return
        if self.log_table:
            self.log_table.carregar_do_banco(registros)

    # ------------------------------------------------------------------
    # Download do banco
    # ------------------------------------------------------------------
    def _baixar_pdf_do_banco(self, record_id: int):
        """Baixa PDF do banco"""
        try:
            resultado = self.repository.baixar_bytes_por_id(record_id)
            if not resultado:
                messagebox.showwarning("Aviso", "Registro não encontrado no banco.")
                return

            nome_arquivo, dados = resultado

            if not dados:
                messagebox.showerror("Erro", "Nenhum dado encontrado para este registro.")
                return

            destino = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF", "*.pdf"), ("Todos", "*.*")],
                initialfile=nome_arquivo or "anexo.pdf",
                title="Salvar PDF como...",
            )
            if not destino:
                return

            with open(destino, "wb") as f:
                f.write(dados)

            messagebox.showinfo("Sucesso", f"✅ PDF salvo em:\n{destino}")

        except Exception as exc:
            messagebox.showerror("Erro", f"Falha ao baixar PDF:\n{exc}")

    # ------------------------------------------------------------------
    # Fluxo de download
    # ------------------------------------------------------------------
    def iniciar_download(self):
        self.btn_baixar.configure(state="disabled")
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
                self._atualizar_status_api("❌ " + mensagem, _VERMELHO)
                self._finalizar_fluxo(False)
                return

            self._log("OK", "Autenticação bem-sucedida.")
            self._atualizar_status_api("✅ Autenticado com sucesso", _VERDE_STATUS)
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
            self._atualizar_progresso(100, "Download concluído!")
            self._carregar_historico()
            self._finalizar_fluxo(True)

        except Exception as exc:
            self._log("Erro Crítico", str(exc))
            self._finalizar_fluxo(False)

    def _processar_email(self, email):
        service = self.service.obter_service()
        if not service:
            raise Exception("Serviço do Gmail não disponível")

        msg_id    = email["id"]
        remetente = self.service.extrair_cabecalho_email(email, "From", "Desconhecido")
        assunto   = self.service.extrair_cabecalho_email(email, "Subject", "Sem assunto")
        municipio = self.controller.obter_municipio_por_email(remetente)
        data      = self.controller.formatar_data(email["internalDate"])

        try:
            data_email = datetime.strptime(data, "%d-%m-%Y")
        except Exception:
            data_email = None

        parts = email["payload"].get("parts", [])
        for part in self.controller.extrair_parts_pdf(parts):

            nome, dados, erro = self.controller.obter_bytes_anexo_pdf(service, msg_id, part)

            record_id = self.repository.registrar_download(
                msg_id        = f"{msg_id}_{nome or 'erro'}",
                remetente     = remetente,
                assunto       = assunto,
                municipio     = municipio,
                data_email    = data_email,
                nome_arquivo  = nome or "erro.pdf",
                arquivo_bytes = dados,
                status        = "sucesso" if dados else "erro",
                erro_mensagem = erro if erro else None,
            )

            if dados:
                self.arquivos_baixados += 1
                self.sucessos += 1
                self._log("OK", f"Salvo no banco: {nome}")
                self.after(0, self._adicionar_linha_safe,
                           record_id, remetente, assunto, nome)
            else:
                self.erros += 1
                self._log("Erro", f"Falha: {erro}")

        self.controller.marcar_email_como_processado(service, msg_id, "salvo")

    def _adicionar_linha_safe(self, record_id, remetente, assunto, nome):
        if not self.winfo_exists():
            return
        if self.log_table:
            self.log_table.adicionar_linha(
                record_id, "sucesso",
                remetente, assunto, nome,
                datetime.now().strftime("%d/%m/%Y %H:%M"),
            )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _log(self, status, mensagem):
        _safe_print(f"[{status}] {mensagem}")

    def _atualizar_progresso(self, valor, status=""):
        def _apply():
            if not self.winfo_exists():
                return
            self.progresso.atualizar(valor, status)
        self.after(0, _apply)

    def _atualizar_status_api(self, texto, cor):
        def _apply():
            if not self.winfo_exists():
                return
            self.lbl_status_api.configure(text=texto, text_color=cor)
        self.after(0, _apply)

    def _atualizar_estatisticas(self):
        def _apply():
            if not self.winfo_exists():
                return
            self.estatisticas.atualizar(
                self.emails_processados,
                self.arquivos_baixados,
                self.sucessos,
                self.erros,
            )
            self.estatisticas.atualizar_ultima_execucao(
                datetime.now().strftime("%d/%m/%Y %H:%M")
            )
        self.after(0, _apply)

    def _resetar_estatisticas(self):
        self.emails_processados = 0
        self.arquivos_baixados  = 0
        self.sucessos           = 0
        self.erros              = 0
        def _apply():
            if not self.winfo_exists():
                return
            self.estatisticas.reset()
        self.after(0, _apply)

    def _finalizar_fluxo(self, sucesso: bool):
        def _apply():
            if not self.winfo_exists():
                return
            if sucesso:
                self.progresso.atualizar(100, "Download concluído com sucesso!")
                messagebox.showinfo("Sucesso", "✅ Download concluído!")
            else:
                self.progresso.atualizar(0, "Falha no download")
            self.btn_baixar.configure(state="normal")
        self.after(0, _apply)

    def _limpar_logs(self):
        if not self.winfo_exists():
            return
        if self.log_table:
            self.log_table.limpar()
        self._resetar_estatisticas()
        self.progresso.reset()