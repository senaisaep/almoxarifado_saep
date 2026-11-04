from flask import Blueprint, render_template, request, session, redirect
from models.usuarios import autenticar
from db import conectar

auth = Blueprint("auth", __name__)

@auth.route("/", methods=["GET", "POST"])
def login():
    conexao = conectar()

    produtos = conexao.execute("""
        SELECT * FROM 
    """)

    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        login = request.form["login"]
        senha = request.form["senha"]
        usuarios = autenticar(login, senha)
        if usuarios:
            session["usuarios"] = usuarios
            return redirect("/home")
        return render_template("login.html", erro="Usuario ou Senha incorretos")