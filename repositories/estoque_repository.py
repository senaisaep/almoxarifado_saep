from infra.database import conectar


def listar_movimentacoes():
    conexao = conectar()
    try:
        movimentos = conexao.execute(
            """SELECT m.id, m.produto_id, p.nome AS produto, m.tipo,
                      m.quantidade, u.nome AS responsavel, m.data_hora
               FROM movimentacoes m
               JOIN produtos p ON p.id = m.produto_id
               JOIN usuarios u ON u.id = m.usuario_id
               ORDER BY m.id DESC"""
        ).fetchall()
        return [dict(movimento) for movimento in movimentos]
    finally:
        conexao.close()


def registrar_movimentacao(produto_id, quantidade, tipo, usuario_id):
    conexao = conectar()
    try:
        conexao.execute("BEGIN IMMEDIATE")
        produto = conexao.execute(
            "SELECT quantidade_estoque FROM produtos WHERE id=?",
            (produto_id,),
        ).fetchone()
        if produto is None:
            conexao.rollback()
            return "Produto não encontrado.", 404

        saldo = produto["quantidade_estoque"]
        if tipo == "saida" and saldo < quantidade:
            conexao.rollback()
            return "Estoque insuficiente.", 400

        operador = "+" if tipo == "entrada" else "-"
        conexao.execute(
            f"UPDATE produtos SET quantidade_estoque=quantidade_estoque{operador}? "
            "WHERE id=?",
            (quantidade, produto_id),
        )
        cursor = conexao.execute(
            """INSERT INTO movimentacoes
               (produto_id, tipo, quantidade, usuario_id)
               VALUES (?, ?, ?, ?)""",
            (produto_id, tipo, quantidade, usuario_id),
        )
        conexao.commit()
        return cursor.lastrowid, 201
    finally:
        conexao.close()