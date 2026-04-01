from services.analiseap_repository import AnaliseapRepository


class AdicionarService:
    def __init__(self):
        self.repo = AnaliseapRepository()
    
    def salvar_inscricao(self, nome, cpf, municipio, memo, tipo, usuario):
        """Salva inscrição no banco"""
        return self.repo.salvar_inscricao(
            nome=nome,
            cpf=cpf,
            municipio=municipio,
            memo=memo,
            tipo=tipo,
            usuario=usuario
        )
    
    def salvar_devolucao(self, nome, cpf, municipio, memo, motivo, usuario):
        """Salva devolução no banco"""
        return self.repo.salvar_devolucao(
            nome=nome,
            cpf=cpf,
            municipio=municipio,
            memo=memo,
            motivo=motivo,
            usuario=usuario
        )
    
    def listar_registros(self, tipo=None, data_inicio=None, data_fim=None):
        """Lista registros do banco"""
        # Implementação opcional para carregar registros existentes
        return []