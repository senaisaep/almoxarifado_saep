from src.models.usuarios import autenticar
from flask import Blueprint, redirect, render_template, request, session

auth = Blueprint('auth', __name__)

@auth.route('/', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        login = request.form["login"]
        senha = request.form["senha"]
        usuario = autenticar(login, senha)
        if usuario:
            session["usuario"] = usuario
            return redirect("/home.html")
        return render_template(
            "login.html",
            erro="Usuario ou senha inválidos"
        )