from src.config.db import conectar


def listar_produtos():
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("SELECT * FROM produtos ORDER BY id")
    produtos = cursor.fetchall()

    cursor.close()
    conexao.close()

    return produtos


def consultar_produto(produto_id):
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM produtos WHERE id = %s",
        (produto_id,)
    )
    produto = cursor.fetchone()

    cursor.close()
    conexao.close()

    return produto


def registrar_saida(produto_id, quantidade):
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT quantidade_estoque FROM produtos WHERE id = %s FOR UPDATE",
            (produto_id,)
        )
        produto = cursor.fetchone()

        if produto is None:
            conexao.rollback()
            return "nao_encontrado"

        if quantidade <= 0 or produto["quantidade_estoque"] < quantidade:
            conexao.rollback()
            return "estoque_insuficiente"

        cursor.execute(
            "UPDATE produtos SET quantidade_estoque = quantidade_estoque - %s WHERE id = %s",
            (quantidade, produto_id)
        )
        cursor.execute(
    """
    INSERT INTO movimentacoes
    (produto_id, tipo, quantidade, usuario_responsavel)
    VALUES (%s, 'saida', %s, 'Sistema')
    """,
    (produto_id, quantidade)
)

        conexao.commit()
        return "sucesso"

    except Exception:
        conexao.rollback()
        raise

    finally:
        cursor.close()
        conexao.close()