from flask import Blueprint, jsonify, request

from services.estoque_service import (
    atualizar_produto,
    cadastrar_produto,
    consultar_produto,
    listar_movimentacoes,
    listar_produtos,
    registrar_entrada,
    registrar_saida,
    remover_produto,
)

estoque = Blueprint("estoque", __name__)


@estoque.route("/produtos", methods=["GET"])
def listar_produtos_route():
    return jsonify(listar_produtos()), 200


@estoque.route("/produtos/<int:produto_id>", methods=["GET"])
def consultar_produto_route(produto_id):
    produto = consultar_produto(produto_id)
    if produto is None:
        return jsonify({"mensagem": "Produto não encontrado."}), 404
    return jsonify(produto), 200


@estoque.route("/produtos", methods=["POST"])
def cadastrar_produto_route():
    dados = request.get_json(silent=True) or {}
    if not dados.get("nome"):
        return jsonify({"mensagem": "O nome do produto é obrigatório."}), 400

    novo_produto = cadastrar_produto(dados)
    return jsonify({"mensagem": "Produto cadastrado.", "id": novo_produto}), 201


@estoque.route("/produtos/<int:produto_id>", methods=["PUT"])
def atualizar_produto_route(produto_id):
    dados = request.get_json(silent=True) or {}
    alterado = atualizar_produto(produto_id, dados)
    if alterado == 0:
        return jsonify({"mensagem": "Produto não encontrado ou sem alterações."}), 404
    return jsonify({"mensagem": "Produto atualizado."}), 200


@estoque.route("/produtos/<int:produto_id>", methods=["DELETE"])
def remover_produto_route(produto_id):
    removidos = remover_produto(produto_id)
    if removidos == 0:
        return jsonify({"mensagem": "Produto não encontrado."}), 404
    return jsonify({"mensagem": "Produto removido."}), 200


@estoque.route("/movimentacoes", methods=["GET"])
def listar_movimentacoes_route():
    return jsonify(listar_movimentacoes()), 200


@estoque.route("/movimentacoes/entrada", methods=["POST"])
def registrar_entrada_route():
    dados = request.get_json(silent=True) or {}
    produto_id = dados.get("produto_id")
    quantidade = dados.get("quantidade")

    if not produto_id or not quantidade or int(quantidade) <= 0:
        return jsonify({"mensagem": "Informe produto_id e quantidade maior que zero."}), 400

    registrar_entrada({"produto_id": produto_id, "quantidade": quantidade})
    return jsonify({"mensagem": "Entrada registrada com sucesso."}), 201


@estoque.route("/movimentacoes/saida", methods=["POST"])
def registrar_saida_route():
    dados = request.get_json(silent=True) or {}
    produto_id = dados.get("produto_id")
    quantidade = dados.get("quantidade")
    registrar_hora = dados.get("hora")

    if not produto_id or not quantidade or int(quantidade) <= 0:
        return jsonify({"mensagem": "Informe produto_id e quantidade maior que zero."}), 400

    resultado = registrar_saida({"produto_id": produto_id, "quantidade": quantidade, "hora": registrar_hora})
    if resultado == "produto_nao_encontrado":
        return jsonify({"mensagem": "Produto não encontrado."}), 404
    if resultado == "estoque_insuficiente":
        return jsonify({"mensagem": "Quantidade em estoque insuficiente."}), 400

    return jsonify({"mensagem": "Saída registrada com sucesso."}), 201
