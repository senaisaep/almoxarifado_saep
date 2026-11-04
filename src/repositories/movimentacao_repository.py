from config.db import conectar


def listar_movimentacoes():
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    sql = """
        SELECT
            m.id,
            p.nome AS produto,
            m.tipo,
            m.quantidade,
            m.data_hora,
            u.nome AS responsavel
        FROM movimentacoes m
        JOIN produtos p ON m.produto_id = p.id
        LEFT JOIN usuarios u ON m.usuario_id = u.id
        ORDER BY m.data_hora DESC
    """

    cursor.execute(sql)
    movimentacoes = cursor.fetchall()

    cursor.close()
    conexao.close()

    return movimentacoes


def registrar_movimentacao(produto_id, tipo, quantidade, usuario_id):
    if tipo not in ["entrada", "saida"]:
        return False, "Tipo de movimentação inválido."

    if quantidade <= 0:
        return False, "A quantidade deve ser maior que zero."

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    try:
        conexao.start_transaction()

        cursor.execute(
            "SELECT quantidade_estoque FROM produtos WHERE id = %s FOR UPDATE",
            (produto_id,)
        )

        produto = cursor.fetchone()

        if not produto:
            conexao.rollback()
            return False, "Produto não encontrado."

        estoque = produto["quantidade_estoque"]

        if tipo == "saida" and quantidade > estoque:
            conexao.rollback()
            return False, "Estoque insuficiente."

        if tipo == "entrada":
            novo_estoque = estoque + quantidade
        else:
            novo_estoque = estoque - quantidade

        cursor.execute(
            "UPDATE produtos SET quantidade_estoque = %s WHERE id = %s",
            (novo_estoque, produto_id)
        )

        cursor.execute(
            """
            INSERT INTO movimentacoes
            (produto_id, tipo, quantidade, usuario_id)
            VALUES (%s, %s, %s, %s)
            """,
            (produto_id, tipo, quantidade, usuario_id)
        )

        conexao.commit()
        return True, "Movimentação registrada com sucesso."

    except Exception as erro:
        conexao.rollback()
        return False, str(erro)

    finally:
        cursor.close()
        conexao.close()