from banco import conectar


def inserir_produto(
    nome,
    descricao,
    quantidade,
    preco,
    estoque_minimo=0,
    estoque_maximo=999999
):
    conexao = conectar()

    try:
        cursor = conexao.execute(
            """
            INSERT INTO produtos (
                nome,
                descricao,
                quantidade,
                preco,
                estoque_minimo,
                estoque_maximo
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                nome,
                descricao,
                quantidade,
                preco,
                estoque_minimo,
                estoque_maximo
            )
        )

        conexao.commit()
        return cursor.lastrowid

    finally:
        conexao.close()


def buscar_produtos():
    conexao = conectar()

    try:
        cursor = conexao.execute(
            """
            SELECT * FROM produtos
            ORDER BY nome ASC
            """
        )

        return cursor.fetchall()

    finally:
        conexao.close()


def buscar_por_id(produto_id):
    conexao = conectar()

    try:
        cursor = conexao.execute(
            """
            SELECT * FROM produtos
            WHERE id = ?
            """,
            (produto_id,)
        )

        return cursor.fetchone()

    finally:
        conexao.close()


def buscar_por_nome(nome):
    conexao = conectar()

    try:
        cursor = conexao.execute(
            """
            SELECT * FROM produtos
            WHERE nome LIKE ?
            ORDER BY nome ASC
            """,
            (f"%{nome}%",)
        )

        return cursor.fetchall()

    finally:
        conexao.close()


def atualizar_produto(
    produto_id,
    nome,
    descricao,
    quantidade,
    preco,
    estoque_minimo,
    estoque_maximo
):
    conexao = conectar()

    try:
        cursor = conexao.execute(
            """
            UPDATE produtos
            SET nome = ?,
                descricao = ?,
                quantidade = ?,
                preco = ?,
                estoque_minimo = ?,
                estoque_maximo = ?
            WHERE id = ?
            """,
            (
                nome,
                descricao,
                quantidade,
                preco,
                estoque_minimo,
                estoque_maximo,
                produto_id
            )
        )

        conexao.commit()
        return cursor.rowcount > 0

    finally:
        conexao.close()


def deletar_produto(produto_id):
    conexao = conectar()

    try:
        cursor = conexao.execute(
            """
            DELETE FROM produtos
            WHERE id = ?
            """,
            (produto_id,)
        )

        conexao.commit()
        return cursor.rowcount > 0

    finally:
        conexao.close()