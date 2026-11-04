from flask import (Blueprint, render_template, session, abort)

sistema = Blueprint("sistema", __name__)

@sistema.rout("login")
def login():
    return render_template("login.htm")

@sistema.route("/sistema")
def sistema():
    if session["usuarios"]["permissao"] == "sistema":
        return render_template("sistema.html")
    else:
        abort(403)

sistema =Blueprint("sistema", __name__)

@sistema.route("/almoxarifado")
def almoxarifado():
    if session["usuario"]["permissao"] == "almoxarifado":
        return render_template("almoxarifado.html")
    else:
        abort(403)