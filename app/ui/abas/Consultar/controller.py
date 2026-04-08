# -*- coding: utf-8 -*-
"""
Controller para operações de consulta no banco de dados (SQL Server)
Tabela: inscrenov
"""

from datetime import datetime, date, timedelta
from typing import List, Tuple


class ConsultaController:
    """Controller para operações de consulta na tabela inscrenov"""
    
    def __init__(self, conexoes, usuario):
        self.usuario = usuario
        # Validar e armazenar conexões
        self.conexoes = self.validar_conexoes(conexoes)
    
    def validar_conexoes(self, conexoes):
        """Valida as conexões com o banco"""
        if not conexoes:
            raise ValueError("Conexão com banco não fornecida.")
        
        if callable(conexoes):
            return [conexoes]
        elif isinstance(conexoes, list):
            return conexoes
        else:
            raise ValueError("Formato inválido de conexão com banco.")
    
    def construir_query(self, filtros):
        """
        Constrói a query SQL baseada nos filtros
        Tabela: inscrenov
        Campos: id, nome, cpf, unloc, memorando, datas, descricao, analise, gerado, lancou, datalan, DataCriacao
        """
        where_clauses = []
        params = []
        
        # Filtro por nome
        if filtros.get('nome'):
            where_clauses.append("nome LIKE ?")
            params.append(f"%{filtros['nome']}%")
        
        # Filtro por CPF
        if filtros.get('cpf'):
            where_clauses.append("cpf LIKE ?")
            params.append(f"%{filtros['cpf']}%")
        
        # Filtro por município (UNLOC)
        if filtros.get('municipio'):
            where_clauses.append("unloc LIKE ?")
            params.append(f"%{filtros['municipio']}%")
        
        # Filtro por memorando
        if filtros.get('memorando'):
            where_clauses.append("memorando LIKE ?")
            params.append(f"%{filtros['memorando']}%")
        
        # Filtro por período (usando DataCriacao)
        filtro_periodo = filtros.get('periodo', 'Últimos 30 dias')
        
        if filtro_periodo == "Últimos 30 dias":
            where_clauses.append("DataCriacao >= ?")
            params.append(date.today() - timedelta(days=30))
        elif filtro_periodo != "Todos" and filtro_periodo.isdigit():
            where_clauses.append("YEAR(DataCriacao) = ?")
            params.append(int(filtro_periodo))
        
        # Monta a query
        if where_clauses:
            where = f"WHERE {' AND '.join(where_clauses)}"
        else:
            where = ""
            params = []
        
        sql = f"""
            SELECT
                id,
                nome,
                cpf,
                unloc,
                memorando,
                datas,
                descricao,
                analise,
                gerado,
                lancou,
                datalan,
                DataCriacao
            FROM inscrenov
            {where}
            ORDER BY DataCriacao DESC
        """
        
        return sql, params
    
    def executar_consulta(self, sql, params):
        """Executa a consulta no SQL Server"""
        todos_dados = []

        for conectar_func in self.conexoes:
            try:
                conn = conectar_func()
                cur = conn.cursor()
                
                # Executar query com parâmetros
                if params:
                    cur.execute(sql, params)
                else:
                    cur.execute(sql)
                
                # Obter resultados
                for row in cur.fetchall():
                    todos_dados.append((
                        row[0],  # id
                        row[1],  # nome
                        row[2],  # cpf
                        row[3],  # unloc (município)
                        row[4],  # memorando
                        row[5],  # datas
                        row[6],  # descricao
                        row[7],  # analise
                        row[8],  # gerado
                        row[9],  # lancou
                        row[10], # datalan
                        row[11], # DataCriacao
                    ))
                
                cur.close()
                conn.close()

            except Exception as e:
                print(f"Erro ao executar consulta: {str(e)}")
                continue

        return todos_dados
    
    def formatar_data_resultados(self, dados):
        """Formata as datas nos resultados"""
        resultados_formatados = []
        
        for linha in dados:
            linha = list(linha)
            
            # Formatar gerado (índice 8) - tipo date
            if len(linha) > 8 and linha[8] and isinstance(linha[8], (datetime, date)):
                linha[8] = linha[8].strftime("%d/%m/%Y")
            
            # Formatar datalan (índice 10) - tipo datetime
            if len(linha) > 10 and linha[10] and isinstance(linha[10], (datetime, date)):
                linha[10] = linha[10].strftime("%d/%m/%Y %H:%M")
            
            # Formatar DataCriacao (índice 11) - tipo datetime
            if len(linha) > 11 and linha[11] and isinstance(linha[11], (datetime, date)):
                linha[11] = linha[11].strftime("%d/%m/%Y %H:%M")
            
            resultados_formatados.append(linha)
        
        return resultados_formatados
    
    def excluir_registro(self, id_registro):
        """Exclui um registro da tabela inscrenov"""
        try:
            for conectar_func in self.conexoes:
                conn = conectar_func()
                cur = conn.cursor()
                cur.execute("DELETE FROM inscrenov WHERE id = ?", (id_registro,))
                conn.commit()
                cur.close()
                conn.close()
            
            return True, "Registro excluído com sucesso."
        except Exception as e:
            return False, f"Erro ao excluir registro: {str(e)}"
    
    def editar_registro(self, id_registro, campo, novo_valor):
        """Edita um registro na tabela inscrenov"""
        try:
            # Validação básica
            if not novo_valor or novo_valor.strip() == "":
                return False, "O novo valor não pode estar vazio."
            
            # Campos permitidos para edição (baseado na estrutura da tabela)
            campos_permitidos = [
                'nome', 'cpf', 'unloc', 'memorando', 'datas', 
                'descricao', 'analise', 'gerado', 'lancou'
            ]
            
            if campo not in campos_permitidos:
                return False, f"Campo '{campo}' não é permitido para edição."
            
            # Executar update
            for conectar_func in self.conexoes:
                conn = conectar_func()
                cur = conn.cursor()
                cur.execute(
                    f"UPDATE inscrenov SET {campo} = ? WHERE id = ?",
                    (novo_valor, id_registro)
                )
                conn.commit()
                cur.close()
                conn.close()
            
            return True, "Registro atualizado com sucesso."
        except Exception as e:
            return False, f"Erro ao editar registro: {str(e)}"