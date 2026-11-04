from flask import (Blueprint, render_template, session, abort)
sistema = Blueprint("sistema", __name__)
@sistema.route("/home")
def home():
    return render_template("home.html")

@sistema.route("/produtos")
def produtos():
    if session["usuario"]["permisao"] == "produtos":
        return render_template("produtos.html")
    else:
        abort(403)

@sistema.route("/estoque")
def relatrio():
    if session["usuario"]["permissao"] == "estoque":
        return render_template("relatorios.html")
    else:
        abort(403)

@sistema.route("/catalogo")
def relatorio():
    if session["usuario"]["permisao"] == "catalogo":
        return render_template("catalogo.html")
    else:
        abort(403)