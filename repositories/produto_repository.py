import sqlite3

from infra.database import conectar


def listar_produtos():
    conexao = conectar()
    try:
        produtos = conexao.execute("SELECT * FROM produtos ORDER BY nome").fetchall()
        return [dict(produto) for produto in produtos]
    finally:
        conexao.close()


def buscar_produto(produto_id):
    conexao = conectar()
    try:
        produto = conexao.execute(
            "SELECT * FROM produtos WHERE id = ?", (produto_id,)
        ).fetchone()
        return dict(produto) if produto else None
    finally:
        conexao.close()


def cadastrar_produto(nome, descricao, preco, quantidade, usuario_id):
    conexao = conectar()
    try:
        cursor = conexao.execute(
            """INSERT INTO produtos (nome, descricao, preco, quantidade_estoque)
               VALUES (?, ?, ?, ?)""",
            (nome, descricao, preco, quantidade),
        )
        produto_id = cursor.lastrowid
        if quantidade:
            conexao.execute(
                """INSERT INTO movimentacoes
                   (produto_id, tipo, quantidade, usuario_id)
                   VALUES (?, 'entrada', ?, ?)""",
                (produto_id, quantidade, usuario_id),
            )
        conexao.commit()
        return produto_id
    finally:
        conexao.close()


def atualizar_produto(produto_id, nome, descricao, preco):
    conexao = conectar()
    try:
        cursor = conexao.execute(
            """UPDATE produtos
               SET nome=?, descricao=?, preco=?
               WHERE id=?""",
            (nome, descricao, preco, produto_id),
        )
        conexao.commit()
        return cursor.rowcount > 0
    finally:
        conexao.close()


def remover_produto(produto_id):
    conexao = conectar()
    try:
        movimento = conexao.execute(
            "SELECT id FROM movimentacoes WHERE produto_id=? LIMIT 1",
            (produto_id,),
        ).fetchone()
        if movimento:
            return "Não é possível remover um produto com movimentações.", 409

        cursor = conexao.execute("DELETE FROM produtos WHERE id=?", (produto_id,))
        conexao.commit()
        if not cursor.rowcount:
            return "Produto não encontrado.", 404
        return "Produto removido.", 200
    except sqlite3.IntegrityError:
        conexao.rollback()
        return "Não é possível remover um produto com movimentações.", 409
    finally:
        conexao.close()
