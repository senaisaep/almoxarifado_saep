import sqlite3

from flask import Blueprint, jsonify, redirect, render_template, request, session
from werkzeug.security import generate_password_hash

from models.usuario import PERFIS
from repositories.usuario_repository import criar_usuario
from services.auth_service import autenticar_usuario, requer_perfil


auth_bp = Blueprint("auth", __name__)


def _iniciar_sessao(usuario_id, nome, perfil):
    session.clear()
    session["usuario_id"] = usuario_id
    session["nome"] = nome
    session["perfil"] = perfil


@auth_bp.route("/login", methods=["POST"])
def realizar_login():
    login = request.form.get("login", "").strip()
    senha = request.form.get("senha", "")
    if not login or not senha:
        return render_template("login.html", erro="Informe login e senha."), 400

    usuario = autenticar_usuario(login, senha)
    if usuario is None:
        return render_template("login.html", erro="Login ou senha inválidos."), 401

    _iniciar_sessao(usuario["id"], usuario["nome"], usuario["perfil"])
    return redirect("/estoque")


@auth_bp.route("/logout", methods=["POST"])
def realizar_logout():
    session.clear()
    return jsonify({"mensagem": "Sessão encerrada."}), 200


@auth_bp.route("/usuarios", methods=["POST"])
@requer_perfil("Administrador")
def cadastrar_usuario():
    dados = request.get_json(silent=True) or {}
    if not isinstance(dados, dict):
        return jsonify({"mensagem": "Envie os dados do usuário em formato JSON."}), 400

    nome = dados.get("nome")
    login = dados.get("login")
    senha = dados.get("senha")
    perfil = dados.get("perfil")

    if not all(isinstance(valor, str) and valor.strip() for valor in (
        nome, login, senha, perfil
    )):
        return jsonify({"mensagem": "Informe nome, login, senha e perfil."}), 400
    if perfil not in PERFIS:
        return jsonify({"mensagem": "Perfil inválido."}), 400
    if len(senha) < 8:
        return jsonify({"mensagem": "A senha deve ter pelo menos 8 caracteres."}), 400
    if len(nome) > 120 or len(login) > 100:
        return jsonify({"mensagem": "Nome ou login excede o limite permitido."}), 400

    try:
        usuario_id = criar_usuario(
            nome.strip(),
            login.strip(),
            generate_password_hash(senha),
            perfil,
        )
    except sqlite3.IntegrityError:
        return jsonify({"mensagem": "Esse login já está cadastrado."}), 409
    return jsonify({"mensagem": "Usuário cadastrado.", "id": usuario_id}), 201


@auth_bp.route("/login", methods=["GET"])
def exibir_login():
    return render_template("login.html")
