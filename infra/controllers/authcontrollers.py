from models.usuarios import autenticar
from flask import (Blueprint, request, render_template,render_template_string, session, redirect)

auth = Blueprint("auth",__name__)

@auth.route("/", methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        login = request.form["login"]
        senha = request.form["senha"]
        usuario = autenticar(login,senha)
        if usuario:
            session["AdmAl"]=usuario
            return redirect("/adm")
        if usuario:
            session["OperadorAl"]=usuario
            return redirect("/operar")
        if usuario:
            session["usuario"]=usuario
            return redirect("/home")
        return render_template(
            "login.html",
            erro="Usuário ou senha incorretos"
        )
def listar():
    produtos = produtos.listar()
    return render_template(
        "lista.html", produtos=produtos
    )
##def apagar():
    id_movimentacao =  request.args["id"]
    movimentacao.apagar(id_movimentacao)
    return render_template_string("<h1>Excluído</h1>")