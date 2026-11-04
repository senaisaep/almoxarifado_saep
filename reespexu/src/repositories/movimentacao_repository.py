# Acesso ao banco: SOMENTE comandos SQL de movimentações.

def inserir(cursor, produto_id, tipo, quantidade, usuario_id):
    cursor.execute(
        "INSERT INTO movimentacoes (produto_id, usuario_id, tipo, quantidade) VALUES (%s, %s, %s, %s)",
        (produto_id, usuario_id, tipo, quantidade))
    return cursor.lastrowid


def listar(cursor, produto_id, tipo, limite, offset):
    condicoes = []
    valores = []
    if produto_id:
        condicoes.append("m.produto_id = %s")
        valores.append(produto_id)
    if tipo:
        condicoes.append("m.tipo = %s")
        valores.append(tipo)
    where = "WHERE " + " AND ".join(condicoes) if condicoes else ""

    cursor.execute(f"SELECT COUNT(*) AS total FROM movimentacoes m {where}", valores)
    total = cursor.fetchone()["total"]

    cursor.execute(
        f"""SELECT m.id, m.produto_id, p.nome AS produto, m.tipo, m.quantidade,
                   m.data_hora, m.usuario_id, u.nome AS usuario
            FROM movimentacoes m
            INNER JOIN produtos p ON p.id = m.produto_id
            LEFT JOIN usuarios u ON u.id = m.usuario_id
            {where}
            ORDER BY m.data_hora DESC, m.id DESC
            LIMIT %s OFFSET %s""",
        valores + [limite, offset])
    return cursor.fetchall(), total
