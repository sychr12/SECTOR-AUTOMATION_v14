# -*- coding: utf-8 -*-
"""
AgroFarm — Painel Administrativo Premium
Com ícones personalizados e integração com abas
"""

import sys
import os
from datetime import datetime
import inspect

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QMessageBox, QStackedWidget,
    QScrollArea, QApplication
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtGui import QPixmap, QIcon, QFont

# Adicionar path
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from services.database import get_connection


# ═══════════════════════════════════════════════════════
# PALETA DE CORES
# ═══════════════════════════════════════════════════════
COLORS = {
    "bg": "#f0f3f0",
    "sidebar": "#0a0f0d",
    "sidebar_dark": "#060a08",
    "card": "#ffffff",
    "emerald": "#00b96b",
    "gold": "#d4af37",
    "danger": "#e05252",
    "info": "#3a8ee8",
    "warn": "#f39c12",
    "purple": "#9b59b6",
    "cyan": "#06b6d4",
    "text_light": "#9ab89e",
    "text_dark": "#1a2a1f",
    "text_muted": "#7a9a7e",
    "border_light": "rgba(255,255,255,0.1)",
}


# ═══════════════════════════════════════════════════════
# GERENCIADOR DE ÍCONES
# ═══════════════════════════════════════════════════════
class IconManager:
    """Gerencia ícones personalizados da sidebar"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.icons = {}
        self.icons_path = None
        self._find_icons_path()
    
    def _find_icons_path(self):
        """Encontra o caminho correto da pasta de ícones"""
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        possible_paths = [
            os.path.join(current_dir, "images", "icons", "sidebar_adm"),
            os.path.join(current_dir, "images", "icons", "sidebar"),
            os.path.join(os.path.dirname(current_dir), "images", "icons", "sidebar_adm"),
            os.path.join(os.path.dirname(current_dir), "images", "icons", "sidebar"),
            r"images\icons\sidebar_adm",
            r"images\icons\sidebar",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                self.icons_path = path
                return
        
        self.icons_path = None
    
    def get_icon(self, name, size=(24, 24)):
        """Retorna um QIcon ou QLabel com o ícone"""
        if not self.icons_path:
            return None
        
        icon_files = {
            "dashboard": "dashboard.png",
            "consultar": "consultar.png",
            "email": "email.png",
            "analises": "analises.png",
            "analiseap": "analiseap.png",
            "relatorios": "relatorios.png",
            "carteira": "carteira.png",
            "lancamentos": "lancamentos.png",
            "devolucao": "devolucao.png",
            "usuarios": "usuarios.png",
            "senha": "senha.png",
            "memorando": "memorando.png",
            "anexar": "anexar.png",
            "adicionar": "adicionar.png",
            "notificacao": "notificacao.png",
            "sair": "sair.png",
            "logo": "logo.png",
        }
        
        filename = icon_files.get(name)
        if not filename:
            return None
        
        filepath = os.path.join(self.icons_path, filename)
        if os.path.exists(filepath):
            pixmap = QPixmap(filepath)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(
                    size[0],
                    size[1],
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                return QIcon(pixmap)
        return None
    
    def get_icon_label(self, name, size=(24, 24)):
        """Retorna um QLabel com o ícone"""
        icon = self.get_icon(name, size)
        if icon:
            label = QLabel()
            label.setPixmap(icon.pixmap(size[0], size[1]))
            return label
        return None


# ═══════════════════════════════════════════════════════
# BOTÃO DE MENU COM ÍCONE
# ═══════════════════════════════════════════════════════
class MenuButton(QPushButton):
    def __init__(self, nome, icone_key, cor=COLORS["emerald"]):
        super().__init__()
        self.nome = nome
        self.cor = cor
        self._active = False
        self.icone_key = icone_key
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(42)
        self._setup_icon()
        self._apply_style()
    
    def _setup_icon(self):
        """Configura o ícone do botão"""
        icon_manager = IconManager()
        icon = icon_manager.get_icon(self.icone_key, (20, 20))
        
        if icon:
            self.setIcon(icon)
            self.setIconSize(QSize(20, 20))
            self.setText(f"   {self.nome}")
        else:
            emojis = {
                "dashboard": "📊", "consultar": "🔍", "email": "📧",
                "analises": "📈", "analiseap": "🔬", "relatorios": "📉",
                "carteira": "💰", "lancamentos": "📝", "devolucao": "🔄",
                "usuarios": "👥", "senha": "🔐", "memorando": "📋",
                "anexar": "📎", "adicionar": "➕", "notificacao": "🔔",
            }
            emoji = emojis.get(self.icone_key, "📄")
            self.setText(f"  {emoji}   {self.nome}")
    
    def _apply_style(self):
        if self._active:
            self.setStyleSheet(f"""
                QPushButton {{
                    text-align: left;
                    padding: 10px 14px;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: 700;
                    color: {self.cor};
                    background: rgba({self._hex_to_rgb(self.cor)},0.15);
                    border-left: 3px solid {self.cor};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    text-align: left;
                    padding: 10px 14px;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: 500;
                    color: {COLORS['text_light']};
                    background: transparent;
                    border: none;
                }}
                QPushButton:hover {{
                    background: rgba(255,255,255,0.08);
                    color: {COLORS['text_light']};
                }}
            """)
    
    def set_active(self, active):
        self._active = active
        self._apply_style()
    
    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
            return f"{r},{g},{b}"
        return "0,185,107"


# ═══════════════════════════════════════════════════════
# TELA PLACEHOLDER
# ═══════════════════════════════════════════════════════
class PlaceholderTela(QWidget):
    def __init__(self, nome, cor=COLORS["emerald"]):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon = QLabel("📄")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size: 48px;")
        
        title = QLabel(nome)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {COLORS['text_dark']};")
        
        status = QLabel("Em Desenvolvimento")
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status.setStyleSheet(f"font-size: 14px; color: {cor};")
        
        layout.addWidget(icon)
        layout.addWidget(title)
        layout.addWidget(status)


# ═══════════════════════════════════════════════════════
# FUNÇÃO PARA CARREGAR TELAS REAIS
# ═══════════════════════════════════════════════════════
def carregar_tela_real(parent, usuario, nome_modulo, nome_classe, nome_tela, conectar_bd=None):
    """Carrega uma tela real do sistema"""
    try:
        modulo_path = f"ui.abas.{nome_modulo}"
        modulo = __import__(modulo_path, fromlist=[nome_classe])

        if hasattr(modulo, nome_classe):
            classe = getattr(modulo, nome_classe)

            tentativas = [
                lambda: classe(parent=parent, usuario=usuario, conectar_bd=conectar_bd),
                lambda: classe(parent=parent, usuario=usuario),
                lambda: classe(parent, usuario),
                lambda: classe(usuario=usuario, conectar_bd=conectar_bd),
                lambda: classe(usuario=usuario),
                lambda: classe(parent=parent),
                lambda: classe(parent),
                lambda: classe(conectar_bd=conectar_bd),
                lambda: classe(),
            ]

            for tentativa in tentativas:
                try:
                    tela = tentativa()
                    if isinstance(tela, QWidget):
                        return tela
                except TypeError:
                    continue
                except Exception as e:
                    print(f"Erro ao instanciar tela {nome_tela}: {e}")
                    return None

        return None
    except Exception as e:
        print(f"Erro ao carregar tela {nome_tela}: {e}")
        return None


# ═══════════════════════════════════════════════════════
# MENU ADMINISTRADOR
# ═══════════════════════════════════════════════════════
class MenuAdministrador(QMainWindow):
    
    def __init__(self, usuario, on_logout=None, conectar_bd=None):
        super().__init__()
        self.usuario = usuario.get("username", usuario.get("nome", "Admin"))
        self.usuario_data = usuario
        self.on_logout = on_logout
        self.conectar_bd = conectar_bd or get_connection
        
        self.setWindowTitle("Sector Automation | Painel Administrativo")
        self.resize(1280, 800)
        self.setMinimumSize(1024, 600)
        
        self.buttons = {}
        self.screens = {}
        self.icon_manager = IconManager()
        
        self._setup_ui()
        self._init_clock()
        
        # Animação de entrada
        self.setWindowOpacity(0.0)
        self.fade_in = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in.setDuration(400)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.fade_in.start()
    
    def _setup_ui(self):
        central = QWidget()
        central.setStyleSheet(f"background: {COLORS['bg']};")
        self.setCentralWidget(central)
        
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        main_layout.addWidget(self._create_sidebar())
        
        # Area de conteudo
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(16)
        
        # Topbar
        content_layout.addWidget(self._create_topbar())
        
        # Stack de telas
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background: {COLORS['card']}; border-radius: 20px;")
        content_layout.addWidget(self.stack)
        
        main_layout.addWidget(content_widget, 1)
        
        # Carregar telas
        self._load_screens()
        
        # Abrir tela inicial
        self.open_screen("Dashboard")
    
    def _create_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 {COLORS['sidebar']}, stop:1 {COLORS['sidebar_dark']});
            }}
        """)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 30, 16, 20)
        layout.setSpacing(8)
        
        # Logo com ícone
        logo_frame = QFrame()
        logo_layout = QHBoxLayout(logo_frame)
        logo_layout.setContentsMargins(8, 0, 8, 0)
        
        logo_icon = self.icon_manager.get_icon_label("logo", (40, 40))
        if logo_icon:
            logo_layout.addWidget(logo_icon)
        
        logo_text = QLabel("Sector")
        logo_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_text.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        logo_layout.addWidget(logo_text)
        logo_layout.addStretch()
        
        layout.addWidget(logo_frame)
        
        # Separador
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background: {COLORS['border_light']}; height: 1px; margin: 10px 0;")
        layout.addWidget(sep)
        
        # Menu seções
        secoes = [
            ("PRINCIPAL", [
                ("dashboard", "Dashboard", COLORS["emerald"]),
                ("consultar", "Consultar", COLORS["info"]),
                ("email", "Email", COLORS["purple"]),
            ]),
            ("ANALISES", [
                ("analises", "Analises", COLORS["info"]),
                ("analiseap", "AnaliseAP", COLORS["cyan"]),
                ("relatorios", "Relatorios", COLORS["warn"]),
            ]),
            ("FINANCEIRO", [
                ("carteira", "Carteira", COLORS["gold"]),
                ("lancamentos", "Lancamentos", COLORS["emerald"]),
                ("devolucao", "Devolucao", COLORS["danger"]),
            ]),
            ("ADMINISTRACAO", [
                ("usuarios", "Usuarios", COLORS["info"]),
                ("senha", "Senha", COLORS["danger"]),
                ("memorando", "Memorando", COLORS["warn"]),
                ("anexar", "Anexar", COLORS["cyan"]),
                ("adicionar", "Adicionar", COLORS["emerald"]),
            ]),
            ("SISTEMA", [
                ("notificacao", "Notificacao", COLORS["danger"]),
            ]),
        ]
        
        for titulo, itens in secoes:
            title = QLabel(titulo)
            title.setStyleSheet(
                f"color: {COLORS['text_muted']}; font-size: 10px; "
                f"font-weight: bold; letter-spacing: 1px; margin-top: 15px;"
            )
            layout.addWidget(title)
            
            for icone_key, nome, cor in itens:
                btn = MenuButton(nome, icone_key, cor)
                btn.clicked.connect(lambda checked=False, x=nome: self.open_screen(x))
                layout.addWidget(btn)
                self.buttons[nome] = btn
        
        layout.addStretch()
        
        # Info usuario
        user_frame = QFrame()
        user_frame.setStyleSheet("background: rgba(255,255,255,0.06); border-radius: 12px; padding: 8px;")
        user_layout = QHBoxLayout(user_frame)
        
        user_icon = QLabel("👤")
        user_icon.setStyleSheet("font-size: 24px;")
        
        user_info = QVBoxLayout()
        user_info.setSpacing(2)
        user_name = QLabel(self.usuario)
        user_name.setStyleSheet("color: white; font-size: 12px; font-weight: bold;")
        user_role = QLabel("Administrador")
        user_role.setStyleSheet("color: #00b96b; font-size: 10px;")
        user_info.addWidget(user_name)
        user_info.addWidget(user_role)
        
        user_layout.addWidget(user_icon)
        user_layout.addLayout(user_info)
        user_layout.addStretch()
        
        layout.addWidget(user_frame)
        
        # Botao sair
        btn_sair = QPushButton("  🚪   Sair")
        btn_sair.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_sair.setStyleSheet("""
            QPushButton {
                padding: 10px;
                border-radius: 10px;
                font-weight: bold;
                color: #ff9090;
                background: rgba(224,82,82,0.15);
                margin-top: 10px;
                text-align: left;
            }
            QPushButton:hover {
                background: #e05252;
                color: white;
            }
        """)
        btn_sair.clicked.connect(self.sair)
        layout.addWidget(btn_sair)
        
        scroll.setWidget(container)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.addWidget(scroll)
        
        return sidebar
    
    def _create_topbar(self):
        topbar = QFrame()
        topbar.setFixedHeight(60)
        topbar.setStyleSheet(f"background: {COLORS['card']}; border-radius: 16px;")
        
        layout = QHBoxLayout(topbar)
        layout.setContentsMargins(24, 0, 24, 0)
        
        self.screen_title = QLabel("Dashboard")
        self.screen_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1a2a1f;")
        
        # Status
        status = QFrame()
        status.setStyleSheet(f"background: {COLORS['emerald']}15; border-radius: 20px;")
        status_layout = QHBoxLayout(status)
        status_layout.setContentsMargins(12, 6, 16, 6)
        
        dot = QLabel("●")
        dot.setStyleSheet(f"color: {COLORS['emerald']}; font-size: 10px;")
        status_text = QLabel("Sistema Online")
        status_text.setStyleSheet(f"color: {COLORS['emerald']}; font-size: 11px; font-weight: 600;")
        
        status_layout.addWidget(dot)
        status_layout.addWidget(status_text)
        
        # Relogio
        self.clock_label = QLabel()
        self.clock_label.setStyleSheet(f"""
            background: {COLORS['bg']};
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            color: {COLORS['text_dark']};
        """)
        
        layout.addWidget(self.screen_title)
        layout.addStretch()
        layout.addWidget(status)
        layout.addSpacing(12)
        layout.addWidget(self.clock_label)
        
        return topbar
    
    def _load_screens(self):
        """Carrega todas as telas no stack"""

        # Dashboard
        dashboard = carregar_tela_real(
            self,
            self.usuario_data,
            "home",
            "HomeUI",
            "Dashboard",
            conectar_bd=self.conectar_bd
        )
        if dashboard is None:
            dashboard = PlaceholderTela("Dashboard")

        self.stack.addWidget(dashboard)
        self.screens["Dashboard"] = dashboard
        
        # Mapeamento das telas
        telas_config = [
            ("Consultar", "Consultar", "ConsultarUI"),
            ("Email", "Email", "BaixarEmailUI"),
            ("Analises", "Analises", "AnaliseUI"),
            ("AnaliseAP", "analiseap", "AnaliseapUI"),
            ("Relatorios", "relatorios", "RelatoriosUI"),
            ("Carteira", "Carteira", "CarteiraDigitalUI"),
            ("Lancamentos", "lancamentos", "LancamentoUI"),
            ("Devolucao", "devolucao", "DevolucaoUI"),
            ("Usuarios", "usuarios", "GerenciarUsuariosUI"),
            ("Senha", "senha", "SenhaUI"),
            ("Memorando", "memorando", "MemorandoUI"),
            ("Anexar", "anexar", "AnexarUI"),
            ("Adicionar", "adicionar", "AdicionarUI"),
            ("Notificacao", "notificacao", "NotificacaoUI"),
        ]
        
        for nome_tela, modulo_nome, classe_nome in telas_config:
            tela = carregar_tela_real(
                self,
                self.usuario_data,
                modulo_nome,
                classe_nome,
                nome_tela,
                conectar_bd=self.conectar_bd
            )
            if tela is None:
                tela = PlaceholderTela(nome_tela)
            
            self.stack.addWidget(tela)
            self.screens[nome_tela] = tela
    
    def open_screen(self, nome):
        if nome in self.screens:
            self.screen_title.setText(nome)
            self.stack.setCurrentWidget(self.screens[nome])
            
            for n, btn in self.buttons.items():
                btn.set_active(n == nome)
    
    def _init_clock(self):
        self.update_clock()
        timer = QTimer(self)
        timer.timeout.connect(self.update_clock)
        timer.start(1000)
    
    def update_clock(self):
        self.clock_label.setText(datetime.now().strftime("%d/%m/%Y  •  %H:%M"))
    
    def sair(self):
        resp = QMessageBox.question(
            self, "Sair",
            "Deseja realmente sair do sistema?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if resp == QMessageBox.StandardButton.Yes:
            self.fade_out = QPropertyAnimation(self, b"windowOpacity")
            self.fade_out.setDuration(300)
            self.fade_out.setStartValue(1.0)
            self.fade_out.setEndValue(0.0)
            self.fade_out.setEasingCurve(QEasingCurve.Type.InCubic)
            self.fade_out.finished.connect(self._do_logout)
            self.fade_out.start()
    
    def _do_logout(self):
        self.close()
        if self.on_logout:
            self.on_logout()


# ═══════════════════════════════════════════════════════
# TESTE DIRETO
# ═══════════════════════════════════════════════════════
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    usuario = {
        "username": "Administrador",
        "nome": "Admin Sistema",
        "perfil": "administrador",
        "email": "admin@agrofarm.com"
    }
    
    window = MenuAdministrador(usuario)
    window.show()
    sys.exit(app.exec())