from src.config.db import transacao
from src.repositories import movimentacao_repository as mov_repo
from src.repositories import produto_repository as produto_repo
from src.utils.erros import ErroApi
from src.utils.validacao import (
    inteiro_nao_negativo,
    paginacao,
    preco_valido,
    resposta_paginada,
    texto_obrigatorio,
    texto_opcional,
)


def listar(args):
    pagina, por_pagina = paginacao(args)
    busca = (args.get("busca") or "").strip()[:120]
    estoque_max = None
    if args.get("estoque_max") not in (None, ""):
        estoque_max = inteiro_nao_negativo(args.get("estoque_max"), "estoque_max")
    with transacao() as cur:
        total = produto_repo.contar(cur, busca, estoque_max)
        dados = produto_repo.listar(
            cur, busca, estoque_max, por_pagina, (pagina - 1) * por_pagina
        )
    return resposta_paginada(dados, total, pagina, por_pagina)


def consultar(produto_id):
    with transacao() as cur:
        produto = produto_repo.buscar_por_id(cur, produto_id)
    if produto is None:
        raise ErroApi("Produto não encontrado.", 404)
    return produto


def cadastrar(dados, usuario_id):
    nome = texto_obrigatorio(dados.get("nome"), "nome", 120)
    descricao = texto_opcional(dados.get("descricao"), "descricao")
    preco = preco_valido(dados.get("preco", 0))
    quantidade = inteiro_nao_negativo(dados.get("quantidade_estoque", 0), "quantidade_estoque")
    with transacao() as cur:
        novo_id = produto_repo.inserir(cur, nome, descricao, preco, quantidade)
        if quantidade > 0:  # estoque inicial também fica rastreado
            mov_repo.inserir(cur, novo_id, "entrada", quantidade, usuario_id)
    return novo_id


def atualizar(produto_id, dados):
    """Saldo NÃO é editável aqui: só muda por entrada/saída (rastreabilidade)."""
    nome = texto_obrigatorio(dados.get("nome"), "nome", 120)
    descricao = texto_opcional(dados.get("descricao"), "descricao")
    preco = preco_valido(dados.get("preco", 0))
    with transacao() as cur:
        if produto_repo.buscar_por_id(cur, produto_id) is None:
            raise ErroApi("Produto não encontrado.", 404)
        produto_repo.atualizar(cur, produto_id, nome, descricao, preco)


def remover(produto_id):
    with transacao() as cur:
        if produto_repo.buscar_por_id(cur, produto_id) is None:
            raise ErroApi("Produto não encontrado.", 404)
        if mov_repo.contar_por_produto(cur, produto_id) > 0:
            raise ErroApi(
                "Produto possui movimentações e não pode ser removido.", 409
            )
        produto_repo.remover(cur, produto_id)
