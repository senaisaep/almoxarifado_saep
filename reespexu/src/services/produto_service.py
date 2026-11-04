# Regras de negócio dos produtos (a rota chama aqui e aqui chamamos o repositório)
from mysql.connector.errors import IntegrityError

from src.config.db import transacao
from src.repositories import movimentacao_repository, produto_repository
from src.utils import validacao
from src.utils.erros import ErroAPI


def listar(args):
    pagina, limite, offset = validacao.paginacao(args)
    nome = args.get("nome", "").strip()
    data_inicio = validacao.data(args.get("data_inicio"), "data_inicio")
    data_fim = validacao.data(args.get("data_fim"), "data_fim", fim_do_dia=True)

    with transacao() as cursor:
        dados, total = produto_repository.listar(
            cursor, nome, data_inicio, data_fim, limite, offset)
    return validacao.montar_pagina(dados, total, pagina, limite)


def consultar(produto_id):
    with transacao() as cursor:
        produto = produto_repository.buscar_por_id(cursor, produto_id)
    if produto is None:
        raise ErroAPI("Produto não encontrado.", 404)
    return produto


def cadastrar(dados, usuario_id):
    dados = validacao.exigir_json(dados)
    nome = validacao.texto(dados.get("nome"), "nome", maximo=120)
    descricao = validacao.texto(dados.get("descricao"), "descricao", obrigatorio=False)
    preco = validacao.preco(dados.get("preco", 0))
    quantidade = validacao.inteiro(dados.get("quantidade_estoque", 0), "quantidade_estoque")

    with transacao() as cursor:
        produto_id = produto_repository.inserir(cursor, nome, descricao, preco, quantidade)
        # Se já nasce com estoque, registramos uma entrada para o histórico ficar completo
        if quantidade > 0:
            movimentacao_repository.inserir(cursor, produto_id, "entrada", quantidade, usuario_id)
    return produto_id


def atualizar(produto_id, dados):
    dados = validacao.exigir_json(dados)
    # Estoque não muda por aqui, senão o histórico de movimentações perde o sentido
    if "quantidade_estoque" in dados:
        raise ErroAPI("O estoque só muda por /movimentacoes/entrada ou /movimentacoes/saida.")

    with transacao() as cursor:
        atual = produto_repository.buscar_por_id(cursor, produto_id)
        if atual is None:
            raise ErroAPI("Produto não encontrado.", 404)

        # Se o campo não veio no JSON, mantém o valor que já estava no banco
        nome = validacao.texto(dados.get("nome", atual["nome"]), "nome", maximo=120)
        descricao = validacao.texto(dados.get("descricao", atual["descricao"]), "descricao", obrigatorio=False)
        preco = validacao.preco(dados.get("preco", atual["preco"]))
        produto_repository.atualizar(cursor, produto_id, nome, descricao, preco)


def remover(produto_id):
    try:
        with transacao() as cursor:
            removidos = produto_repository.remover(cursor, produto_id)
    except IntegrityError:
        # O banco não deixa apagar produto que já tem movimentações
        raise ErroAPI("Este produto possui movimentações e não pode ser removido.", 409)
    if removidos == 0:
        raise ErroAPI("Produto não encontrado.", 404)
