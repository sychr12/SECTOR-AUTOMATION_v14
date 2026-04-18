# -*- coding: utf-8 -*-
"""
Controller para operações de gerenciamento de usuários
Versão adaptada para SQL Server
"""

import re
import bcrypt
import pyodbc  # Substituir psycopg2


class UsuarioController:

    def __init__(self, conectar_bd, usuario_logado):
        self.conectar_bd = conectar_bd
        self.usuario_logado = usuario_logado

    # =========================================================
    # UTIL - SENHA
    # =========================================================

    def _hash_senha(self, senha: str) -> str:
        if not senha or len(senha) < 4:
            raise ValueError("Senha inválida.")
        return bcrypt.hashpw(
            senha.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

    def _verificar_senha(self, senha_digitada: str, senha_hash: str) -> bool:
        if not senha_digitada or not senha_hash:
            return False

        return bcrypt.checkpw(
            senha_digitada.encode("utf-8"),
            senha_hash.encode("utf-8")
        )

    # =========================================================
    # LISTAR USUÁRIOS
    # =========================================================

    def carregar_usuarios(self):
        conn = None
        try:
            conn = self.conectar_bd()
            if not conn:
                return []

            cursor = conn.cursor()
            cursor.execute("""
                SELECT username, perfil, ativo, cpf, email,
                       observacoes, data_criacao, ultimo_acesso
                FROM requerentes
                ORDER BY username
            """)
            
            rows = cursor.fetchall()
            cursor.close()

            usuarios = []

            for row in rows:
                u = {
                    'username': row[0],
                    'perfil': row[1],
                    'ativo': row[2],
                    'cpf': row[3],
                    'email': row[4],
                    'observacoes': row[5],
                    'data_criacao': row[6],
                    'ultimo_acesso': row[7],
                }

                u["data_criacao_fmt"] = (
                    u["data_criacao"].strftime("%d/%m/%Y %H:%M")
                    if u.get("data_criacao") else "--"
                )

                u["ultimo_acesso_fmt"] = (
                    u["ultimo_acesso"].strftime("%d/%m/%Y %H:%M")
                    if u.get("ultimo_acesso") else "Nunca"
                )

                usuarios.append(u)

            return usuarios

        except Exception as e:
            # print(f"Erro ao carregar usuários: {e}")
            return []

        finally:
            if conn:
                conn.close()

    # =========================================================
    # VALIDAÇÕES
    # =========================================================

    def validar_cpf(self, cpf_raw):
        if not cpf_raw:
            return False, None

        cpf = re.sub(r"\D", "", cpf_raw)

        if len(cpf) != 11 or cpf == cpf[0] * 11:
            return False, None

        def calc(digs):
            s = sum(int(d) * m for d, m in zip(digs, range(len(digs) + 1, 1, -1)))
            r = (s * 10) % 11
            return r if r < 10 else 0

        d1 = calc(cpf[:9])
        d2 = calc(cpf[:9] + str(d1))

        if int(cpf[9]) == d1 and int(cpf[10]) == d2:
            return True, cpf

        return False, None

    def validar_usuario(self, form_data, is_new_user):
        erros = []

        if not form_data.get("username"):
            erros.append("Nome de usuário é obrigatório")

        if not form_data.get("perfil"):
            erros.append("Perfil é obrigatório")

        if is_new_user and not form_data.get("senha"):
            erros.append("Senha é obrigatória para novo usuário")

        cpf_raw = form_data.get("cpf")
        if cpf_raw:
            cpf_valido, cpf_limpo = self.validar_cpf(cpf_raw)
            if not cpf_valido:
                erros.append("CPF inválido")
            else:
                form_data["cpf"] = cpf_limpo

        return erros

    # =========================================================
    # SALVAR (CRIAR OU ATUALIZAR)
    # =========================================================

    def salvar_usuario(self, form_data, user_data=None):
        conn = None

        try:
            conn = self.conectar_bd()
            if not conn:
                return False, "Erro de conexão com banco"

            cursor = conn.cursor()

            # -------------------------------------------------
            # NOVO USUÁRIO
            # -------------------------------------------------
            if not user_data:

                senha_hash = self._hash_senha(form_data["senha"])

                cursor.execute("""
                    INSERT INTO requerentes
                    (username, perfil, ativo, cpf, senha,
                     email, observacoes, data_criacao)
                    VALUES (?, ?, ?, ?, ?, ?, ?, GETDATE())
                """, (
                    form_data["username"],
                    form_data["perfil"],
                    form_data.get("ativo", True),
                    form_data.get("cpf"),
                    senha_hash,
                    form_data.get("email"),
                    form_data.get("observacoes"),
                ))

            # -------------------------------------------------
            # ATUALIZAÇÃO
            # -------------------------------------------------
            else:
                username_original = user_data["username"]

                cursor.execute("""
                    UPDATE requerentes
                    SET perfil=?,
                        ativo=?,
                        cpf=?,
                        email=?,
                        observacoes=?
                    WHERE username=?
                """, (
                    form_data["perfil"],
                    form_data.get("ativo", True),
                    form_data.get("cpf"),
                    form_data.get("email"),
                    form_data.get("observacoes"),
                    username_original
                ))

                if cursor.rowcount == 0:
                    conn.rollback()
                    cursor.close()
                    return False, "Usuário não encontrado"

                # Atualiza senha apenas se preenchida
                if form_data.get("senha"):
                    nova_hash = self._hash_senha(form_data["senha"])

                    cursor.execute("""
                        UPDATE requerentes
                        SET senha=?
                        WHERE username=?
                    """, (nova_hash, username_original))

            cursor.close()
            conn.commit()
            return True, "Usuário salvo com sucesso"

        except Exception as e:
            if conn:
                conn.rollback()
            return False, f"Erro ao salvar usuário: {str(e)}"

        finally:
            if conn:
                conn.close()

    # =========================================================
    # EXCLUIR
    # =========================================================

    def excluir_usuario(self, username):
        conn = None

        try:
            conn = self.conectar_bd()
            if not conn:
                return False, "Erro de conexão"

            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM requerentes WHERE username=?",
                (username,)
            )

            if cursor.rowcount == 0:
                conn.rollback()
                cursor.close()
                return False, "Usuário não encontrado"

            cursor.close()
            conn.commit()
            return True, "Usuário excluído"

        except Exception as e:
            if conn:
                conn.rollback()
            return False, f"Erro ao excluir: {str(e)}"

        finally:
            if conn:
                conn.close()

    # =========================================================
    # ALTERAR SENHA (COM VERIFICAÇÃO)
    # =========================================================

    def alterar_senha(self, username, senha_atual, nova_senha):
        conn = None

        try:
            if not nova_senha:
                return False, "Nova senha inválida"

            conn = self.conectar_bd()
            if not conn:
                return False, "Erro de conexão"

            cursor = conn.cursor()
            cursor.execute(
                "SELECT senha FROM requerentes WHERE username=?",
                (username,)
            )

            row = cursor.fetchone()

            if not row:
                cursor.close()
                return False, "Usuário não encontrado"

            senha_hash = row[0]

            if not self._verificar_senha(senha_atual, senha_hash):
                cursor.close()
                return False, "Senha atual incorreta"

            nova_hash = self._hash_senha(nova_senha)

            cursor.execute(
                "UPDATE requerentes SET senha=? WHERE username=?",
                (nova_hash, username)
            )
            cursor.close()
            conn.commit()
            return True, "Senha alterada com sucesso"

        except Exception as e:
            if conn:
                conn.rollback()
            return False, f"Erro ao alterar senha: {str(e)}"

        finally:
            if conn:
                conn.close()