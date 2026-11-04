from src.config.db import transacao
from src.repositories import movimentacao_repository as mov_repo
from src.repositories import produto_repository as produto_repo
from src.utils.erros import ErroApi, EstoqueInsuficiente
from src.utils.validacao import (
    data_iso,
    inteiro_positivo,
    paginacao,
    resposta_paginada,
)


def _movimentar(tipo, usuario_id, produto_id, quantidade):
    produto_id = inteiro_positivo(produto_id, "produto_id")
    quantidade = inteiro_positivo(quantidade, "quantidade")

    # Tudo numa única transação: ou grava movimentação + novo saldo, ou nada.
    # Qualquer exceção (inclusive EstoqueInsuficiente) dispara rollback.
    with transacao() as cur:
        produto = produto_repo.buscar_para_atualizar(cur, produto_id)  # trava a linha
        if produto is None:
            raise ErroApi("Produto não encontrado.", 404)

        saldo = produto["quantidade_estoque"]
        if tipo == "saida":
            if quantidade > saldo:
                raise EstoqueInsuficiente(saldo, quantidade)
            novo_saldo = saldo - quantidade
        else:
            novo_saldo = saldo + quantidade

        produto_repo.atualizar_saldo(cur, produto_id, novo_saldo)
        mov_id = mov_repo.inserir(cur, produto_id, tipo, quantidade, usuario_id)
        movimentacao = mov_repo.buscar_por_id(cur, mov_id)  # traz data_hora e responsável

    return {"movimentacao": movimentacao, "saldo_anterior": saldo, "saldo_atual": novo_saldo}


def registrar_entrada(usuario_id, produto_id, quantidade):
    return _movimentar("entrada", usuario_id, produto_id, quantidade)


def registrar_saida(usuario_id, produto_id, quantidade):
    return _movimentar("saida", usuario_id, produto_id, quantidade)


def listar_movimentacoes(args):
    pagina, por_pagina = paginacao(args)
    tipo = args.get("tipo")
    if tipo not in (None, "", "entrada", "saida"):
        raise ErroApi("tipo deve ser 'entrada' ou 'saida'.", 400)
    filtros = {
        "tipo": tipo or None,
        "produto_id": (
            inteiro_positivo(args["produto_id"], "produto_id")
            if args.get("produto_id") else None
        ),
        "data_inicio": data_iso(args.get("data_inicio"), "data_inicio"),
        "data_fim": data_iso(args.get("data_fim"), "data_fim"),
    }
    with transacao() as cur:
        total = mov_repo.contar(cur, filtros)
        dados = mov_repo.listar(cur, filtros, por_pagina, (pagina - 1) * por_pagina)
    return resposta_paginada(dados, total, pagina, por_pagina)
