# Acesso ao banco: SOMENTE comandos SQL de produtos, sem regra de negócio.

def listar(cursor, nome, data_inicio, data_fim, limite, offset):
    # Monta o WHERE só com os filtros que vieram
    condicoes = []
    valores = []
    if nome:
        condicoes.append("nome LIKE %s")
        valores.append(f"%{nome}%")
    if data_inicio:
        condicoes.append("data_cadastro >= %s")
        valores.append(data_inicio)
    if data_fim:
        condicoes.append("data_cadastro <= %s")
        valores.append(data_fim)
    where = "WHERE " + " AND ".join(condicoes) if condicoes else ""

    cursor.execute(f"SELECT COUNT(*) AS total FROM produtos {where}", valores)
    total = cursor.fetchone()["total"]

    cursor.execute(
        f"SELECT * FROM produtos {where} ORDER BY id LIMIT %s OFFSET %s",
        valores + [limite, offset])
    return cursor.fetchall(), total


def buscar_por_id(cursor, produto_id, travar=False):
    sql = "SELECT * FROM produtos WHERE id = %s"
    if travar:
        sql += " FOR UPDATE"  # trava a linha até o fim da transação
    cursor.execute(sql, (produto_id,))
    return cursor.fetchone()


def inserir(cursor, nome, descricao, preco, quantidade_estoque):
    cursor.execute(
        "INSERT INTO produtos (nome, descricao, preco, quantidade_estoque) VALUES (%s, %s, %s, %s)",
        (nome, descricao, preco, quantidade_estoque))
    return cursor.lastrowid


def atualizar(cursor, produto_id, nome, descricao, preco):
    cursor.execute(
        "UPDATE produtos SET nome=%s, descricao=%s, preco=%s WHERE id=%s",
        (nome, descricao, preco, produto_id))


def alterar_estoque(cursor, produto_id, delta):
    cursor.execute(
        "UPDATE produtos SET quantidade_estoque = quantidade_estoque + %s WHERE id = %s",
        (delta, produto_id))


def remover(cursor, produto_id):
    cursor.execute("DELETE FROM produtos WHERE id = %s", (produto_id,))
    return cursor.rowcount
