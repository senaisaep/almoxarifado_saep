from flask import Blueprint, jsonify, request
from src.services import produto_service

produtos = Blueprint("produtos", __name__, url_prefix="/api")

@produtos.get("/produtos")
def listar():
    return jsonify(produto_service.listar_produtos()), 200

@produtos.get("/produtos/<int:produto_id>")
def consultar(produto_id):
    try:
        return jsonify(produto_service.obter_produto(produto_id)), 200
    except LookupError as erro:  
        return jsonify({"erro": str(erro)}), 404

@produtos.post("/produtos")
def cadastrar():
    dados = request.get_json(silent=True) or {}
    try:
        novo_id = produto_service.cadastrar_produto(dados)
        return jsonify({"mensagem": "Produto cadastrado.", "id": novo_id}), 201
    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 400

@produtos.put("/produtos/<int:produto_id>")
def atualizar(produto_id):
    dados = request.get_json(silent=True) or {}
    try:
        produto_service.atualizar_produto(produto_id, dados)
        return jsonify({"mensagem": "Produto atualizado."}), 200
    except LookupError as erro:
        return jsonify({"erro": str(erro)}), 404
    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 400

@produtos.delete("/produtos/<int:produto_id>")
def excluir(produto_id):
    try:
        produto_service.excluir_produto(produto_id)
        return jsonify({"mensagem": "Produto excluído."}), 200
    except LookupError as erro:
        return jsonify({"erro": str(erro)}), 404
    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 409
