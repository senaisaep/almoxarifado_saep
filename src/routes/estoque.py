from flask import Blueprint, request, jsonify

from src.services.estoque_service import (
    listar_produtos as buscar_produtos,
    consultar_produto as buscar_produto_por_id,
    registrar_saida
)

estoque = Blueprint("estoque", __name__)


@estoque.route("/produtos", methods=["GET"])
def listar_produtos():
    dados = buscar_produtos()
    return jsonify(dados), 200


@estoque.route("/produtos/<int:produto_id>", methods=["GET"])
def consultar_produto(produto_id):
    produto = buscar_produto_por_id(produto_id)

    if produto is None:
        return jsonify({"mensagem": "Produto não encontrado."}), 404

    return jsonify(produto), 200


@estoque.route("/produtos/<int:produto_id>/saida", methods=["POST"])
def saida_produto(produto_id):
    dados = request.get_json(silent=True) or {}

    try:
        quantidade = int(dados.get("quantidade", 0))
    except (ValueError, TypeError):
        return jsonify({"mensagem": "Quantidade inválida."}), 400

    resultado = registrar_saida(produto_id, quantidade)

    if resultado == "nao_encontrado":
        return jsonify({"mensagem": "Produto não encontrado."}), 404

    if resultado == "estoque_insuficiente":
        return jsonify({"mensagem": "Quantidade inválida ou estoque insuficiente."}), 400

    return jsonify({"mensagem": "Saída registrada com sucesso."}), 200