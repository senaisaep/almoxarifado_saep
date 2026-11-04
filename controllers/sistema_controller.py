from flask import Blueprint, abort, render_template, session

sistema = Blueprint("sistema", __name__)


@sistema.route("/home")
def home():
    print(session)
    return render_template("home.html")


@sistema.route("/produtos")
def produtos():
    usuarios = session.get("usuarios")
    if usuarios and usuarios.get("permissao") == "produtos":
        return render_template("produtos.html")
    abort(403)


@sistema.route("/movimentacoes")
def movimentacoes():  # Nome corrigido aqui
    usuarios = session.get("usuarios")
    if usuarios and usuarios.get("permissao") == "movimentacoes":
        return render_template("movimentacoes.html")
    abort(403)