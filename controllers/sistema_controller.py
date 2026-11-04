from flask import Blueprint, render_template, session, abort

sistema = Blueprint("sistema", __name__)

@sistema.route ("/home")
def home():
    return render_template("home.html")

@sistema.route ("/produtos")
def produtos():
    if session["usuarios"]["permissao"] == "produtos":
        return render_template("produtos.html")
    else:
        abort(403)

@sistema.route ("/movimentacoes")
def produtos():
    if session["usuarios"]["permissao"] == "movimentacoes":
        return render_template("movimentacoes.html")
    else:
        abort(403)

