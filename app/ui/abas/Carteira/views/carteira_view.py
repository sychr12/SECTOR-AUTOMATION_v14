# -*- coding: utf-8 -*-
"""
carteira_view.py — Interface principal da Carteira Digital.
Local: app/ui/abas/Carteira/views/carteira_view.py
"""
import os
import re
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image

from ui.base_ui import BaseUI
from app.theme import AppTheme
from ..controller import CarteiraController
from ..carteira_service import CarteiraService
from ..utils.constants import *
from ..utils.formatters import format_cpf, format_date
from ..utils.validators import validate_cpf, validate_date
from ..utils.pdf_parser import PDFParser
from ..assets import open_image
from .historico_view import HistoricoView
from .batch_view import BatchCarteiraView


class CarteiraDigitalUI(BaseUI):
    """Interface principal da carteira digital"""

    def __init__(self, master, usuario):
        super().__init__(master)
        self.usuario = usuario
        self.service = CarteiraService()
        self.controller = CarteiraController(usuario, self.service)
        self.pdf_parser = PDFParser()

        self.lado = "frente"
        self._after_id = None
        self._pdf_path = None
        self.fotos = {"foto1": None, "foto2": None, "foto3": None}
        self._lbl_fotos = {}
        self._labels_frente = {}
        self._labels_verso = {}

        self.configure(fg_color=AppTheme.BG_APP)
        self._setup_ui()
        self._setup_shortcuts()

    def _setup_shortcuts(self):
        """Configura atalhos de teclado"""
        self.bind("<Control-s>", lambda _: self._salvar_banco())
        self.bind("<Control-l>", lambda _: self._confirmar_limpar())
        self.bind("<F5>", lambda _: self._virar_cartao())
        self.focus_set()

    def _setup_ui(self):
        """Configura interface"""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Cart.TNotebook",
                        background=AppTheme.BG_APP, borderwidth=0)
        style.configure("Cart.TNotebook.Tab",
                        background=AppTheme.BG_CARD,
                        foreground=MUTED,
                        font=("Segoe UI", 12),
                        padding=(22, 10))
        style.map("Cart.TNotebook.Tab",
                  background=[("selected", AppTheme.BG_INPUT)],
                  foreground=[("selected", AppTheme.TXT_MAIN)])

        notebook = ttk.Notebook(self, style="Cart.TNotebook")
        notebook.pack(fill="both", expand=True)

        # Aba 1 - Gerar em Lote
        aba_batch = ctk.CTkFrame(notebook, fg_color=AppTheme.BG_APP)
        notebook.add(aba_batch, text="  Gerar em Lote  ")
        BatchCarteiraView(
            aba_batch,
            usuario=self.usuario,
            repo=self.service,
            sefaz_repo=self.service.sefaz_repo,
        ).pack(fill="both", expand=True)

        # Aba 2 - Cadastro Individual
        aba_individual = ctk.CTkFrame(notebook, fg_color=AppTheme.BG_APP)
        notebook.add(aba_individual, text="  Cadastro Individual  ")
        self._build_individual_tab(aba_individual)

    def _build_individual_tab(self, parent):
        """Constrói aba de cadastro individual"""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=36, pady=28)
        container.grid_columnconfigure(0, weight=0)
        container.grid_columnconfigure(1, weight=1)
        
        self._build_card_preview(container)
        self._build_form(container)

    def _build_card_preview(self, parent):
        """Constrói área de prévia do cartão"""
        col = ctk.CTkFrame(parent, fg_color="transparent")
        col.grid(row=0, column=0, sticky="n", padx=(0, 28))
        
        ctk.CTkLabel(
            col, text="PRÉVIA DO CARTÃO",
            font=("Segoe UI", 10, "bold"),
            text_color=MUTED
        ).pack(anchor="w", pady=(0, 8))
        
        card_container = ctk.CTkFrame(
            col, fg_color=AppTheme.BG_CARD,
            corner_radius=16,
            border_width=1,
            border_color=AppTheme.BORDER
        )
        card_container.pack()
        
        self.card = ctk.CTkFrame(
            card_container,
            width=self.controller.CARD_W,
            height=self.controller.CARD_H,
            fg_color="transparent",
        )
        self.card.pack(padx=12, pady=12)
        self.card.pack_propagate(False)
        
        self.lbl_bg = ctk.CTkLabel(self.card, text="")
        self.lbl_bg.place(x=0, y=0)
        self._render_card()
        
        # Botões de ação
        buttons = [
            ("🔄  Virar cartão", AppTheme.BG_INPUT, AppTheme.BORDER, self._virar_cartao, False),
            ("💾  Salvar no Banco", VERDE, VERDE_HOVER, self._salvar_banco, True),
            ("📜  Histórico", AZUL, AZUL_HOVER, self.abrir_historico, False),
            ("🗑️  Limpar Formulário", AppTheme.BG_INPUT, AppTheme.BORDER, self._confirmar_limpar, False),
        ]
        
        for text, color, hover, command, bold in buttons:
            ctk.CTkButton(
                col, text=text,
                width=self.controller.CARD_W,
                height=40,
                corner_radius=10,
                fg_color=color,
                hover_color=hover,
                text_color=AppTheme.TXT_MAIN,
                font=("Segoe UI", 11, "bold") if bold else ("Segoe UI", 11),
                command=command,
            ).pack(pady=(6, 0))

    def _render_card(self):
        """Renderiza a prévia do cartão"""
        img_path = (
            self.controller.IMG_FRENTE
            if self.lado == "frente"
            else self.controller.IMG_VERSO
        )
        
        try:
            pil_img = open_image(
                img_path,
                "FRENTE" if self.lado == "frente" else "VERSO"
            )
            pil_img = pil_img.resize(
                (self.controller.CARD_W, self.controller.CARD_H),
                Image.Resampling.LANCZOS
            )
            ctk_img = ctk.CTkImage(
                light_image=pil_img,
                size=(self.controller.CARD_W, self.controller.CARD_H)
            )
            self.lbl_bg.configure(image=ctk_img, text="")
            self.lbl_bg.image = ctk_img
        except Exception:
            label = "FRENTE" if self.lado == "frente" else "VERSO"
            self.lbl_bg.configure(
                image=None,
                text=f"[ {label} ]",
                font=("Segoe UI", 14),
                text_color=AppTheme.TXT_MUTED,
            )
        
        # Limpa labels antigas
        for widget in self.card.winfo_children():
            if widget is not self.lbl_bg:
                widget.destroy()
        
        self._labels_frente.clear()
        self._labels_verso.clear()
        
        if self.lado == "frente":
            self._build_front_labels()
        else:
            self._build_back_labels()

    def _build_front_labels(self):
        """Constrói labels da frente do cartão"""
        self._labels_frente = {
            "registro": self._create_label(self.card, 27, 100, 180, ("Segoe UI", 12)),
            "cpf": self._create_label(self.card, 211, 100, 190, ("Segoe UI", 12)),
            "nome": self._create_label(self.card, 27, 136, 370, ("Segoe UI", 12, "bold")),
            "propriedade": self._create_label(self.card, 27, 173, 370, ("Segoe UI", 12)),
            "unloc": self._create_label(self.card, 26, 210, 124, ("Segoe UI", 12)),
            "inicio": self._create_label(self.card, 190, 210, 106, ("Segoe UI", 12)),
            "validade": self._create_label(self.card, 300, 210, 140, ("Segoe UI", 12)),
        }

    def _build_back_labels(self):
        """Constrói labels do verso do cartão"""
        self._labels_verso = {
            "endereco": self._create_label(self.card, 21, 73, 385, ("Segoe UI", 12)),
            "atividade1": self._create_label(self.card, 21, 127, 385, ("Segoe UI", 12)),
            "atividade2": self._create_label(self.card, 21, 167, 385, ("Segoe UI", 12)),
            "georef": self._create_label(self.card, 21, 206, 385, ("Segoe UI", 12)),
        }

    def _create_label(self, parent, x, y, width, font):
        """Cria um label posicionado"""
        frame = ctk.CTkFrame(parent, width=width, height=18, fg_color="transparent")
        frame.place(x=x, y=y)
        frame.pack_propagate(False)
        label = ctk.CTkLabel(
            frame,
            text="---",
            font=font,
            text_color=AppTheme.TXT_MAIN,
            anchor="w"
        )
        label.pack(fill="x")
        return label

    def _build_form(self, parent):
        """Constrói o formulário de cadastro"""
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.grid(row=0, column=1, sticky="nsew")
        
        # Dados do Produtor
        self._add_section(scroll, "DADOS DO PRODUTOR")
        form_panel = self._create_form_panel(scroll)
        
        self.registro = self._create_field(form_panel, "Registro estadual")

        cpf_row = ctk.CTkFrame(form_panel, fg_color="transparent")
        cpf_row.pack(fill="x", padx=16, pady=4)

        self.cpf = ctk.CTkEntry(
            cpf_row,
            placeholder_text="CPF",
            fg_color=AppTheme.BG_INPUT,
            border_color=AppTheme.BORDER,
            text_color=AppTheme.TXT_MAIN,
            height=36,
            corner_radius=8,
        )
        self.cpf.pack(side="left", fill="x", expand=True)
        self.cpf.bind("<KeyRelease>", self._debounce_preview)

        self._btn_buscar_cpf = ctk.CTkButton(
            cpf_row,
            text="🔍 Buscar CPF",
            width=130,
            height=36,
            corner_radius=8,
            fg_color=AZUL,
            hover_color=AZUL_HOVER,
            text_color="#fff",
            font=("Segoe UI", 10, "bold"),
            command=self._buscar_por_cpf,
        )
        self._btn_buscar_cpf.pack(side="left", padx=(8, 0))

        self._lbl_buscar_status = ctk.CTkLabel(
            cpf_row,
            text="",
            font=("Segoe UI", 9),
            text_color=MUTED,
)
        self._lbl_buscar_status.pack(side="left", padx=(8, 0))

        self.nome = self._create_field(form_panel, "Nome do produtor")
        self.propriedade = self._create_field(form_panel, "Propriedade")
        
        # Linha com 3 campos
        row = ctk.CTkFrame(form_panel, fg_color="transparent")
        row.pack(fill="x", padx=16)
        row.grid_columnconfigure((0, 1, 2), weight=1)
        self.unloc = self._create_grid_field(row, "UNLOC", 0)
        self.inicio = self._create_grid_field(row, "Início", 1, formatter="date")
        self.validade = self._create_grid_field(row, "Validade", 2, formatter="date")
        
        # Informações Complementares
        self._add_section(scroll, "INFORMAÇÕES COMPLEMENTARES")
        p2 = self._create_form_panel(scroll)
        self.endereco = self._create_field(p2, "Endereço")
        self.atividade1 = self._create_field(p2, "Atividade primária")
        self.atividade2 = self._create_field(p2, "Atividade secundária")
        self.georef = self._create_field(p2, "Georreferenciamento")
        
        # Importar PDF
        self._add_section(scroll, "IMPORTAR PDF DA CARTEIRA")
        p_pdf = self._create_form_panel(scroll)
        self._build_import_pdf(p_pdf)
        
        # Fotos
        self._add_section(scroll, "FOTOS")
        p3 = self._create_form_panel(scroll)
        self._build_photos_section(p3)

    def _add_section(self, parent, title):
        """Adiciona seção ao formulário"""
        ctk.CTkLabel(
            parent, text=title,
            font=("Segoe UI", 10, "bold"),
            text_color=VERDE
        ).pack(anchor="w", pady=(18, 4))

    def _create_form_panel(self, parent):
        """Cria painel do formulário"""
        panel = ctk.CTkFrame(
            parent,
            fg_color=AppTheme.BG_INPUT,
            corner_radius=12,
            border_width=1,
            border_color=AppTheme.BORDER
        )
        panel.pack(fill="x")
        return panel

    def _create_field(self, parent, placeholder, formatter=None):
        """Cria campo de entrada"""
        entry = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            fg_color=AppTheme.BG_INPUT,
            border_color=AppTheme.BORDER,
            text_color=AppTheme.TXT_MAIN,
            height=36,
            corner_radius=8,
        )
        entry.pack(fill="x", padx=16, pady=4)
        entry.bind("<KeyRelease>", self._debounce_preview)
        
        if formatter == "date":
            entry.bind("<KeyRelease>", lambda e: self._format_date(e), add="+")
        
        return entry

    def _create_grid_field(self, parent, placeholder, col, formatter=None):
        """Cria campo em grid"""
        entry = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            fg_color=AppTheme.BG_INPUT,
            border_color=AppTheme.BORDER,
            text_color=AppTheme.TXT_MAIN,
            height=36,
            corner_radius=8,
        )
        entry.grid(row=0, column=col, sticky="ew", padx=4, pady=4)
        entry.bind("<KeyRelease>", self._debounce_preview)
        
        return entry

    def _format_cpf(self, entry):
        """Apenas valida e limita a 11 dígitos se necessário"""
        try:
            digits = re.sub(r"\D", "", entry.get())
            if len(digits) > 11:
                entry.delete(0, "end")
                entry.insert(0, digits[:11])
        except Exception:
            pass

    def _format_date(self, entry):
        """Apenas valida e limita a 8 dígitos se necessário"""
        try:
            digits = re.sub(r"\D", "", entry.get())
            if len(digits) > 8:
                entry.delete(0, "end")
                entry.insert(0, digits[:8])
        except Exception:
            pass

    def _debounce_preview(self, _=None):
        """Debounce para atualizar preview"""
        if self._after_id:
            self.after_cancel(self._after_id)
        self._after_id = self.after(DEBOUNCE_DELAY, self._update_preview)

    def _update_preview(self):
        """Atualiza preview do cartão"""
        if self.lado == "frente":
            labels = self._labels_frente
            self._safe_set(labels.get("registro"), self.registro.get())
            self._safe_set(labels.get("cpf"), format_cpf(self.cpf.get()))
            self._safe_set(labels.get("nome"), self.nome.get())
            self._safe_set(labels.get("propriedade"), self.propriedade.get())
            self._safe_set(labels.get("unloc"), self.unloc.get())
            self._safe_set(labels.get("inicio"), self.inicio.get())
            self._safe_set(labels.get("validade"), self.validade.get())
        else:
            labels = self._labels_verso
            self._safe_set(labels.get("endereco"), self.endereco.get())
            self._safe_set(labels.get("atividade1"), self.atividade1.get())
            self._safe_set(labels.get("atividade2"), self.atividade2.get())
            self._safe_set(labels.get("georef"), self.georef.get())

    def _safe_set(self, label, value):
        """Define texto do label com segurança"""
        try:
            if label and label.winfo_exists():
                label.configure(text=str(value).strip() if value else "---")
        except Exception:
            pass

    def _virar_cartao(self):
        """Vira o cartão"""
        self.lado = "verso" if self.lado == "frente" else "frente"
        self._render_card()
        self._update_preview()

    def _buscar_por_cpf(self):
        """Inicia busca com pequena espera (melhor experiência de usuário)."""
        cpf_text = self.cpf.get().strip()
        cpf_limpo = re.sub(r"\D", "", cpf_text)

        if not cpf_limpo:
            messagebox.showwarning("CPF obrigatório", "Digite um CPF antes de pesquisar.")
            return

        if len(cpf_limpo) != 11:
            messagebox.showwarning("CPF inválido", "CPF deve ter 11 dígitos.")
            return

        self._btn_buscar_cpf.configure(state="disabled")
        self._lbl_buscar_status.configure(text="Pesquisando...")

        # Atraso intencional para simulação de pesquisa (onde o usuário nota a ação)
        self.after(700, lambda: self._buscar_por_cpf_exec(cpf_limpo))

    def _buscar_por_cpf_exec(self, cpf_limpo):
        """Executa a busca real por CPF."""
        try:
            resultado = self.controller.buscar_por_cpf(cpf_limpo)

            if not resultado:
                messagebox.showinfo("Não encontrado", "Nenhum cadastro encontrado para este CPF.")
                return

            self.registro.delete(0, "end")
            self.registro.insert(0, resultado.get("registro", ""))
            self.cpf.delete(0, "end")
            self.cpf.insert(0, format_cpf(resultado.get("cpf", "")))
            self.nome.delete(0, "end")
            self.nome.insert(0, resultado.get("nome", ""))
            self.propriedade.delete(0, "end")
            self.propriedade.insert(0, resultado.get("propriedade", ""))
            self.unloc.delete(0, "end")
            self.unloc.insert(0, resultado.get("unloc", ""))
            self.inicio.delete(0, "end")
            self.inicio.insert(0, resultado.get("inicio", ""))
            self.validade.delete(0, "end")
            self.validade.insert(0, resultado.get("validade", ""))
            self.endereco.delete(0, "end")
            self.endereco.insert(0, resultado.get("endereco", ""))
            self.atividade1.delete(0, "end")
            self.atividade1.insert(0, resultado.get("atividade1", ""))
            self.atividade2.delete(0, "end")
            self.atividade2.insert(0, resultado.get("atividade2", ""))
            self.georef.delete(0, "end")
            self.georef.insert(0, resultado.get("georef", ""))

            self._update_preview()
            messagebox.showinfo("Encontrado", "Dados carregados a partir do CPF encontrado.")
        finally:
            self._btn_buscar_cpf.configure(state="normal")
            self._lbl_buscar_status.configure(text="")

    def _build_import_pdf(self, parent):
        """Constrói área de importação de PDF"""
        row1 = ctk.CTkFrame(parent, fg_color="transparent")
        row1.pack(fill="x", padx=16, pady=(12, 6))

        self._btn_importar_pdf = ctk.CTkButton(
            row1, text="📄 Selecionar PDF",
            width=160, height=38, corner_radius=8,
            fg_color=AZUL, hover_color=AZUL_HOVER,
            text_color="#fff", font=("Segoe UI", 12, "bold"),
            command=self._select_pdf)
        self._btn_importar_pdf.pack(side="left")

        self._lbl_pdf = ctk.CTkLabel(
            row1, text="Nenhum PDF selecionado",
            font=("Segoe UI", 11), text_color=MUTED)
        self._lbl_pdf.pack(side="left", padx=12)

        row2 = ctk.CTkFrame(parent, fg_color="transparent")
        row2.pack(fill="x", padx=16, pady=(0, 12))

        self._btn_extrair = ctk.CTkButton(
            row2, text="🔍 Extrair Informações do PDF",
            width=220, height=38, corner_radius=8,
            fg_color=AppTheme.BG_INPUT, hover_color=AppTheme.BORDER,
            text_color=AppTheme.TXT_MAIN, font=("Segoe UI", 11),
            command=self._extract_pdf, state="disabled")
        self._btn_extrair.pack(side="left")

        self._lbl_extrair_status = ctk.CTkLabel(
            row2, text="", font=("Segoe UI", 11), text_color=MUTED)
        self._lbl_extrair_status.pack(side="left", padx=12)
        self._pdf_path = None

    def _build_photos_section(self, parent):
        """Constrói seção de fotos"""
        for i in range(1, 4):
            chave = f"foto{i}"
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=5)
            
            ctk.CTkButton(
                row, text=f"📷 Foto {i}", width=120,
                fg_color=AZUL, hover_color=AZUL_HOVER,
                text_color="#fff", corner_radius=8,
                command=lambda c=chave: self._select_photo(c),
            ).pack(side="left")
            
            lbl = ctk.CTkLabel(row, text="—",
                               text_color=MUTED, font=("Segoe UI", 11))
            lbl.pack(side="left", padx=10)
            self._lbl_fotos[chave] = lbl

    def _select_photo(self, chave):
        """Seleciona foto"""
        caminho = filedialog.askopenfilename(
            title=f"Selecionar {chave.replace('foto', 'Foto ')}",
            filetypes=SUPPORTED_IMAGE_FORMATS,
        )
        if not caminho or not os.path.exists(caminho):
            return
        
        # Valida tamanho
        mb = os.path.getsize(caminho) / (1024 * 1024)
        if mb > 10:
            messagebox.showerror(
                "Erro", f"Arquivo muito grande ({mb:.1f} MB). Máximo: 10 MB")
            return
        
        # Valida imagem
        try:
            with Image.open(caminho) as img:
                img.verify()
            with Image.open(caminho) as img:
                w, h = img.size
                fmt = img.format
        except Exception as exc:
            messagebox.showerror("Erro", f"Imagem inválida:\n{exc}")
            return
        
        self.fotos[chave] = caminho
        nome = os.path.basename(caminho)
        if len(nome) > MAX_FILENAME_DISPLAY:
            nome = nome[:MAX_FILENAME_DISPLAY - 3] + "..."
        self._lbl_fotos[chave].configure(
            text=f"✓ {nome} ({w}×{h}, {fmt})", text_color=VERDE)

    def _select_pdf(self):
        """Seleciona PDF para importação"""
        caminho = filedialog.askopenfilename(
            title="Selecionar PDF da Carteira",
            filetypes=[("PDF", "*.pdf"), ("Todos", "*.*")])
        if not caminho or not os.path.exists(caminho):
            return
        
        self._pdf_path = caminho
        nome = os.path.basename(caminho)
        if len(nome) > MAX_FILENAME_DISPLAY:
            nome = nome[:MAX_FILENAME_DISPLAY - 3] + "..."
        self._lbl_pdf.configure(text=f"✓ {nome}", text_color=VERDE)
        self._btn_extrair.configure(state="normal")
        self._lbl_extrair_status.configure(text="")

    def _extract_pdf(self):
        """Extrai dados do PDF em thread separada"""
        if not self._pdf_path:
            return
        
        self._btn_extrair.configure(state="disabled", text="⏳ Extraindo...")
        self._lbl_extrair_status.configure(text="Lendo PDF...", text_color=MUTED)
        threading.Thread(target=self._worker_extract_pdf, daemon=True).start()

    def _worker_extract_pdf(self):
        """Worker para extrair dados do PDF"""
        try:
            text = self.pdf_parser.extract_text(self._pdf_path)
            if not text.strip():
                self.after(0, self._show_extraction_result,
                           None, "PDF sem texto legível (pode ser imagem escaneada).")
                return
            
            dados = self.pdf_parser.parse(text)
            self.after(0, self._show_extraction_result, dados, None)
        except Exception as e:
            self.after(0, self._show_extraction_result, None, str(e))

    def _show_extraction_result(self, dados, erro):
        """Exibe resultado da extração"""
        self._btn_extrair.configure(state="normal", text="🔍 Extrair Informações do PDF")
        
        if erro:
            self._lbl_extrair_status.configure(text=f"❌ {erro[:60]}", text_color=VERMELHO)
            messagebox.showerror("Erro ao extrair PDF", erro)
            return
        
        if not dados:
            self._lbl_extrair_status.configure(text="⚠️ Nenhum campo identificado.", text_color=VERMELHO)
            return

        mapa = {
            "registro": self.registro, "cpf": self.cpf,
            "nome": self.nome, "propriedade": self.propriedade,
            "unloc": self.unloc, "inicio": self.inicio,
            "validade": self.validade, "endereco": self.endereco,
            "atividade1": self.atividade1, "atividade2": self.atividade2,
            "georef": self.georef,
        }
        
        preenchidos = 0
        for chave, entry in mapa.items():
            valor = dados.get(chave, "")
            if valor:
                entry.delete(0, "end")
                entry.insert(0, valor)
                preenchidos += 1
        
        self._update_preview()
        
        total = len(mapa)
        cor = VERDE if preenchidos >= total // 2 else MUTED
        self._lbl_extrair_status.configure(
            text=f"✅ {preenchidos}/{total} campos preenchidos", text_color=cor)

    def _salvar_banco(self):
        """Salva carteira no banco"""
        dados = {
            "registro": self.registro.get().strip(),
            "cpf": self.cpf.get().strip(),
            "nome": self.nome.get().strip(),
            "propriedade": self.propriedade.get().strip(),
            "unloc": self.unloc.get().strip(),
            "inicio": self.inicio.get().strip(),
            "validade": self.validade.get().strip(),
            "endereco": self.endereco.get().strip(),
            "atividade1": self.atividade1.get().strip(),
            "atividade2": self.atividade2.get().strip(),
            "georef": self.georef.get().strip(),
        }
        
        # Valida campos obrigatórios
        required = [("registro", "Registro Estadual"), ("cpf", "CPF"),
                    ("nome", "Nome do Produtor"), ("propriedade", "Propriedade")]
        missing = [name for field, name in required if not dados.get(field)]
        
        if missing:
            messagebox.showwarning("Validação", "Campos obrigatórios:\n• " + "\n• ".join(missing))
            return
        
        # Valida CPF
        if len(re.sub(r"\D", "", dados["cpf"])) != 11:
            messagebox.showwarning("Validação", "CPF deve ter 11 dígitos.")
            return
        
        # Valida datas
        for campo, nome in [("inicio", "Início"), ("validade", "Validade")]:
            v = dados.get(campo, "")
            if v and not re.match(r"^\d{2}/\d{2}/\d{4}$", v):
                messagebox.showwarning("Validação", f"{nome} inválida. Use dd/mm/aaaa.")
                return
        
        # Confirma se não tem fotos
        if not any(self.fotos.values()):
            if not messagebox.askyesno("Aviso", "Nenhuma foto selecionada. Continuar mesmo assim?"):
                return
        
        ok, msg = self.controller.salvar_carteira(dados, self.fotos)
        if ok:
            messagebox.showinfo("Sucesso", msg)
            self._clear_form()
        else:
            messagebox.showerror("Erro", msg)

    def _clear_form(self):
        """Limpa formulário"""
        for e in [self.registro, self.cpf, self.nome, self.propriedade,
                  self.unloc, self.inicio, self.validade,
                  self.endereco, self.atividade1, self.atividade2, self.georef]:
            e.delete(0, "end")
        
        self.fotos = {"foto1": None, "foto2": None, "foto3": None}
        for lbl in self._lbl_fotos.values():
            lbl.configure(text="—", text_color=MUTED)
        
        if self.lado == "verso":
            self.lado = "frente"
            self._render_card()
        
        self._update_preview()

    def _confirmar_limpar(self):
        """Confirma limpeza do formulário"""
        has_data = any([
            self.registro.get().strip(),
            self.cpf.get().strip(),
            self.nome.get().strip(),
            any(self.fotos.values()),
        ])
        
        if has_data and not messagebox.askyesno("Confirmação", "Limpar todos os campos?"):
            return
        
        self._clear_form()

    def abrir_historico(self):
        """Abre janela de histórico"""
        HistoricoView(self, self.usuario, self.controller).grab_set()