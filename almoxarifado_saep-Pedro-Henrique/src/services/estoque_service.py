from src.config.db import conectar

class EstoqueErro(Exception):
    pass

def registrar_movimentacao(produto_id, quantidade, tipo, usuario_id):
    if tipo not in ("entrada", "saida"):
        raise EstoqueErro("Tipo de movimentação inválido.")
    try:
        quantidade = int(quantidade)
    except (TypeError, ValueError):
        raise EstoqueErro("Informe uma quantidade inteira maior que zero.")
    if quantidade <= 0:
        raise EstoqueErro("Informe uma quantidade maior que zero.")

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)
    try:
        conexao.start_transaction()
        cursor.execute(
            "SELECT id, nome, quantidade_estoque FROM produtos WHERE id=%s FOR UPDATE",
            (produto_id,)
        )
        produto = cursor.fetchone()
        if not produto:
            raise EstoqueErro("Produto não encontrado.")

        saldo = int(produto["quantidade_estoque"])
        if tipo == "saida" and quantidade > saldo:
            raise EstoqueErro(
                f"Saída não permitida: estoque insuficiente. Disponível: {saldo}. Solicitado: {quantidade}."
            )

        operador = 1 if tipo == "entrada" else -1
        cursor.execute(
            "UPDATE produtos SET quantidade_estoque = quantidade_estoque + %s WHERE id=%s",
            (operador * quantidade, produto_id)
        )
        cursor.execute(
            """INSERT INTO movimentacoes (produto_id, tipo, quantidade, usuario_id, data_hora)
               VALUES (%s, %s, %s, %s, NOW())""",
            (produto_id, tipo, quantidade, usuario_id)
        )
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        cursor.close()
        conexao.close()
