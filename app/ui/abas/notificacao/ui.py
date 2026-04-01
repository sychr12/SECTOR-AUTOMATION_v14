# -*- coding: utf-8 -*-
"""
Interface principal para configuração de email
"""

import customtkinter as ctk
from tkinter import messagebox
from app.theme import AppTheme
from .controller import EmailController
from .views import EmailConfigView

class EmailConfigUI(ctk.CTkToplevel):
    """Interface principal para configuração de email"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        self.parent = parent
        self.controller = EmailController()
        # Ignorar quaisquer argumentos extras (como conectar_bd) passados via kwargs
        
        self._create_interface()
        self._setup_events()
    
    def _create_interface(self):
        """Cria a interface principal"""
        self.title("Configuração de Email")
        self.geometry("600x700")
        self.resizable(False, False)
        
        # Centralizar
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # Criar view de configuração
        self.config_view = EmailConfigView(self, self.controller)
        self.config_view.pack(fill="both", expand=True)
        
        # Configurar callbacks dos botões
        self.config_view.btn_salvar.configure(command=self._salvar_configuracoes)
        self.config_view.btn_testar.configure(command=self._testar_conexao)
        
        self.grab_set()
        self.focus_set()
        self.bind('<Escape>', lambda e: self.destroy())
    
    def _setup_events(self):
        """Configura eventos da interface"""
        # Enter para salvar
        self.config_view.entry_smtp_server.bind('<Return>', lambda e: self._salvar_configuracoes())
        self.config_view.entry_smtp_port.bind('<Return>', lambda e: self._salvar_configuracoes())
        self.config_view.entry_email_remetente.bind('<Return>', lambda e: self._salvar_configuracoes())
    
    def _salvar_configuracoes(self):
        """Salva as configurações de email"""
        dados = self.config_view.get_form_data()
        
        sucesso, mensagem = self.controller.salvar_configuracao(
            servidor=dados['servidor'],
            porta=dados['porta'],
            email=dados['email'],
            senha=dados['senha'],
            assunto=dados['assunto'],
            habilitado=dados['habilitado'],
            template=dados['template']
        )
        
        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
        else:
            messagebox.showerror("Erro", mensagem)
    
    def _testar_conexao(self):
        """Testa a conexão com o servidor SMTP"""
        # Primeiro salvar configurações
        dados = self.config_view.get_form_data()
        
        sucesso, mensagem = self.controller.salvar_configuracao(
            servidor=dados['servidor'],
            porta=dados['porta'],
            email=dados['email'],
            senha=dados['senha'],
            assunto=dados['assunto'],
            habilitado=dados['habilitado'],
            template=dados['template']
        )
        
        if not sucesso:
            messagebox.showwarning("Aviso", f"Não foi possível salvar configuração antes do teste:\n{mensagem}")
            return
        
        # Testar conexão
        self.config_view.btn_testar.configure(state="disabled", text="Testando...")
        self.update()
        
        sucesso, mensagem = self.controller.testar_conexao()
        
        self.config_view.btn_testar.configure(state="normal", text="📤 Testar Conexão")
        
        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
        else:
            messagebox.showerror("Erro", mensagem)

# Funções auxiliares para uso em outros módulos
def abrir_configuracao_email(parent, **kwargs):
    """Abre janela de configuração de email"""
    try:
        janela = EmailConfigUI(parent, **kwargs)
        return janela
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao abrir configuração de email:\n{str(e)}")
        return None

def enviar_email_novo_usuario(usuario_info):
    """Envia email para novo usuário (para uso no GerenciarUsuariosUI)"""
    controller = EmailController()
    return controller.enviar_email_novo_usuario(usuario_info)

def obter_servico_email():
    """Retorna o serviço de email configurado"""
    controller = EmailController()
    return controller.obter_configuracao()

# Teste do módulo
if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Teste Configuração Email")
    app.geometry("400x200")
    
    def abrir_config():
        abrir_configuracao_email(app)
    
    btn = ctk.CTkButton(app, text="Abrir Configuração", command=abrir_config)
    btn.pack(pady=50)
    
    app.mainloop()