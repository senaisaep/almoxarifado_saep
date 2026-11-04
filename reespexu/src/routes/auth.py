from flask import Blueprint, jsonify, request

from src.services import auth_service

auth = Blueprint("auth", __name__)


@auth.route("/auth/cadastro", methods=["POST"])
def cadastro():
    novo_id = auth_service.cadastrar(request.get_json(silent=True))
    return jsonify({"mensagem": "Usuário cadastrado como operador.", "id": novo_id}), 201


@auth.route("/auth/login", methods=["POST"])
def login():
    return jsonify(auth_service.login(request.get_json(silent=True))), 200
