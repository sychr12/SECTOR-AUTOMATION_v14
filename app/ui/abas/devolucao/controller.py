# -*- coding: utf-8 -*-
"""
Controller para operações de devolução de documentos
"""

class DevolucaoController:
    """Controller para operações de devolução"""
    
    def __init__(self, usuario, pdf_service, email_service):
        self.usuario = usuario
        self.pdf_service = pdf_service
        self.email_service = email_service
    
    def validar_conteudo(self, conteudo):
        """Valida o conteúdo da devolução"""
        if not conteudo or not conteudo.strip():
            return False, "Nenhum conteúdo informado."
        
        # Validações adicionais podem ser adicionadas aqui
        if len(conteudo.strip()) < 10:
            return False, "O conteúdo deve ter pelo menos 10 caracteres."
        
        return True, "Conteúdo válido."
    
    def gerar_pdf_devolucao(self, conteudo):
        """Gera PDF de devolução"""
        try:
            # Validar conteúdo
            valido, mensagem = self.validar_conteudo(conteudo)
            if not valido:
                return False, mensagem
            
            # Gerar PDF
            caminho = self.pdf_service.gerar_pdf_lancamento(conteudo)
            
            if not caminho:
                return False, "Falha ao gerar o PDF."
            
            return True, caminho
            
        except Exception as e:
            return False, f"Erro ao gerar PDF: {str(e)}"
    
    def enviar_email_devolucao(self, conteudo, destinatarios):
        """Envia email de devolução"""
        try:
            # Validar conteúdo
            valido, mensagem = self.validar_conteudo(conteudo)
            if not valido:
                return False, mensagem
            
            # Validar destinatários
            if not destinatarios:
                return False, "Nenhum destinatário configurado."
            
            # Enviar email
            self.email_service.enviar_email(
                assunto="Devolução",
                corpo=conteudo,
                destinatarios=destinatarios
            )
            
            return True, "Email enviado com sucesso."
            
        except Exception as e:
            return False, f"Erro ao enviar email: {str(e)}"
    
    def gerar_e_enviar_tudo(self, conteudo, destinatarios):
        """Gera PDF e envia email em uma operação"""
        try:
            # Validar conteúdo
            valido, mensagem = self.validar_conteudo(conteudo)
            if not valido:
                return False, mensagem
            
            # Gerar PDF
            sucesso_pdf, resultado_pdf = self.gerar_pdf_devolucao(conteudo)
            if not sucesso_pdf:
                return False, resultado_pdf
            
            # Enviar email
            sucesso_email, resultado_email = self.enviar_email_devolucao(conteudo, destinatarios)
            if not sucesso_email:
                return False, resultado_email
            
            return True, f"PDF gerado: {resultado_pdf}\nEmail enviado com sucesso."
            
        except Exception as e:
            return False, f"Erro na operação completa: {str(e)}"