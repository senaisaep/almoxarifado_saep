from config.db import conectar


def buscar_por_email(email):
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    sql = "SELECT * FROM usuarios WHERE email = %s"
    cursor.execute(sql, (email,))

    usuario = cursor.fetchone()

    cursor.close()
    conexao.close()

    return usuario


def contar_usuarios():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("SELECT COUNT(*) FROM usuarios")
    total = cursor.fetchone()[0]

    cursor.close()
    conexao.close()

    return total


def criar_usuario(nome, email, senha, perfil):
    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
        INSERT INTO usuarios (nome, email, senha, perfil)
        VALUES (%s, %s, %s, %s)
    """

    cursor.execute(sql, (nome, email, senha, perfil))
    conexao.commit()

    cursor.close()
    conexao.close()