from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash
)

from services import produto_service

produto_bp = Blueprint("produto", __name__, url_prefix="/produtos")


# Listar produtos
@produto_bp.route("/", methods=["GET"])
def listar():

    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    produtos = produto_service.listar_produtos()

    return render_template(
        "produtos.html",
        produtos=produtos
    )


# Cadastrar produto
@produto_bp.route("/cadastrar", methods=["POST"])
def cadastrar():

    if "usuario_id" not in session:
        return redirect(url_for("auth.login"))

    usuario = {
        "id": session["usuario_id"],
        "nome": session["nome"],
        "perfil": session["perfil"]
    }

    try:
        nome = request.form.get("nome", "").strip()
        descricao = request.form.get("descricao", "").strip()
        quantidade = int(request.form.get("quantidade", 0))
        preco = float(request.form.get("preco", 0))

        produto_service.inserir_produto(
            usuario,
            nome,
            descricao,
            quantidade,
            preco
        )

        flash("Produto cadastrado com sucesso!", "success")

    except (ValueError, PermissionError) as erro:
        flash(str(erro), "error")

    return redirect(url_for("produto.listar"))