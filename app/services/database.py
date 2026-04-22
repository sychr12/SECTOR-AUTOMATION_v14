# -*- coding: utf-8 -*-
"""
Database connection module for SQL Server.
"""
import pyodbc
import sys
import os
from functools import lru_cache


# Configurações do banco - podem ser sobrescritas por variáveis de ambiente
_DB_CONFIG = {
    'server': os.environ.get('DB_SERVER', 'SRVCPPTESTE\\SQLEXPRESS'),
    'database': os.environ.get('DB_NAME', 'bancocpp'),
    'username': os.environ.get('DB_USER', 'usercpp'),
    'password': os.environ.get('DB_PASSWORD', 'idam2026@'),
    'driver': None,  # Será detectado automaticamente
}


def _get_best_driver():
    """Detecta o melhor driver ODBC disponível."""
    drivers = pyodbc.drivers()
    
    # Prioridade: Driver 18 > Driver 17 > Native Client > SQL Server
    preferred = [
        'ODBC Driver 18 for SQL Server',
        'ODBC Driver 17 for SQL Server',
        'SQL Server Native Client 11.0',
        'SQL Server Native Client 10.0',
        'SQL Server'
    ]
    
    for driver in preferred:
        if driver in drivers:
            return driver
    
    return drivers[0] if drivers else None


def get_connection_string():
    """Retorna a string de conexão para o banco de dados."""
    driver = _DB_CONFIG['driver']
    if not driver:
        driver = _get_best_driver()
        _DB_CONFIG['driver'] = driver
    
    if not driver:
        raise Exception("Nenhum driver ODBC do SQL Server encontrado. Instale o ODBC Driver 18 for SQL Server.")
    
    return (
        f"DRIVER={{{driver}}};"
        f"SERVER={_DB_CONFIG['server']};"
        f"DATABASE={_DB_CONFIG['database']};"
        f"UID={_DB_CONFIG['username']};"
        f"PWD={_DB_CONFIG['password']};"
        f"Encrypt=no;"
        f"TrustServerCertificate=yes;"
        f"Connection Timeout=30;"
    )


def get_connection():
    """
    Estabelece conexão com o banco de dados SQL Server.
    Retorna a conexão ou None em caso de erro.
    """
    try:
        conn_string = get_connection_string()
        conn = pyodbc.connect(conn_string)
        return conn
        
    except pyodbc.Error as e:
        error_msg = str(e)
        print(f"[Database] Erro ODBC: {error_msg}")
        
        if "28000" in error_msg or "Login failed" in error_msg:
            print("[Database] Falha no login - verifique usuário/senha")
        elif "08001" in error_msg:
            print("[Database] Não foi possível conectar ao servidor - verifique se o servidor está online")
        elif "IM002" in error_msg:
            print("[Database] Driver ODBC não encontrado - instale o ODBC Driver 18 for SQL Server")
        
        return None
        
    except Exception as e:
        print(f"[Database] Erro inesperado: {str(e)}")
        return None


def get_connection_or_raise():
    """
    Estabelece conexão com o banco de dados SQL Server.
    Retorna a conexão ou levanta exceção.
    """
    conn = get_connection()
    if conn is None:
        raise Exception("Conexão com banco não fornecida. Verifique as configurações.")
    return conn


def get_cursor(conn):
    """
    Obtém um cursor da conexão.
    NOTA: pyodbc NÃO aceita keyword arguments em cursor().
    """
    return conn.cursor()


def fetch_all_as_dict(cursor):
    """Converte todas as linhas do cursor em lista de dicionários."""
    if not cursor.description:
        return []
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def fetch_one_as_dict(cursor):
    """Converte uma linha do cursor em dicionário."""
    row = cursor.fetchone()
    if not row:
        return None
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))


def test_connection():
    """Testa a conexão com o banco de dados."""
    try:
        conn = get_connection()
        if conn is None:
            return False, "Falha na conexão"
        
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION as version, DB_NAME() as db_name, GETDATE() as server_time")
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return True, {
            'version': row[0][:100] if row else 'Unknown',
            'database': row[1] if row else 'Unknown',
            'server_time': str(row[2]) if row else 'Unknown'
        }
    except Exception as e:
        return False, str(e)


def get_connection_info():
    """Retorna informações de diagnóstico da conexão."""
    drivers = pyodbc.drivers()
    sql_drivers = [d for d in drivers if 'SQL Server' in d]
    
    conn_string = get_connection_string()
    # Ocultar senha
    import re
    conn_string_hidden = re.sub(r'PWD=[^;]+', 'PWD=***', conn_string)
    
    return {
        'odbc_drivers': sql_drivers,
        'connection_string': conn_string_hidden,
        'server': _DB_CONFIG['server'],
        'database': _DB_CONFIG['database'],
        'user': _DB_CONFIG['username'],
        'driver_used': _DB_CONFIG['driver']
    }


def configure_connection(server=None, database=None, username=None, password=None, driver=None):
    """Permite configurar a conexão dinamicamente."""
    if server:
        _DB_CONFIG['server'] = server
    if database:
        _DB_CONFIG['database'] = database
    if username:
        _DB_CONFIG['username'] = username
    if password:
        _DB_CONFIG['password'] = password
    if driver:
        _DB_CONFIG['driver'] = driver
    
    # Limpar cache da string de conexão
    get_connection_string.cache_clear() if hasattr(get_connection_string, 'cache_clear') else None


# Teste rápido se executado diretamente
if __name__ == "__main__":
    print("=" * 60)
    print("TESTE DE CONEXÃO COM BANCO DE DADOS")
    print("=" * 60)
    
    print("\n1. DRIVERS ODBC DISPONÍVEIS:")
    drivers = pyodbc.drivers()
    for d in drivers:
        print(f"   - {d}")
    
    print("\n2. INFORMAÇÕES DE CONEXÃO:")
    info = get_connection_info()
    print(f"   Servidor: {info['server']}")
    print(f"   Banco: {info['database']}")
    print(f"   Usuário: {info['user']}")
    print(f"   Driver: {info['driver_used']}")
    print(f"   String: {info['connection_string']}")
    
    print("\n3. TESTANDO CONEXÃO...")
    success, result = test_connection()
    
    if success:
        print("   ✅ CONEXÃO BEM SUCEDIDA!")
        print(f"   Banco: {result['database']}")
        print(f"   Versão: {result['version']}")
        print(f"   Hora: {result['server_time']}")
    else:
        print(f"   ❌ FALHA NA CONEXÃO!")
        print(f"   Erro: {result}")
        
        print("\n4. SUGESTÕES:")
        if "IM002" in str(result):
            print("   - Instale o 'ODBC Driver 18 for SQL Server'")
            print("   - Download: https://learn.microsoft.com/pt-br/sql/connect/odbc/download-odbc-driver-for-sql-server")
        elif "28000" in str(result):
            print("   - Verifique usuário e senha")
        elif "08001" in str(result):
            print("   - Verifique se o servidor está online")
            print("   - Verifique se o SQL Server está configurado para aceitar conexões TCP/IP")
    
    print("\n" + "=" * 60)