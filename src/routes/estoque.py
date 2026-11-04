from flask import Blueprint
from repositories.Estoque_repository import listagem_produtos, consulta_produto, cadastro_produto, atualizacao_produto, remocao_produto, listagem_movimentacao, registro_entrada

estoque = Blueprint("estoque", __name__)

# Lógica de negócio e comandos SQL concentrados neste arquivo de rotas.

@estoque.route("/produtos", methods=["GET"])
def listar_produtos(): 
    return listagem_produtos()

@estoque.route("/produtos/<int:produto_id>", methods=["GET"])
def consultar_produto(produto_id): 
    return consulta_produto(produto_id)

@estoque.route("/produtos", methods=["POST"])
def cadastrar_produto(): 
    return cadastro_produto()

@estoque.route("/produtos/<int:produto_id>", methods=["PUT"])
def atualizar_produto(produto_id): 
    return atualizacao_produto(produto_id)

@estoque.route("/produtos/<int:produto_id>", methods=["DELETE"])
def remover_produto(produto_id): 
    return remocao_produto(produto_id)

@estoque.route("/movimentacoes", methods=["GET"])
def listar_movimentacoes():
    return listagem_movimentacao()

@estoque.route("/movimentacoes/entrada", methods=["POST"])
def registrar_entrada():
    return registro_entrada()