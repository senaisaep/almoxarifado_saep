from flask import Blueprint, request, jsonify, session

from services import estoque_service
from repositories import produto_repository
from repositories import movimentacao_repository

from routes.permissoes import (
    login_obrigatorio,
    administrador_obrigatorio
)

estoque_bp = Blueprint("estoque", __name__)

# CADASTRAR PRODUTO
@estoque_bp.route("/produtos", methods=["POST"])
@login_obrigatorio
def cadastrar_produto():
    dados = request.get_json(silent=True) or {}

    try:
        nome = dados.get("nome")
        descricao = dados.get("descricao", "")
        quantidade = int(dados.get("quantidade_estoque", 0))
        preco = float(dados.get("preco", 0))
    except (ValueError, TypeError):
        return jsonify({"erro": "Quantidade ou preço inválido."}), 400

    sucesso, mensagem = estoque_service.cadastrar_produto(
        nome, descricao, quantidade, preco
    )

    if not sucesso:
        return jsonify({"erro": mensagem}), 400

    return jsonify({"mensagem": mensagem}), 201

