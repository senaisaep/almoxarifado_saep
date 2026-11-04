from config.db import conectar


def listar_produtos():
    try:
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT * FROM produtos ORDER BY id")
        dados = cursor.fetchall()
        cursor.close()
        conexao.close()
        return dados
    except Exception:
        return []


def consultar_produto(produto_id):
    try:
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT * FROM produtos WHERE id = %s", (produto_id,))
        produto = cursor.fetchone()
        cursor.close()
        conexao.close()
        return produto
    except Exception:
        return None


def cadastrar_produto(dados):
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute(
            "INSERT INTO produtos (nome, descricao, preco, quantidade_estoque) VALUES (%s, %s, %s, %s)",
            (
                dados["nome"],
                dados.get("descricao", ""),
                dados.get("preco", 0),
                dados.get("quantidade_estoque", 0),
            ),
        )
        conexao.commit()
        novo_id = cursor.lastrowid
        cursor.close()
        conexao.close()
        return novo_id
    except Exception:
        return None


def atualizar_produto(produto_id, dados):
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute(
            """UPDATE produtos
               SET nome=%s, descricao=%s, preco=%s, quantidade_estoque=%s
               WHERE id=%s""",
            (
                dados.get("nome"),
                dados.get("descricao", ""),
                dados.get("preco", 0),
                dados.get("quantidade_estoque", 0),
                produto_id,
            ),
        )
        conexao.commit()
        alterados = cursor.rowcount
        cursor.close()
        conexao.close()
        return alterados
    except Exception:
        return 0


def remover_produto(produto_id):
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM produtos WHERE id=%s", (produto_id,))
        conexao.commit()
        removidos = cursor.rowcount
        cursor.close()
        conexao.close()
        return removidos
    except Exception:
        return 0


def listar_movimentacoes():
    try:
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)
        cursor.execute(
            """SELECT m.id, m.produto_id, p.nome AS produto, m.tipo, m.quantidade
               FROM movimentacoes m
               INNER JOIN produtos p ON p.id=m.produto_id
               ORDER BY m.id DESC"""
        )
        dados = cursor.fetchall()
        cursor.close()
        conexao.close()
        return dados
    except Exception:
        return []


def registrar_entrada(dados):
    try:
        produto_id = dados.get("produto_id")
        quantidade = int(dados.get("quantidade"))

        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute(
            "INSERT INTO movimentacoes (produto_id, tipo, quantidade) VALUES (%s, 'entrada', %s)",
            (produto_id, quantidade),
        )
        cursor.execute(
            "UPDATE produtos SET quantidade_estoque=quantidade_estoque+%s WHERE id=%s",
            (quantidade, produto_id),
        )
        conexao.commit()
        cursor.close()
        conexao.close()
        return True
    except Exception:
        return False


def registrar_saida(dados):
    try:
        produto_id = dados.get("produto_id")
        quantidade = int(dados.get("quantidade"))
        registrar_hora = dados.get("hora")

        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT quantidade_estoque FROM produtos WHERE id=%s", (produto_id,))
        produto = cursor.fetchone()

        if not produto:
            cursor.close()
            conexao.close()
            return "produto_nao_encontrado"

        if produto["quantidade_estoque"] < quantidade:
            cursor.close()
            conexao.close()
            return "estoque_insuficiente"

        cursor.execute(
            "INSERT INTO movimentacoes (produto_id, tipo, quantidade) VALUES (%s, 'saida', %s)",
            (produto_id, quantidade),
        )
        cursor.execute(
            "UPDATE produtos SET quantidade_estoque=quantidade_estoque-%s WHERE id=%s",
            (quantidade, produto_id),
        )

        if registrar_hora:
            cursor.execute(
                "UPDATE movimentacoes SET hora=NOW() WHERE produto_id=%s AND tipo='saida' ORDER BY id DESC LIMIT 1",
                (produto_id,),
            )

        conexao.commit()
        cursor.close()
        conexao.close()
        return "sucesso"
    except Exception:
        return "erro_bd"
