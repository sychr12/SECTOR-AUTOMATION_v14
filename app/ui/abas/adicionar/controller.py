import re
from datetime import datetime
from tkinter import messagebox, END


class AdicionarController:
    def __init__(self, usuario, repo):
        self.usuario = usuario
        self.repo = repo

    def formatar_cpf(self, cpf_texto):
        """Formata CPF automaticamente (XXX.XXX.XXX-XX)"""
        if not cpf_texto:
            return ""
        
        # Remove caracteres não numéricos
        cpf_limpo = re.sub(r"\D", "", cpf_texto)
        cpf_limpo = cpf_limpo[:11]
        
        if len(cpf_limpo) == 11:
            return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
        return cpf_limpo

    def limpar_cpf(self, cpf_texto):
        """Remove formatação do CPF"""
        return re.sub(r"\D", "", cpf_texto)

    def validar_cpf(self, cpf_texto):
        """Valida se CPF tem 11 dígitos"""
        cpf_limpo = self.limpar_cpf(cpf_texto)
        return len(cpf_limpo) == 11

    def validar_campos_obrigatorios(self, dados):
        """Valida campos obrigatórios"""
        campos_faltantes = []
        
        if not dados.get('nome', '').strip():
            campos_faltantes.append("Nome Completo")
        
        if not dados.get('cpf', '').strip():
            campos_faltantes.append("CPF")
        elif not self.validar_cpf(dados['cpf']):
            return False, "O CPF deve conter 11 dígitos!"
        
        if not dados.get('municipio', '').strip():
            campos_faltantes.append("Município")
        
        if not dados.get('memo', '').strip():
            campos_faltantes.append("Memorando")
        
        if campos_faltantes:
            return False, f"Preencha todos os campos obrigatórios!\n\nCampos faltando: {', '.join(campos_faltantes)}"
        
        return True, ""

    def salvar_inscricao(self, dados):
        """Salva uma inscrição no banco"""
        try:
            # Validar campos
            validacao, mensagem = self.validar_campos_obrigatorios(dados)
            if not validacao:
                return False, mensagem
            
            if not dados.get('tipo'):
                return False, "Selecione o tipo da inscrição!"
            
            cpf_limpo = self.limpar_cpf(dados['cpf'])
            
            self.repo.salvar_inscricao(
                nome=dados['nome'].strip(),
                cpf=cpf_limpo,
                municipio=dados['municipio'].strip(),
                memo=dados['memo'].strip(),
                tipo=dados['tipo'],
                usuario=self.usuario
            )
            
            return True, "Inscrição salva com sucesso!"
            
        except Exception as e:
            return False, f"Erro ao salvar inscrição:\n{str(e)}"

    def salvar_devolucao(self, dados):
        """Salva uma devolução no banco"""
        try:
            # Validar campos
            validacao, mensagem = self.validar_campos_obrigatorios(dados)
            if not validacao:
                return False, mensagem
            
            if not dados.get('motivo', '').strip():
                return False, "Informe o motivo da devolução!"
            
            cpf_limpo = self.limpar_cpf(dados['cpf'])
            
            self.repo.salvar_devolucao(
                nome=dados['nome'].strip(),
                cpf=cpf_limpo,
                municipio=dados['municipio'].strip(),
                memo=dados['memo'].strip(),
                motivo=dados['motivo'].strip(),
                usuario=self.usuario
            )
            
            return True, "Devolução salva com sucesso!"
            
        except Exception as e:
            return False, f"Erro ao salvar devolução:\n{str(e)}"

    def obter_registro_tabela(self, dados, tipo_registro):
        """Obtém dados formatados para a tabela"""
        cpf_formatado = self.formatar_cpf(dados.get('cpf', ''))
        data_atual = datetime.now().strftime("%d/%m/%Y")
        
        return (
            dados.get('nome', '').strip(),
            cpf_formatado,
            dados.get('municipio', '').strip(),
            dados.get('memo', '').strip(),
            data_atual
        )

    def limpar_dados_formulario(self):
        """Retorna estrutura vazia para limpar formulário"""
        return {
            'nome': '',
            'cpf': '',
            'municipio': '',
            'memo': '',
            'tipo': 'INSC',
            'motivo': ''
        }