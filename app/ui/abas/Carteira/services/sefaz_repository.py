# -*- coding: utf-8 -*-
from services.database import get_connection, fetch_one_as_dict


class SefazRepository:

    def obter_credencial(self):
        print("=" * 50)
        print("[DEBUG] Buscando credencial SEFAZ...")
        
        conn = get_connection()
        try:
            cur = conn.cursor()
            
            # Verificar quantos registros existem
            cur.execute("SELECT COUNT(*) FROM sefaz_credenciais")
            count = cur.fetchone()[0]
            print(f"[DEBUG] Total de registros na tabela: {count}")
            
            if count == 0:
                print("[DEBUG] Tabela vazia!")
                return None
            
            # Verificar registros com ativo=1
            cur.execute("SELECT COUNT(*) FROM sefaz_credenciais WHERE ativo = 1")
            count_ativo = cur.fetchone()[0]
            print(f"[DEBUG] Registros com ativo=1: {count_ativo}")
            
            # Buscar a credencial
            cur.execute("""
                SELECT TOP 1 usuario, senha
                FROM sefaz_credenciais
                WHERE ativo = 1
                ORDER BY id DESC
            """)
            
            row = cur.fetchone()
            cur.close()
            
            if row:
                print(f"[DEBUG] Credencial encontrada!")
                print(f"[DEBUG] Usuário: {row[0]}")
                print(f"[DEBUG] Senha: {row[1][:10]}...")  # mostra só os 10 primeiros
                return {
                    'usuario': row[0],
                    'senha': row[1]
                }
            else:
                print("[DEBUG] Nenhum registro com ativo=1 encontrado!")
                return None
                
        except Exception as e:
            print(f"[DEBUG] ERRO: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            conn.close()