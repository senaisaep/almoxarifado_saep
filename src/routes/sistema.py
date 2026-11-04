from functools import wraps

from flask import Blueprint, redirect, render_template, request, session, url_for

from controllers.sistema_controllers import (
    autenticar_usuario,
    logout,
    possui_permissao,
    usuario_logado,
)
from services.estoque_service import cadastrar_produto, listar_produtos, registrar_saida

sistema = Blueprint("sistema", __name__)


def login_obrigatorio(*permissoes):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            if not usuario_logado():
                return redirect(url_for("sistema.login"))
            if permissoes and not possui_permissao(*permissoes):
                return "Acesso negado.", 403
            return view_func(*args, **kwargs)

        return wrapper

    return decorator


@sistema.route("/", methods=["GET"])
def inicio():
    if usuario_logado():
        return redirect(url_for("sistema.home"))
    return redirect(url_for("sistema.login"))


@sistema.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        senha = request.form.get("senha", "")

        if autenticar_usuario(usuario, senha):
            return redirect(url_for("sistema.home"))

        return render_template("login.html", erro="Usuário ou senha inválidos."), 401

    return render_template("login.html")


@sistema.route("/logout")
def sair():
    logout()
    return redirect(url_for("sistema.login"))


@sistema.route("/home")
@login_obrigatorio()
def home():
    return render_template("home.html", usuario=session.get("usuario"))


@sistema.route("/painel/produtos")
@login_obrigatorio("estoque")
def painel_produtos():
    produtos = listar_produtos()
    return render_template("painel_produtos.html", produtos=produtos)


@sistema.route("/painel/relatorios")
@login_obrigatorio("relatorios")
def painel_relatorios():
    return render_template("painel_relatorios.html")


@sistema.route("/registrar", methods=["GET", "POST"])
@login_obrigatorio("estoque")
def registrar_produto():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        descricao = request.form.get("descricao", "").strip()
        preco = request.form.get("preco", 0)
        quantidade = request.form.get("quantidade_estoque", 0)

        if not nome:
            return "Nome do produto é obrigatório.", 400

        produto = {
            "nome": nome,
            "descricao": descricao,
            "preco": float(preco or 0),
            "quantidade_estoque": int(quantidade or 0),
        }
        if cadastrar_produto(produto) is None:
            return "Não foi possível cadastrar o produto no momento.", 500
        return redirect(url_for("sistema.painel_produtos"))

    return render_template("registrar_produto.html")


@sistema.route("/retirar", methods=["GET", "POST"])
@login_obrigatorio("estoque")
def retirar_produto():
    if request.method == "POST":
        produto_id = request.form.get("produto_id")
        quantidade = request.form.get("quantidade")

        if not produto_id or not quantidade:
            return "Informe produto_id e quantidade.", 400

        resultado = registrar_saida(
            {
                "produto_id": int(produto_id),
                "quantidade": int(quantidade),
                "hora": False,
            }
        )

        if resultado == "produto_nao_encontrado":
            return "Produto não encontrado.", 404
        if resultado == "estoque_insuficiente":
            return "Quantidade em estoque insuficiente.", 400
        if resultado == "erro_bd":
            return "Não foi possível registrar a saída no momento.", 500

        return redirect(url_for("sistema.painel_produtos"))

    produtos = listar_produtos()
    return render_template("retirar_produto.html", produtos=produtos)


@sistema.route("/lista_produtos")
@login_obrigatorio("estoque")
def lista_produtos():
    produtos = listar_produtos()
    return render_template("lista_produtos.html", produtos=produtos)
