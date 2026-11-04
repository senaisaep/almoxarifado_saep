from flask import Blueprint, g, jsonify, request

from src.services import produto_service
from src.utils.auth import login_obrigatorio, perfil_requerido

produtos = Blueprint("produtos", __name__)


@produtos.route("/produtos", methods=["GET"])
@login_obrigatorio
def listar_produtos():
    return jsonify(produto_service.listar(request.args)), 200


@produtos.route("/produtos/<int:produto_id>", methods=["GET"])
@login_obrigatorio
def consultar_produto(produto_id):
    return jsonify(produto_service.consultar(produto_id)), 200


@produtos.route("/produtos", methods=["POST"])
@login_obrigatorio
def cadastrar_produto():
    novo_id = produto_service.cadastrar(request.get_json(silent=True), g.usuario["id"])
    return jsonify({"mensagem": "Produto cadastrado.", "id": novo_id}), 201


@produtos.route("/produtos/<int:produto_id>", methods=["PUT"])
@login_obrigatorio
def atualizar_produto(produto_id):
    produto_service.atualizar(produto_id, request.get_json(silent=True))
    return jsonify({"mensagem": "Produto atualizado."}), 200


@produtos.route("/produtos/<int:produto_id>", methods=["DELETE"])
@login_obrigatorio
@perfil_requerido("admin")
def remover_produto(produto_id):
    produto_service.remover(produto_id)
    return jsonify({"mensagem": "Produto removido."}), 200
