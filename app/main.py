# -*- coding: utf-8 -*-
"""
Main PyQt6 - Sistema Sector Automation
"""

import os
import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

# Configurar output para UTF-8 no Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configurar path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Importar módulos
from core.login import Login
from core.menu import AppPrincipal
from core.menu_administrador import MenuAdministrador
from services.database import test_connection, get_connection


class MainApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyle("Fusion")
        
        # Configurar fonte padrão
        from PyQt6.QtGui import QFont
        font = QFont("Segoe UI", 9)
        self.app.setFont(font)
        
        self.janela = None
        self.login = None
        
        # Configurar para High DPI displays
        self._setup_high_dpi()
        
        # Testar conexão com banco antes de iniciar
        if not self._testar_conexao_banco():
            QMessageBox.critical(
                None,
                "Erro de Conexao",
                "Nao foi possivel conectar ao banco de dados.\n\n"
                "Verifique as configuracoes de rede e tente novamente."
            )
            sys.exit(1)
        
        self.mostrar_login()
        sys.exit(self.app.exec())

    def _setup_high_dpi(self):
        """Configura para High DPI displays."""
        if hasattr(Qt, 'AA_EnableHighDpiScaling'):
            QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
            QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    def _testar_conexao_banco(self):
        """Testa a conexão com o banco de dados antes de iniciar."""
        try:
            success, result = test_connection()
            if success:
                print(f"[Main] OK - Conectado ao banco: {result['database']}")
                return True
            else:
                print(f"[Main] ERRO - Falha na conexao: {result}")
                return False
        except Exception as e:
            print(f"[Main] ERRO - Erro ao testar conexao: {e}")
            return False

    def mostrar_login(self):
        """Mostra a tela de login."""
        self.login = Login(on_success=self.login_sucesso)
        self.login.show()

    def login_sucesso(self, usuario):
        """Callback após login bem-sucedido."""
        if self.login:
            self.login.close()
            self.login = None
        
        perfil = usuario.get("perfil", "usuario").lower()
        usuario_nome = usuario.get("username", "Usuario")
        
        print(f"[Main] Login bem-sucedido: {usuario_nome} (Perfil: {perfil})")
        
        try:
            if perfil in ("administrador", "admin", "chefe"):
                self.janela = MenuAdministrador(
                    usuario=usuario,
                    on_logout=self.logout,
                    conectar_bd=get_connection
                )
            else:
                self.janela = AppPrincipal(
                    usuario=usuario,
                    on_logout=self.logout,
                    conectar_bd=get_connection
                )
            
            self.janela.show()
            self.janela.raise_()
            self.janela.activateWindow()
            
        except Exception as e:
            print(f"[Main] Erro ao criar janela principal: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                None,
                "Erro",
                f"Erro ao iniciar aplicacao:\n\n{str(e)}"
            )
            self.mostrar_login()

    def logout(self):
        """Callback para logout."""
        print("[Main] Usuario desconectado")
        if self.janela:
            self.janela.close()
            self.janela = None
            
        self.mostrar_login()


if __name__ == "__main__":
    MainApp()