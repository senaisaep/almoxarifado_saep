from contextlib import contextmanager
from werkzeug.security import generate_password_hash
from src.config.db import conectar
@contextmanager
def cursor_usuario():
    conexao = conectar()
    cursor = None
    try:
        cursor = conexao.cursor(dictionary=True)
        yield conexao, cursor
    except Exception:
        conexao.rollback()
        raise
    finally:
        try:
            if cursor is not None:
                cursor.close()
        finally:
            conexao.close()


def buscar_por_id(usuario_id):
    with cursor_usuario() as (_, cursor):
        cursor.execute("SELECT id, username, tipo FROM usuarios WHERE id=%s", (usuario_id,))
        return cursor.fetchone()


def buscar_por_nome(username):
    with cursor_usuario() as (_, cursor):
        cursor.execute("SELECT id, username, tipo, senha_hash FROM usuarios WHERE username=%s", (username,))
        return cursor.fetchone()


def criar_usuario(username, senha, tipo="consulta"):
    if not isinstance(username, str) or not 3 <= len(username.strip()) <= 80:
        raise ValueError("O usuário deve ter entre 3 e 80 caracteres.")
    if not isinstance(senha, str) or not 8 <= len(senha) <= 128:
        raise ValueError("A senha deve ter entre 8 e 128 caracteres.")
    if tipo not in ("administrador", "operador", "consulta"):
        raise ValueError("Tipo de usuário inválido.")
    username = username.strip()
    senha_hash = generate_password_hash(senha)
    with cursor_usuario() as (conexao, cursor):
        cursor.execute("INSERT INTO usuarios (username, senha_hash, tipo) VALUES (%s, %s, %s)",
                       (username, senha_hash, tipo))
        usuario_id = cursor.lastrowid
        conexao.commit()
    return {"id": usuario_id, "username": username, "tipo": tipo}