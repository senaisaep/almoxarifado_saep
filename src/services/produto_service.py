from decimal import Decimal, InvalidOperation
from src.repositories import produto_repository

def validar_produto(dados):
    nome = str(dados.get("nome", "")).strip()
    descricao = str(dados.get("descricao", "")).strip()

    if not nome:
        raise ValueError("Informe o nome do produto.")
    if len(nome) > 120:
        raise ValueError("O nome deve ter no máximo 120 caracteres.")

    try:
        preco = Decimal(str(dados.get("preco", "0")))
    except (InvalidOperation, TypeError):
        raise ValueError("Informe um preço válido.")

    try:
        quantidade = int(dados.get("quantidade_estoque", 0))
    except (ValueError, TypeError):
        raise ValueError("A quantidade deve ser um número inteiro.")

    if preco < 0:
        raise ValueError("O preço não pode ser negativo.")
    if quantidade < 0:
        raise ValueError("A quantidade não pode ser negativa.")

    return {
        "nome": nome,
        "descricao": descricao,
        "preco": preco,
        "quantidade_estoque": quantidade
    }

def listar_produtos():
    return produto_repository.listar()

def obter_produto(produto_id):
    produto = produto_repository.buscar_por_id(produto_id)
    if produto is None:
        raise LookupError("Produto não encontrado.")
    return produto

def cadastrar_produto(dados):
    produto = validar_produto(dados)
    return produto_repository.criar(produto)

def atualizar_produto(produto_id, dados):
    obter_produto(produto_id)
    produto = validar_produto(dados)
    produto_repository.atualizar(produto_id, produto)

def excluir_produto(produto_id):
    obter_produto(produto_id)
    try:
        produto_repository.excluir(produto_id)
    except Exception as erro:
        if getattr(erro, "errno", None) == 1451:
            raise ValueError("Este produto possui movimentações vinculadas e não pode ser excluído.")
        raise
