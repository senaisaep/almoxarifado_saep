from flask import Blueprint, render_template, session, abort

sistema = Blueprint("sistema", __name__)

@sistema.route("/home")
def home():
    return render_template("home.html")

@sistema.route("/adm")
def adm():
    if session["usuario"]["permissao"] == "adm":
        return render_template("adm.html")
    else:
        abort(403)

@sistema.route("/operar")
def operador():
    if session["usuario"]["permissao"] == "operar":
        return render_template("operar.html")
    else:
        abort(403)