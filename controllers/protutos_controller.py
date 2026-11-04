from flask import Blueprint, request, redirect, url_for, render_template, session

produtos_bp = Blueprint("produtos", __name__)

@produtos_bp.route("/produtos", methods=["GET"])
def produtos_route():
    return render_template("produtos.html")

@produtos_bp.route("/produtos", methods=["POST"])
def cadastrar_produto():
    nome = request.form.get("nome")

    if not nome:
        return render_template("produtos.html", mensagem="O nome do produto é obrigatório."), 400

    return redirect(url_for("produtos.produtos_route"))