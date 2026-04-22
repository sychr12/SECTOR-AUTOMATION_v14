# -*- coding: utf-8 -*-
"""
Tela Home com Dashboard do Sistema - Versão PyQt6
"""

import sys
import os
from datetime import datetime, timedelta
from typing import List, Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QScrollArea, QPushButton,
    QMessageBox, QApplication
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QColor, QPalette


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


# ── Estilos CSS para PyQt6 ──────────────────────────────────────────────────────
STYLES = {
    "card": f"""
        QFrame {{
            background: {_BRANCO};
            border-radius: 12px;
            border: 1px solid {_CINZA_BORDER};
        }}
    """,
    "card_hover": f"""
        QFrame {{
            background: {_CINZA_BG};
            border-radius: 12px;
            border: 1px solid {_ACCENT};
        }}
    """,
    "stat_value": f"""
        font-size: 32px;
        font-weight: bold;
    """,
    "stat_title": f"""
        font-size: 12px;
        color: {_MUTED};
    """,
    "user_item": f"""
        QFrame {{
            border-radius: 8px;
        }}
        QFrame:hover {{
            background: {_CINZA_BG};
        }}
    """,
    "activity_item": f"""
        QFrame {{
            border-radius: 8px;
        }}
        QFrame:hover {{
            background: {_CINZA_BG};
        }}
    """,
}


# ── Classe para buscar dados em thread separada ────────────────────────────────
class DashboardWorker(QThread):
    """Worker para buscar dados do dashboard em background"""
    
    dados_carregados = pyqtSignal(object, object, object)  # stats, usuarios, atividades
    erro = pyqtSignal(str)
    
    def __init__(self, conectar_bd):
        super().__init__()
        self.conectar_bd = conectar_bd
    
    def run(self):
        try:
            from .services import DashboardService
            service = DashboardService()
            
            stats = service.obter_estatisticas(self.conectar_bd)
            usuarios = service.obter_usuarios_ativos(self.conectar_bd)
            atividades = service.obter_atividades_recentes(self.conectar_bd, limit=15)
            
            self.dados_carregados.emit(stats, usuarios, atividades)
        except Exception as e:
            self.erro.emit(str(e))


# ── Card de Estatística ─────────────────────────────────────────────────────────
class StatCard(QFrame):
    def __init__(self, titulo, cor, icone):
        super().__init__()
        self.setStyleSheet(STYLES["card"])
        self.setFixedHeight(120)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        
        # Esquerda - Informação
        left = QVBoxLayout()
        left.setSpacing(6)
        
        self.lbl_titulo = QLabel(titulo)
        self.lbl_titulo.setStyleSheet(f"font-size: 12px; color: {_MUTED};")
        
        self.lbl_valor = QLabel("0")
        self.lbl_valor.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {cor};")
        
        left.addWidget(self.lbl_titulo)
        left.addWidget(self.lbl_valor)
        
        # Direita - Ícone
        right = QVBoxLayout()
        right.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_icone = QLabel(icone)
        lbl_icone.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_icone.setStyleSheet(f"""
            font-size: 32px;
            background: {cor}15;
            border-radius: 16px;
            padding: 12px;
            min-width: 56px;
            min-height: 56px;
        """)
        
        right.addWidget(lbl_icone)
        
        layout.addLayout(left, 1)
        layout.addLayout(right)
    
    def set_valor(self, valor):
        self.lbl_valor.setText(str(valor))


# ── Mini Card ──────────────────────────────────────────────────────────────────
class MiniCard(QFrame):
    def __init__(self, titulo, cor, icone):
        super().__init__()
        self.setStyleSheet(STYLES["card"])
        self.setFixedHeight(80)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        
        # Ícone
        lbl_icone = QLabel(icone)
        lbl_icone.setStyleSheet(f"""
            font-size: 24px;
            background: {cor}15;
            border-radius: 12px;
            padding: 8px;
            min-width: 40px;
            min-height: 40px;
        """)
        lbl_icone.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Informação
        info = QVBoxLayout()
        info.setSpacing(2)
        
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet(f"font-size: 11px; color: {_MUTED};")
        
        self.lbl_valor = QLabel("0")
        self.lbl_valor.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {cor};")
        
        info.addWidget(lbl_titulo)
        info.addWidget(self.lbl_valor)
        
        layout.addWidget(lbl_icone)
        layout.addLayout(info, 1)
    
    def set_valor(self, valor):
        self.lbl_valor.setText(str(valor))


# ── Item de Usuário Ativo ──────────────────────────────────────────────────────
class UsuarioItem(QFrame):
    def __init__(self, usuario):
        super().__init__()
        self.setStyleSheet(STYLES["user_item"])
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        
        # Status online
        status = QLabel("🟢")
        status.setStyleSheet(f"font-size: 12px; color: {_VERDE_STATUS};")
        
        # Informações
        info = QVBoxLayout()
        info.setSpacing(2)
        
        nome = QLabel(usuario.nome)
        nome.setStyleSheet("font-size: 13px; font-weight: bold; color: #1e2f3e;")
        
        detalhe = QLabel(f"@{usuario.username} · {usuario.perfil}")
        detalhe.setStyleSheet(f"font-size: 11px; color: {_MUTED};")
        
        info.addWidget(nome)
        info.addWidget(detalhe)
        
        # Tempo online
        tempo = QLabel(usuario.tempo_online)
        tempo.setStyleSheet(f"font-size: 11px; color: {_VERDE_STATUS if 'minuto' in usuario.tempo_online else _MUTED};")
        tempo.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        layout.addWidget(status)
        layout.addLayout(info, 1)
        layout.addWidget(tempo)


# ── Item de Atividade Recente ──────────────────────────────────────────────────
class AtividadeItem(QFrame):
    def __init__(self, atividade):
        super().__init__()
        self.setStyleSheet(STYLES["activity_item"])
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        
        # Definir ícone e cor baseado no tipo
        tipo = atividade.tipo.upper() if hasattr(atividade, 'tipo') else ""
        
        if "LOGIN" in tipo:
            icone, cor = "🔐", _VERDE_STATUS
        elif "RELATORIO" in tipo:
            icone, cor = "📊", _AZUL
        elif "INSCRICAO" in tipo:
            icone, cor = "📝", _AMARELO
        elif "DEVOLUCAO" in tipo:
            icone, cor = "📤", _VERMELHO
        elif "CADASTRO" in tipo:
            icone, cor = "✓", _VERDE_STATUS
        else:
            icone, cor = "📋", _MUTED
        
        lbl_icone = QLabel(icone)
        lbl_icone.setStyleSheet(f"font-size: 18px; color: {cor};")
        
        # Informações
        info = QVBoxLayout()
        info.setSpacing(2)
        
        descricao = atividade.descricao
        if len(descricao) > 50:
            descricao = descricao[:50] + "..."
        
        lbl_desc = QLabel(descricao)
        lbl_desc.setStyleSheet("font-size: 12px; color: #1e2f3e;")
        
        usuario = getattr(atividade, 'usuario', 'Sistema')
        data = atividade.data_hora_formatada() if hasattr(atividade, 'data_hora_formatada') else ""
        
        lbl_detalhe = QLabel(f"👤 {usuario} · {data}")
        lbl_detalhe.setStyleSheet(f"font-size: 10px; color: {_MUTED};")
        
        info.addWidget(lbl_desc)
        info.addWidget(lbl_detalhe)
        
        layout.addWidget(lbl_icone)
        layout.addLayout(info, 1)


# ── Tela Home Principal (PyQt6) ────────────────────────────────────────────────
class HomeUI(QWidget):
    """Tela Home com Dashboard - Versão PyQt6"""
    
    def __init__(self, usuario, conectar_bd):
        super().__init__()
        self.usuario = usuario
        self.conectar_bd = conectar_bd
        
        self.stats = None
        self.usuarios_ativos = []
        self.atividades = []
        
        self._setup_ui()
        self._init_clock()
        self._carregar_dados()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(20)
        
        # Header
        container_layout.addWidget(self._criar_header())
        
        # Cards de estatísticas
        container_layout.addWidget(self._criar_cards_stats())
        
        # Grid de mini cards
        container_layout.addWidget(self._criar_mini_cards())
        
        # Conteúdo principal (usuários + atividades)
        content = QHBoxLayout()
        content.setSpacing(16)
        content.addWidget(self._criar_painel_usuarios(), 1)
        content.addWidget(self._criar_painel_atividades(), 1)
        container_layout.addLayout(content)
        
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        # Loading overlay
        self.loading = QFrame(self)
        self.loading.setStyleSheet(f"background: rgba(248,250,252,0.9); border-radius: 16px;")
        self.loading.hide()
        
        loading_layout = QVBoxLayout(self.loading)
        loading_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_loading = QLabel("⏳")
        lbl_loading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_loading.setStyleSheet("font-size: 48px;")
        
        lbl_texto = QLabel("Carregando dashboard...")
        lbl_texto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_texto.setStyleSheet("font-size: 14px; color: #5a6e8a;")
        
        loading_layout.addWidget(lbl_loading)
        loading_layout.addWidget(lbl_texto)
    
    def _criar_header(self):
        header = QFrame()
        header.setStyleSheet("background: transparent;")
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        
        left = QFrame()
        left.setStyleSheet("background: transparent;")
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        titulo = QLabel("Dashboard")
        titulo.setStyleSheet("font-size: 28px; font-weight: bold; color: #1e2f3e;")
        
        nome_usuario = self.usuario.get("nome", self.usuario.get("username", "Usuário")) if isinstance(self.usuario, dict) else self.usuario
        saudacao = QLabel(f"Bem-vindo, {nome_usuario}!")
        saudacao.setStyleSheet(f"font-size: 13px; color: {_MUTED};")
        
        left_layout.addWidget(titulo)
        left_layout.addWidget(saudacao)
        
        right = QFrame()
        right.setStyleSheet("background: transparent;")
        right_layout = QVBoxLayout(right)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.lbl_data = QLabel()
        self.lbl_data.setStyleSheet(f"font-size: 13px; color: {_MUTED};")
        
        btn_atualizar = QPushButton("🔄 Atualizar")
        btn_atualizar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_atualizar.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {_MUTED};
                padding: 6px 12px;
                border-radius: 8px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: {_CINZA_BORDER};
            }}
        """)
        btn_atualizar.clicked.connect(self._carregar_dados)
        
        right_layout.addWidget(self.lbl_data)
        right_layout.addWidget(btn_atualizar)
        
        layout.addWidget(left)
        layout.addStretch()
        layout.addWidget(right)
        
        return header
    
    def _criar_cards_stats(self):
        cards_frame = QFrame()
        cards_frame.setStyleSheet("background: transparent;")
        
        layout = QHBoxLayout(cards_frame)
        layout.setSpacing(16)
        
        self.card_online = StatCard("Usuários Online", _VERDE_STATUS, "🟢")
        self.card_offline = StatCard("Usuários Offline", _MUTED, "⚫")
        self.card_relatorios_hoje = StatCard("Relatórios Hoje", _AZUL, "📊")
        self.card_relatorios_total = StatCard("Total Relatórios", _AMARELO, "📈")
        
        layout.addWidget(self.card_online)
        layout.addWidget(self.card_offline)
        layout.addWidget(self.card_relatorios_hoje)
        layout.addWidget(self.card_relatorios_total)
        
        return cards_frame
    
    def _criar_mini_cards(self):
        mini_frame = QFrame()
        mini_frame.setStyleSheet("background: transparent;")
        
        layout = QHBoxLayout(mini_frame)
        layout.setSpacing(16)
        
        self.mini_inscricoes = MiniCard("Inscrições", _AZUL, "📝")
        self.mini_devolucoes = MiniCard("Devoluções", _VERMELHO, "📤")
        self.mini_relatorios_mes = MiniCard("Relatórios/Mês", _VERDE_STATUS, "📅")
        
        self.lbl_ultimo_acesso = QLabel("Último acesso: --")
        self.lbl_ultimo_acesso.setStyleSheet(f"""
            background: {_BRANCO};
            border-radius: 12px;
            border: 1px solid {_CINZA_BORDER};
            padding: 16px;
            font-size: 13px;
            color: {_MUTED};
        """)
        
        layout.addWidget(self.mini_inscricoes)
        layout.addWidget(self.mini_devolucoes)
        layout.addWidget(self.mini_relatorios_mes)
        layout.addWidget(self.lbl_ultimo_acesso)
        
        return mini_frame
    
    def _criar_painel_usuarios(self):
        painel = QFrame()
        painel.setStyleSheet(STYLES["card"])
        
        layout = QVBoxLayout(painel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Cabeçalho
        header = QFrame()
        header.setStyleSheet("background: transparent;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 16, 20, 12)
        
        titulo = QLabel("👥 Usuários Ativos")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #1e2f3e;")
        
        self.lbl_online_count = QLabel("0 online")
        self.lbl_online_count.setStyleSheet(f"font-size: 11px; color: {_VERDE_STATUS};")
        
        header_layout.addWidget(titulo)
        header_layout.addStretch()
        header_layout.addWidget(self.lbl_online_count)
        
        # Separador
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background: {_CINZA_BORDER}; height: 1px;")
        
        # Lista de usuários
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        self.container_usuarios = QWidget()
        self.container_usuarios.setStyleSheet("background: transparent;")
        self.usuarios_layout = QVBoxLayout(self.container_usuarios)
        self.usuarios_layout.setContentsMargins(12, 8, 12, 8)
        self.usuarios_layout.setSpacing(4)
        self.usuarios_layout.addStretch()
        
        scroll.setWidget(self.container_usuarios)
        
        layout.addWidget(header)
        layout.addWidget(sep)
        layout.addWidget(scroll)
        
        return painel
    
    def _criar_painel_atividades(self):
        painel = QFrame()
        painel.setStyleSheet(STYLES["card"])
        
        layout = QVBoxLayout(painel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Cabeçalho
        header = QFrame()
        header.setStyleSheet("background: transparent;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 16, 20, 12)
        
        titulo = QLabel("📋 Atividades Recentes")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #1e2f3e;")
        
        self.lbl_atividades_count = QLabel("0 atividades")
        self.lbl_atividades_count.setStyleSheet(f"font-size: 11px; color: {_MUTED};")
        
        header_layout.addWidget(titulo)
        header_layout.addStretch()
        header_layout.addWidget(self.lbl_atividades_count)
        
        # Separador
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background: {_CINZA_BORDER}; height: 1px;")
        
        # Lista de atividades
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        self.container_atividades = QWidget()
        self.container_atividades.setStyleSheet("background: transparent;")
        self.atividades_layout = QVBoxLayout(self.container_atividades)
        self.atividades_layout.setContentsMargins(12, 8, 12, 8)
        self.atividades_layout.setSpacing(4)
        self.atividades_layout.addStretch()
        
        scroll.setWidget(self.container_atividades)
        
        layout.addWidget(header)
        layout.addWidget(sep)
        layout.addWidget(scroll)
        
        return painel
    
    def _init_clock(self):
        self._atualizar_relogio()
        timer = QTimer(self)
        timer.timeout.connect(self._atualizar_relogio)
        timer.start(1000)
    
    def _atualizar_relogio(self):
        self.lbl_data.setText(datetime.now().strftime("%d/%m/%Y - %H:%M:%S"))
    
    def _mostrar_loading(self):
        self.loading.setGeometry(self.rect())
        self.loading.raise_()
        self.loading.show()
    
    def _esconder_loading(self):
        self.loading.hide()
    
    def _carregar_dados(self):
        self._mostrar_loading()
        
        self.worker = DashboardWorker(self.conectar_bd)
        self.worker.dados_carregados.connect(self._aplicar_dados)
        self.worker.erro.connect(self._erro_carregar)
        self.worker.start()
    
    def _aplicar_dados(self, stats, usuarios, atividades):
        self.stats = stats
        self.usuarios_ativos = usuarios
        self.atividades = atividades
        
        # Atualizar cards
        self.card_online.set_valor(stats.usuarios_online)
        self.card_offline.set_valor(stats.usuarios_offline)
        self.card_relatorios_hoje.set_valor(stats.relatorios_gerados_hoje)
        self.card_relatorios_total.set_valor(stats.relatorios_gerados_total)
        
        # Atualizar mini cards
        self.mini_inscricoes.set_valor(stats.total_inscricoes)
        self.mini_devolucoes.set_valor(stats.total_devolucoes)
        self.mini_relatorios_mes.set_valor(stats.relatorios_gerados_mes)
        self.lbl_ultimo_acesso.setText(f"Último acesso: {stats.ultimo_acesso}")
        
        # Atualizar contadores
        self.lbl_online_count.setText(f"{stats.usuarios_online} online")
        self.lbl_atividades_count.setText(f"{len(atividades)} atividades")
        
        # Atualizar listas
        self._atualizar_usuarios()
        self._atualizar_atividades()
        
        self._esconder_loading()
    
    def _erro_carregar(self, erro):
        self._esconder_loading()
        QMessageBox.warning(self, "Erro", f"Erro ao carregar dados:\n{erro}")
    
    def _atualizar_usuarios(self):
        # Limpar lista
        while self.usuarios_layout.count() > 1:
            item = self.usuarios_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not self.usuarios_ativos:
            msg = QLabel("😴 Nenhum usuário ativo no momento")
            msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            msg.setStyleSheet(f"font-size: 13px; color: {_MUTED}; padding: 20px;")
            self.usuarios_layout.insertWidget(0, msg)
        else:
            for usuario in self.usuarios_ativos[:10]:
                item = UsuarioItem(usuario)
                self.usuarios_layout.insertWidget(self.usuarios_layout.count() - 1, item)
    
    def _atualizar_atividades(self):
        # Limpar lista
        while self.atividades_layout.count() > 1:
            item = self.atividades_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not self.atividades:
            msg = QLabel("📭 Nenhuma atividade recente")
            msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            msg.setStyleSheet(f"font-size: 13px; color: {_MUTED}; padding: 20px;")
            self.atividades_layout.insertWidget(0, msg)
        else:
            for atividade in self.atividades[:15]:
                item = AtividadeItem(atividade)
                self.atividades_layout.insertWidget(self.atividades_layout.count() - 1, item)


# ── Teste direto ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    def mock_conectar_bd():
        return None
    
    usuario = {"username": "admin", "nome": "Administrador", "perfil": "admin"}
    
    window = HomeUI(usuario, mock_conectar_bd)
    window.setWindowTitle("Dashboard - AgroFarm")
    window.resize(1200, 700)
    window.show()
    
    sys.exit(app.exec())