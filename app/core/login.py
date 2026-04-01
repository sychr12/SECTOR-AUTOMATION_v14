# -*- coding: utf-8 -*-
"""
Tela de Login - Sistema com Redirecionamento por Perfil
Carteira do Produtor Rural
"""

import customtkinter as ctk
from tkinter import messagebox
import webbrowser
import json
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from services.login_repository import validar_usuario, registrar_acesso
from app.theme import AppTheme


# ── Paleta Corporativa Premium ────────────────────────────────────────────────────
_PRIMARY_DARK    = "#0a2540"      # Azul marinho profundo
_PRIMARY         = "#1a4b6e"      # Azul corporativo médio
_PRIMARY_LIGHT   = "#2c6e9e"      # Azul para destaques
_ACCENT          = "#2c6e9e"      # Azul principal como acento
_ACCENT_DARK     = "#1e4a6e"      # Azul escuro para hover
_ACCENT_LIGHT    = "#e8f0f8"      # Azul muito claro para fundos
_BRANCO          = "#ffffff"
_CINZA_BG        = "#f5f7fc"      # Fundo cinza azulado
_CINZA_CARD      = "#ffffff"      # Branco para cards
_CINZA_BORDER    = "#e2e8f0"      # Borda suave
_CINZA_MEDIO     = "#5a6e8a"      # Cinza azulado para textos secundários
_CINZA_TEXTO     = "#1e2f3e"      # Azul acinzentado escuro
_VERDE_STATUS    = "#2c6e9e"      # Azul para status
_DANGER          = "#dc2626"      # Vermelho para erros
_DANGER_DK       = "#b91c1c"      # Vermelho escuro
_DANGER_LIGHT    = "#fee2e2"      # Vermelho claro para fundo de erro

# Elementos de texto
_TEXTO_SUAVE     = "#2c6e9e"
_MUTED           = "#5a6e8a"
_BORDER_FOCUS    = "#2c6e9e"

# ── Configurações de "Lembrar-me" ────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)
REMEMBER_FILE = os.path.join(DATA_DIR, "remember_me.json")
SALT_FILE = os.path.join(DATA_DIR, "salt.key")

class RememberMeManager:
    """Gerenciador de credenciais para 'Lembrar-me'"""
    
    def __init__(self):
        self.cipher = None
        self._init_crypto()
    
    def _init_crypto(self):
        """Inicializa a criptografia para armazenamento seguro"""
        try:
            # Carrega ou cria o salt
            if os.path.exists(SALT_FILE):
                with open(SALT_FILE, 'rb') as f:
                    salt = f.read()
            else:
                salt = os.urandom(16)
                with open(SALT_FILE, 'wb') as f:
                    f.write(salt)
            
            # Deriva a chave usando PBKDF2
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            # Chave fixa derivada de um identificador do sistema
            key = base64.urlsafe_b64encode(kdf.derive(b"SECTOR_AUTOMATION_SECRET_KEY_2026"))
            self.cipher = Fernet(key)
        except Exception:
            # Fallback: gera chave aleatória se falhar
            self.cipher = Fernet(Fernet.generate_key())
    
    def _encrypt(self, data: str) -> str:
        """Criptografa dados"""
        if not data:
            return ""
        return self.cipher.encrypt(data.encode()).decode()
    
    def _decrypt(self, encrypted_data: str) -> str:
        """Descriptografa dados"""
        if not encrypted_data:
            return ""
        try:
            return self.cipher.decrypt(encrypted_data.encode()).decode()
        except Exception:
            return ""
    
    def save_credentials(self, username: str, password: str, remember: bool):
        """Salva credenciais se 'lembrar' estiver marcado"""
        if remember and username and password:
            data = {
                "username": self._encrypt(username),
                "password": self._encrypt(password),
                "remember": True
            }
            with open(REMEMBER_FILE, 'w') as f:
                json.dump(data, f)
        elif not remember and os.path.exists(REMEMBER_FILE):
            # Remove o arquivo se não quiser lembrar
            os.remove(REMEMBER_FILE)
    
    def load_credentials(self):
        """Carrega credenciais salvas"""
        try:
            if os.path.exists(REMEMBER_FILE):
                with open(REMEMBER_FILE, 'r') as f:
                    data = json.load(f)
                if data.get("remember", False):
                    username = self._decrypt(data.get("username", ""))
                    password = self._decrypt(data.get("password", ""))
                    return username, password, True
        except Exception:
            pass
        return "", "", False


class Login(ctk.CTkFrame):
    """Tela de login do sistema - Design Corporativo"""

    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.on_success = on_success
        self.janela     = None
        self.processando = False
        self.remember_manager = RememberMeManager()

        self.configure(fg_color=_CINZA_BG)
        self.pack(expand=True, fill="both")

        self._criar_layout()
        self._carregar_credenciais_salvas()
        self._configurar_atalhos()

    # ══════════════════════════════════════════════════════════════════
    # FUNÇÕES DE "LEMBRAR-ME"
    # ══════════════════════════════════════════════════════════════════
    def _carregar_credenciais_salvas(self):
        """Carrega credenciais salvas e preenche os campos"""
        username, password, remember = self.remember_manager.load_credentials()
        if username and remember:
            self.entry_usuario.insert(0, username)
            self.entry_senha.insert(0, password)
            self.var_lembrar.set(True)
            # Opcional: focar no botão de login
            self.btn_entrar.focus()
    
    def _salvar_credenciais(self):
        """Salva credenciais se o checkbox estiver marcado"""
        username = self.entry_usuario.get().strip()
        password = self.entry_senha.get().strip()
        remember = self.var_lembrar.get()
        
        if remember:
            # Só salva se o login for bem-sucedido
            self.remember_manager.save_credentials(username, password, remember)
        else:
            # Remove credenciais salvas se desmarcou
            self.remember_manager.save_credentials("", "", False)
    
    def _limpar_credenciais_salvas(self):
        """Limpa credenciais salvas (usado em logout)"""
        self.remember_manager.save_credentials("", "", False)

    # ══════════════════════════════════════════════════════════════════
    # LAYOUT
    # ══════════════════════════════════════════════════════════════════
    def _criar_layout(self):
        # ── Painel esquerdo institucional ──────────────────────────────────────
        self.painel_esq = ctk.CTkFrame(
            self,
            width=420,
            corner_radius=0,
            fg_color=_PRIMARY_DARK,
        )
        self.painel_esq.place(relx=0, rely=0, relheight=1, relwidth=0.4)
        self.painel_esq.pack_propagate(False)

        # Conteúdo do painel esquerdo
        painel_inner = ctk.CTkFrame(self.painel_esq, fg_color="transparent")
        painel_inner.place(relx=0.5, rely=0.5, anchor="center")

        # Brasão/Logo institucional
        logo_container = ctk.CTkFrame(
            painel_inner,
            width=80,
            height=80,
            corner_radius=40,
            fg_color=_ACCENT,
        )
        logo_container.pack(pady=(0, 32))
        logo_container.pack_propagate(False)
        
        ctk.CTkLabel(
            logo_container,
            text="⚖️",
            font=("Segoe UI", 40),
            text_color=_BRANCO,
        ).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            painel_inner,
            text="Carteira do\nProdutor Rural",
            font=("Segoe UI", 28, "bold"),
            text_color=_BRANCO,
            justify="center",
        ).pack(pady=(0, 12))

        # Linha decorativa
        ctk.CTkFrame(
            painel_inner,
            width=60,
            height=2,
            fg_color=_ACCENT,
            corner_radius=1,
        ).pack(pady=(0, 24))

        ctk.CTkLabel(
            painel_inner,
            text="Instituto de Desenvolvimento\nAgropecuário do Amazonas",
            font=("Segoe UI", 12),
            text_color="#b8d0e5",
            justify="center",
        ).pack(pady=(0, 16))

        ctk.CTkLabel(
            painel_inner,
            text="IDAM",
            font=("Segoe UI", 14, "bold"),
            text_color=_BRANCO,
        ).pack()

        # ── Card direito (formulário) ──────────────────────────────────────────
        self.card = ctk.CTkFrame(
            self,
            corner_radius=16,
            fg_color=_CINZA_CARD,
        )
        self.card.place(relx=0.4, rely=0.5, anchor="w", relwidth=0.55, relheight=0.82)
        
        # Borda sutil
        self.card.configure(border_width=1, border_color=_CINZA_BORDER)

        # Container interno
        outer = ctk.CTkFrame(self.card, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=48, pady=48)

        # Título
        title_frame = ctk.CTkFrame(outer, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 36))
        
        ctk.CTkLabel(
            title_frame,
            text="Acessar Sistema",
            font=("Segoe UI", 28, "bold"),
            text_color=_CINZA_TEXTO,
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_frame,
            text="Informe suas credenciais para continuar",
            font=("Segoe UI", 13),
            text_color=_MUTED,
        ).pack(anchor="w", pady=(6, 0))

        # ── Campo Usuário ─────────────────────────────────────────────────────
        ctk.CTkLabel(
            outer,
            text="USUÁRIO",
            font=("Segoe UI", 11, "bold"),
            text_color=_MUTED,
        ).pack(anchor="w", pady=(0, 8))

        self.entry_usuario = ctk.CTkEntry(
            outer,
            placeholder_text="Digite seu nome de usuário",
            height=48,
            corner_radius=8,
            font=("Segoe UI", 13),
            fg_color=_CINZA_BG,
            border_width=1,
            border_color=_CINZA_BORDER,
            text_color=_CINZA_TEXTO,
        )
        self.entry_usuario.pack(fill="x", pady=(0, 24))
        self.entry_usuario.focus()

        # ── Campo Senha ───────────────────────────────────────────────────────
        ctk.CTkLabel(
            outer,
            text="SENHA",
            font=("Segoe UI", 11, "bold"),
            text_color=_MUTED,
        ).pack(anchor="w", pady=(0, 8))

        frame_senha = ctk.CTkFrame(outer, fg_color="transparent")
        frame_senha.pack(fill="x", pady=(0, 8))

        self.entry_senha = ctk.CTkEntry(
            frame_senha,
            placeholder_text="Digite sua senha",
            height=48,
            corner_radius=8,
            show="*",
            font=("Segoe UI", 13),
            fg_color=_CINZA_BG,
            border_width=1,
            border_color=_CINZA_BORDER,
            text_color=_CINZA_TEXTO,
        )
        self.entry_senha.pack(side="left", fill="x", expand=True, padx=(0, 12))

        self.btn_ver_senha = ctk.CTkButton(
            frame_senha,
            text="👁️",
            width=48,
            height=48,
            corner_radius=8,
            font=("Segoe UI", 14),
            fg_color=_CINZA_BG,
            hover_color=_ACCENT_LIGHT,
            text_color=_MUTED,
            border_width=1,
            border_color=_CINZA_BORDER,
            command=self._toggle_senha,
        )
        self.btn_ver_senha.pack(side="left")

        # ── Linha lembrar + esqueci ───────────────────────────────────────────
        linha_opts = ctk.CTkFrame(outer, fg_color="transparent")
        linha_opts.pack(fill="x", pady=(24, 32))

        self.var_lembrar = ctk.BooleanVar(value=False)
        self.chk_lembrar = ctk.CTkCheckBox(
            linha_opts,
            text="Lembrar-me",
            variable=self.var_lembrar,
            font=("Segoe UI", 12),
            text_color=_MUTED,
            fg_color=_ACCENT,
            hover_color=_ACCENT_DARK,
            border_color=_CINZA_BORDER,
            checkmark_color=_BRANCO,
            border_width=2,
            corner_radius=4,
            command=self._on_lembrar_changed,
        )
        self.chk_lembrar.pack(side="left")

        # Label clicável para recuperar senha
        forgot_label = ctk.CTkLabel(
            linha_opts,
            text="Esqueci minha senha",
            font=("Segoe UI", 12),
            text_color=_ACCENT,
            cursor="hand2",
        )
        forgot_label.pack(side="right")
        forgot_label.bind("<Button-1>", lambda e: self._recuperar_senha())
        forgot_label.bind("<Enter>", lambda e: forgot_label.configure(text_color=_ACCENT_DARK))
        forgot_label.bind("<Leave>", lambda e: forgot_label.configure(text_color=_ACCENT))

        # ── Botão entrar ──────────────────────────────────────────────────────
        self.btn_entrar = ctk.CTkButton(
            outer,
            text="Entrar no Sistema",
            height=52,
            corner_radius=8,
            font=("Segoe UI", 14, "bold"),
            fg_color=_ACCENT,
            hover_color=_ACCENT_DARK,
            text_color=_BRANCO,
            command=self.fazer_login,
        )
        self.btn_entrar.pack(pady=(0, 24))

        # ── Linha divisória ───────────────────────────────────────────────────
        divider = ctk.CTkFrame(outer, fg_color="transparent")
        divider.pack(fill="x", pady=(0, 20))
        
        ctk.CTkFrame(
            divider,
            height=1,
            fg_color=_CINZA_BORDER,
        ).pack(fill="x")

        # ── Rodapé institucional ──────────────────────────────────────────────
        footer_frame = ctk.CTkFrame(outer, fg_color="transparent")
        footer_frame.pack(fill="x")
        
        ctk.CTkLabel(
            footer_frame,
            text="© 2026 IDAM - Instituto de Desenvolvimento Agropecuário do Amazonas",
            font=("Segoe UI", 10),
            text_color=_MUTED,
            wraplength=380,
            justify="center",
        ).pack(pady=(16, 0))

        # ── Botão tema (canto superior direito) ───────────────────────────────
        self.btn_tema = ctk.CTkButton(
            self,
            text="🌙",
            width=40,
            height=40,
            corner_radius=20,
            font=("Segoe UI", 16),
            fg_color=_BRANCO,
            hover_color=_ACCENT_LIGHT,
            text_color=_MUTED,
            border_width=1,
            border_color=_CINZA_BORDER,
            command=self._alternar_tema,
        )
        self.btn_tema.place(relx=0.96, rely=0.04, anchor="ne")

        # Bind Enter
        self.entry_usuario.bind("<Return>", lambda _: self.entry_senha.focus())
        self.entry_senha.bind("<Return>", lambda _: self.fazer_login())

    def _on_lembrar_changed(self):
        """Callback quando o checkbox de lembrar é alterado"""
        # Se o usuário desmarcar, limpa as credenciais salvas
        if not self.var_lembrar.get():
            self.remember_manager.save_credentials("", "", False)

    # ══════════════════════════════════════════════════════════════════
    # FUNÇÕES DE UI
    # ══════════════════════════════════════════════════════════════════
    def _toggle_senha(self):
        if self.entry_senha.cget("show") == "*":
            self.entry_senha.configure(show="")
            self.btn_ver_senha.configure(text="🙈")
        else:
            self.entry_senha.configure(show="*")
            self.btn_ver_senha.configure(text="👁️")

    def _set_ui_estado_processando(self, processando):
        self.processando = processando
        if processando:
            try:
                self.btn_entrar.configure(
                    state="disabled", 
                    text="⏳ Autenticando...",
                    fg_color=_CINZA_MEDIO)
                self.entry_usuario.configure(state="disabled")
                self.entry_senha.configure(state="disabled")
                self.chk_lembrar.configure(state="disabled")
            except Exception:
                pass
        else:
            try:
                self.btn_entrar.configure(
                    state="normal", 
                    text="Entrar no Sistema",
                    fg_color=_ACCENT)
                self.entry_usuario.configure(state="normal")
                self.entry_senha.configure(state="normal")
                self.chk_lembrar.configure(state="normal")
            except Exception:
                pass

    def _animacao_login(self, sucesso):
        if sucesso:
            # Efeito de brilho no card
            original_border = self.card.cget("border_color")
            self.card.configure(border_color=_ACCENT, border_width=2)
            self.after(500, lambda: self.card.configure(border_color=original_border, border_width=1))
        else:
            # Efeito de erro nos campos
            self.entry_usuario.configure(border_color=_DANGER, border_width=1)
            self.entry_senha.configure(border_color=_DANGER, border_width=1)
            self.after(800, lambda: (
                self.entry_usuario.configure(border_color=_CINZA_BORDER),
                self.entry_senha.configure(border_color=_CINZA_BORDER),
            ))

    def _alternar_tema(self):
        modo = ctk.get_appearance_mode()
        novo = "Light" if modo == "Dark" else "Dark"
        ctk.set_appearance_mode(novo)
        self.btn_tema.configure(text="☀️" if novo == "Light" else "🌙")

    # ══════════════════════════════════════════════════════════════════
    # VALIDAÇÃO
    # ══════════════════════════════════════════════════════════════════
    def _validar_campos(self):
        usuario = self.entry_usuario.get().strip()
        senha   = self.entry_senha.get().strip()
        erros   = []

        self.entry_usuario.configure(border_color=_CINZA_BORDER)
        self.entry_senha.configure(border_color=_CINZA_BORDER)

        if not usuario:
            erros.append("• Informe o usuário")
            self.entry_usuario.configure(border_color=_DANGER)
        elif len(usuario) < 3:
            erros.append("• O usuário deve ter pelo menos 3 caracteres")
            self.entry_usuario.configure(border_color=_DANGER)

        if not senha:
            erros.append("• Informe a senha")
            self.entry_senha.configure(border_color=_DANGER)
        elif len(senha) < 4:
            erros.append("• Senha muito curta")
            self.entry_senha.configure(border_color=_DANGER)

        return erros

    # ══════════════════════════════════════════════════════════════════
    # LOGIN
    # ══════════════════════════════════════════════════════════════════
    def fazer_login(self):
        if self.processando:
            return

        erros = self._validar_campos()
        if erros:
            messagebox.showerror(
                "Erro de Validação",
                "Por favor, corrija:\n\n" + "\n".join(erros))
            return

        usuario_digitado = self.entry_usuario.get().strip()
        senha_digitada   = self.entry_senha.get().strip()

        self._set_ui_estado_processando(True)

        try:
            usuario_validado = validar_usuario(usuario_digitado, senha_digitada)

            if not usuario_validado:
                messagebox.showerror(
                    "Acesso Negado",
                    "Usuário ou senha incorretos.\n\nVerifique suas credenciais.")
                self._animacao_login(False)
                self.entry_senha.delete(0, "end")
                self.entry_senha.focus()
                return

            # Login bem-sucedido - salva credenciais se "Lembrar-me" estiver marcado
            self._salvar_credenciais()

            registrar_acesso(usuario_validado)
            self._animacao_login(True)

            perfil = usuario_validado.get("perfil", "usuario").capitalize()
            messagebox.showinfo(
                "Acesso Autorizado",
                f"Bem-vindo(a), {usuario_validado['username']}!\n\n"
                f"Perfil: {perfil}")

            self.destroy()
            self.on_success(usuario_validado)

        except Exception as e:
            messagebox.showerror(
                "Erro no Sistema",
                f"Erro inesperado ao fazer login:\n\n{str(e)}")

        finally:
            self._set_ui_estado_processando(False)

    # ══════════════════════════════════════════════════════════════════
    # RECUPERAÇÃO DE SENHA
    # ══════════════════════════════════════════════════════════════════
    def _recuperar_senha(self):
        if self.janela:
            self.janela.destroy()

        self.janela = ctk.CTkToplevel(self)
        self.janela.title("Recuperar Senha - IDAM")
        self.janela.geometry("540x500")
        self.janela.resizable(False, False)
        self.janela.configure(fg_color=_BRANCO)
        self.janela.grab_set()
        self.janela.focus()
        self.after(50, self._centralizar_janela)

        # Faixa superior institucional
        top_bar = ctk.CTkFrame(
            self.janela,
            height=4,
            corner_radius=0,
            fg_color=_ACCENT,
        )
        top_bar.pack(fill="x")

        frame = ctk.CTkFrame(self.janela, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=48, pady=40)

        # Ícone e título
        ctk.CTkLabel(
            frame,
            text="🔐",
            font=("Segoe UI", 56),
            text_color=_ACCENT,
        ).pack(pady=(0, 16))
        
        ctk.CTkLabel(
            frame,
            text="Recuperação de Acesso",
            font=("Segoe UI", 24, "bold"),
            text_color=_CINZA_TEXTO,
        ).pack(pady=(0, 8))

        ctk.CTkLabel(
            frame,
            text="Entre em contato com nossa central de suporte",
            font=("Segoe UI", 13),
            text_color=_MUTED,
        ).pack(pady=(0, 32))

        # Cards de contato
        contatos = [
            ("📧", "E-mail Institucional", "suporte@idam.am.gov.br", 
             "mailto:suporte@idam.am.gov.br?subject=Recuperação de Senha - Sistema IDAM"),
            ("📞", "Central de Atendimento", "(92) 2121-0000", None),
            ("💬", "WhatsApp Institucional", "(92) 98400-0000", 
             "https://wa.me/5592984000000?text=Recuperação de Senha - Sistema IDAM"),
        ]
        
        for icone, titulo, valor, link in contatos:
            card = ctk.CTkFrame(frame, fg_color=_CINZA_BG, corner_radius=12)
            card.pack(fill="x", pady=(0, 12))
            
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=16)
            
            # Ícone
            icon_frame = ctk.CTkFrame(row, width=48, height=48, corner_radius=12, fg_color=_BRANCO)
            icon_frame.pack(side="left", padx=(0, 16))
            icon_frame.pack_propagate(False)
            
            ctk.CTkLabel(
                icon_frame,
                text=icone,
                font=("Segoe UI", 20),
                text_color=_ACCENT,
            ).place(relx=0.5, rely=0.5, anchor="center")
            
            # Texto
            text_frame = ctk.CTkFrame(row, fg_color="transparent")
            text_frame.pack(side="left")
            
            ctk.CTkLabel(
                text_frame,
                text=titulo,
                font=("Segoe UI", 11),
                text_color=_MUTED,
            ).pack(anchor="w")
            
            valor_label = ctk.CTkLabel(
                text_frame,
                text=valor,
                font=("Segoe UI", 14, "bold"),
                text_color=_ACCENT if link else _CINZA_TEXTO,
                cursor="hand2" if link else "",
            )
            valor_label.pack(anchor="w", pady=(4, 0))
            
            if link:
                valor_label.bind("<Button-1>", lambda e, l=link: webbrowser.open(l))
                valor_label.bind("<Enter>", lambda e, lbl=valor_label: lbl.configure(text_color=_ACCENT_DARK))
                valor_label.bind("<Leave>", lambda e, lbl=valor_label: lbl.configure(text_color=_ACCENT))

        # Informação adicional
        info_frame = ctk.CTkFrame(frame, fg_color=_ACCENT_LIGHT, corner_radius=8)
        info_frame.pack(fill="x", pady=(24, 16))
        
        ctk.CTkLabel(
            info_frame,
            text="ℹ️ Atendimento: Segunda a Sexta, 8h às 18h",
            font=("Segoe UI", 11),
            text_color=_CINZA_TEXTO,
        ).pack(pady=12)

        ctk.CTkButton(
            frame,
            text="Fechar",
            height=48,
            corner_radius=8,
            font=("Segoe UI", 13, "bold"),
            fg_color=_CINZA_BG,
            hover_color=_ACCENT_LIGHT,
            text_color=_CINZA_TEXTO,
            border_width=1,
            border_color=_CINZA_BORDER,
            command=self._fechar_janela,
        ).pack()

    def _centralizar_janela(self):
        if not self.janela:
            return
        self.janela.update_idletasks()
        w, h = self.janela.winfo_width(), self.janela.winfo_height()
        x = self.janela.winfo_screenwidth() // 2 - w // 2
        y = self.janela.winfo_screenheight() // 2 - h // 2
        self.janela.geometry(f"{w}x{h}+{x}+{y}")

    def _fechar_janela(self):
        if self.janela:
            self.janela.grab_release()
            self.janela.destroy()
            self.janela = None

    # ══════════════════════════════════════════════════════════════════
    # ATALHOS
    # ══════════════════════════════════════════════════════════════════
    def _configurar_atalhos(self):
        self.bind("<Return>", lambda e: self.fazer_login())
        self.bind("<Control-q>", lambda e: self.winfo_toplevel().destroy())
        self.bind("<Control-r>", lambda e: self._recuperar_senha())
        self.bind("<Escape>", lambda e: self._limpar_campos())

    def _limpar_campos(self):
        self.entry_usuario.delete(0, "end")
        self.entry_senha.delete(0, "end")
        self.entry_usuario.configure(border_color=_CINZA_BORDER)
        self.entry_senha.configure(border_color=_CINZA_BORDER)
        self.entry_usuario.focus()