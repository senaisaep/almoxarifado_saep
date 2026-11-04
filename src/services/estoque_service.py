from src.config.db import conectar


# Listar produtos
def listar_produtos(nome="", pagina=1):
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    inicio = (pagina - 1) * 5

    cursor.execute("""
        SELECT * FROM produtos
        WHERE nome LIKE %s
        ORDER BY id
        LIMIT 5 OFFSET %s
    """, (f"%{nome}%", inicio))

    produtos = cursor.fetchall()

    cursor.close()
    conexao.close()

    return produtos


# Buscar produto pelo ID
def buscar_produto(produto_id):
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


# Cadastrar produto
def cadastrar_produto(nome, descricao, preco, quantidade):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO produtos (nome, descricao, preco, quantidade_estoque)
        VALUES (%s, %s, %s, %s)
    """, (nome, descricao, preco, quantidade))

    conexao.commit()

    cursor.close()
    conexao.close()


# Atualizar produto
def atualizar_produto(produto_id, nome, descricao, preco, quantidade):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE produtos
        SET nome = %s, descricao = %s, preco = %s, quantidade_estoque = %s
        WHERE id = %s
    """, (nome, descricao, preco, quantidade, produto_id))

    conexao.commit()
    alterados = cursor.rowcount

    cursor.close()
    conexao.close()

    return alterados


# Excluir produto
def excluir_produto(produto_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        "DELETE FROM produtos WHERE id = %s",
        (produto_id,)
    )

    conexao.commit()
    excluidos = cursor.rowcount

    cursor.close()
    conexao.close()

    return excluidos


# Registrar entrada ou saída
def movimentar_estoque(produto_id, tipo, quantidade, usuario_id):

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute(
        "SELECT quantidade_estoque FROM produtos WHERE id = %s",
        (produto_id,)
    )

    produto = cursor.fetchone()

    if produto is None:
        cursor.close()
        conexao.close()
        return False, "Produto não encontrado."

    estoque = produto["quantidade_estoque"]

    if quantidade <= 0:
        cursor.close()
        conexao.close()
        return False, "Quantidade inválida."

    if tipo == "saida" and quantidade > estoque:
        cursor.close()
        conexao.close()
        return False, "Estoque insuficiente."

    if tipo == "entrada":
        novo_estoque = estoque + quantidade
    elif tipo == "saida":
        novo_estoque = estoque - quantidade
    else:
        cursor.close()
        conexao.close()
        return False, "Tipo inválido."

    cursor.execute("""
        UPDATE produtos
        SET quantidade_estoque = %s
        WHERE id = %s
    """, (novo_estoque, produto_id))

    cursor.execute("""
        INSERT INTO movimentacoes (produto_id, tipo, quantidade, usuario_id)
        VALUES (%s, %s, %s, %s)
    """, (produto_id, tipo, quantidade, usuario_id))

    conexao.commit()

    cursor.close()
    conexao.close()

    return True, "Movimentação registrada com sucesso."


# Listar movimentações
def listar_movimentacoes(nome="", data=""):
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT movimentacoes.*, produtos.nome AS produto,
               usuarios.nome AS responsavel
        FROM movimentacoes
        JOIN produtos ON produtos.id = movimentacoes.produto_id
        LEFT JOIN usuarios ON usuarios.id = movimentacoes.usuario_id
        WHERE produtos.nome LIKE %s
        ORDER BY movimentacoes.id DESC
    """, (f"%{nome}%",))

    resultado = cursor.fetchall()

    if data:
        resultado = [
            item for item in resultado
            if str(item["data_movimentacao"])[:10] == data
        ]

    cursor.close()
    conexao.close()

    return resultado
