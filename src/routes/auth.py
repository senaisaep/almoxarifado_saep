from flask import Blueprint, request, session, render_template, redirect
from src.config.db import conectar

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():

    # Abre a tela de login
    if request.method == "GET":
        return render_template("login.html")

    # Recebe os dados digitados
    email = request.form.get("email")
    senha = request.form.get("senha")

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, nome, email, senha, perfil
        FROM usuarios
        WHERE email = %s AND senha = %s
    """, (email, senha))

    usuario = cursor.fetchone()

    cursor.close()
    conexao.close()

    # Verifica se o usuário existe
    if usuario is None:
        return render_template(
            "login.html",
            erro="Email ou senha incorretos."
        )

    # Salva os dados na sessão
    session["usuario_id"] = usuario["id"]
    session["nome"] = usuario["nome"]
    session["perfil"] = usuario["perfil"]

    return redirect("/produtos")


@auth.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect("/login")
