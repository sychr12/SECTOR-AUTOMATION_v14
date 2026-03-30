import customtkinter as ctk
from tkinter import ttk
from tkinter import messagebox

from ui.base_ui import BaseUI
from theme import AppTheme
from .controller import AdicionarController
from .services import AdicionarService


# ── Paleta Corporativa ──────────────────────────────────────────────────────────
_PRIMARY_DARK    = "#0a2540"      # Azul marinho profundo
_PRIMARY         = "#1a4b6e"      # Azul corporativo médio
_ACCENT          = "#2c6e9e"      # Azul para destaques
_ACCENT_DARK     = "#1e4a6e"      # Azul escuro para hover
_ACCENT_LIGHT    = "#e8f0f8"      # Azul muito claro para fundos
_BRANCO          = "#ffffff"
_CINZA_BG        = "#f5f7fc"      # Fundo cinza azulado
_CINZA_BORDER    = "#e2e8f0"      # Borda suave
_CINZA_MEDIO     = "#5a6e8a"      # Cinza azulado para textos secundários
_CINZA_TEXTO     = "#1e2f3e"      # Azul acinzentado escuro
_VERDE_STATUS    = "#10b981"      # Verde para status
_VERDE_HOVER     = "#d1fae5"      # Verde claro para hover
_DANGER          = "#dc2626"      # Vermelho para erros
_DANGER_DK       = "#b91c1c"      # Vermelho escuro
_SUCESSO         = "#10b981"      # Verde sucesso
_SUCESSO_DARK    = "#059669"      # Verde escuro


class AdicionarUI(BaseUI):
    def __init__(self, master, usuario):
        super().__init__(master)
        self.usuario = usuario
        self.service = AdicionarService()
        self.controller = AdicionarController(usuario, self.service.repo)

        # Frame principal
        self.frame = ctk.CTkFrame(self, fg_color=_CINZA_BG)
        self.frame.pack(fill="both", expand=True, padx=24, pady=24)

        self.radio = ctk.StringVar(value="insc")

        self._criar_topo()
        self._criar_tabela()
        self._criar_formulario()

    def _criar_topo(self):
        """Cabeçalho com radio buttons e título"""
        header = ctk.CTkFrame(
            self.frame, 
            fg_color=_BRANCO, 
            corner_radius=12,
            border_width=1,
            border_color=_CINZA_BORDER
        )
        header.pack(fill="x", padx=0, pady=(0, 20))
        
        # Container principal do header
        header_container = ctk.CTkFrame(header, fg_color="transparent")
        header_container.pack(fill="x", padx=24, pady=20)
        
        # Título e ícone
        title_container = ctk.CTkFrame(header_container, fg_color="transparent")
        title_container.pack(anchor="w", pady=(0, 16))
        
        ctk.CTkLabel(
            title_container,
            text="📝",
            font=("Segoe UI", 24),
            text_color=_ACCENT
        ).pack(side="left", padx=(0, 12))
        
        ctk.CTkLabel(
            title_container,
            text="Registro de Operações",
            font=("Segoe UI", 20, "bold"),
            text_color=_CINZA_TEXTO
        ).pack(side="left")
        
        # Subtítulo
        ctk.CTkLabel(
            header_container,
            text="Selecione o tipo de operação e preencha os dados do produtor rural",
            font=("Segoe UI", 12),
            text_color=_CINZA_MEDIO
        ).pack(anchor="w", pady=(0, 20))
        
        # Radio buttons container
        radio_container = ctk.CTkFrame(header_container, fg_color=_ACCENT_LIGHT, corner_radius=8)
        radio_container.pack(fill="x", pady=(0, 0))
        
        # Padding interno dos radios
        radio_inner = ctk.CTkFrame(radio_container, fg_color="transparent")
        radio_inner.pack(padx=20, pady=16)
        
        # Inscrição Radio
        self.radio_insc = ctk.CTkRadioButton(
            radio_inner,
            text="📋 Inscrição / Renovação",
            variable=self.radio,
            value="insc",
            command=self._alternar_formulario,
            fg_color=_ACCENT,
            hover_color=_ACCENT_DARK,
            text_color=_CINZA_TEXTO,
            font=("Segoe UI", 13, "bold"),
            border_width_checked=6
        )
        self.radio_insc.pack(side="left", padx=(0, 32))
        
        # Devolução Radio
        self.radio_dev = ctk.CTkRadioButton(
            radio_inner,
            text="🔄 Devolução / Cancelamento",
            variable=self.radio,
            value="dev",
            command=self._alternar_formulario,
            fg_color=_ACCENT,
            hover_color=_ACCENT_DARK,
            text_color=_CINZA_TEXTO,
            font=("Segoe UI", 13, "bold"),
            border_width_checked=6
        )
        self.radio_dev.pack(side="left")

    def _criar_tabela(self):
        """Tabela de registros com design moderno"""
        table_container = ctk.CTkFrame(
            self.frame,
            fg_color=_BRANCO,
            corner_radius=12,
            border_width=1,
            border_color=_CINZA_BORDER
        )
        table_container.pack(fill="both", expand=True, padx=0, pady=(0, 20))
        
        # Header da tabela com ícone
        table_header = ctk.CTkFrame(table_container, fg_color="transparent")
        table_header.pack(fill="x", padx=24, pady=(20, 12))
        
        ctk.CTkLabel(
            table_header,
            text="📊",
            font=("Segoe UI", 18),
            text_color=_ACCENT
        ).pack(side="left", padx=(0, 8))
        
        ctk.CTkLabel(
            table_header,
            text="Registros Recentes",
            font=("Segoe UI", 14, "bold"),
            text_color=_CINZA_TEXTO
        ).pack(side="left")

        tree_frame = ctk.CTkFrame(table_container, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("NOME", "CPF", "MUNICÍPIO", "MEMORANDO", "DATA"),
            show="headings",
            yscrollcommand=scrollbar.set,
            height=8
        )
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.tree.yview)

        colunas_config = {
            "NOME": {"width": 220, "icon": "👤"},
            "CPF": {"width": 140, "icon": "🆔"},
            "MUNICÍPIO": {"width": 160, "icon": "📍"},
            "MEMORANDO": {"width": 160, "icon": "📄"},
            "DATA": {"width": 120, "icon": "📅"}
        }

        for col, config in colunas_config.items():
            self.tree.heading(col, text=f"{config['icon']} {col}")
            self.tree.column(col, anchor="center", width=config['width'])

        # Estilo da Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background=_BRANCO,
            foreground=_CINZA_TEXTO,
            fieldbackground=_BRANCO,
            borderwidth=0,
            font=("Segoe UI", 10),
            rowheight=35
        )
        style.configure(
            "Treeview.Heading",
            background=_ACCENT_LIGHT,
            foreground=_ACCENT,
            borderwidth=1,
            font=("Segoe UI", 11, "bold"),
            relief="flat"
        )
        style.map("Treeview", 
                  background=[("selected", _ACCENT_LIGHT)],
                  foreground=[("selected", _ACCENT)])
        style.map("Treeview.Heading", 
                  background=[("active", _ACCENT_LIGHT)])

    def _criar_formulario(self):
        """Formulário de entrada com design moderno"""
        form_container = ctk.CTkFrame(
            self.frame,
            fg_color=_BRANCO,
            corner_radius=12,
            border_width=1,
            border_color=_CINZA_BORDER
        )
        form_container.pack(fill="x", padx=0, pady=(0, 0))

        # Header do formulário
        form_header = ctk.CTkFrame(form_container, fg_color="transparent")
        form_header.pack(fill="x", padx=24, pady=(20, 16))
        
        ctk.CTkLabel(
            form_header,
            text="✏️",
            font=("Segoe UI", 18),
            text_color=_ACCENT
        ).pack(side="left", padx=(0, 8))
        
        ctk.CTkLabel(
            form_header,
            text="Dados do Registro",
            font=("Segoe UI", 14, "bold"),
            text_color=_CINZA_TEXTO
        ).pack(side="left")

        # Container do formulário com grid
        self.form_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        self.form_frame.pack(fill="x", padx=24, pady=(0, 24))

        # Grid layout para campos
        self.form_frame.grid_columnconfigure(0, weight=1)
        self.form_frame.grid_columnconfigure(1, weight=1)

        # Campos do formulário
        row = 0
        
        # Nome
        self._criar_campo_formulario(row, 0, "👤 Nome Completo", "Digite o nome completo do produtor")
        self.nome_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="Ex: João da Silva",
            height=44,
            corner_radius=8,
            border_width=1,
            border_color=_CINZA_BORDER,
            fg_color=_BRANCO,
            text_color=_CINZA_TEXTO,
            font=("Segoe UI", 13)
        )
        self.nome_entry.grid(row=row, column=0, sticky="ew", padx=(0, 10), pady=8)
        
        # CPF
        self._criar_campo_formulario(row, 1, "🆔 CPF", "000.000.000-00")
        self.cpf_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="000.000.000-00",
            height=44,
            corner_radius=8,
            border_width=1,
            border_color=_CINZA_BORDER,
            fg_color=_BRANCO,
            text_color=_CINZA_TEXTO,
            font=("Segoe UI", 13)
        )
        self.cpf_entry.grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=8)
        
        row += 1
        
        # Município
        self._criar_campo_formulario(row, 0, "📍 Município", "Digite o município de origem")
        self.municipio_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="Ex: Manaus",
            height=44,
            corner_radius=8,
            border_width=1,
            border_color=_CINZA_BORDER,
            fg_color=_BRANCO,
            text_color=_CINZA_TEXTO,
            font=("Segoe UI", 13)
        )
        self.municipio_entry.grid(row=row, column=0, sticky="ew", padx=(0, 10), pady=8)
        
        # Memorando
        self._criar_campo_formulario(row, 1, "📄 Nº Memorando", "Número do documento")
        self.memo_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="Ex: 2026/00123",
            height=44,
            corner_radius=8,
            border_width=1,
            border_color=_CINZA_BORDER,
            fg_color=_BRANCO,
            text_color=_CINZA_TEXTO,
            font=("Segoe UI", 13)
        )
        self.memo_entry.grid(row=row, column=1, sticky="ew", padx=(10, 0), pady=8)
        
        row += 1
        
        # Tipo (apenas para inscrição)
        self._criar_campo_formulario(row, 0, "🏷️ Tipo", "Selecione o tipo de operação")
        self.tipo_combo = ctk.CTkComboBox(
            self.form_frame,
            values=["INSC - Inscrição", "RENOV - Renovação"],
            height=44,
            corner_radius=8,
            border_width=1,
            border_color=_CINZA_BORDER,
            fg_color=_BRANCO,
            button_color=_ACCENT,
            button_hover_color=_ACCENT_DARK,
            text_color=_CINZA_TEXTO,
            font=("Segoe UI", 13),
            dropdown_font=("Segoe UI", 12)
        )
        self.tipo_combo.grid(row=row, column=0, sticky="ew", padx=(0, 10), pady=8)
        self.tipo_combo.set("INSC - Inscrição")
        
        # Motivo (apenas para devolução)
        self.motivo_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.motivo_frame.grid(row=row, column=1, sticky="nsew", padx=(10, 0), pady=8)
        
        ctk.CTkLabel(
            self.motivo_frame,
            text="💬 Motivo da Devolução",
            font=("Segoe UI", 12, "bold"),
            text_color=_CINZA_TEXTO
        ).pack(anchor="w", pady=(0, 6))
        
        self.motivo_text = ctk.CTkTextbox(
            self.motivo_frame,
            height=100,
            corner_radius=8,
            border_width=1,
            border_color=_CINZA_BORDER,
            fg_color=_BRANCO,
            text_color=_CINZA_TEXTO,
            font=("Segoe UI", 12)
        )
        self.motivo_text.pack(fill="both", expand=True)
        
        # Ocultar motivo inicialmente
        self.motivo_frame.grid_remove()
        
        # Bind para formatação automática do CPF
        self.cpf_entry.bind("<KeyRelease>", self._formatar_cpf)

        # Botão salvar
        btn_container = ctk.CTkFrame(self.frame, fg_color="transparent")
        btn_container.pack(fill="x", padx=0, pady=(20, 0))
        
        ctk.CTkButton(
            btn_container,
            text="💾 Salvar Registro",
            command=self._salvar_registro,
            height=48,
            fg_color=_SUCESSO,
            hover_color=_SUCESSO_DARK,
            text_color=_BRANCO,
            font=("Segoe UI", 14, "bold"),
            corner_radius=8
        ).pack(pady=0, ipadx=40)

    def _criar_campo_formulario(self, row, col, label, placeholder):
        """Helper para criar label de campo de formulário"""
        frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        frame.grid(row=row, column=col, sticky="nsew", padx=(0 if col == 0 else 10, 0), pady=8)
        
        ctk.CTkLabel(
            frame,
            text=label,
            font=("Segoe UI", 12, "bold"),
            text_color=_CINZA_TEXTO
        ).pack(anchor="w", pady=(0, 6))
        
        ctk.CTkLabel(
            frame,
            text=placeholder,
            font=("Segoe UI", 10),
            text_color=_CINZA_MEDIO
        ).pack(anchor="w")
        
        return frame

    def _alternar_formulario(self):
        """Alterna entre formulário de inscrição e devolução"""
        if self.radio.get() == "dev":
            # Modo devolução - mostrar motivo, esconder tipo
            self.tipo_combo.grid_remove()
            self.motivo_frame.grid()
        else:
            # Modo inscrição - mostrar tipo, esconder motivo
            self.tipo_combo.grid()
            self.motivo_frame.grid_remove()
            self.tipo_combo.set("INSC - Inscrição")

    def _formatar_cpf(self, event=None):
        """Formata CPF automaticamente enquanto digita"""
        texto = self.cpf_entry.get()
        posicao = self.cpf_entry.index("insert")
        
        # Formatar usando o controller
        cpf_formatado = self.controller.formatar_cpf(texto)
        
        # Atualizar campo mantendo cursor
        self.cpf_entry.delete(0, "end")
        self.cpf_entry.insert(0, cpf_formatado)
        
        # Reposicionar cursor
        try:
            nova_posicao = min(posicao, len(cpf_formatado))
            self.cpf_entry.icursor(nova_posicao)
        except:
            pass

    def _salvar_registro(self):
        """Salva o registro no banco"""
        tipo_registro = self.radio.get()
        
        # Validar campos obrigatórios
        if not self.nome_entry.get().strip():
            messagebox.showwarning("Atenção", "⚠️ O campo Nome é obrigatório!")
            self.nome_entry.focus()
            return
            
        if not self.cpf_entry.get().strip():
            messagebox.showwarning("Atenção", "⚠️ O campo CPF é obrigatório!")
            self.cpf_entry.focus()
            return
            
        if not self.municipio_entry.get().strip():
            messagebox.showwarning("Atenção", "⚠️ O campo Município é obrigatório!")
            self.municipio_entry.focus()
            return
            
        if not self.memo_entry.get().strip():
            messagebox.showwarning("Atenção", "⚠️ O campo Memorando é obrigatório!")
            self.memo_entry.focus()
            return
        
        # Coletar dados do formulário
        dados = {
            'nome': self.nome_entry.get().strip(),
            'cpf': self.cpf_entry.get().strip(),
            'municipio': self.municipio_entry.get().strip(),
            'memo': self.memo_entry.get().strip(),
            'tipo': self.tipo_combo.get() if tipo_registro == "insc" else "",
            'motivo': self.motivo_text.get("1.0", "end-1c").strip() if tipo_registro == "dev" else ""
        }

        # Validar motivo para devolução
        if tipo_registro == "dev" and not dados['motivo']:
            messagebox.showwarning("Atenção", "⚠️ O campo Motivo da Devolução é obrigatório!")
            self.motivo_text.focus()
            return

        # Salvar usando o controller
        if tipo_registro == "insc":
            success, message = self.controller.salvar_inscricao(dados)
        else:
            success, message = self.controller.salvar_devolucao(dados)

        if not success:
            messagebox.showwarning("Atenção", f"⚠️ {message}")
            return

        # Adicionar na tabela
        valores_tabela = self.controller.obter_registro_tabela(dados, tipo_registro)
        self.tree.insert("", 0, values=valores_tabela)

        # Limpar formulário
        self._limpar_formulario()
        
        # Mostrar mensagem de sucesso
        messagebox.showinfo("Sucesso", f"✅ {message}")

    def _limpar_formulario(self):
        """Limpa todos os campos do formulário"""
        self.nome_entry.delete(0, "end")
        self.cpf_entry.delete(0, "end")
        self.municipio_entry.delete(0, "end")
        self.memo_entry.delete(0, "end")
        self.motivo_text.delete("1.0", "end")
        self.tipo_combo.set("INSC - Inscrição")

    def obter_dados_formulario(self):
        """Obtém dados atuais do formulário"""
        return {
            'nome': self.nome_entry.get().strip(),
            'cpf': self.cpf_entry.get().strip(),
            'municipio': self.municipio_entry.get().strip(),
            'memo': self.memo_entry.get().strip(),
            'tipo': self.tipo_combo.get() if self.radio.get() == "insc" else "",
            'motivo': self.motivo_text.get("1.0", "end-1c").strip() if self.radio.get() == "dev" else ""
        }