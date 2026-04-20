# -*- coding: utf-8 -*-
"""
Repositório PostgreSQL — tabela analise_ap (para consulta)
e carteiras_digitais/sefaz_credenciais (para anexar)
"""

from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor


class DatabaseConnection:
    """Gerenciador de conexões com o banco de dados"""
    
    _instances = {}
    
    @classmethod
    def get_connection(cls, db_name="postgres"):
        """Obtém conexão com o banco de dados (Singleton por database)"""
        if db_name not in cls._instances:
            # Configurações - devem vir de variáveis de ambiente ou config
            cls._instances[db_name] = psycopg2.connect(
                host="localhost",
                port=5432,
                database=db_name,
                user="seu_usuario",
                password="sua_senha"
            )
        return cls._instances[db_name]
    
    @classmethod
    def close_all(cls):
        """Fecha todas as conexões"""
        for conn in cls._instances.values():
            conn.close()
        cls._instances.clear()


class ConsultaRepository:
    """Repositório para operações na tabela analise_ap"""
    
    def __init__(self, conectar_func):
        self.conectar_func = conectar_func
    
    def executar_consulta(self, sql: str, params: tuple) -> list:
        """Executa consulta SQL e retorna resultados"""
        resultados = []
        conn = self.conectar_func()
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, params)
                for row in cur.fetchall():
                    resultados.append((
                        row.get("id"),
                        row.get("nome"),
                        row.get("cpf"),
                        row.get("municipio"),
                        row.get("memorando"),
                        row.get("tipo"),
                        row.get("motivo"),
                        row.get("usuario"),
                        row.get("criado_em"),
                    ))
        finally:
            conn.close()
        
        return resultados
    
    def excluir_registro(self, id_registro: int) -> bool:
        """Exclui um registro da tabela analise_ap"""
        conn = self.conectar_func()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM analise_ap WHERE id = %s", (id_registro,))
                conn.commit()
                return True
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def editar_registro(self, id_registro: int, campo: str, novo_valor: str) -> bool:
        """Edita um campo específico do registro"""
        campos_permitidos = ['nome', 'cpf', 'municipio', 'memorando', 'tipo', 'motivo']
        if campo not in campos_permitidos:
            raise ValueError(f"Campo '{campo}' não é editável")
        
        conn = self.conectar_func()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"UPDATE analise_ap SET {campo} = %s WHERE id = %s",
                    (novo_valor, id_registro)
                )
                conn.commit()
                return True
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


class AnexarRepository:
    """Repositório para operações nas tabelas carteiras_digitais e sefaz_credenciais"""
    
    def __init__(self, conectar_func):
        self.conectar_func = conectar_func
    
    def buscar_credencial_sefaz(self) -> Optional[dict]:
        """Retorna o primeiro usuário ativo da tabela sefaz_credenciais"""
        sql = """
        SELECT usuario, senha
        FROM   sefaz_credenciais
        WHERE  ativo = TRUE
        ORDER  BY id
        LIMIT  1
        """
        conn = self.conectar_func()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql)
                row = cur.fetchone()
                return dict(row) if row else None
        finally:
            conn.close()
    
    def buscar_carteiras_pendentes(self) -> list:
        """Retorna carteiras onde pdf IS NULL"""
        sql = """
        SELECT  id, nome, cpf, unloc, validade,
                criado_em, registro, propriedade,
                inicio, endereco, atividade1, atividade2,
                georef, usuario
        FROM    carteiras_digitais
        WHERE   pdf IS NULL
        ORDER   BY criado_em DESC
        """
        conn = self.conectar_func()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql)
                return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()
    
    def salvar_pdf(self, record_id: int, pdf_bytes: bytes) -> None:
        """Persiste o PDF gerado na coluna `pdf` da carteira"""
        sql = "UPDATE carteiras_digitais SET pdf = %s WHERE id = %s"
        conn = self.conectar_func()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (psycopg2.Binary(pdf_bytes), record_id))
                conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()