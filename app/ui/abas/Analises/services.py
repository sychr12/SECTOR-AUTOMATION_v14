from services.analise_repository import AnaliseRepository
from services.analiseap_repository import AnaliseapRepository
from services.credenciais_service import SefazRepository


class AnaliseService:
    def __init__(self):
        self.repo = AnaliseRepository()
        self.repo_ap = AnaliseapRepository()
        self.sefaz_repo = SefazRepository()
    
    # Métodos para análise
    def salvar_pdf(self, nome_pdf, caminho_pdf, urgencia, usuario):
        """Salva PDF no banco"""
        return self.repo.salvar_pdf(
            nome_pdf=nome_pdf,
            caminho_pdf=caminho_pdf,
            urgencia=urgencia,
            usuario=usuario
        )
    
    def listar_pendentes(self):
        """Lista registros pendentes"""
        return self.repo.listar_pendentes()
    
    def buscar_pdf_binario(self, analise_id):
        """Busca PDF no banco"""
        return self.repo.buscar_pdf_binario(analise_id)
    
    def atualizar_status(self, ids, novo_status, motivo=None):
        """Atualiza status dos registros"""
        return self.repo.atualizar_status(ids, novo_status, motivo)
    
    def salvar_historico(self, ids, status_anterior, novo_status, usuario, motivo=None):
        """Salva histórico de movimentação"""
        return self.repo.salvar_historico(
            ids=ids,
            status_anterior=status_anterior,
            novo_status=novo_status,
            usuario=usuario,
            motivo=motivo
        )
    
    def listar_historico(self):
        """Lista histórico de movimentações"""
        return self.repo.listar_historico()

    def buscar_por_id(self, analise_id):
        """Busca análise por ID"""
        return self.repo.buscar_por_id(analise_id)
    
    # Métodos para análise ap
    def salvar_inscricao(self, nome, cpf, municipio, memorando, tipo, usuario):
        """Salva inscrição"""
        return self.repo_ap.salvar_inscricao(
            nome=nome,
            cpf=cpf,
            municipio=municipio,
            memorando=memorando,
            tipo=tipo,
            usuario=usuario
        )
    
    def salvar_devolucao(self, nome, cpf, municipio, memorando, motivo, usuario):
        """Salva devolução"""
        return self.repo_ap.salvar_devolucao(
            nome=nome,
            cpf=cpf,
            municipio=municipio,
            memorando=memorando,
            motivo=motivo,
            usuario=usuario
        )
    
    # Métodos para SIGED
    def buscar_credenciais_sefaz(self):
        """Busca credenciais SIGED"""
        # ✅ CORRIGIDO: obter_credencial() — método correto do SefazRepository
        return self.sefaz_repo.obter_credencial()