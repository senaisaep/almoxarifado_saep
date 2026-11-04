from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from src.services.auth_service import autenticar

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        usuario = autenticar(email, senha)
        if usuario:
            session.clear()
            session["usuario"] = usuario
            flash(f"Bem-vindo(a), {usuario['nome']}!", "sucesso")
            return redirect(url_for("produtos.dashboard"))
        flash("E-mail ou senha inválidos. Confira os dados e tente novamente.", "erro")
    return render_template("login.html")

@auth.route("/sair", methods=["POST"])
def sair():
    session.clear()
    flash("Você saiu do sistema.", "sucesso")
    return redirect(url_for("auth.login"))
