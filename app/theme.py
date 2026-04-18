# -*- coding: utf-8 -*-
"""
AppTheme - Definições de cores e estilos do aplicativo para PyQt6
"""


class AppTheme:
    """Definições de cores e estilos do aplicativo"""
    
    # Cores de Background (tema claro)
    BG_APP = "#f5f7fc"          # Fundo principal (cinza azulado claro)
    BG_CARD = "#ffffff"         # Cards e containers (branco)
    BG_INPUT = "#ffffff"        # Inputs (branco)
    BG_SIDEBAR = "#0a0f0d"      # Sidebar (verde escuro)
    BG_HEADER = "#ffffff"       # Header (branco)
    BG_CARD_HOVER = "#f1f5f9"   # Hover em cards
    
    # Cores de Texto
    TXT_MAIN = "#1e2f3e"        # Texto principal (azul escuro)
    TXT_MUTED = "#5a6e8a"       # Texto secundário
    TXT_DARK = "#1e2f3e"        # Texto escuro
    TXT_LIGHT = "#ffffff"       # Texto claro
    
    # Cores de Botões
    BTN_PRIMARY = "#2c6e9e"     # Botão primário (azul corporativo)
    BTN_PRIMARY_HOVER = "#1e4a6e"
    BTN_SUCCESS = "#10b981"     # Botão de sucesso (verde)
    BTN_SUCCESS_HOVER = "#059669"
    BTN_DANGER = "#ef4444"      # Botão de perigo (vermelho)
    BTN_DANGER_HOVER = "#dc2626"
    BTN_WARNING = "#f59e0b"     # Botão de aviso (laranja)
    BTN_WARNING_HOVER = "#d97706"
    BTN_INFO = "#3b82f6"        # Botão de informação (azul)
    BTN_INFO_HOVER = "#2563eb"
    
    # Cores de Borda
    BORDER = "#e2e8f0"          # Borda padrão
    BORDER_COLOR = "#e2e8f0"    # Alias para compatibilidade
    BORDER_LIGHT = "#f1f5f9"    # Borda clara
    
    # Cores de Status
    STATUS_SUCCESS = "#10b981"  # Verde
    STATUS_ERROR = "#ef4444"    # Vermelho
    STATUS_WARNING = "#f59e0b"  # Laranja
    STATUS_INFO = "#3b82f6"     # Azul
    
    # Cores de Fundo para Status
    BG_SUCCESS = "#d1fae5"
    BG_ERROR = "#fee2e2"
    BG_WARNING = "#fef3c7"
    BG_INFO = "#dbeafe"
    
    # Cores da Sidebar
    SIDEBAR_BG = "#0a0f0d"
    SIDEBAR_BG_DARK = "#060a08"
    SIDEBAR_TEXT = "#9ab89e"
    SIDEBAR_TEXT_ACTIVE = "#00b96b"
    
    # Fontes
    FONT_FAMILY = "Segoe UI"
    FONT_TITLE = (FONT_FAMILY, 22, "bold")
    FONT_SUBTITLE = (FONT_FAMILY, 18, "bold")
    FONT_TEXT = (FONT_FAMILY, 12)
    FONT_SMALL = (FONT_FAMILY, 11)
    FONT_TINY = (FONT_FAMILY, 10)
    
    # Espaçamentos
    PADDING_SMALL = 8
    PADDING_MEDIUM = 16
    PADDING_LARGE = 24
    PADDING_XLARGE = 32
    
    # Border Radius
    RADIUS_SMALL = 8
    RADIUS_MEDIUM = 12
    RADIUS_LARGE = 16
    RADIUS_XLARGE = 20


def get_stylesheet():
    """Retorna um stylesheet CSS para PyQt6 baseado no tema"""
    return f"""
    /* Estilos globais */
    QWidget {{
        background-color: {AppTheme.BG_APP};
        color: {AppTheme.TXT_MAIN};
        font-family: '{AppTheme.FONT_FAMILY}';
        font-size: 12px;
    }}
    
    /* Cards */
    QFrame[frameShape="4"] {{  /* QFrame.StyledPanel */
        background-color: {AppTheme.BG_CARD};
        border: 1px solid {AppTheme.BORDER};
        border-radius: {AppTheme.RADIUS_LARGE}px;
    }}
    
    /* Botões primários */
    QPushButton[primary="true"] {{
        background-color: {AppTheme.BTN_PRIMARY};
        color: white;
        border: none;
        border-radius: {AppTheme.RADIUS_MEDIUM}px;
        padding: 8px 16px;
        font-weight: bold;
    }}
    QPushButton[primary="true"]:hover {{
        background-color: {AppTheme.BTN_PRIMARY_HOVER};
    }}
    
    /* Botões de sucesso */
    QPushButton[success="true"] {{
        background-color: {AppTheme.BTN_SUCCESS};
        color: white;
        border: none;
        border-radius: {AppTheme.RADIUS_MEDIUM}px;
        padding: 8px 16px;
        font-weight: bold;
    }}
    QPushButton[success="true"]:hover {{
        background-color: {AppTheme.BTN_SUCCESS_HOVER};
    }}
    
    /* Botões de perigo */
    QPushButton[danger="true"] {{
        background-color: {AppTheme.BTN_DANGER};
        color: white;
        border: none;
        border-radius: {AppTheme.RADIUS_MEDIUM}px;
        padding: 8px 16px;
        font-weight: bold;
    }}
    QPushButton[danger="true"]:hover {{
        background-color: {AppTheme.BTN_DANGER_HOVER};
    }}
    
    /* Campos de entrada */
    QLineEdit, QTextEdit, QComboBox {{
        background-color: {AppTheme.BG_INPUT};
        border: 1px solid {AppTheme.BORDER};
        border-radius: {AppTheme.RADIUS_MEDIUM}px;
        padding: 6px 10px;
        selection-background-color: {AppTheme.BTN_PRIMARY};
    }}
    
    QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
        border: 2px solid {AppTheme.BTN_PRIMARY};
    }}
    
    /* Tabelas */
    QTableWidget {{
        background-color: {AppTheme.BG_CARD};
        border: 1px solid {AppTheme.BORDER};
        border-radius: {AppTheme.RADIUS_MEDIUM}px;
        gridline-color: {AppTheme.BORDER};
    }}
    
    QTableWidget::item {{
        padding: 8px;
    }}
    
    QTableWidget::item:selected {{
        background-color: {AppTheme.BTN_PRIMARY};
        color: white;
    }}
    
    QHeaderView::section {{
        background-color: {AppTheme.BG_INPUT};
        padding: 8px;
        border: none;
        font-weight: bold;
    }}
    
    /* Abas (QTabWidget) */
    QTabWidget::pane {{
        background-color: {AppTheme.BG_CARD};
        border: 1px solid {AppTheme.BORDER};
        border-radius: {AppTheme.RADIUS_MEDIUM}px;
    }}
    
    QTabBar::tab {{
        background-color: {AppTheme.BG_INPUT};
        padding: 8px 20px;
        margin-right: 2px;
        border-top-left-radius: {AppTheme.RADIUS_SMALL}px;
        border-top-right-radius: {AppTheme.RADIUS_SMALL}px;
    }}
    
    QTabBar::tab:selected {{
        background-color: {AppTheme.BG_CARD};
        border-bottom: 2px solid {AppTheme.BTN_SUCCESS};
    }}
    
    QTabBar::tab:hover {{
        background-color: {AppTheme.BORDER};
    }}
    
    /* Scrollbars */
    QScrollBar:vertical {{
        background-color: {AppTheme.BG_INPUT};
        width: 10px;
        border-radius: 5px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {AppTheme.BORDER};
        border-radius: 5px;
        min-height: 20px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {AppTheme.BTN_PRIMARY};
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    
    /* Progress Bar */
    QProgressBar {{
        border: none;
        border-radius: {AppTheme.RADIUS_SMALL}px;
        background-color: {AppTheme.BORDER};
        text-align: center;
    }}
    
    QProgressBar::chunk {{
        background-color: {AppTheme.BTN_SUCCESS};
        border-radius: {AppTheme.RADIUS_SMALL}px;
    }}
    
    /* Labels */
    QLabel[heading="true"] {{
        font-size: 18px;
        font-weight: bold;
        color: {AppTheme.TXT_MAIN};
    }}
    
    QLabel[subheading="true"] {{
        font-size: 14px;
        color: {AppTheme.TXT_MUTED};
    }}
    
    QLabel[error="true"] {{
        color: {AppTheme.BTN_DANGER};
    }}
    
    QLabel[success="true"] {{
        color: {AppTheme.BTN_SUCCESS};
    }}
    """


def apply_theme(app):
    """Aplica o tema à aplicação PyQt6"""
    app.setStyleSheet(get_stylesheet())


# Funções auxiliares para criar estilos (compatibilidade)
def button_style(color_type="primary"):
    """Retorna um dicionário com estilos para botões"""
    styles = {
        "primary": {
            "bg": AppTheme.BTN_PRIMARY,
            "hover": AppTheme.BTN_PRIMARY_HOVER,
            "color": "white"
        },
        "success": {
            "bg": AppTheme.BTN_SUCCESS,
            "hover": AppTheme.BTN_SUCCESS_HOVER,
            "color": "white"
        },
        "danger": {
            "bg": AppTheme.BTN_DANGER,
            "hover": AppTheme.BTN_DANGER_HOVER,
            "color": "white"
        },
        "warning": {
            "bg": AppTheme.BTN_WARNING,
            "hover": AppTheme.BTN_WARNING_HOVER,
            "color": "white"
        },
        "info": {
            "bg": AppTheme.BTN_INFO,
            "hover": AppTheme.BTN_INFO_HOVER,
            "color": "white"
        }
    }
    
    return styles.get(color_type, styles["primary"])


def input_style():
    """Retorna um dicionário com estilos para campos de entrada"""
    return {
        "bg": AppTheme.BG_INPUT,
        "border": AppTheme.BORDER,
        "color": AppTheme.TXT_MAIN,
        "radius": AppTheme.RADIUS_MEDIUM
    }


def card_style():
    """Retorna um dicionário com estilos para cards"""
    return {
        "bg": AppTheme.BG_CARD,
        "border": AppTheme.BORDER,
        "radius": AppTheme.RADIUS_LARGE,
        "border_width": 1
    }


def get_css_button(style="primary"):
    """Retorna CSS para botão com o estilo especificado"""
    btn_style = button_style(style)
    return f"""
        QPushButton {{
            background-color: {btn_style['bg']};
            color: {btn_style['color']};
            border: none;
            border-radius: {AppTheme.RADIUS_MEDIUM}px;
            padding: 8px 16px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {btn_style['hover']};
        }}
        QPushButton:disabled {{
            background-color: {AppTheme.BORDER};
            color: {AppTheme.TXT_MUTED};
        }}
    """


def get_css_input():
    """Retorna CSS para campos de entrada"""
    return f"""
        QLineEdit, QTextEdit, QComboBox {{
            background-color: {AppTheme.BG_INPUT};
            border: 1px solid {AppTheme.BORDER};
            border-radius: {AppTheme.RADIUS_MEDIUM}px;
            padding: 6px 10px;
        }}
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
            border: 2px solid {AppTheme.BTN_PRIMARY};
        }}
    """


def get_css_card():
    """Retorna CSS para cards"""
    return f"""
        QFrame {{
            background-color: {AppTheme.BG_CARD};
            border: 1px solid {AppTheme.BORDER};
            border-radius: {AppTheme.RADIUS_LARGE}px;
        }}
    """