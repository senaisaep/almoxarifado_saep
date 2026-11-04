from flask import Flask, jsonify, render_template, redirect, session
from src.routes.estoque import estoque
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__, template_folder="../template")

app.secret_key = os.getenv("SECRET_KEY", "chave-local")

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax"
)

app.register_blueprint(estoque)


@app.route("/")
def inicio():
    if "usuario_id" in session:
        return redirect("/painel")
    return redirect("/login")


@app.route("/login")
def pagina_login():
    if "usuario_id" in session:
        return redirect("/painel")
    return render_template("login.html")


@app.route("/painel")
def painel():
    if "usuario_id" not in session:
        return redirect("/login")
    return render_template("produtos.html")


@app.route("/novo-produto")
def novo_produto():
    if "usuario_id" not in session:
        return redirect("/login")
    return render_template("cadastrar_produto.html")


@app.route("/pagina-movimentacoes")
def pagina_movimentacoes():
    if "usuario_id" not in session:
        return redirect("/login")
    return render_template("movimentacoes.html")


@app.route("/pagina-usuarios")
def pagina_usuarios():
    if "usuario_id" not in session:
        return redirect("/login")

    if session.get("tipo") != "administrador":
        return redirect("/painel")

    return render_template("usuarios.html")


@app.errorhandler(404)
def pagina_nao_encontrada(e):
    return jsonify({"erro": "Página não encontrada."}), 404


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=int(os.getenv("PORT", "5000")),
        debug=True
    )
