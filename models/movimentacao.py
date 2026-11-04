
from src.config.db import conectar


def registrar(produto_id, usuario_id, tipo, quantidade):

    if tipo not in ("entrada", "saida"):
        return False, "Tipo de movimentação inválido."

    if quantidade <= 0:
        return False, "A quantidade deve ser maior que zero."

    con = conectar()
    cur = con.cursor(dictionary=True)

    try:
        con.start_transaction()

        cur.execute("""
            SELECT quantidade_estoque
            FROM produtos
            WHERE id = %s
            FOR UPDATE
        """, (produto_id,))

        produto = cur.fetchone()

        if not produto:
            con.rollback()
            return False, "Produto não encontrado."

        saldo = produto["quantidade_estoque"]

        if tipo == "saida" and quantidade > saldo:
            con.rollback()
            return False, (
                f"Saída não permitida: estoque insuficiente. "
                f"Disponível: {saldo}. Solicitado: {quantidade}."
            )

        novo_saldo = (
            saldo + quantidade if tipo == "entrada"
            else saldo - quantidade
        )

        cur.execute("""
            UPDATE produtos
            SET quantidade_estoque = %s
            WHERE id = %s
        """, (novo_saldo, produto_id))

        cur.execute("""
            INSERT INTO movimentacoes
            (produto_id, usuario_id, tipo, quantidade)
            VALUES (%s, %s, %s, %s)
        """, (produto_id, usuario_id, tipo, quantidade))

        con.commit()
        return True, "Movimentação registrada com sucesso."

    except Exception:
        con.rollback()
        raise

    finally:
        cur.close()
        con.close()


def listar():
    con = conectar()
    cur = con.cursor(dictionary=True)

    cur.execute("""
        SELECT
            m.id,
            p.nome AS produto,
            u.nome AS responsavel,
            m.tipo,
            m.quantidade,
            m.data_hora
        FROM movimentacoes m
        INNER JOIN produtos p ON p.id = m.produto_id
        INNER JOIN usuarios u ON u.id = m.usuario_id
        ORDER BY m.id DESC
    """)

    dados = cur.fetchall()
    cur.close()
    con.close()

    return dados