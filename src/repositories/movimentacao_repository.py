_SELECT = """SELECT m.id, m.produto_id, p.nome AS produto, m.tipo, m.quantidade,
                    m.data_hora, m.usuario_id, u.nome AS responsavel
             FROM movimentacoes m
             INNER JOIN produtos p ON p.id = m.produto_id
             INNER JOIN usuarios u ON u.id = m.usuario_id"""


def _filtros(filtros):
    condicoes, params = [], []
    if filtros.get("tipo"):
        condicoes.append("m.tipo = %s")
        params.append(filtros["tipo"])
    if filtros.get("produto_id"):
        condicoes.append("m.produto_id = %s")
        params.append(filtros["produto_id"])
    if filtros.get("data_inicio"):
        condicoes.append("m.data_hora >= %s")
        params.append(filtros["data_inicio"])
    if filtros.get("data_fim"):
        condicoes.append("m.data_hora < DATE_ADD(%s, INTERVAL 1 DAY)")
        params.append(filtros["data_fim"])
    onde = (" WHERE " + " AND ".join(condicoes)) if condicoes else ""
    return onde, params


def inserir(cur, produto_id, tipo, quantidade, usuario_id):
    # data_hora é preenchida pelo banco (DEFAULT CURRENT_TIMESTAMP)
    cur.execute(
        """INSERT INTO movimentacoes (produto_id, tipo, quantidade, usuario_id)
           VALUES (%s, %s, %s, %s)""",
        (produto_id, tipo, quantidade, usuario_id),
    )
    return cur.lastrowid


def buscar_por_id(cur, movimentacao_id):
    cur.execute(f"{_SELECT} WHERE m.id = %s", (movimentacao_id,))
    return cur.fetchone()


def listar(cur, filtros, limite, deslocamento):
    onde, params = _filtros(filtros)
    cur.execute(
        f"{_SELECT}{onde} ORDER BY m.data_hora DESC, m.id DESC LIMIT %s OFFSET %s",
        params + [limite, deslocamento],
    )
    return cur.fetchall()


def contar(cur, filtros):
    onde, params = _filtros(filtros)
    cur.execute(f"SELECT COUNT(*) AS total FROM movimentacoes m{onde}", params)
    return cur.fetchone()["total"]


def contar_por_produto(cur, produto_id):
    cur.execute(
        "SELECT COUNT(*) AS total FROM movimentacoes WHERE produto_id = %s",
        (produto_id,),
    )
    return cur.fetchone()["total"]
