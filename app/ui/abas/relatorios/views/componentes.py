# -*- coding: utf-8 -*-
"""
Componentes reutilizáveis para interface de relatórios
"""
# Componentes visuais específicos para a aba de relatórios SEFAZ.
import customtkinter as ctk
from app.theme import AppTheme

class ProgressoRelatorioFrame(ctk.CTkToplevel):
    """Janela de progresso para geração de relatórios"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.title("Gerando Relatórios")
        self.geometry("400x200")
        self.resizable(False, False)
        
        # Centralizar
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        self.grab_set()
        self.focus_set()
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Cria widgets da janela de progresso"""
        container = ctk.CTkFrame(self, fg_color=AppTheme.BG_APP)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Ícone
        ctk.CTkLabel(
            container,
            text="⏳",
            font=("Segoe UI", 40),
            text_color=AppTheme.BTN_PRIMARY
        ).pack(pady=(10, 0))
        
        # Título
        ctk.CTkLabel(
            container,
            text="Gerando Relatórios SEFAZ",
            font=("Segoe UI", 16, "bold"),
            text_color=AppTheme.TXT_MAIN
        ).pack(pady=(10, 5))
        
        # Mensagem de progresso
        self.lbl_progresso = ctk.CTkLabel(
            container,
            text="Iniciando...",
            font=("Segoe UI", 12),
            text_color=AppTheme.TXT_MUTED
        )
        self.lbl_progresso.pack(pady=(0, 15))
        
        # Barra de progresso
        self.progress_bar = ctk.CTkProgressBar(
            container,
            width=300,
            height=6,
            fg_color=AppTheme.BG_INPUT,
            progress_color=AppTheme.BTN_SUCCESS
        )
        self.progress_bar.pack(pady=(0, 20))
        self.progress_bar.set(0)
        
        # Label de detalhes
        self.lbl_detalhes = ctk.CTkLabel(
            container,
            text="",
            font=("Segoe UI", 11),
            text_color=AppTheme.TXT_MUTED,
            wraplength=350
        )
        self.lbl_detalhes.pack()
    
    def atualizar_progresso(self, atual: int, total: int, municipio_atual: str = ""):
        """Atualiza progresso da geração"""
        if total > 0:
            progresso = atual / total
            self.progress_bar.set(progresso)
        
        self.lbl_progresso.configure(
            text=f"Processando: {atual}/{total} municípios"
        )
        
        if municipio_atual:
            self.lbl_detalhes.configure(
                text=f"Município atual: {municipio_atual}"
            )
    
    def mostrar_conclusao(self, sucesso: bool, mensagem: str):
        """Mostra mensagem de conclusão"""
        if sucesso:
            self.progress_bar.configure(progress_color=AppTheme.BTN_SUCCESS)
            self.lbl_progresso.configure(
                text="✅ Concluído!",
                text_color=AppTheme.STATUS_SUCCESS
            )
        else:
            self.progress_bar.configure(progress_color=AppTheme.STATUS_ERROR)
            self.lbl_progresso.configure(
                text="❌ Erro!",
                text_color=AppTheme.STATUS_ERROR
            )
        
        self.lbl_detalhes.configure(
            text=mensagem,
            text_color=AppTheme.STATUS_SUCCESS if sucesso else AppTheme.STATUS_ERROR
        )
        
        # Fechar automaticamente após 5 segundos se sucesso
        if sucesso:
            self.after(5000, self.destroy)

class ResumoRelatorioFrame(ctk.CTkFrame):
    """Frame para exibir resumo dos relatórios gerados"""
    
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=AppTheme.BG_CARD, corner_radius=12)
        self.controller = controller
        
        self._create_widgets()
        self.update_resumo()
    
    def _create_widgets(self):
        """Cria widgets do resumo"""
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        ctk.CTkLabel(
            content,
            text="📈 Resumo da Última Execução",
            font=("Segoe UI", 14, "bold"),
            text_color=AppTheme.TXT_MAIN
        ).pack(anchor="w", pady=(0, 15))
        
        # Grid para métricas
        self.metrics_frame = ctk.CTkFrame(content, fg_color="transparent")
        self.metrics_frame.pack(fill="x")
        
        # Colunas
        self.metric_col1 = ctk.CTkFrame(self.metrics_frame, fg_color="transparent")
        self.metric_col1.pack(side="left", fill="x", expand=True)
        
        self.metric_col2 = ctk.CTkFrame(self.metrics_frame, fg_color="transparent")
        self.metric_col2.pack(side="left", fill="x", expand=True, padx=(20, 0))
        
        # Labels das métricas (serão atualizadas)
        self.lbl_arquivos = self._create_metric_label(
            self.metric_col1, "📄 Arquivos Gerados:", "0"
        )
        
        self.lbl_registros = self._create_metric_label(
            self.metric_col1, "👥 Total de Registros:", "0"
        )
        
        self.lbl_municipios = self._create_metric_label(
            self.metric_col2, "📍 Municípios Processados:", "0"
        )
        
        self.lbl_ultima_exec = self._create_metric_label(
            self.metric_col2, "🕒 Última Execução:", "Nunca"
        )
    
    def _create_metric_label(self, parent, label_text: str, value_text: str):
        """Cria label de métrica"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            frame,
            text=label_text,
            font=("Segoe UI", 11),
            text_color=AppTheme.TXT_MUTED,
            anchor="w"
        ).pack(side="left")
        
        value_label = ctk.CTkLabel(
            frame,
            text=value_text,
            font=("Segoe UI", 11, "bold"),
            text_color=AppTheme.TXT_MAIN,
            anchor="w"
        )
        value_label.pack(side="right")
        
        return value_label
    
    def update_resumo(self):
        """Atualiza o resumo com dados do controller"""
        resumo = self.controller.obter_resumo()
        
        self.lbl_arquivos.configure(text=str(resumo["total_arquivos"]))
        self.lbl_registros.configure(text=str(resumo["total_registros"]))
        self.lbl_municipios.configure(text=str(resumo["municipios_processados"]))
        self.lbl_ultima_exec.configure(text=resumo["ultima_execucao"])