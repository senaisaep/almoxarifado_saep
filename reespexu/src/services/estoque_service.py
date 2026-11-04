# Regras de negócio das movimentações de estoque (entrada e saída)
from src.config.db import transacao
from src.repositories import movimentacao_repository, produto_repository
from src.utils import validacao
from src.utils.erros import ErroAPI


def _registrar(tipo, dados, usuario_id):
    dados = validacao.exigir_json(dados)
    produto_id = validacao.inteiro(dados.get("produto_id"), "produto_id", minimo=1)
    quantidade = validacao.inteiro(dados.get("quantidade"), "quantidade", minimo=1)

    # Tudo na mesma transação: ou grava a movimentação E o estoque, ou não grava nada
    with transacao() as cursor:
        # Trava o produto enquanto confere o saldo, para duas saídas ao mesmo tempo
        # não deixarem o estoque negativo
        produto = produto_repository.buscar_por_id(cursor, produto_id, travar=True)
        if produto is None:
            raise ErroAPI("Produto não encontrado.", 404)

        saldo = produto["quantidade_estoque"]
        if tipo == "saida" and saldo < quantidade:
            raise ErroAPI(
                f"Saída não permitida: estoque insuficiente. Disponível: {saldo}. Solicitado: {quantidade}.",
                409, {"disponivel": saldo, "solicitado": quantidade})

        # Entrada soma no estoque, saída subtrai
        delta = quantidade if tipo == "entrada" else -quantidade
        movimentacao_id = movimentacao_repository.inserir(cursor, produto_id, tipo, quantidade, usuario_id)
        produto_repository.alterar_estoque(cursor, produto_id, delta)

    return {"movimentacao_id": movimentacao_id, "produto_id": produto_id, "estoque_atual": saldo + delta}


def registrar_entrada(dados, usuario_id):
    return _registrar("entrada", dados, usuario_id)


def registrar_saida(dados, usuario_id):
    return _registrar("saida", dados, usuario_id)


def listar_movimentacoes(args):
    pagina, limite, offset = validacao.paginacao(args)

    tipo = args.get("tipo")
    if tipo and tipo not in ("entrada", "saida"):
        raise ErroAPI("tipo inválido. Use 'entrada' ou 'saida'.")
    produto_id = validacao.inteiro(args["produto_id"], "produto_id", 1) if args.get("produto_id") else None

    with transacao() as cursor:
        dados, total = movimentacao_repository.listar(cursor, produto_id, tipo, limite, offset)
    return validacao.montar_pagina(dados, total, pagina, limite)
