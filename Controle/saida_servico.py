from Controle import produto_repositorio


class ProdutoNaoEncontrado(Exception):
    pass


class EstoqueInsuficiente(Exception):
    pass


def registrar_saida(cursor, produto_id, quantidade, usuario):
    saldo = produto_repositorio.buscar_saldo(cursor, produto_id)
    if saldo is None:
        raise ProdutoNaoEncontrado
    if saldo < quantidade:
        raise EstoqueInsuficiente
    produto_repositorio.atualizar_saldo(cursor, produto_id, quantidade)
    produto_repositorio.registrar_saida(cursor, produto_id, quantidade, usuario)
