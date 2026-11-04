# Acesso ao banco: SOMENTE comandos SQL de usuários.

def buscar_por_email(cursor, email):
    cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
    return cursor.fetchone()


def buscar_por_id(cursor, usuario_id):
    cursor.execute(
        "SELECT id, nome, email, perfil, ativo FROM usuarios WHERE id = %s", (usuario_id,))
    return cursor.fetchone()


def inserir(cursor, nome, email, senha_hash, perfil):
    cursor.execute(
        "INSERT INTO usuarios (nome, email, senha_hash, perfil) VALUES (%s, %s, %s, %s)",
        (nome, email, senha_hash, perfil))
    return cursor.lastrowid
