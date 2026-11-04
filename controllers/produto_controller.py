from flask import Blueprint, jsonify, request, session

from services.auth_service import requer_perfil
from services import produto_service


produto_bp = Blueprint("produtos", __name__)


@produto_bp.route("/produtos", methods=["GET"])
@requer_perfil()
def listar_produtos():
    return jsonify(produto_service.listar_produtos()), 200


@produto_bp.route("/produtos/<int:produto_id>", methods=["GET"])
@requer_perfil()
def consultar_produto(produto_id):
    produto = produto_service.buscar_produto(produto_id)
    if produto is None:
        return jsonify({"mensagem": "Produto não encontrado."}), 404
    return jsonify(produto), 200


@produto_bp.route("/produtos", methods=["POST"])
@requer_perfil("Administrador")
def cadastrar_produto():
    resultado, status = produto_service.cadastrar_produto(
        request.get_json(silent=True) or {},
        session["usuario_id"],
    )
    if status != 201:
        return jsonify({"mensagem": resultado}), status
    return jsonify({"mensagem": "Produto cadastrado.", "id": resultado}), status


@produto_bp.route("/produtos/<int:produto_id>", methods=["PUT"])
@requer_perfil("Administrador")
def atualizar_produto(produto_id):
    mensagem, status = produto_service.atualizar_produto(
        produto_id,
        request.get_json(silent=True) or {},
    )
    return jsonify({"mensagem": mensagem}), status


@produto_bp.route("/produtos/<int:produto_id>", methods=["DELETE"])
@requer_perfil("Administrador")
def remover_produto(produto_id):
    mensagem, status = produto_service.remover_produto(produto_id)
    return jsonify({"mensagem": mensagem}), status