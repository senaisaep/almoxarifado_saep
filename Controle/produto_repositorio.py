def buscar_saldo(cursor, produto_id):
    cursor.execute(
        "SELECT quantidade_estoque FROM produtos WHERE id=%s AND ativo=1 FOR UPDATE",
        (produto_id,),
    )
    produto = cursor.fetchone()
    return produto["quantidade_estoque"] if produto else None


def atualizar_saldo(cursor, produto_id, quantidade):
    cursor.execute(
        "UPDATE produtos SET quantidade_estoque=quantidade_estoque-%s WHERE id=%s",
        (quantidade, produto_id),
    )


def registrar_saida(cursor, produto_id, quantidade, usuario):
    cursor.execute(
        "INSERT INTO movimentacoes "
        "(produto_id, tipo, quantidade, usuario_id, usuario_nome) "
        "VALUES (%s, 'saida', %s, %s, %s)",
        (produto_id, quantidade, usuario["id"], usuario["nome"]),
    )
