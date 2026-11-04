from src.config.db import conectar


def listar():
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)
    try:
        cursor.execute(
            """SELECT id, produto_id, tipo, quantidade, responsavel, data_hora
               FROM movimentacoes ORDER BY data_hora DESC, id DESC"""
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conexao.close()


def buscar_por_id(movimentacao_id):
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)
    try:
        cursor.execute(
            """SELECT id, produto_id, tipo, quantidade, responsavel, data_hora
               FROM movimentacoes WHERE id = %s""",
            (movimentacao_id,)
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
            """INSERT INTO movimentacoes (produto_id, tipo, quantidade, responsavel, data_hora)
               VALUES (%s, %s, %s, %s, %s)""",
            (
                dados["produto_id"],
                dados["tipo"],
                dados["quantidade"],
                dados["responsavel"],
                dados["data_hora"],
            )
        )
        conexao.commit()
        return buscar_por_id(cursor.lastrowid)
    except Exception:
        conexao.rollback()
        raise
    finally:
        cursor.close()
        conexao.close()
