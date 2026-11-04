from flask import Blueprint, request, jsonify, session
from services import auth_service

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/cadastro", methods=["POST"])
def cadastro():
    dados = request.get_json()

    if not dados:
        return jsonify({"erro": "Envie os dados do cadastro."}), 400

    nome = dados.get("nome")
    email = dados.get("email")
    senha = dados.get("senha")

    sucesso, mensagem = auth_service.cadastrar(
        nome, email, senha
    )

    if not sucesso:
        return jsonify({"erro": mensagem}), 400

    return jsonify({"mensagem": mensagem}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    dados = request.get_json()

    if not dados:
        return jsonify({"erro": "Envie email e senha."}), 400

    email = dados.get("email")
    senha = dados.get("senha")

    usuario = auth_service.fazer_login(email, senha)

    if not usuario:
        return jsonify({"erro": "Email ou senha incorretos."}), 401

    session["usuario_id"] = usuario["id"]
    session["nome"] = usuario["nome"]
    session["perfil"] = usuario["perfil"]

    return jsonify({
        "mensagem": "Login realizado com sucesso.",
        "usuario": {
            "id": usuario["id"],
            "nome": usuario["nome"],
            "email": usuario["email"],
            "perfil": usuario["perfil"]
        }
    })


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()

    return jsonify({
        "mensagem": "Logout realizado com sucesso."
    })


@auth_bp.route("/perfil", methods=["GET"])
def perfil():
    if "usuario_id" not in session:
        return jsonify({"erro": "Faça login primeiro."}), 401

    return jsonify({
        "id": session["usuario_id"],
        "nome": session["nome"],
        "perfil": session["perfil"]
    })