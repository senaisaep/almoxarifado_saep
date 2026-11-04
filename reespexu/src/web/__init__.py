"""Interface web do almoxarifado (templates + proxy para a API REST).

Telas:
  GET /login     -> tela de login (login.html)
  GET /produtos  -> tela de produtos  (produtos.html, exige token no navegador)

O navegador fala com /api/<caminho>, que repassa tudo para a API REST
(http://127.0.0.1:5000) mantendo o header Authorization — assim não há
problema de CORS e o token continua sendo validado pela API.
"""
import os

import requests
from flask import Blueprint, redirect, render_template, request, url_for

API = os.getenv("API_URL", "http://127.0.0.1:5000")

web = Blueprint("web", __name__,
                template_folder="templates",
                static_folder="static", static_url_path="/web-static")


# ---------------------------- TELAS ----------------------------
@web.route("/app")
def inicio():
    return redirect(url_for("web.tela_login"))


@web.route("/app/login")
def tela_login():
    return render_template("login.html")


@web.route("/app/produtos")
def tela_produtos():
    # A checagem do token é feita no navegador (app.js redireciona sem token)
    return render_template("produtos.html")


# ---------------------------- PROXY ----------------------------
@web.route("/api/<path:caminho>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy(caminho):
    resposta = requests.request(
        request.method, f"{API}/{caminho}",
        json=request.get_json(silent=True),
        params=request.args,
        headers={"Authorization": request.headers.get("Authorization", "")},
        timeout=10)
    try:
        return resposta.json(), resposta.status_code, \
               {"Content-Type": "application/json; charset=utf-8"}
    except ValueError:
        return resposta.text, resposta.status_code
