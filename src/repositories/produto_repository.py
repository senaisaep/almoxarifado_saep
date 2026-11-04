from config.db import conectar


def listar_produtos(nome="", pagina=1, limite=10):
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    inicio = (pagina - 1) * limite

    sql = """
        SELECT *
        FROM produtos
        WHERE nome LIKE %s
        ORDER BY id DESC
        LIMIT %s OFFSET %s
    """

    cursor.execute(
        sql,
        (f"%{nome}%", limite, inicio)
    )

    produtos = cursor.fetchall()

    cursor.close()
    conexao.close()

    return produtos


def buscar_produto(id):
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM produtos WHERE id = %s",
        (id,)
    )

    produto = cursor.fetchone()

    cursor.close()
    conexao.close()

    return produto


def cadastrar_produto(nome, descricao, quantidade, preco):
    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
        INSERT INTO produtos
        (nome, descricao, quantidade_estoque, preco)
        VALUES (%s, %s, %s, %s)
    """

    cursor.execute(
        sql,
        (nome, descricao, quantidade, preco)
    )

    conexao.commit()

    cursor.close()
    conexao.close()


def atualizar_produto(id, nome, descricao, preco):
    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
        UPDATE produtos
        SET nome = %s, descricao = %s, preco = %s
        WHERE id = %s
    """

    cursor.execute(
        sql,
        (nome, descricao, preco, id)
    )

    conexao.commit()

    cursor.close()
    conexao.close()


def excluir_produto(id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        "DELETE FROM produtos WHERE id = %s",
        (id,)
    )

    conexao.commit()

    cursor.close()
    conexao.close()