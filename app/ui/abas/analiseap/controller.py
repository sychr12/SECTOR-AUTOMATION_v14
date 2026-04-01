# -*- coding: utf-8 -*-
import re

class AnaliseapController:
    def __init__(self, usuario, repo):
        self.usuario = usuario
        self.repo = repo
        
    def validar_cpf(self, cpf):
        """Valida e limpa o CPF"""
        cpf_limpo = re.sub(r"\D", "", cpf)
        return len(cpf_limpo) == 11, cpf_limpo
    
    def validar_campos_obrigatorios(self, campos):
        """Valida se todos os campos estão preenchidos"""
        return all(campos)
    
    def formatar_cpf(self, texto_cpf):
        """Formata CPF com pontos e traço"""
        texto = re.sub(r"\D", "", texto_cpf)[:11]
        if len(texto) == 11:
            texto = re.sub(r"(\d{3})(\d{3})(\d{3})(\d{2})", r"\1.\2.\3-\4", texto)
        return texto
    
    def salvar_inscricao(self, nome, cpf, municipio, memorando, tipo):
        """Salva dados de inscrição"""
        try:
            # Validar CPF
            cpf_valido, cpf_limpo = self.validar_cpf(cpf)
            if not cpf_valido:
                return False, "CPF inválido!"
            
            # Salvar no repositório
            self.repo.salvar_inscricao(
                nome=nome,
                cpf=cpf_limpo,
                municipio=municipio,
                memorando=memorando,
                tipo=tipo,
                usuario=self.usuario
            )
            
            return True, "Registro salvo no banco."
            
        except Exception as e:
            return False, f"Erro ao salvar registro: {str(e)}"
    
    def salvar_devolucao(self, nome, cpf, municipio, memorando, motivo_combo, motivo_texto):
        """Salva dados de devolução"""
        try:
            # Validar CPF
            cpf_valido, cpf_limpo = self.validar_cpf(cpf)
            if not cpf_valido:
                return False, "CPF inválido!"
            
            # Formatar motivo
            motivo = f"{motivo_combo} - {motivo_texto}"
            
            # Salvar no repositório
            self.repo.salvar_devolucao(
                nome=nome,
                cpf=cpf_limpo,
                municipio=municipio,
                memorando=memorando,
                motivo=motivo,
                usuario=self.usuario
            )
            
            return True, "Devolução salva no banco."
            
        except Exception as e:
            return False, f"Erro ao salvar devolução: {str(e)}"