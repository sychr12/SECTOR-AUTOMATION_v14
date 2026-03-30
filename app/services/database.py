import pyodbc


def get_connection():
<<<<<<< HEAD
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="sistemadocumentos",  # ← SEM ;
        user="postgres",
        password="120506",
        cursor_factory=RealDictCursor
    )
=======
    try:
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 18 for SQL Server};"
            "SERVER=SRVCPPTESTE\\SQLEXPRESS;"
            "DATABASE=bancocpp;"
            "UID=usercpp;"
            "PWD=idam2026@;"
            "Encrypt=no;"
            "TrustServerCertificate=yes;"
        )
        return conn

    except Exception as e:
        raise Exception(f"Erro ao conectar no banco: {e}")
>>>>>>> f4a3e3b (.)


def get_cursor(conn):
    """
    SEMPRE use esta função para criar cursors nos repositórios.
    O pyodbc NAO aceita keyword arguments em cursor().
    NUNCA chame conn.cursor(as_dict=True) — isso causa o erro:
      'Connection.cursor() takes no keyword arguments'
    Use fetch_all_as_dict() ou fetch_one_as_dict() para converter em dict.
    """
    return conn.cursor()


# CONVERTER VARIAS LINHAS EM DICT
def fetch_all_as_dict(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


# CONVERTER UMA LINHA EM DICT
def fetch_one_as_dict(cursor):
    row = cursor.fetchone()

    if not row:
        return None

    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))