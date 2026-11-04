from flask import Blueprint, g, jsonify, request

from src.security.decoradores import login_obrigatorio, requer_perfil
from src.security.perfis import ADMIN, ALMOXARIFE
from src.services import produto_service
from src.utils.validacao import corpo_json

produtos = Blueprint("produtos", __name__, url_prefix="/produtos")


@produtos.route("", methods=["GET"])
@login_obrigatorio
def listar():
    return jsonify(produto_service.listar(request.args)), 200


@produtos.route("/<int:produto_id>", methods=["GET"])
@login_obrigatorio
def consultar(produto_id):
    return jsonify(produto_service.consultar(produto_id)), 200


@produtos.route("", methods=["POST"])
@requer_perfil(ADMIN, ALMOXARIFE)
def cadastrar():
    novo_id = produto_service.cadastrar(corpo_json(request), g.usuario["id"])
    return jsonify({"mensagem": "Produto cadastrado.", "id": novo_id}), 201


@produtos.route("/<int:produto_id>", methods=["PUT"])
@requer_perfil(ADMIN, ALMOXARIFE)
def atualizar(produto_id):
    produto_service.atualizar(produto_id, corpo_json(request))
    return jsonify({"mensagem": "Produto atualizado."}), 200


@produtos.route("/<int:produto_id>", methods=["DELETE"])
@requer_perfil(ADMIN)
def remover(produto_id):
    produto_service.remover(produto_id)
    return jsonify({"mensagem": "Produto removido."}), 200
