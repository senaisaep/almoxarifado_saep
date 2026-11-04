from flask import Blueprint, render_template, request, redirect, session, url_for

from services.auth_service import autenticar

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/", methods=["GET"])
def login():
    return render_template("login.html")


@auth_bp.route("/login", methods=["POST"])
def realizar_login():

    login = request.form.get("login", "").strip()
    senha = request.form.get("senha", "")

    usuario = autenticar(login, senha)

    if usuario is None:
        return render_template(
            "login.html",
            erro="Login ou senha inválidos"
        )

    session.clear()

    session["usuario_id"] = usuario["id"]
    session["nome"] = usuario["nome"]
    session["perfil"] = usuario["perfil"]

    return redirect(url_for("produto.listar"))


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))