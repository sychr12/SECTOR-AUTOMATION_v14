# -*- coding: utf-8 -*-
import os
from services.database import get_connection, fetch_all_as_dict


def _to_str(valor):
    if valor is None:
        return None
    if isinstance(valor, memoryview):
        valor = valor.tobytes()
    if isinstance(valor, bytes):
        valor = valor.decode("utf-8", errors="ignore")
    return str(valor).strip()


def salvar_memorando(numero, descricao, data_emissao, unloc, municipio,
                     memo_entrada, quantidade, caminho_word, usuario):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO memorandos_saida (
                numero, descricao, pdf, data_emissao, unloc,
                municipio, memo_entrada, quantidade, caminho_word, usuario
            ) VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (
            _to_str(numero), _to_str(descricao), None, data_emissao,
            _to_str(unloc), _to_str(municipio), _to_str(memo_entrada),
            int(quantidade) if quantidade else 0,
            _to_str(caminho_word), _to_str(usuario)
        ))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise Exception(f"Erro ao salvar memorando: {e}")
    finally:
        conn.close()


def listar_memorandos(limit=50):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT TOP (?)
                id, numero, unloc, municipio, data_emissao,
                quantidade, caminho_word, criado_em, usuario
            FROM memorandos_saida
            ORDER BY criado_em DESC
        """, (limit,))
        return fetch_all_as_dict(cur)
    finally:
        conn.close()


def obter_caminho_word_por_id(memorando_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT caminho_word FROM memorandos_saida WHERE id = ?", (memorando_id,))
        row = cur.fetchone()
        return _to_str(row[0]) if row else None
    finally:
        conn.close()


def abrir_word(memorando_id):
    caminho = obter_caminho_word_por_id(memorando_id)
    if not caminho:
        raise Exception("Memorando não possui arquivo Word.")
    caminho = os.path.normpath(caminho)
    if not os.path.isfile(caminho):
        raise Exception(f"Arquivo não encontrado:\n{caminho}")
    os.startfile(caminho)