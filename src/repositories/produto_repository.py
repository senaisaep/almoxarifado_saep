from src.config.db import conectar

def listar():
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)
    try:
        cursor.execute(
            """SELECT id, nome, descricao, preco, quantidade_estoque, data_cadastro
               FROM produtos ORDER BY id DESC"""
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conexao.close()

def buscar_por_id(produto_id):
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, nome, descricao, preco, quantidade_estoque, data_cadastro FROM produtos WHERE id = %s",
            (produto_id,)
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conexao.close()

def criar(dados):
    conexao = conectar()
    cursor = conexao.cursor()
    try:
        cursor.execute(
            """INSERT INTO produtos (nome, descricao, preco, quantidade_estoque)
               VALUES (%s, %s, %s, %s)""",
            (dados["nome"], dados["descricao"], dados["preco"], dados["quantidade_estoque"])
        )
        conexao.commit()
        return cursor.lastrowid
    except Exception:
        conexao.rollback()
        raise
    finally:
        cursor.close()
        conexao.close()

def atualizar(produto_id, dados):
    conexao = conectar()
    cursor = conexao.cursor()
    try:
        cursor.execute(
            """UPDATE produtos
               SET nome = %s, descricao = %s, preco = %s, quantidade_estoque = %s
               WHERE id = %s""",
            (dados["nome"], dados["descricao"], dados["preco"], dados["quantidade_estoque"], produto_id)
        )
        conexao.commit()
        return cursor.rowcount
    except Exception:
        conexao.rollback()
        raise
    finally:
        cursor.close()
        conexao.close()


def atualizar_quantidade(produto_id, quantidade):
    conexao = conectar()
    cursor = conexao.cursor()
    try:
        cursor.execute(
            "UPDATE produtos SET quantidade_estoque = %s WHERE id = %s",
            (quantidade, produto_id)
        )
        conexao.commit()
        return cursor.rowcount
    except Exception:
        conexao.rollback()
        raise
    finally:
        cursor.close()
        conexao.close()


def excluir(produto_id):
    conexao = conectar()
    cursor = conexao.cursor()
    try:
        cursor.execute("DELETE FROM produtos WHERE id = %s", (produto_id,))
        conexao.commit()
        return cursor.rowcount
    except Exception:
        conexao.rollback()
        raise
    finally:
        cursor.close()
        conexao.close()
