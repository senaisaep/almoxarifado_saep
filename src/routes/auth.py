from flask import Blueprint, g, jsonify, request

from src.security.decoradores import login_obrigatorio
from src.services import auth_service
from src.utils.validacao import corpo_json

auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.route("/login", methods=["POST"])
def login():
    dados = corpo_json(request)
    return jsonify(auth_service.login(dados.get("email"), dados.get("senha"))), 200


@auth.route("/me", methods=["GET"])
@login_obrigatorio
def me():
    return jsonify(g.usuario), 200


@auth.route("/trocar-senha", methods=["POST"])
@login_obrigatorio
def trocar_senha():
    dados = corpo_json(request)
    auth_service.trocar_senha(
        g.usuario["id"], dados.get("senha_atual"), dados.get("nova_senha")
    )
    return jsonify({"mensagem": "Senha alterada com sucesso."}), 200
