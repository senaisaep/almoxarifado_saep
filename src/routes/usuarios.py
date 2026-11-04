from flask import Blueprint, g, jsonify, request

from src.security.decoradores import requer_perfil
from src.security.perfis import ADMIN
from src.services import usuario_service
from src.utils.validacao import corpo_json

usuarios = Blueprint("usuarios", __name__, url_prefix="/usuarios")


@usuarios.route("", methods=["GET"])
@requer_perfil(ADMIN)
def listar():
    return jsonify(usuario_service.listar()), 200


@usuarios.route("/<int:usuario_id>", methods=["GET"])
@requer_perfil(ADMIN)
def consultar(usuario_id):
    return jsonify(usuario_service.consultar(usuario_id)), 200


@usuarios.route("", methods=["POST"])
@requer_perfil(ADMIN)
def criar():
    novo_id = usuario_service.criar(corpo_json(request))
    return jsonify({"mensagem": "Usuário cadastrado.", "id": novo_id}), 201


@usuarios.route("/<int:usuario_id>", methods=["PUT"])
@requer_perfil(ADMIN)
def atualizar(usuario_id):
    usuario_service.atualizar(usuario_id, corpo_json(request), g.usuario["id"])
    return jsonify({"mensagem": "Usuário atualizado."}), 200


@usuarios.route("/<int:usuario_id>/senha", methods=["PUT"])
@requer_perfil(ADMIN)
def redefinir_senha(usuario_id):
    usuario_service.redefinir_senha(usuario_id, corpo_json(request).get("nova_senha"))
    return jsonify({"mensagem": "Senha redefinida."}), 200


@usuarios.route("/<int:usuario_id>", methods=["DELETE"])
@requer_perfil(ADMIN)
def desativar(usuario_id):
    usuario_service.desativar(usuario_id, g.usuario["id"])
    return jsonify({"mensagem": "Usuário desativado."}), 200
