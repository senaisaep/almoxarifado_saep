from infra.database import conectar


def buscar_usuario_por_login(login):
    conexao = conectar()
    try:
        usuario = conexao.execute(
            "SELECT id, nome, login, senha, perfil FROM usuarios WHERE login = ?",
            (login,),
        ).fetchone()
        return dict(usuario) if usuario else None
    finally:
        conexao.close()


def contar_usuarios():
    conexao = conectar()
    try:
        return conexao.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
    finally:
        conexao.close()


def criar_usuario(nome, login, senha_hash, perfil):
    conexao = conectar()
    try:
        cursor = conexao.execute(
            "INSERT INTO usuarios (nome, login, senha, perfil) VALUES (?, ?, ?, ?)",
            (nome, login, senha_hash, perfil),
        )
        conexao.commit()
        return cursor.lastrowid
    finally:
        conexao.close()

