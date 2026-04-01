import customtkinter as ctk


class AppTheme:
    """Definições de cores e estilos do aplicativo"""
    
    # Cores de Background (tema claro: branco + verde suave)
    BG_APP = "#ffffff"          # Fundo principal (branco)
    BG_CARD = "#ffffff"         # Cards e containers (branco)
    BG_INPUT = "#f3f4f6"        # Inputs e hover states (cinza muito claro)
    BG_SIDEBAR = "#ffffff"      # Sidebar (branco)
    BG_HEADER = "#ffffff"       # Header (branco)
    
    # Cores de Texto
    TXT_MAIN = "#000000"        # Texto principal (preto)
    TXT_MUTED = "#000000"       # Texto secundário/desabilitado (usar preto conforme solicitado)
    TXT_DARK = "#000000"        # Texto escuro (para fundos claros)
    
    # Cores de Botões
    BTN_PRIMARY = "#22c55e"     # Botão primário (verde claro)
    BTN_PRIMARY_HOVER = "#16a34a"
    BTN_SUCCESS = "#22c55e"     # Botão de sucesso (verde suave)
    BTN_SUCCESS_HOVER = "#16a34a"
    BTN_DANGER = "#ef4444"      # Botão de perigo (vermelho)
    BTN_DANGER_HOVER = "#dc2626"
    BTN_WARNING = "#f59e0b"     # Botão de aviso (laranja)
    BTN_WARNING_HOVER = "#d97706"
    BTN_INFO = "#06b6d4"        # Botão de informação (cyan)
    BTN_INFO_HOVER = "#0891b2"
    
    # Cores de Borda
    BORDER = "#e5e7eb"          # Borda padrão (clara)
    BORDER_LIGHT = "#f0fdf4"    # Borda clara com leve tom verde
    
    # Cores de Status
    STATUS_SUCCESS = "#22c55e"  # Verde (suave)
    STATUS_ERROR = "#ef4444"    # Vermelho
    STATUS_WARNING = "#f59e0b"  # Laranja
    STATUS_INFO = "#3b82f6"     # Azul
    
    # Fontes
    FONT_FAMILY = "Segoe UI"
    FONT_TITLE = (FONT_FAMILY, 22, "bold")
    FONT_SUBTITLE = (FONT_FAMILY, 18, "bold")
    FONT_TEXT = (FONT_FAMILY, 13)
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


def apply_theme():
    """Aplica o tema claro ao CustomTkinter"""

    # Definir aparência e tema de cor (modo claro)
    ctk.set_appearance_mode("light")
    # Mantemos o modo claro e usamos as cores definidas abaixo
    try:
        ctk.set_default_color_theme("green")
    except Exception:
        # fallback se tema 'green' não existir no CustomTkinter
        ctk.set_default_color_theme("blue")
    
    # Configurações adicionais de tema
    ctk.ThemeManager.theme["CTk"]["fg_color"] = [AppTheme.BG_APP, AppTheme.BG_APP]
    
    # Configurações de botões
    ctk.ThemeManager.theme["CTkButton"]["fg_color"] = [AppTheme.BTN_PRIMARY, AppTheme.BTN_PRIMARY]
    ctk.ThemeManager.theme["CTkButton"]["hover_color"] = [AppTheme.BTN_PRIMARY_HOVER, AppTheme.BTN_PRIMARY_HOVER]
    ctk.ThemeManager.theme["CTkButton"]["text_color"] = [AppTheme.TXT_MAIN, AppTheme.TXT_MAIN]
    ctk.ThemeManager.theme["CTkButton"]["corner_radius"] = AppTheme.RADIUS_MEDIUM
    
    # Configurações de entrada de texto
    ctk.ThemeManager.theme["CTkEntry"]["fg_color"] = [AppTheme.BG_INPUT, AppTheme.BG_INPUT]
    ctk.ThemeManager.theme["CTkEntry"]["border_color"] = [AppTheme.BORDER, AppTheme.BORDER]
    ctk.ThemeManager.theme["CTkEntry"]["text_color"] = [AppTheme.TXT_MAIN, AppTheme.TXT_MAIN]
    
    # Configurações de frame
    ctk.ThemeManager.theme["CTkFrame"]["fg_color"] = [AppTheme.BG_CARD, AppTheme.BG_CARD]
    ctk.ThemeManager.theme["CTkFrame"]["border_color"] = [AppTheme.BORDER, AppTheme.BORDER]
    
    # Configurações de label
    ctk.ThemeManager.theme["CTkLabel"]["text_color"] = [AppTheme.TXT_MAIN, AppTheme.TXT_MAIN]
    ctk.ThemeManager.theme["CTkLabel"]["font"] = [AppTheme.FONT_TEXT, AppTheme.FONT_TEXT]

    # Ajustes gerais de bordas e cantos
    ctk.ThemeManager.theme["CTk"]["corner_radius"] = AppTheme.RADIUS_SMALL
    ctk.ThemeManager.theme["CTkEntry"]["corner_radius"] = AppTheme.RADIUS_MEDIUM
    ctk.ThemeManager.theme["CTkButton"]["corner_radius"] = AppTheme.RADIUS_MEDIUM

    # Forçar tamanho/rótulos padrão para melhor legibilidade
    ctk.ThemeManager.theme["CTkLabel"]["text_font"] = AppTheme.FONT_TEXT
    ctk.ThemeManager.theme["CTkButton"]["text_font"] = (AppTheme.FONT_FAMILY, 14, "bold")


# Função auxiliar para criar estilos de botão
def button_style(color_type="primary"):
    """Retorna um dicionário com estilos para botões"""
    styles = {
        "primary": {
            "fg_color": AppTheme.BTN_PRIMARY,
            "hover_color": AppTheme.BTN_PRIMARY_HOVER,
            "text_color": AppTheme.TXT_MAIN
        },
        "success": {
            "fg_color": AppTheme.BTN_SUCCESS,
            "hover_color": AppTheme.BTN_SUCCESS_HOVER,
            "text_color": AppTheme.TXT_MAIN
        },
        "danger": {
            "fg_color": AppTheme.BTN_DANGER,
            "hover_color": AppTheme.BTN_DANGER_HOVER,
            "text_color": AppTheme.TXT_MAIN
        },
        "warning": {
            "fg_color": AppTheme.BTN_WARNING,
            "hover_color": AppTheme.BTN_WARNING_HOVER,
            "text_color": AppTheme.TXT_MAIN
        },
        "info": {
            "fg_color": AppTheme.BTN_INFO,
            "hover_color": AppTheme.BTN_INFO_HOVER,
            "text_color": AppTheme.TXT_MAIN
        }
    }
    
    return styles.get(color_type, styles["primary"])


# Função auxiliar para criar estilos de entrada
def input_style():
    """Retorna um dicionário com estilos para campos de entrada"""
    return {
        "fg_color": AppTheme.BG_INPUT,
        "border_color": AppTheme.BORDER,
        "text_color": AppTheme.TXT_MAIN,
        "corner_radius": AppTheme.RADIUS_MEDIUM
    }


# Função auxiliar para criar estilos de card
def card_style():
    """Retorna um dicionário com estilos para cards"""
    return {
        "fg_color": AppTheme.BG_CARD,
        "border_color": AppTheme.BORDER,
        "corner_radius": AppTheme.RADIUS_LARGE,
        "border_width": 1
    }