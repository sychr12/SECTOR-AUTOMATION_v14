# -*- coding: utf-8 -*-
"""
View para configuração de email
"""

import customtkinter as ctk
from app.theme import AppTheme

class EmailConfigView(ctk.CTkFrame):
    """View para configuração de email"""
    
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        self._create_widgets()
        self._load_current_config()
    
    def _create_widgets(self):
        """Cria os widgets da view"""
        main_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        ctk.CTkLabel(
            main_frame,
            text="📧 Configuração de Notificações por Email",
            font=("Segoe UI", 20, "bold"),
            text_color=AppTheme.TXT_MAIN
        ).pack(anchor="w", pady=(0, 20))
        
        # Frame de configuração
        config_frame = ctk.CTkFrame(
            main_frame,
            fg_color=AppTheme.BG_CARD,
            corner_radius=12
        )
        config_frame.pack(fill="x", pady=(0, 20))
        
        content = ctk.CTkFrame(config_frame, fg_color="transparent")
        content.pack(fill="x", padx=20, pady=20)
        
        # Servidor SMTP
        ctk.CTkLabel(
            content,
            text="Servidor SMTP:",
            font=("Segoe UI", 12, "bold"),
            text_color=AppTheme.TXT_MUTED,
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))
        
        self.entry_smtp_server = ctk.CTkEntry(
            content,
            placeholder_text="Ex: smtp.gmail.com",
            height=40,
            font=("Segoe UI", 12),
            fg_color=AppTheme.BG_INPUT,
            border_color=AppTheme.BORDER,
            text_color=AppTheme.TXT_MAIN
        )
        self.entry_smtp_server.pack(fill="x", pady=(0, 15))
        
        # Porta
        ctk.CTkLabel(
            content,
            text="Porta SMTP:",
            font=("Segoe UI", 12, "bold"),
            text_color=AppTheme.TXT_MUTED,
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))
        
        self.entry_smtp_port = ctk.CTkEntry(
            content,
            placeholder_text="Ex: 587",
            height=40,
            font=("Segoe UI", 12),
            fg_color=AppTheme.BG_INPUT,
            border_color=AppTheme.BORDER,
            text_color=AppTheme.TXT_MAIN
        )
        self.entry_smtp_port.pack(fill="x", pady=(0, 15))
        
        # Email do remetente
        ctk.CTkLabel(
            content,
            text="Email do Remetente:",
            font=("Segoe UI", 12, "bold"),
            text_color=AppTheme.TXT_MUTED,
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))
        
        self.entry_email_remetente = ctk.CTkEntry(
            content,
            placeholder_text="seuemail@gmail.com",
            height=40,
            font=("Segoe UI", 12),
            fg_color=AppTheme.BG_INPUT,
            border_color=AppTheme.BORDER,
            text_color=AppTheme.TXT_MAIN
        )
        self.entry_email_remetente.pack(fill="x", pady=(0, 15))
        
        # Senha (app password)
        ctk.CTkLabel(
            content,
            text="Senha (App Password):",
            font=("Segoe UI", 12, "bold"),
            text_color=AppTheme.TXT_MUTED,
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))
        
        senha_frame = ctk.CTkFrame(content, fg_color="transparent")
        senha_frame.pack(fill="x", pady=(0, 15))
        
        self.entry_senha = ctk.CTkEntry(
            senha_frame,
            placeholder_text="Senha de aplicativo",
            height=40,
            font=("Segoe UI", 12),
            fg_color=AppTheme.BG_INPUT,
            border_color=AppTheme.BORDER,
            text_color=AppTheme.TXT_MAIN,
            show="•"
        )
        self.entry_senha.pack(side="left", fill="x", expand=True)
        
        # Botão para mostrar/esconder senha
        self.btn_toggle_senha = ctk.CTkButton(
            senha_frame,
            text="👁️",
            width=50,
            height=40,
            command=self._toggle_mostrar_senha,
            fg_color=AppTheme.BG_INPUT,
            hover_color=AppTheme.TXT_MUTED,
            text_color=AppTheme.TXT_MAIN,
            font=("Segoe UI", 12)
        )
        self.btn_toggle_senha.pack(side="right", padx=(10, 0))
        
        # Assunto padrão
        ctk.CTkLabel(
            content,
            text="Assunto Padrão:",
            font=("Segoe UI", 12, "bold"),
            text_color=AppTheme.TXT_MUTED,
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))
        
        self.entry_assunto = ctk.CTkEntry(
            content,
            placeholder_text="Assunto dos emails",
            height=40,
            font=("Segoe UI", 12),
            fg_color=AppTheme.BG_INPUT,
            border_color=AppTheme.BORDER,
            text_color=AppTheme.TXT_MAIN
        )
        self.entry_assunto.pack(fill="x", pady=(0, 15))
        
        # Habilitado/Desabilitado
        self.var_habilitado = ctk.BooleanVar()
        
        ctk.CTkCheckBox(
            content,
            text="Habilitar notificações por email",
            variable=self.var_habilitado,
            font=("Segoe UI", 12),
            text_color=AppTheme.TXT_MUTED,
            checkbox_height=20,
            checkbox_width=20,
            fg_color=AppTheme.BTN_PRIMARY,
            hover_color=AppTheme.BTN_PRIMARY_HOVER,
            border_color=AppTheme.BORDER
        ).pack(anchor="w", pady=(0, 20))
        
        # Frame de templates
        template_frame = ctk.CTkFrame(
            main_frame,
            fg_color=AppTheme.BG_CARD,
            corner_radius=12
        )
        template_frame.pack(fill="x", pady=(0, 20))
        
        template_content = ctk.CTkFrame(template_frame, fg_color="transparent")
        template_content.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            template_content,
            text="📝 Templates de Email",
            font=("Segoe UI", 16, "bold"),
            text_color=AppTheme.TXT_MAIN
        ).pack(anchor="w", pady=(0, 15))
        
        # Template para novo usuário
        ctk.CTkLabel(
            template_content,
            text="Template - Novo Usuário:",
            font=("Segoe UI", 12, "bold"),
            text_color=AppTheme.TXT_MUTED,
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))
        
        self.text_template_novo = ctk.CTkTextbox(
            template_content,
            height=120,
            font=("Segoe UI", 11),
            fg_color=AppTheme.BG_INPUT,
            border_color=AppTheme.BORDER,
            text_color=AppTheme.TXT_MAIN
        )
        self.text_template_novo.pack(fill="x", pady=(0, 15))
        
        # Botões de ação
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x")
        
        self.btn_salvar = ctk.CTkButton(
            btn_frame,
            text="💾 Salvar Configuração",
            height=45,
            font=("Segoe UI", 13, "bold"),
            fg_color=AppTheme.BTN_SUCCESS,
            hover_color=AppTheme.BTN_SUCCESS_HOVER,
            corner_radius=10
        )
        self.btn_salvar.pack(side="left", padx=(0, 10))
        
        self.btn_testar = ctk.CTkButton(
            btn_frame,
            text="📤 Testar Conexão",
            height=45,
            font=("Segoe UI", 13),
            fg_color=AppTheme.BTN_PRIMARY,
            hover_color=AppTheme.BTN_PRIMARY_HOVER,
            corner_radius=10
        )
        self.btn_testar.pack(side="left")
        
        btn_fechar = ctk.CTkButton(
            btn_frame,
            text="❌ Fechar",
            command=self.destroy,
            height=45,
            font=("Segoe UI", 13),
            fg_color=AppTheme.BG_INPUT,
            hover_color=AppTheme.TXT_MUTED,
            corner_radius=10
        )
        btn_fechar.pack(side="right")
    
    def _load_current_config(self):
        """Carrega configuração atual nos campos"""
        config = self.controller.carregar_configuracao_atual()
        
        self.entry_smtp_server.insert(0, config.get('smtp_server', ''))
        self.entry_smtp_port.insert(0, str(config.get('smtp_port', '')))
        self.entry_email_remetente.insert(0, config.get('email_remetente', ''))
        self.entry_senha.insert(0, config.get('senha_remetente', ''))
        self.entry_assunto.insert(0, config.get('assunto_padrao', ''))
        self.var_habilitado.set(config.get('habilitado', False))
        self.text_template_novo.insert("1.0", config.get('template_novo_usuario', ''))
    
    def _toggle_mostrar_senha(self):
        """Alterna entre mostrar e esconder senha"""
        if self.entry_senha.cget('show') == '•':
            self.entry_senha.configure(show='')
            self.btn_toggle_senha.configure(text="🙈")
        else:
            self.entry_senha.configure(show='•')
            self.btn_toggle_senha.configure(text="👁️")
    
    def get_form_data(self):
        """Retorna os dados do formulário"""
        try:
            porta = int(self.entry_smtp_port.get().strip())
        except ValueError:
            porta = 587
        
        return {
            'servidor': self.entry_smtp_server.get().strip(),
            'porta': porta,
            'email': self.entry_email_remetente.get().strip(),
            'senha': self.entry_senha.get(),
            'assunto': self.entry_assunto.get().strip(),
            'habilitado': self.var_habilitado.get(),
            'template': self.text_template_novo.get("1.0", "end-1c").strip()
        }