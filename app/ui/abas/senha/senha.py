# -*- coding: utf-8 -*-
"""
Módulo para trocar senha SEFAZ — Design Corporativo com Ícones
"""

import customtkinter as ctk
from tkinter import END, messagebox
import os
from PIL import Image

from selenium import webdriver
from selenium.webdriver.common.by import By

from ui.base_ui import BaseUI
from app.theme import AppTheme
from services.database import get_connection


# ── Paleta Corporativa ──────────────────────────────────────────────────────────
_PRIMARY_DARK    = "#0a2540"
_PRIMARY         = "#1a4b6e"
_ACCENT          = "#2c6e9e"
_ACCENT_DARK     = "#1e4a6e"
_ACCENT_LIGHT    = "#e8f0f8"
_BRANCO          = "#ffffff"
_CINZA_BG        = "#f8fafc"
_CINZA_BORDER    = "#e2e8f0"
_CINZA_MEDIO     = "#5a6e8a"
_CINZA_TEXTO     = "#1e2f3e"
_VERDE_STATUS    = "#10b981"
_VERDE_DARK      = "#059669"
_VERDE_LIGHT     = "#d1fae5"
_AMARELO         = "#f59e0b"
_VERMELHO        = "#ef4444"
_VERMELHO_DARK   = "#dc2626"
_AZUL            = "#3b82f6"
_AZUL_DARK       = "#2563eb"
_MUTED           = "#5a6e8a"
_ICON_COLOR      = "#1e293b"


class IconManager:
    """Gerenciador de ícones para a interface de senha"""
    
    def __init__(self):
        self.icons = {}
        self._find_icons_path()
        
    def _find_icons_path(self):
        """Encontra o caminho correto para a pasta de ícones"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        possible_paths = [
            os.path.join(current_dir, "..", "..", "..", "images", "icons", "senha"),
            os.path.join(current_dir, "..", "..", "..", "..", "images", "icons", "senha"),
            r"images\icons\senha",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                self.icons_dir = path
                print(f"[IconManager] ✅ Ícones encontrados em: {self.icons_dir}")
                return
        
        self.icons_dir = possible_paths[0]
        print(f"[IconManager] ⚠️ Pasta de ícones não encontrada: {self.icons_dir}")
    
    def load_icon(self, filename, size=(24, 24), colorize_to=None):
        """Carrega um ícone da pasta e aplica cor se necessário"""
        try:
            path = os.path.join(self.icons_dir, filename)
            if os.path.exists(path):
                img = Image.open(path)
                img = img.resize(size, Image.Resampling.LANCZOS)
                
                if colorize_to:
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    
                    data = img.getdata()
                    new_data = []
                    
                    if isinstance(colorize_to, tuple):
                        target_r, target_g, target_b = colorize_to
                    else:
                        hex_color = colorize_to.lstrip('#')
                        target_r, target_g, target_b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                    
                    for item in data:
                        r, g, b, a = item
                        if a > 0:
                            new_data.append((target_r, target_g, target_b, a))
                        else:
                            new_data.append((r, g, b, a))
                    
                    img.putdata(new_data)
                
                return ctk.CTkImage(light_image=img, dark_image=img, size=size)
        except Exception as e:
            print(f"[IconManager] Erro ao carregar {filename}: {e}")
        return None
    
    def setup_icons(self):
        """Configura todos os ícones com cor preta"""
        icons_config = {
            "lock": ("lock.png", (28, 28), _ICON_COLOR),
            "key": ("key.png", (24, 24), _ICON_COLOR),
            "check": ("check.png", (20, 20), _ICON_COLOR),
            "close": ("close.png", (20, 20), _ICON_COLOR),
        }
        
        for name, (filename, size, color) in icons_config.items():
            self.icons[name] = self.load_icon(filename, size, color)
        
        return self.icons
    
    def get(self, name):
        """Retorna um ícone pelo nome"""
        return self.icons.get(name)


class SenhaUI(BaseUI):
    """Interface para troca de senha SEFAZ com design corporativo"""

    def __init__(self, parent, usuario):
        super().__init__(parent)
        self.usuario = usuario
        
        # Inicializar ícones
        self.icon_manager = IconManager()
        self.icons = self.icon_manager.setup_icons()
        
        # Inicializar atributos
        self.entry_nova = None
        self.entry_confirmar = None
        self.req_min = None
        self.status_label = None
        self.btn_trocar = None
        self.btn_cancelar = None
        self.visivel_nova = False
        self.visivel_confirmar = False
        
        self.configure(fg_color=_CINZA_BG)

        # Container principal
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=32, pady=32)

        self._criar_ui(container)

    # ──────────────────────────────────────────────────────────────────────────
    # UI Principal
    # ──────────────────────────────────────────────────────────────────────────
    def _criar_ui(self, container):
        # Card central
        card = ctk.CTkFrame(
            container,
            fg_color=_BRANCO,
            corner_radius=16,
            border_width=1,
            border_color=_CINZA_BORDER,
            width=520,
        )
        card.pack(expand=True, fill="both", padx=10, pady=10)
        card.pack_propagate(False)

        # Conteúdo interno
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(expand=True, fill="both", padx=32, pady=28)

        # ──────────────────────────────────────────────────────────────────────
        # Cabeçalho com ícone
        # ──────────────────────────────────────────────────────────────────────
        self._build_header(content)
        
        # Linha divisória
        separator = ctk.CTkFrame(content, height=1, fg_color=_CINZA_BORDER)
        separator.pack(fill="x", pady=(0, 24))

        # ──────────────────────────────────────────────────────────────────────
        # Formulário
        # ──────────────────────────────────────────────────────────────────────
        form = ctk.CTkFrame(content, fg_color="transparent")
        form.pack(fill="x", pady=(0, 20))

        # Campo Nova Senha
        self.entry_nova, self.btn_ver_nova = self._criar_campo_senha_com_visibilidade(
            form,
            "Nova Senha",
            "Digite a nova senha"
        )

        # Campo Confirmar Senha
        self.entry_confirmar, self.btn_ver_confirmar = self._criar_campo_senha_com_visibilidade(
            form,
            "Confirmar Senha",
            "Digite novamente a senha"
        )

        # ──────────────────────────────────────────────────────────────────────
        # Requisitos de senha
        # ──────────────────────────────────────────────────────────────────────
        req_frame = ctk.CTkFrame(form, fg_color=_CINZA_BG, corner_radius=8)
        req_frame.pack(fill="x", pady=(8, 0))
        
        if self.icons.get("check"):
            ctk.CTkLabel(
                req_frame, text="", image=self.icons["check"],
                width=16, height=16
            ).pack(side="left", padx=(10, 6), pady=8)
        
        self.req_min = ctk.CTkLabel(
            req_frame,
            text="Mínimo de 4 caracteres",
            font=("Segoe UI", 11),
            text_color=_MUTED,
        )
        self.req_min.pack(side="left", pady=8)

        # ──────────────────────────────────────────────────────────────────────
        # Botões
        # ──────────────────────────────────────────────────────────────────────
        self._build_botoes(content)

        # ──────────────────────────────────────────────────────────────────────
        # Status
        # ──────────────────────────────────────────────────────────────────────
        self.status_label = ctk.CTkLabel(
            content,
            text="",
            font=("Segoe UI", 11),
            text_color=_MUTED,
        )
        self.status_label.pack(pady=(16, 0))

    def _build_header(self, parent):
        """Cabeçalho com título e ícone"""
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))

        # Ícone do cadeado
        if self.icons.get("lock"):
            icon_label = ctk.CTkLabel(
                header, text="", image=self.icons["lock"],
                width=32, height=32
            )
            icon_label.pack(side="left", padx=(0, 12))
        
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left")
        
        ctk.CTkLabel(
            title_frame,
            text="Trocar Senha SEFAZ",
            font=("Segoe UI", 22, "bold"),
            text_color=_CINZA_TEXTO,
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_frame,
            text="Altere a senha de acesso ao sistema",
            font=("Segoe UI", 12),
            text_color=_MUTED,
        ).pack(anchor="w", pady=(2, 0))

    def _criar_campo_senha_com_visibilidade(self, parent, label, placeholder):
        """Cria um campo de senha com botão de visibilidade"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(0, 16))

        # Label do campo
        ctk.CTkLabel(
            frame,
            text=label,
            font=("Segoe UI", 12, "bold"),
            text_color=_MUTED,
        ).pack(anchor="w", pady=(0, 6))

        # Container do input
        input_frame = ctk.CTkFrame(
            frame,
            fg_color=_CINZA_BG,
            corner_radius=10,
            border_width=1,
            border_color=_CINZA_BORDER,
            height=44,
        )
        input_frame.pack(fill="x")
        input_frame.pack_propagate(False)

        # Ícone dentro do input
        icon_label = ctk.CTkLabel(
            input_frame,
            text="🔒",
            font=("Segoe UI", 14),
            text_color=_MUTED,
            width=36,
        )
        icon_label.pack(side="left", padx=(12, 0), pady=10)

        # Campo de entrada
        entry = ctk.CTkEntry(
            input_frame,
            placeholder_text=placeholder,
            show="*",
            font=("Segoe UI", 13),
            fg_color="transparent",
            border_width=0,
            height=38,
        )
        entry.pack(side="left", fill="x", expand=True, padx=(0, 8), pady=3)

        # Botão de visibilidade
        btn_ver = ctk.CTkButton(
            input_frame,
            text="👁️",
            width=36,
            height=36,
            corner_radius=8,
            fg_color="transparent",
            hover_color=_CINZA_BORDER,
            text_color=_MUTED,
            font=("Segoe UI", 14),
            command=lambda: self._toggle_senha_visibilidade(entry, btn_ver)
        )
        btn_ver.pack(side="right", padx=(0, 8), pady=4)

        # Vincular evento para verificar requisitos
        if "Nova" in label:
            entry.bind("<KeyRelease>", self._verificar_requisitos)

        return entry, btn_ver

    def _toggle_senha_visibilidade(self, entry, btn):
        """Alterna a visibilidade da senha"""
        if entry.cget("show") == "*":
            entry.configure(show="")
            btn.configure(text="🙈")
        else:
            entry.configure(show="*")
            btn.configure(text="👁️")

    def _build_botoes(self, parent):
        """Cria os botões de ação"""
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(16, 0))
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

        self.btn_trocar = ctk.CTkButton(
            btn_frame,
            text=" Alterar Senha",
            image=self.icons.get("key"),
            compound="left",
            height=44,
            corner_radius=10,
            font=("Segoe UI", 13, "bold"),
            fg_color=_VERDE_STATUS,
            hover_color=_VERDE_DARK,
            text_color=_BRANCO,
            command=self.salvar_nova_senha,
        )
        self.btn_trocar.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        self.btn_cancelar = ctk.CTkButton(
            btn_frame,
            text=" Limpar",
            image=self.icons.get("close"),
            compound="left",
            height=44,
            corner_radius=10,
            font=("Segoe UI", 13),
            fg_color=_CINZA_BG,
            hover_color=_CINZA_BORDER,
            text_color=_CINZA_TEXTO,
            command=self._limpar_campos,
        )
        self.btn_cancelar.grid(row=0, column=1, padx=(8, 0), sticky="ew")

    # ──────────────────────────────────────────────────────────────────────────
    # Validação em tempo real
    # ──────────────────────────────────────────────────────────────────────────
    def _verificar_requisitos(self, event=None):
        """Verifica os requisitos da senha em tempo real"""
        if self.entry_nova and self.req_min:
            senha = self.entry_nova.get().strip()
            
            if len(senha) >= 4:
                self.req_min.configure(
                    text="✓ Mínimo de 4 caracteres (ok)",
                    text_color=_VERDE_STATUS
                )
            else:
                self.req_min.configure(
                    text="• Mínimo de 4 caracteres",
                    text_color=_MUTED
                )

    def _limpar_campos(self):
        """Limpa todos os campos"""
        if self.entry_nova:
            self.entry_nova.delete(0, END)
        if self.entry_confirmar:
            self.entry_confirmar.delete(0, END)
        if self.status_label:
            self.status_label.configure(text="")
        self._verificar_requisitos()

    # ──────────────────────────────────────────────────────────────────────────
    # Banco de Dados
    # ──────────────────────────────────────────────────────────────────────────
    def substituir_senha_no_banco(self, nova_senha: str) -> bool:
        """Substitui a senha antiga pela nova no banco de dados"""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Desativar todas as senhas antigas
            cursor.execute("UPDATE sefaz_credenciais SET ativo = 0")
            
            # Inserir nova senha como ativa
            cursor.execute("""
                INSERT INTO sefaz_credenciais (usuario, senha, ativo, criado_em)
                VALUES (?, ?, 1, GETDATE())
            """, ('03483401253', nova_senha))
            
            cursor.close()
            conn.commit()
            return True
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"[SenhaUI] Erro ao substituir senha: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def carregar_senha_do_banco(self) -> str:
        """Carrega a senha ativa do banco de dados"""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT TOP 1 senha
                FROM sefaz_credenciais
                WHERE ativo = 1
                ORDER BY id DESC
            """)
            row = cursor.fetchone()
            cursor.close()
            return row[0] if row else ""
        except Exception as e:
            print(f"[SenhaUI] Erro ao carregar senha: {e}")
            return ""
        finally:
            if conn:
                conn.close()

    # ──────────────────────────────────────────────────────────────────────────
    # Lógica Principal
    # ──────────────────────────────────────────────────────────────────────────
    def salvar_nova_senha(self):
        if not self.entry_nova or not self.entry_confirmar:
            return
            
        nova_senha = self.entry_nova.get().strip()
        confirmar_senha = self.entry_confirmar.get().strip()
        
        # Validações
        if not nova_senha:
            self._mostrar_status("Digite a nova senha!", "error")
            self.entry_nova.focus()
            return
        
        if not confirmar_senha:
            self._mostrar_status("Confirme a nova senha!", "error")
            self.entry_confirmar.focus()
            return
        
        if nova_senha != confirmar_senha:
            self._mostrar_status("As senhas não coincidem!", "error")
            self.entry_nova.delete(0, END)
            self.entry_confirmar.delete(0, END)
            self.entry_nova.focus()
            return
        
        if len(nova_senha) < 4:
            self._mostrar_status("A senha deve ter pelo menos 4 caracteres!", "error")
            self.entry_nova.delete(0, END)
            self.entry_confirmar.delete(0, END)
            self.entry_nova.focus()
            return

        # Desabilitar botão durante o processo
        if self.btn_trocar:
            self.btn_trocar.configure(state="disabled", text="⏳ Salvando...")
        self._mostrar_status("Salvando senha...", "info")

        # Substituir senha no banco
        if self.substituir_senha_no_banco(nova_senha):
            self._mostrar_status("✅ Senha salva! Testando login...", "success")
            self._limpar_campos()
            
            # Testar a nova senha no SEFAZ
            self.iniciar_automacao_web_trocar_senha()
        else:
            self._mostrar_status("❌ Erro ao salvar senha!", "error")
            if self.btn_trocar:
                self.btn_trocar.configure(state="normal", text="Alterar Senha")

    def _mostrar_status(self, mensagem: str, tipo: str):
        """Mostra mensagem de status com cor adequada"""
        if not self.status_label:
            return
            
        cores = {
            "success": _VERDE_STATUS,
            "error": _VERMELHO,
            "info": _AZUL,
            "warning": _AMARELO
        }
        self.status_label.configure(
            text=mensagem,
            text_color=cores.get(tipo, _MUTED)
        )
        self.update_idletasks()

    # ──────────────────────────────────────────────────────────────────────────
    # Selenium
    # ──────────────────────────────────────────────────────────────────────────
    def iniciar_automacao_web_trocar_senha(self):
        senha = self.carregar_senha_do_banco()
        
        if not senha:
            self._mostrar_status("❌ Nenhuma senha encontrada!", "error")
            if self.btn_trocar:
                self.btn_trocar.configure(state="normal", text="Alterar Senha")
            return

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-notifications")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--log-level=3")
        options.add_argument("--no-console")
        options.add_argument("--disable-logging")

        driver = None
        try:
            driver = webdriver.Chrome(options=options)
            driver.get("http://sistemas.sefaz.am.gov.br/gcc/entrada.do")

            usuario = driver.find_element(By.ID, "username")
            senha_da_pagina = driver.find_element(By.ID, "password")
            botao_login = driver.find_element(
                By.XPATH,
                '//*[@id="fm1"]/fieldset/div[3]/div/div[4]/input[4]'
            )

            usuario.send_keys("03483401253")
            senha_da_pagina.send_keys(senha)
            botao_login.click()

            try:
                mensagem_erro = driver.find_element(By.XPATH, '//*[@id="msg"]')
                if mensagem_erro:
                    self._mostrar_status("❌ Login falhou!", "error")
                    self.substituir_senha_no_banco("")
            except Exception:
                self._mostrar_status("✅ Login realizado com sucesso!", "success")
                messagebox.showinfo("Sucesso", "Senha alterada e testada com sucesso!")

        except Exception as e:
            self._mostrar_status(f"❌ Erro: {str(e)[:50]}", "error")
        finally:
            try:
                if driver:
                    driver.quit()
            except:
                pass
            if self.btn_trocar:
                self.btn_trocar.configure(state="normal", text="Alterar Senha")