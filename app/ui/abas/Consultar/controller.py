# -*- coding: utf-8 -*-
"""
Controller para operações de consulta no banco de dados
"""

from datetime import datetime, date, timedelta

class ConsultaController:
    """Controller para operações de consulta"""
    
    def __init__(self, conexoes, usuario):
        self.usuario = usuario
        # Validar e armazenar conexões
        self.conexoes = self.validar_conexoes(conexoes)
    
    def validar_conexoes(self, conexoes):
        """Valida as conexões com o banco"""
        if not conexoes:
            raise ValueError("Conexão com banco não fornecida.")
        
        # Se for uma função única, transforma em lista
        if callable(conexoes):
            return [conexoes]
        # Se já for uma lista, retorna
        elif isinstance(conexoes, list):
            return conexoes
        else:
            raise ValueError("Formato inválido de conexão com banco.")
    
    def construir_query(self, filtros):
        """Constrói a query SQL baseada nos filtros"""
        where_clauses = []
        params = []
        
        # Filtro por nome
        if filtros.get('nome'):
            where_clauses.append("nome ILIKE %s")
            params.append(f"%{filtros['nome']}%")
        
        # Filtro por CPF
        if filtros.get('cpf'):
            where_clauses.append("cpf ILIKE %s")
            params.append(f"%{filtros['cpf']}%")
        
        # Filtro por município
        if filtros.get('municipio'):
            where_clauses.append("municipio ILIKE %s")
            params.append(f"%{filtros['municipio']}%")
        
        # Filtro por memorando
        if filtros.get('memorando'):
            where_clauses.append("memorando ILIKE %s")
            params.append(f"%{filtros['memorando']}%")
        
        # Filtro por período
        filtro_ano = filtros.get('periodo', 'Últimos 30 dias')
        
        if filtro_ano == "Últimos 30 dias":
            where_clauses.append("criado_em >= %s")
            params.append(date.today() - timedelta(days=30))
        elif filtro_ano != "Todos":
            where_clauses.append("EXTRACT(YEAR FROM criado_em) = %s")
            params.append(int(filtro_ano))
        
        # Monta a query
        where = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        
        sql = f"""
            SELECT
                id,
                nome,
                cpf,
                municipio,
                memorando,
                tipo,
                motivo,
                usuario,
                criado_em
            FROM analise_ap
            {where}
            ORDER BY criado_em DESC
        """
        
        return sql, params
    
    def executar_consulta(self, sql, params):
        """Executa a consulta no banco de dados"""
        todos_dados = []

        for conectar_func in self.conexoes:
            try:
                conn = conectar_func()
                # RealDictCursor permite acessar colunas por nome (row["campo"])
                from psycopg2.extras import RealDictCursor
                cur = conn.cursor(cursor_factory=RealDictCursor)
                cur.execute(sql, params)

                for row in cur.fetchall():
                    todos_dados.append((
                        row["id"],
                        row["nome"],
                        row["cpf"],
                        row["municipio"],
                        row["memorando"],
                        row["tipo"],
                        row["motivo"],
                        row["usuario"],
                        row["criado_em"],
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
            # Formatar data (última coluna)
            if isinstance(linha[8], (datetime, date)):
                linha[8] = linha[8].strftime("%d/%m/%Y")
            resultados_formatados.append(linha)
        
        return resultados_formatados
    
    def excluir_registro(self, id_registro):
        """Exclui um registro do banco"""
        try:
            for conectar_func in self.conexoes:
                conn = conectar_func()
                cur = conn.cursor()
                cur.execute("DELETE FROM analise_ap WHERE id = %s", (id_registro,))
                conn.commit()
                cur.close()
                conn.close()
            
            return True, "Registro excluído com sucesso."
        except Exception as e:
            return False, f"Erro ao excluir registro: {str(e)}"
    
    def editar_registro(self, id_registro, campo, novo_valor):
        """Edita um registro no banco"""
        try:
            # Validação básica
            if not novo_valor or novo_valor.strip() == "":
                return False, "O novo valor não pode estar vazio."
            
            # Campos permitidos para edição
            campos_permitidos = ['nome', 'cpf', 'municipio', 'memorando', 'tipo', 'motivo']
            if campo not in campos_permitidos:
                return False, f"Campo '{campo}' não é permitido para edição."
            
            # Executar update em todas as conexões
            for conectar_func in self.conexoes:
                conn = conectar_func()
                cur = conn.cursor()
                cur.execute(
                    f"UPDATE analise_ap SET {campo} = %s WHERE id = %s",
                    (novo_valor, id_registro)
                )
                conn.commit()
                cur.close()
                conn.close()
            
            return True, "Registro atualizado com sucesso."
        except Exception as e:
            return False, f"Erro ao editar registro: {str(e)}"