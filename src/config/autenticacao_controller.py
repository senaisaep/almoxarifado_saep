from models.ususario import autenticacao
from flask import (Blueprint, request, render_template, session, redirect)

autentic = Blueprint("autentic", __name__)
@autentic.route("/", methods=["GET", "POST"])
def loguin():
    if request.method == "GET":
        return render_template("loguin.html")
    if request.method == "POST":
        loguin = request.form["loguin"]
        senha = request.form["senha"]
        usuario = autenticacao(loguin, senha)
        if usuario:
            session["usuario"] = usuario
            return redirect("/home")
        return render_template(
            "loguin.html",
            erro = "Usuario ou senha estao incorretos"
        )