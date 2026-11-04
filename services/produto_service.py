import math

from repositories import produto_repository


def listar_produtos():
    return produto_repository.listar_produtos()


def buscar_produto(produto_id):
    return produto_repository.buscar_produto(produto_id)


def cadastrar_produto(dados, usuario_id):
    if not isinstance(dados, dict):
        return "Envie os dados do produto em formato JSON.", 400

    nome = dados.get("nome")
    quantidade = dados.get("quantidade_estoque", 0)
    preco = dados.get("preco", 0)
    descricao = dados.get("descricao", "")
    if not isinstance(nome, str) or not nome.strip():
        return "O nome do produto é obrigatório.", 400
    if (
        not isinstance(quantidade, int)
        or isinstance(quantidade, bool)
        or quantidade < 0
        or quantidade > 2147483647
    ):
        return "O estoque deve ser um número inteiro não negativo.", 400
    if (
        not isinstance(preco, (int, float))
        or isinstance(preco, bool)
        or preco < 0
        or preco > 99999999.99
        or not math.isfinite(preco)
    ):
        return "O preço deve ser um número não negativo.", 400
    if len(nome.strip()) > 120:
        return "O nome do produto deve ter no máximo 120 caracteres.", 400
    if not isinstance(descricao, str):
        return "A descrição deve ser um texto.", 400

    produto_id = produto_repository.cadastrar_produto(
        nome.strip(),
        descricao,
        preco,
        quantidade,
        usuario_id,
    )
    return produto_id, 201


def atualizar_produto(produto_id, dados):
    if not isinstance(dados, dict):
        return "Envie os dados do produto em formato JSON.", 400

    nome = dados.get("nome")
    preco = dados.get("preco", 0)
    descricao = dados.get("descricao", "")
    if not isinstance(nome, str) or not nome.strip():
        return "O nome do produto é obrigatório.", 400
    if "quantidade_estoque" in dados:
        return "Altere o saldo por meio de uma movimentação.", 400
    if (
        not isinstance(preco, (int, float))
        or isinstance(preco, bool)
        or preco < 0
        or preco > 99999999.99
        or not math.isfinite(preco)
    ):
        return "O preço deve ser um número não negativo.", 400
    if len(nome.strip()) > 120:
        return "O nome do produto deve ter no máximo 120 caracteres.", 400
    if not isinstance(descricao, str):
        return "A descrição deve ser um texto.", 400

    atualizado = produto_repository.atualizar_produto(
        produto_id,
        nome.strip(),
        descricao,
        preco,
    )

    if not atualizado:
        return "Produto não encontrado.", 404
    return "Produto atualizado.", 200


def remover_produto(produto_id):
    return produto_repository.remover_produto(produto_id)