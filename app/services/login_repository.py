from datetime import datetime
from services.database import get_connection
from services.database import fetch_one_as_dict


def validar_usuario(username, senha):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        query = """
            SELECT username, perfil, ativo, email, ultimo_acesso
            FROM requerentes
            WHERE username = ?
              AND senha = ?
              AND ativo = 1
        """

        cursor.execute(query, (username, senha))
        return fetch_one_as_dict(cursor)

    except Exception as e:
        print("Erro ao validar usuário:", e)
        return None

    finally:
        conn.close()


def registrar_acesso(usuario):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        query = """
            UPDATE requerentes
            SET ultimo_acesso = ?
            WHERE username = ?
        """

        cursor.execute(query, (datetime.now(), usuario["username"]))
        conn.commit()

    except Exception as e:
        print("Erro ao registrar acesso:", e)

    finally:
        conn.close()