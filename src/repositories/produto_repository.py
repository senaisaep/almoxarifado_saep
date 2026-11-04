def _filtros(busca, estoque_max):
    condicoes, params = [], []
    if busca:
        condicoes.append("(nome LIKE %s OR descricao LIKE %s)")
        params += [f"%{busca}%", f"%{busca}%"]
    if estoque_max is not None:
        condicoes.append("quantidade_estoque <= %s")
        params.append(estoque_max)
    onde = (" WHERE " + " AND ".join(condicoes)) if condicoes else ""
    return onde, params


def listar(cur, busca, estoque_max, limite, deslocamento):
    onde, params = _filtros(busca, estoque_max)
    cur.execute(
        f"SELECT * FROM produtos{onde} ORDER BY id LIMIT %s OFFSET %s",
        params + [limite, deslocamento],
    )
    return cur.fetchall()


def contar(cur, busca, estoque_max):
    onde, params = _filtros(busca, estoque_max)
    cur.execute(f"SELECT COUNT(*) AS total FROM produtos{onde}", params)
    return cur.fetchone()["total"]


def buscar_por_id(cur, produto_id):
    cur.execute("SELECT * FROM produtos WHERE id = %s", (produto_id,))
    return cur.fetchone()


def buscar_para_atualizar(cur, produto_id):
    """Bloqueia a linha até o fim da transação (impede saídas concorrentes
    lerem o mesmo saldo e deixarem o estoque negativo)."""
    cur.execute("SELECT * FROM produtos WHERE id = %s FOR UPDATE", (produto_id,))
    return cur.fetchone()


def inserir(cur, nome, descricao, preco, quantidade):
    cur.execute(
        """INSERT INTO produtos (nome, descricao, preco, quantidade_estoque)
           VALUES (%s, %s, %s, %s)""",
        (nome, descricao, preco, quantidade),
    )
    return cur.lastrowid


def atualizar(cur, produto_id, nome, descricao, preco):
    cur.execute(
        "UPDATE produtos SET nome=%s, descricao=%s, preco=%s WHERE id=%s",
        (nome, descricao, preco, produto_id),
    )


def atualizar_saldo(cur, produto_id, novo_saldo):
    cur.execute(
        "UPDATE produtos SET quantidade_estoque=%s WHERE id=%s",
        (novo_saldo, produto_id),
    )


def remover(cur, produto_id):
    cur.execute("DELETE FROM produtos WHERE id=%s", (produto_id,))
