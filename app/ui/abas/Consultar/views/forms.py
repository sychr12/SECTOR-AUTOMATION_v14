# -*- coding: utf-8 -*-
"""
Formulários para operações de edição e diálogos
"""

import customtkinter as ctk
from tkinter import messagebox
from app.theme import AppTheme

class FormularioEdicao(ctk.CTkToplevel):
    """Formulário para edição de registros"""
    
    def __init__(self, parent, registro_atual, campos_editaveis=None, on_salvar=None):
        super().__init__(parent)
        
        self.registro_atual = registro_atual
        self.campos_editaveis = campos_editaveis or ['nome', 'cpf', 'municipio', 'memorando', 'tipo', 'motivo']
        self.on_salvar = on_salvar
        self.resultado = None
        
        self._configurar_janela()
        self._criar_widgets()
    
    def _configurar_janela(self):
        """Configura as propriedades da janela"""
        self.title("Editar Registro")
        self.geometry("520x620")
        self.resizable(False, False)
        self.grab_set()
        self.focus_set()
        # Centralizar APÓS build via after() para janela ter tamanho real
        self.after(0, self._centralizar)

    def _centralizar(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = self.winfo_screenwidth()  // 2 - w // 2
        y = self.winfo_screenheight() // 2 - h // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
    
    def _criar_widgets(self):
        """Cria os widgets do formulário"""
        # Container principal
        container = ctk.CTkFrame(self, fg_color=AppTheme.BG_APP)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        ctk.CTkLabel(
            container,
            text="📝 Editar Registro",
            font=("Segoe UI", 20, "bold"),
            text_color=AppTheme.TXT_MAIN
        ).pack(pady=(0, 20))
        
        # Frame do formulário
        form_frame = ctk.CTkFrame(container, fg_color=AppTheme.BG_CARD, corner_radius=12)
        form_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Campos do formulário
        campos = [
            ("ID", self.registro_atual[0], False),
            ("Nome", self.registro_atual[1], 'nome' in self.campos_editaveis),
            ("CPF", self.registro_atual[2], 'cpf' in self.campos_editaveis),
            ("Município", self.registro_atual[3], 'municipio' in self.campos_editaveis),
            ("Memorando", self.registro_atual[4], 'memorando' in self.campos_editaveis),
            ("Tipo", self.registro_atual[5], 'tipo' in self.campos_editaveis),
            ("Motivo", self.registro_atual[6], 'motivo' in self.campos_editaveis),
            ("Usuário", self.registro_atual[7], False),
            ("Data", self.registro_atual[8], False)
        ]
        
        self.entradas = {}
        row = 0
        
        for label_text, valor, editavel in campos:
            # Label
            ctk.CTkLabel(
                form_frame,
                text=label_text + ":",
                font=("Segoe UI", 12, "bold"),
                anchor="w"
            ).grid(row=row, column=0, sticky="w", padx=20, pady=(15, 5))
            
            # Campo de entrada
            if editavel:
                entrada = ctk.CTkEntry(
                    form_frame,
                    fg_color=AppTheme.BG_INPUT,
                    border_color=AppTheme.BTN_PRIMARY,
                    text_color=AppTheme.TXT_MAIN,
                    font=("Segoe UI", 12),
                    height=35
                )
                entrada.insert(0, str(valor))
                entrada.grid(row=row, column=1, sticky="ew", padx=(0, 20), pady=(15, 5))
                self.entradas[label_text.lower()] = entrada
            else:
                # Label apenas para leitura
                ctk.CTkLabel(
                    form_frame,
                    text=str(valor),
                    font=("Segoe UI", 12),
                    text_color=AppTheme.TXT_MUTED
                ).grid(row=row, column=1, sticky="w", padx=(0, 20), pady=(15, 5))
            
            row += 1
        
        # Configurar pesos das colunas
        form_frame.columnconfigure(1, weight=1)
        
        # Botões
        botoes_frame = ctk.CTkFrame(container, fg_color="transparent")
        botoes_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkButton(
            botoes_frame,
            text="Cancelar",
            width=120,
            height=40,
            fg_color=AppTheme.BG_INPUT,
            hover_color=AppTheme.TXT_MUTED,
            text_color=AppTheme.TXT_MAIN,
            font=("Segoe UI", 12),
            command=self._cancelar
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            botoes_frame,
            text="Salvar",
            width=120,
            height=40,
            fg_color=AppTheme.BTN_SUCCESS,
            hover_color=AppTheme.BTN_SUCCESS_HOVER,
            font=("Segoe UI", 12, "bold"),
            command=self._salvar
        ).pack(side="right")
    
    def _salvar(self):
        """Salva as alterações do formulário"""
        try:
            # Coletar valores alterados
            valores_alterados = {}
            
            for campo, entrada in self.entradas.items():
                valor_atual = self._obter_valor_original(campo)
                valor_novo = entrada.get().strip()
                
                if valor_novo != str(valor_atual):
                    valores_alterados[campo] = valor_novo
            
            if not valores_alterados:
                messagebox.showinfo("Informação", "Nenhuma alteração foi feita.")
                self.destroy()
                return
            
            # Chamar callback de salvamento
            if self.on_salvar:
                self.on_salvar(self.registro_atual[0], valores_alterados)
            
            self.resultado = valores_alterados
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
    
    def _obter_valor_original(self, campo):
        """Obtém o valor original do campo — chaves sem acento, lowercase."""
        mapeamento = {
            'id':        0,
            'nome':      1,
            'cpf':       2,
            'municipio': 3,   # sem acento — igual à chave do dict
            'memorando': 4,
            'tipo':      5,
            'motivo':    6,
        }
        idx = mapeamento.get(campo)
        if idx is not None and idx < len(self.registro_atual):
            return self.registro_atual[idx]
        return ""
    
    def _cancelar(self):
        """Cancela a edição"""
        self.destroy()
    
    def show(self):
        """Mostra o formulário e aguarda resultado"""
        self.wait_window()
        return self.resultado

class FormularioConfirmacao(ctk.CTkToplevel):
    """Formulário de confirmação personalizado"""
    
    def __init__(self, parent, titulo, mensagem, tipo="info"):
        super().__init__(parent)
        
        self.titulo = titulo
        self.mensagem = mensagem
        self.tipo = tipo
        self.resposta = False
        
        self._configurar_janela()
        self._criar_widgets()
    
    def _configurar_janela(self):
        """Configura as propriedades da janela"""
        self.title(self.titulo)
        self.geometry("400x220")
        self.resizable(False, False)
        self.grab_set()
        self.focus_set()
        self.after(0, lambda: (
            self.update_idletasks(),
            self.geometry(
                f"{self.winfo_width()}x{self.winfo_height()}"
                f"+{self.winfo_screenwidth()//2 - self.winfo_width()//2}"
                f"+{self.winfo_screenheight()//2 - self.winfo_height()//2}"
            )
        ))
    
    def _criar_widgets(self):
        """Cria os widgets do formulário"""
        container = ctk.CTkFrame(self, fg_color=AppTheme.BG_APP)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Ícone baseado no tipo
        icones = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'error': '❌',
            'success': '✅',
            'question': '❓'
        }
        
        icone = icones.get(self.tipo, 'ℹ️')
        
        # Ícone
        ctk.CTkLabel(
            container,
            text=icone,
            font=("Segoe UI", 40)
        ).pack(pady=(10, 0))
        
        # Mensagem
        ctk.CTkLabel(
            container,
            text=self.mensagem,
            font=("Segoe UI", 14),
            text_color=AppTheme.TXT_MAIN,
            wraplength=350,
            justify="center"
        ).pack(pady=20, fill="x")
        
        # Botões
        botoes_frame = ctk.CTkFrame(container, fg_color="transparent")
        botoes_frame.pack(fill="x", pady=(10, 0))
        
        if self.tipo == 'question':
            # Para perguntas, mostrar Sim e Não
            ctk.CTkButton(
                botoes_frame,
                text="Não",
                width=100,
                height=35,
                fg_color=AppTheme.BG_INPUT,
                hover_color=AppTheme.TXT_MUTED,
                text_color=AppTheme.TXT_MAIN,
                command=self._nao
            ).pack(side="left", padx=(0, 10))
            
            ctk.CTkButton(
                botoes_frame,
                text="Sim",
                width=100,
                height=35,
                fg_color=AppTheme.BTN_SUCCESS,
                hover_color=AppTheme.BTN_SUCCESS_HOVER,
                command=self._sim
            ).pack(side="right")
        else:
            # Para outros tipos, mostrar apenas OK
            ctk.CTkButton(
                botoes_frame,
                text="OK",
                width=100,
                height=35,
                fg_color=AppTheme.BTN_PRIMARY,
                hover_color=AppTheme.BTN_PRIMARY_HOVER,
                command=self._ok
            ).pack(side="right")
    
    def _sim(self):
        """Resposta Sim"""
        self.resposta = True
        self.destroy()
    
    def _nao(self):
        """Resposta Não"""
        self.resposta = False
        self.destroy()
    
    def _ok(self):
        """Botão OK"""
        self.resposta = True
        self.destroy()
    
    def show(self):
        """Mostra o formulário e retorna a resposta"""
        self.wait_window()
        return self.resposta

class FormularioFiltroAvancado(ctk.CTkToplevel):
    """Formulário para filtros avançados"""
    
    def __init__(self, parent, filtros_atuais=None, on_aplicar=None):
        super().__init__(parent)
        
        self.filtros_atuais = filtros_atuais or {}
        self.on_aplicar = on_aplicar
        self.resultado = None
        
        self._configurar_janela()
        self._criar_widgets()
    
    def _configurar_janela(self):
        """Configura as propriedades da janela"""
        self.title("Filtros Avançados")
        self.geometry("500x400")
        self.resizable(False, False)
        self.grab_set()
        self.focus_set()
        self.after(0, lambda: (
            self.update_idletasks(),
            self.geometry(
                f"{self.winfo_width()}x{self.winfo_height()}"
                f"+{self.winfo_screenwidth()//2 - self.winfo_width()//2}"
                f"+{self.winfo_screenheight()//2 - self.winfo_height()//2}"
            )
        ))
    
    def _criar_widgets(self):
        """Cria os widgets do formulário"""
        container = ctk.CTkFrame(self, fg_color=AppTheme.BG_APP)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        ctk.CTkLabel(
            container,
            text="🔍 Filtros Avançados",
            font=("Segoe UI", 18, "bold"),
            text_color=AppTheme.TXT_MAIN
        ).pack(pady=(0, 20))
        
        # Frame do formulário
        form_frame = ctk.CTkFrame(container, fg_color=AppTheme.BG_CARD, corner_radius=12)
        form_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Período personalizado
        ctk.CTkLabel(
            form_frame,
            text="Período Personalizado:",
            font=("Segoe UI", 12, "bold"),
            anchor="w"
        ).pack(anchor="w", padx=20, pady=(20, 5))
        
        periodo_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        periodo_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(periodo_frame, text="De:").pack(side="left")
        self.data_inicio = ctk.CTkEntry(periodo_frame, width=100)
        self.data_inicio.pack(side="left", padx=(5, 20))
        
        ctk.CTkLabel(periodo_frame, text="Até:").pack(side="left")
        self.data_fim = ctk.CTkEntry(periodo_frame, width=100)
        self.data_fim.pack(side="left", padx=(5, 0))
        
        # Tipos específicos
        ctk.CTkLabel(
            form_frame,
            text="Filtrar por Tipo:",
            font=("Segoe UI", 12, "bold"),
            anchor="w"
        ).pack(anchor="w", padx=20, pady=(10, 5))
        
        tipos_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        tipos_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        self.tipo_insc = ctk.CTkCheckBox(tipos_frame, text="INSC", fg_color=AppTheme.BTN_PRIMARY)
        self.tipo_insc.pack(side="left", padx=(0, 10))
        
        self.tipo_renov = ctk.CTkCheckBox(tipos_frame, text="RENOV", fg_color=AppTheme.BTN_PRIMARY)
        self.tipo_renov.pack(side="left", padx=(0, 10))
        
        # Urgência
        ctk.CTkLabel(
            form_frame,
            text="Filtrar por Urgência:",
            font=("Segoe UI", 12, "bold"),
            anchor="w"
        ).pack(anchor="w", padx=20, pady=(10, 5))
        
        urgencia_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        urgencia_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        self.urgencia_alta = ctk.CTkCheckBox(urgencia_frame, text="Alta", fg_color=AppTheme.BTN_PRIMARY)
        self.urgencia_alta.pack(side="left", padx=(0, 10))
        
        self.urgencia_media = ctk.CTkCheckBox(urgencia_frame, text="Média", fg_color=AppTheme.BTN_PRIMARY)
        self.urgencia_media.pack(side="left", padx=(0, 10))
        
        self.urgencia_baixa = ctk.CTkCheckBox(urgencia_frame, text="Baixa", fg_color=AppTheme.BTN_PRIMARY)
        self.urgencia_baixa.pack(side="left", padx=(0, 10))
        
        # Preencher com filtros atuais
        self._preencher_filtros()
        
        # Botões
        botoes_frame = ctk.CTkFrame(container, fg_color="transparent")
        botoes_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkButton(
            botoes_frame,
            text="Limpar",
            width=100,
            height=35,
            fg_color=AppTheme.BG_INPUT,
            hover_color=AppTheme.TXT_MUTED,
            text_color=AppTheme.TXT_MAIN,
            command=self._limpar
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            botoes_frame,
            text="Aplicar",
            width=100,
            height=35,
            fg_color=AppTheme.BTN_SUCCESS,
            hover_color=AppTheme.BTN_SUCCESS_HOVER,
            command=self._aplicar
        ).pack(side="right")
    
    def _preencher_filtros(self):
        """Preenche os campos com os filtros atuais"""
        if 'data_inicio' in self.filtros_atuais:
            self.data_inicio.insert(0, self.filtros_atuais['data_inicio'])
        
        if 'data_fim' in self.filtros_atuais:
            self.data_fim.insert(0, self.filtros_atuais['data_fim'])
        
        if 'tipos' in self.filtros_atuais:
            tipos = self.filtros_atuais['tipos']
            if 'INSC' in tipos:
                self.tipo_insc.select()
            if 'RENOV' in tipos:
                self.tipo_renov.select()
    
    def _limpar(self):
        """Limpa todos os filtros"""
        self.data_inicio.delete(0, 'end')
        self.data_fim.delete(0, 'end')
        self.tipo_insc.deselect()
        self.tipo_renov.deselect()
        self.urgencia_alta.deselect()
        self.urgencia_media.deselect()
        self.urgencia_baixa.deselect()
    
    def _aplicar(self):
        """Aplica os filtros"""
        filtros = {}
        
        # Coletar dados
        data_inicio = self.data_inicio.get().strip()
        data_fim = self.data_fim.get().strip()
        
        if data_inicio:
            filtros['data_inicio'] = data_inicio
        if data_fim:
            filtros['data_fim'] = data_fim
        
        # Tipos
        tipos = []
        if self.tipo_insc.get():
            tipos.append('INSC')
        if self.tipo_renov.get():
            tipos.append('RENOV')
        if tipos:
            filtros['tipos'] = tipos
        
        # Urgência
        urgencias = []
        if self.urgencia_alta.get():
            urgencias.append('Alta')
        if self.urgencia_media.get():
            urgencias.append('Média')
        if self.urgencia_baixa.get():
            urgencias.append('Baixa')
        if urgencias:
            filtros['urgencias'] = urgencias
        
        self.resultado = filtros
        
        if self.on_aplicar:
            self.on_aplicar(filtros)
        
        self.destroy()
    
    def show(self):
        """Mostra o formulário e retorna os filtros"""
        self.wait_window()
        return self.resultado