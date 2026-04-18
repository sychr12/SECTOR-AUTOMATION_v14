# -*- coding: utf-8 -*-
"""
Tela de Login - PyQt6 com HTML/CSS/JS (Design Agropecuário) - Versão Corrigida
Carteira do Produtor Rural
"""

import sys
import json
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QMessageBox
from PyQt6.QtCore import QObject, pyqtSlot, QTimer, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel

# Importações do seu sistema
from services.login_repository import validar_usuario, registrar_acesso

# ── Configurações de "Lembrar-me" (com criptografia) ──────────────────────────
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)
REMEMBER_FILE = os.path.join(DATA_DIR, "remember_me.json")
SALT_FILE = os.path.join(DATA_DIR, "salt.key")


class RememberMeManager:
    def __init__(self):
        self.cipher = None
        self._init_crypto()

    def _init_crypto(self):
        try:
            if os.path.exists(SALT_FILE):
                with open(SALT_FILE, 'rb') as f:
                    salt = f.read()
            else:
                salt = os.urandom(16)
                with open(SALT_FILE, 'wb') as f:
                    f.write(salt)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(b"SECTOR_AUTOMATION_SECRET_KEY_2026"))
            self.cipher = Fernet(key)
        except Exception:
            self.cipher = Fernet(Fernet.generate_key())

    def _encrypt(self, data: str) -> str:
        if not data:
            return ""
        return self.cipher.encrypt(data.encode()).decode()

    def _decrypt(self, encrypted_data: str) -> str:
        if not encrypted_data:
            return ""
        try:
            return self.cipher.decrypt(encrypted_data.encode()).decode()
        except Exception:
            return ""

    def save_credentials(self, username: str, password: str, remember: bool):
        if remember and username and password:
            data = {
                "username": self._encrypt(username),
                "password": self._encrypt(password),
                "remember": True
            }
            with open(REMEMBER_FILE, 'w') as f:
                json.dump(data, f)
        elif not remember and os.path.exists(REMEMBER_FILE):
            os.remove(REMEMBER_FILE)

    def load_credentials(self):
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


# ── Bridge JS ↔ Python ────────────────────────────────────────────────────────
class LoginBridge(QObject):
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.remember_manager = RememberMeManager()

    @pyqtSlot(str)
    def doLogin(self, data_json):
        try:
            data = json.loads(data_json)
            username = data.get("username", "")
            password = data.get("password", "")
            remember = data.get("remember", False)

            if not username or not password:
                self.window.show_message("Preencha todos os campos!", error=True)
                return

            usuario = validar_usuario(username, password)

            if usuario:
                if remember:
                    self.remember_manager.save_credentials(username, password, True)
                else:
                    self.remember_manager.save_credentials("", "", False)

                registrar_acesso(usuario)

                nome_exibicao = usuario.get('nome') or usuario.get('username') or 'Usuario'
                msg = f"Acesso autorizado! Bem-vindo(a), {nome_exibicao}."
                self.window.show_message(msg, error=False)
                
                # Pequeno delay para mostrar a mensagem antes de redirecionar
                QTimer.singleShot(500, lambda: self.window.redirect_after_login(usuario))
            else:
                self.window.show_message("Usuario ou senha invalidos.", error=True)
                self.window.run_js('document.getElementById("passwordModern").value = "";')
        except Exception as e:
            self.window.show_message(f"Erro interno: {str(e)}", error=True)

    @pyqtSlot()
    def forgotPassword(self):
        QMessageBox.information(
            self.window,
            "Recuperar Senha",
            "Entre em contato com o suporte:\n\n"
            "suporte@idam.am.gov.br\n"
            "(92) 2121-0000\n"
            "WhatsApp (92) 98400-0000"
        )

    @pyqtSlot()
    def register(self):
        self.window.run_js('''
            document.getElementById("usernameModern").value = "admin";
            document.getElementById("passwordModern").value = "admin123";
            document.getElementById("rememberModern").checked = true;
            showMessage("Credenciais de demonstracao preenchidas! Clique em Entrar.", false);
        ''')

    @pyqtSlot(result=str)
    def loadSavedCredentials(self):
        user, pwd, remember = self.remember_manager.load_credentials()
        if user and remember:
            return json.dumps({"username": user, "password": pwd, "remember": True})
        return json.dumps({"username": "", "password": "", "remember": False})


# ── Janela Principal de Login (PyQt6) ─────────────────────────────────────────
class Login(QMainWindow):
    def __init__(self, on_success=None, parent=None):
        super().__init__(parent)
        self.on_success = on_success
        self.setWindowTitle("Sector Automation | Sistema Agropecuario")
        self.resize(1280, 800)
        self.setMinimumSize(900, 600)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)

        self.bridge = LoginBridge(self)
        
        # Configurar QWebChannel
        self.channel = QWebChannel(self.web_view.page())
        self.channel.registerObject("bridge", self.bridge)
        self.web_view.page().setWebChannel(self.channel)
        
        # Carregar o HTML
        self.web_view.setHtml(self._get_html())
        
        # Aguardar o carregamento da página para carregar as credenciais salvas
        self.web_view.loadFinished.connect(self._on_page_loaded)

    def _on_page_loaded(self, ok):
        if ok:
            # Carregar credenciais salvas
            self.run_js('''
                setTimeout(function() {
                    if (typeof loadSavedCredentials === 'function') {
                        loadSavedCredentials();
                    }
                }, 500);
            ''')

    def _get_html(self):
        # HTML compactado e otimizado
        return '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,user-scalable=yes">
<title>Sector Automation Login</title>
<script src="qrc:///qtwebchannel/qwebchannel.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',Roboto,Helvetica,Arial,sans-serif;background:#0f2a1f;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:1.5rem;background-image:radial-gradient(circle at 10% 20%,rgba(70,110,60,0.2)0%,rgba(20,45,30,0.95)90%)}
.login-wrapper{width:100%;max-width:1280px;background:rgba(255,255,245,0.96);border-radius:48px;overflow:hidden;display:flex;flex-wrap:wrap;box-shadow:0 20px 40px rgba(0,0,0,0.25);position:relative;z-index:2}
.agro-brand{flex:1.1;background:linear-gradient(125deg,#1d3e2b 0%,#2b5a36 100%);padding:2.8rem 2rem;display:flex;flex-direction:column;justify-content:space-between;color:#fef3da;position:relative;overflow:hidden}
.agro-brand::after{content:"🌾";font-size:180px;position:absolute;bottom:-30px;right:-30px;opacity:0.08;pointer-events:none}
.brand-header{margin-bottom:2rem;z-index:2;position:relative}
.logo-area{display:flex;align-items:center;gap:12px;margin-bottom:2rem}
.logo-icon{background:#f5b642;width:52px;height:52px;display:flex;align-items:center;justify-content:center;border-radius:28px;font-size:28px;color:#1f442d;box-shadow:0 8px 12px rgba(0,0,0,0.2)}
.logo-text h2{font-size:1.7rem;font-weight:800;letter-spacing:-0.5px;color:#ffefcf}
.logo-text p{font-size:0.75rem;opacity:0.8}
.brand-quote h3{font-size:2rem;font-weight:700;line-height:1.2;margin-bottom:1rem}
.highlight{color:#ffd966;border-bottom:2px solid #ffb347;display:inline-block}
.brand-features{margin-top:2rem;display:flex;flex-direction:column;gap:1rem}
.feature-item{display:flex;align-items:center;gap:14px;background:rgba(255,245,205,0.1);padding:0.8rem 1.2rem;border-radius:60px;width:fit-content;font-weight:500;font-size:0.9rem}
.sustainable-badge{margin-top:auto;padding-top:2rem;font-size:0.7rem;display:flex;gap:16px;flex-wrap:wrap;opacity:0.7}
.form-side{flex:1;background:#fff;padding:2.8rem 2.5rem;display:flex;flex-direction:column;justify-content:center}
.form-header .greeting{font-size:2rem;font-weight:800;color:#1f3d2c;letter-spacing:-0.3px}
.form-header .sub{color:#6e5c43;margin-top:8px;font-size:0.9rem;border-left:3px solid #e6b05c;padding-left:12px}
.input-field{margin-bottom:1.5rem}
.input-field label{display:block;margin-bottom:8px;font-weight:600;font-size:0.8rem;color:#4b5e3a}
.input-icon{position:relative}
.input-field input{width:100%;padding:14px 20px 14px 20px;font-size:0.95rem;border:1.5px solid #e9e0cf;border-radius:40px;background:#fefcf8;outline:none;color:#2b4127;transition:0.2s}
.input-field input:focus{border-color:#c29a4a;box-shadow:0 0 0 3px rgba(194,154,74,0.2);background:#fff}
.form-extras{display:flex;justify-content:space-between;align-items:center;margin:1rem 0 2rem;flex-wrap:wrap;gap:12px}
.checkbox-custom{display:flex;align-items:center;gap:8px;cursor:pointer;font-size:0.8rem;color:#5a6e48;font-weight:500}
.checkbox-custom input{width:18px;height:18px;accent-color:#c29a4a}
.forgot-link{font-size:0.8rem;color:#b46f2a;text-decoration:none;font-weight:600;cursor:pointer}
.btn-agro{background:linear-gradient(105deg,#2b623b,#1d452a);border:none;width:100%;padding:14px;border-radius:44px;font-weight:700;font-size:1rem;color:#fff;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:12px;box-shadow:0 6px 12px rgba(0,0,0,0.1);transition:0.2s}
.btn-agro:hover{background:linear-gradient(105deg,#235831,#153a22);transform:translateY(-2px);box-shadow:0 10px 18px rgba(0,0,0,0.15)}
.signup-text{text-align:center;margin-top:2rem;font-size:0.85rem;color:#7d6b4b;border-top:1px solid #efe3cf;padding-top:1.5rem}
.signup-text a{color:#2b623b;font-weight:700;text-decoration:none;margin-left:6px;cursor:pointer}
.toast-modern{visibility:hidden;min-width:260px;background:#2f5230;color:#fff5e3;text-align:center;border-radius:60px;padding:12px 20px;position:fixed;bottom:30px;left:50%;transform:translateX(-50%);font-weight:600;font-size:0.85rem;z-index:1000;box-shadow:0 6px 20px rgba(0,0,0,0.2);transition:visibility 0s,opacity 0.25s;opacity:0;pointer-events:none}
.toast-modern.show{visibility:visible;opacity:1}
@media(max-width:850px){.login-wrapper{flex-direction:column;max-width:550px}.agro-brand{padding:2rem}.brand-quote h3{font-size:1.6rem}.form-side{padding:2rem 1.8rem}.feature-item{width:100%}}
@media(max-width:480px){.form-header .greeting{font-size:1.7rem}.logo-text h2{font-size:1.3rem}}
@keyframes fadeSlide{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.form-side,.agro-brand{animation:fadeSlide 0.4s ease-out}
</style>
</head>
<body>
<div class="login-wrapper">
<div class="agro-brand">
<div class="brand-header"><div class="logo-area"><div class="logo-icon">🌿</div><div class="logo-text"><h2>Sector<span style="font-weight:400">Automation</span></h2><p>solucoes integradas para o agro</p></div></div><div class="brand-quote"><h3>Conectando o <span class="highlight">campo</span> ao <span class="highlight">futuro</span></h3></div></div>
<div class="brand-features">
<div class="feature-item">Gestao de Processos</div>
<div class="feature-item">Carteira Digital</div>
<div class="feature-item">Anexacao de Documentos</div>
<div class="feature-item">Analise de Processos</div>
</div>
<div class="sustainable-badge"><span>Seguranca de Dados</span><span>Suporte 24h</span></div>
</div>
<div class="form-side">
<div class="form-header"><div class="greeting">Bem-vindo</div><div class="sub">Acesse sua conta e gerencie suas operacoes</div></div>
<form id="loginFormModern">
<div class="input-field"><label>Usuario</label><div class="input-icon"><input type="text" id="usernameModern" placeholder="ex: admin" autocomplete="off"></div></div>
<div class="input-field"><label>Senha</label><div class="input-icon"><input type="password" id="passwordModern" placeholder="••••••••"></div></div>
<div class="form-extras"><label class="checkbox-custom"><input type="checkbox" id="rememberModern"> Manter conectado</label><a href="#" id="forgotModernLink" class="forgot-link">Esqueci minha senha</a></div>
<button type="submit" class="btn-agro">Entrar no sistema</button>
<div class="signup-text">Nao possui uma conta? <a href="#" id="registerModernLink">Credenciais de demonstracao</a></div>
</form>
<div style="display:flex;justify-content:center;gap:16px;margin-top:28px;font-size:0.7rem;color:#b9aa87"><span>Seguranca de dados</span><span>Suporte 24h</span></div>
</div>
</div>
<div id="toastModern" class="toast-modern">Sistema Sector Automation</div>
<script>
var bridge = null;

function showMessage(msg, isError) {
    var toast = document.getElementById('toastModern');
    toast.textContent = msg;
    toast.style.backgroundColor = isError ? '#b6512e' : '#2f5230';
    toast.classList.add('show');
    setTimeout(function() {
        toast.classList.remove('show');
        toast.style.backgroundColor = '#2f5230';
    }, 2800);
}

function loadSavedCredentials() {
    if (bridge && typeof bridge.loadSavedCredentials === 'function') {
        try {
            var data = JSON.parse(bridge.loadSavedCredentials());
            if (data.username && data.remember) {
                document.getElementById('usernameModern').value = data.username;
                document.getElementById('passwordModern').value = data.password;
                document.getElementById('rememberModern').checked = true;
            }
        } catch(e) {
            console.error('Erro ao carregar credenciais:', e);
        }
    }
}

// Inicializar QWebChannel
new QWebChannel(qt.webChannelTransport, function(channel) {
    bridge = channel.objects.bridge;
    console.log('Bridge conectado com sucesso!');
    loadSavedCredentials();
});

document.getElementById('loginFormModern').addEventListener('submit', function(e) {
    e.preventDefault();
    var u = document.getElementById('usernameModern').value;
    var p = document.getElementById('passwordModern').value;
    var r = document.getElementById('rememberModern').checked;
    if (!u || !p) {
        showMessage('Preencha todos os campos!', true);
        return;
    }
    if (bridge && typeof bridge.doLogin === 'function') {
        bridge.doLogin(JSON.stringify({username: u, password: p, remember: r}));
    } else {
        showMessage('Erro de comunicacao. Reinicie o sistema.', true);
    }
});

document.getElementById('forgotModernLink').addEventListener('click', function(e) {
    e.preventDefault();
    if (bridge && typeof bridge.forgotPassword === 'function') {
        bridge.forgotPassword();
    }
});

document.getElementById('registerModernLink').addEventListener('click', function(e) {
    e.preventDefault();
    if (bridge && typeof bridge.register === 'function') {
        bridge.register();
    }
});
</script>
</body>
</html>'''

    def run_js(self, code):
        self.web_view.page().runJavaScript(code)

    def show_message(self, msg, error=False):
        safe_msg = json.dumps(msg)
        self.run_js(f'showMessage({safe_msg}, {str(error).lower()});')

    def redirect_after_login(self, usuario):
        if self.on_success:
            self.on_success(usuario)
        self.close()