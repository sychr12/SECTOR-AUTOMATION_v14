# -*- coding: utf-8 -*-
"""
Menu Principal - AppPrincipal (Usuário Comum)
Com todas as telas integradas do sistema
HOME é o DASHBOARD principal
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
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve

# Adicionar path
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)


# ═══════════════════════════════════════════════════════
# PALETA DE CORES PREMIUM
# ═══════════════════════════════════════════════════════
C = {
    "bg":           "#f5f7fa",
    "sidebar":      "#1a3a2a",
    "sidebar_dark": "#0f2a1f",
    "card":         "#ffffff",
    "surface":      "#f0f4ef",
    "emerald":      "#00b96b",
    "gold":         "#f5b642",
    "danger":       "#ef4444",
    "info":         "#3b82f6",
    "warn":         "#f59e0b",
    "purple":       "#8b5cf6",
    "cyan":         "#06b6d4",
    "txt_primary":  "#1f2937",
    "txt_secondary": "#6b7280",
    "txt_muted":    "#9ca3af",
    "txt_sidebar":  "#d4d8d4",
    "txt_white":    "#ffffff",
    "border":       "rgba(0,0,0,0.06)",
    "border_light": "rgba(255,255,255,0.1)",
}


# ═══════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════
def label(txt, size=13, weight=500, color="#000"):
    l = QLabel(txt)
    l.setStyleSheet(f"font-size:{size}px; font-weight:{weight}; color:{color}; background:transparent;")
    return l


def separator():
    sep = QFrame()
    sep.setFrameShape(QFrame.Shape.HLine)
    sep.setStyleSheet(f"background: {C['border_light']}; height: 1px; margin: 8px 0;")
    return sep


# ═══════════════════════════════════════════════════════
# BOTAO DE MENU PREMIUM
# ═══════════════════════════════════════════════════════
class MenuButton(QPushButton):
    def __init__(self, emoji, nome, cor=C["emerald"]):
        super().__init__(f"  {emoji}   {nome}")
        self.nome = nome
        self.cor = cor
        self._active = False
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(42)
        self._apply_style()
        
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
                    color: {C['txt_sidebar']};
                    background: transparent;
                    border: none;
                }}
                QPushButton:hover {{
                    background: rgba(255,255,255,0.08);
                    color: {C['txt_white']};
                    padding-left: 20px;
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
        return "245,182,66"


# ═══════════════════════════════════════════════════════
# JANELA PRINCIPAL - APP PRINCIPAL
# ═══════════════════════════════════════════════════════
class AppPrincipal(QMainWindow):

    def __init__(self, usuario, on_logout=None):
        super().__init__()
        self.usuario = usuario.get("username", usuario.get("nome", "Usuário"))
        self.usuario_data = usuario
        self.perfil = usuario.get("perfil", "usuario")
        self.on_logout = on_logout

        self.setWindowTitle("AgroFarm | Gestão Agropecuária")
        self.resize(1300, 850)
        self.setMinimumSize(1100, 700)
        
        self.telas = {}
        self.botoes = {}
        
        self._setup_ui()
        self._init_clock()
        
        # Animacao de entrada
        self.setWindowOpacity(0.0)
        self.fade_in = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in.setDuration(400)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.fade_in.start()
    
    def _setup_ui(self):
        central = QWidget()
        central.setStyleSheet(f"background: {C['bg']};")
        self.setCentralWidget(central)
        
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        main_layout.addWidget(self._criar_sidebar())
        
        # Area de conteudo
        content_area = QVBoxLayout()
        content_area.setContentsMargins(16, 16, 16, 16)
        content_area.setSpacing(16)
        
        # Topbar
        content_area.addWidget(self._criar_topbar())
        
        # Stack de telas
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"""
            QStackedWidget {{
                background: {C['card']};
                border-radius: 20px;
            }}
        """)
        content_area.addWidget(self.stack)
        
        main_layout.addLayout(content_area, 1)
        
        # Carregar telas
        self._carregar_telas()
        
        # Abrir tela inicial (HOME como Dashboard)
        QTimer.singleShot(100, lambda: self.abrir_tela("Dashboard"))
    
    def _criar_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 {C['sidebar']}, stop:1 {C['sidebar_dark']});
                border-top-right-radius: 24px;
                border-bottom-right-radius: 24px;
            }}
        """)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 24, 16, 24)
        layout.setSpacing(12)
        
        # ========== LOGO ==========
        logo_frame = QFrame()
        logo_layout = QHBoxLayout(logo_frame)
        logo_layout.setContentsMargins(8, 0, 8, 0)
        
        logo_icon = QLabel("🌿")
        logo_icon.setStyleSheet(f"""
            font-size: 28px;
            background: {C['gold']};
            border-radius: 16px;
            padding: 8px;
            min-width: 48px;
            min-height: 48px;
        """)
        logo_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        logo_text = QLabel("AgroFarm\nTech")
        logo_text.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 800;
            color: {C['txt_white']};
            letter-spacing: -0.5px;
        """)
        
        logo_layout.addWidget(logo_icon)
        logo_layout.addWidget(logo_text)
        logo_layout.addStretch()
        layout.addWidget(logo_frame)
        layout.addWidget(separator())
        
        # ========== SECAO PRINCIPAL ==========
        layout.addWidget(label("PRINCIPAL", 10, 700, C["txt_muted"]))
        layout.addSpacing(4)
        
        btn_dash = MenuButton("🏠", "Dashboard", C["emerald"])
        btn_dash.clicked.connect(lambda: self.abrir_tela("Dashboard"))
        layout.addWidget(btn_dash)
        self.botoes["Dashboard"] = btn_dash
        
        btn_consultar = MenuButton("🔍", "Consultar", C["info"])
        btn_consultar.clicked.connect(lambda: self.abrir_tela("Consultar"))
        layout.addWidget(btn_consultar)
        self.botoes["Consultar"] = btn_consultar
        
        layout.addSpacing(8)
        
        # ========== SECAO ANALISES ==========
        layout.addWidget(label("ANÁLISES", 10, 700, C["txt_muted"]))
        layout.addSpacing(4)
        
        btn_analises = MenuButton("📈", "Análises", C["purple"])
        btn_analises.clicked.connect(lambda: self.abrir_tela("Analises"))
        layout.addWidget(btn_analises)
        self.botoes["Analises"] = btn_analises
        
        btn_analiseap = MenuButton("🔬", "Análise AP", C["cyan"])
        btn_analiseap.clicked.connect(lambda: self.abrir_tela("AnaliseAP"))
        layout.addWidget(btn_analiseap)
        self.botoes["AnaliseAP"] = btn_analiseap
        
        btn_relatorios = MenuButton("📊", "Relatórios", C["warn"])
        btn_relatorios.clicked.connect(lambda: self.abrir_tela("Relatorios"))
        layout.addWidget(btn_relatorios)
        self.botoes["Relatorios"] = btn_relatorios
        
        layout.addSpacing(8)
        
        # ========== SECAO FINANCEIRO ==========
        layout.addWidget(label("FINANCEIRO", 10, 700, C["txt_muted"]))
        layout.addSpacing(4)
        
        btn_carteira = MenuButton("💰", "Carteira", C["gold"])
        btn_carteira.clicked.connect(lambda: self.abrir_tela("Carteira"))
        layout.addWidget(btn_carteira)
        self.botoes["Carteira"] = btn_carteira
        
        btn_lancamentos = MenuButton("📝", "Lançamentos", C["emerald"])
        btn_lancamentos.clicked.connect(lambda: self.abrir_tela("Lancamentos"))
        layout.addWidget(btn_lancamentos)
        self.botoes["Lancamentos"] = btn_lancamentos
        
        btn_devolucao = MenuButton("🔄", "Devolução", C["danger"])
        btn_devolucao.clicked.connect(lambda: self.abrir_tela("Devolucao"))
        layout.addWidget(btn_devolucao)
        self.botoes["Devolucao"] = btn_devolucao
        
        layout.addSpacing(8)
        
        # ========== SECAO DOCUMENTOS ==========
        layout.addWidget(label("DOCUMENTOS", 10, 700, C["txt_muted"]))
        layout.addSpacing(4)
        
        btn_email = MenuButton("📧", "E-mail", C["purple"])
        btn_email.clicked.connect(lambda: self.abrir_tela("Email"))
        layout.addWidget(btn_email)
        self.botoes["Email"] = btn_email
        
        btn_memorando = MenuButton("📋", "Memorando", C["info"])
        btn_memorando.clicked.connect(lambda: self.abrir_tela("Memorando"))
        layout.addWidget(btn_memorando)
        self.botoes["Memorando"] = btn_memorando
        
        btn_anexar = MenuButton("📎", "Anexar", C["cyan"])
        btn_anexar.clicked.connect(lambda: self.abrir_tela("Anexar"))
        layout.addWidget(btn_anexar)
        self.botoes["Anexar"] = btn_anexar
        
        btn_adicionar = MenuButton("➕", "Adicionar", C["emerald"])
        btn_adicionar.clicked.connect(lambda: self.abrir_tela("Adicionar"))
        layout.addWidget(btn_adicionar)
        self.botoes["Adicionar"] = btn_adicionar
        
        layout.addSpacing(8)
        
        # ========== SECAO SISTEMA ==========
        layout.addWidget(label("SISTEMA", 10, 700, C["txt_muted"]))
        layout.addSpacing(4)
        
        btn_senha = MenuButton("🔐", "Alterar Senha", C["danger"])
        btn_senha.clicked.connect(lambda: self.abrir_tela("Senha"))
        layout.addWidget(btn_senha)
        self.botoes["Senha"] = btn_senha
        
        layout.addStretch()
        layout.addWidget(separator())
        
        # ========== USUARIO ==========
        user_frame = QFrame()
        user_frame.setStyleSheet(f"""
            QFrame {{
                background: rgba(255,255,255,0.06);
                border-radius: 16px;
                padding: 8px;
            }}
        """)
        
        user_layout = QHBoxLayout(user_frame)
        user_layout.setContentsMargins(12, 10, 12, 10)
        user_layout.setSpacing(12)
        
        avatar = QLabel("👤")
        avatar.setStyleSheet(f"""
            font-size: 24px;
            background: rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 6px;
        """)
        
        user_info = QVBoxLayout()
        user_info.setSpacing(2)
        user_info.addWidget(label(self.usuario, 12, 700, C["txt_white"]))
        
        status_lbl = QLabel("● Online")
        status_lbl.setStyleSheet(f"font-size: 10px; color: {C['emerald']};")
        user_info.addWidget(status_lbl)
        
        user_layout.addWidget(avatar)
        user_layout.addLayout(user_info)
        user_layout.addStretch()
        
        layout.addWidget(user_frame)
        layout.addSpacing(8)
        
        # ========== BOTAO SAIR ==========
        btn_sair = QPushButton("  🚪   Sair do Sistema")
        btn_sair.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_sair.setStyleSheet(f"""
            QPushButton {{
                text-align: left;
                padding: 12px 16px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
                color: #ffb3b3;
                background: rgba(239,68,68,0.15);
                border: 1px solid rgba(239,68,68,0.3);
            }}
            QPushButton:hover {{
                background: {C['danger']};
                color: white;
                border-color: {C['danger']};
            }}
        """)
        btn_sair.clicked.connect(self.sair)
        layout.addWidget(btn_sair)
        
        scroll.setWidget(container)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.addWidget(scroll)
        
        return sidebar
    
    def _criar_topbar(self):
        topbar = QFrame()
        topbar.setFixedHeight(64)
        topbar.setStyleSheet(f"""
            QFrame {{
                background: {C['card']};
                border-radius: 20px;
                border: 1px solid {C['border']};
            }}
        """)
        
        layout = QHBoxLayout(topbar)
        layout.setContentsMargins(24, 0, 24, 0)
        
        self.titulo_label = QLabel("Dashboard")
        self.titulo_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 800;
            color: {C['txt_primary']};
        """)
        
        status_frame = QFrame()
        status_frame.setStyleSheet(f"""
            QFrame {{
                background: {C['emerald']}12;
                border-radius: 20px;
                border: 1px solid {C['emerald']}25;
            }}
        """)
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(12, 6, 16, 6)
        status_layout.setSpacing(8)
        
        status_dot = QLabel("●")
        status_dot.setStyleSheet(f"color: {C['emerald']}; font-size: 10px;")
        status_text = label("Sistema Online", 11, 600, C["emerald"])
        
        status_layout.addWidget(status_dot)
        status_layout.addWidget(status_text)
        
        self.clock_label = QLabel()
        self.clock_label.setStyleSheet(f"""
            font-size: 12px;
            font-weight: 600;
            color: {C['txt_secondary']};
            background: {C['bg']};
            padding: 8px 18px;
            border-radius: 20px;
        """)
        
        layout.addWidget(self.titulo_label)
        layout.addStretch()
        layout.addWidget(status_frame)
        layout.addSpacing(12)
        layout.addWidget(self.clock_label)
        
        return topbar

    def _instanciar_tela(self, classe, nome_tela):
        """
        Instancia as telas de forma segura, sem inverter parent/usuario.
        """
        try:
            if nome_tela == "Memorando":
                return classe(self, self.usuario_data)

            try:
                return classe(parent=self, usuario=self.usuario_data)
            except TypeError:
                pass

            try:
                return classe(self, self.usuario_data)
            except TypeError:
                pass

            try:
                return classe(usuario=self.usuario_data)
            except TypeError:
                pass

            try:
                return classe(parent=self)
            except TypeError:
                pass

            try:
                return classe(self)
            except TypeError:
                pass

            try:
                return classe(conectar_bd=self._conectar_bd)
            except TypeError:
                pass

            try:
                return classe()
            except TypeError:
                pass

            return None
        except Exception as e:
            print(f"Erro ao instanciar tela {nome_tela}: {e}")
            return None
    
    def _carregar_tela_real(self, nome_modulo, nome_classe, nome_tela):
        """Tenta carregar uma tela real do sistema"""
        try:
            modulo_path = f"ui.abas.{nome_modulo}"
            modulo = __import__(modulo_path, fromlist=[nome_classe])
            
            if hasattr(modulo, nome_classe):
                classe = getattr(modulo, nome_classe)
                tela = self._instanciar_tela(classe, nome_tela)
                if isinstance(tela, QWidget):
                    return tela
            return None
        except Exception as e:
            print(f"Erro ao carregar tela {nome_tela}: {e}")
            return None
    
    def _conectar_bd(self):
        """Conexão com banco de dados"""
        try:
            from services.database import get_connection
            return get_connection()
        except Exception:
            return None
    
    def _criar_tela_placeholder(self, nome):
        """Cria uma tela placeholder para módulos não implementados"""
        tela = QWidget()
        tela.setStyleSheet("background: transparent;")
        
        layout = QVBoxLayout(tela)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        
        icones = {
            "Consultar": "🔍", "Email": "📧", "Analises": "📈",
            "AnaliseAP": "🔬", "Relatorios": "📊", "Carteira": "💰",
            "Lancamentos": "📝", "Devolucao": "🔄", "Memorando": "📋",
            "Anexar": "📎", "Adicionar": "➕", "Senha": "🔐"
        }
        
        icon_lbl = QLabel(icones.get(nome, "📄"))
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet("font-size: 56px; padding: 24px;")
        
        titulo_lbl = QLabel(nome)
        titulo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo_lbl.setStyleSheet("font-size: 24px; font-weight: 800; color: #1f2937;")
        
        msg_lbl = QLabel("Módulo em Desenvolvimento")
        msg_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg_lbl.setStyleSheet("font-size: 14px; color: #9ca3af;")
        
        layout.addWidget(icon_lbl)
        layout.addWidget(titulo_lbl)
        layout.addWidget(msg_lbl)
        
        return tela
    
    def _carregar_telas(self):
        """Carrega todas as telas no stack"""
        try:
            from ui.abas.home import home
            if hasattr(home, 'Home'):
                try:
                    dashboard = home.Home(parent=self, usuario=self.usuario_data)
                except TypeError:
                    try:
                        dashboard = home.Home(self, self.usuario_data)
                    except TypeError:
                        dashboard = home.Home(self.usuario_data)
            elif hasattr(home, 'home'):
                try:
                    dashboard = home.home(parent=self, usuario=self.usuario_data)
                except TypeError:
                    try:
                        dashboard = home.home(self, self.usuario_data)
                    except TypeError:
                        dashboard = home.home(self.usuario_data)
            elif callable(home):
                try:
                    dashboard = home(parent=self, usuario=self.usuario_data)
                except TypeError:
                    try:
                        dashboard = home(self, self.usuario_data)
                    except TypeError:
                        dashboard = home(self.usuario_data)
            else:
                dashboard = self._criar_tela_placeholder("Dashboard")
        except Exception as e:
            print(f"Erro ao carregar home: {e}")
            dashboard = self._criar_tela_placeholder("Dashboard")
        
        self.stack.addWidget(dashboard)
        self.telas["Dashboard"] = dashboard
        
        telas_config = [
            ("Consultar", "Consultar", "ConsultarUI"),
            ("Email", "Email", "BaixarEmailUI"),
            ("Analises", "Analises", "Analises"),
            ("AnaliseAP", "analiseap", "AnaliseAP"),
            ("Relatorios", "relatorios", "RelatoriosUI"),
            ("Carteira", "Carteira", "CarteiraDigitalUI"),
            ("Lancamentos", "lancamentos", "LancamentoUI"),
            ("Devolucao", "devolucao", "DevolucaoUI"),
            ("Memorando", "memorando", "MemorandoUI"),
            ("Anexar", "anexar", "AnexarUI"),
            ("Adicionar", "adicionar", "AdicionarUI"),
            ("Senha", "senha", "SenhaUI"),
        ]
        
        for nome_tela, modulo_nome, classe_nome in telas_config:
            tela = self._carregar_tela_real(modulo_nome, classe_nome, nome_tela)
            if tela is None:
                tela = self._criar_tela_placeholder(nome_tela)
            
            self.stack.addWidget(tela)
            self.telas[nome_tela] = tela
    
    def abrir_tela(self, nome):
        """Abre uma tela especifica"""
        if nome in self.telas:
            self.titulo_label.setText(nome)
            self.stack.setCurrentWidget(self.telas[nome])
            
            for n, btn in self.botoes.items():
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
            self, "Sair do Sistema",
            "Deseja realmente encerrar sua sessão?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    usuario = {
        "username": "João Silva",
        "nome": "João Silva",
        "perfil": "usuario",
        "email": "joao@agrofarm.com"
    }
    
    window = AppPrincipal(usuario)
    window.show()
    sys.exit(app.exec())