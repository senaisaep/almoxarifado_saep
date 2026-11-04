from flask import Blueprint, request, jsonify, session, render_template, redirect

from src.services.estoque_service import (
    listar_produtos,
    buscar_produto,
    cadastrar_produto,
    atualizar_produto,
    excluir_produto,
    movimentar_estoque,
    listar_movimentacoes
)

estoque = Blueprint("estoque", __name__)


def logado():
    return "usuario_id" in session


def administrador():
    return session.get("perfil") == "administrador"


@estoque.route("/produtos", methods=["GET"])
def produtos():
    if not logado():
        return redirect("/login")

    nome = request.args.get("nome", "")
    pagina = request.args.get("pagina", 1, type=int)

    if pagina < 1:
        pagina = 1

    resultado = listar_produtos(nome, pagina)

    if isinstance(resultado, dict):
        lista_produtos = resultado.get("produtos", [])
    else:
        lista_produtos = resultado

    return render_template(
        "produtos.html",
        produtos=lista_produtos
    )


@estoque.route("/produtos", methods=["POST"])
def criar_produto():
    if not logado():
        return jsonify({"erro": "Faça login primeiro."}), 401

    if not administrador():
        return jsonify({"erro": "Apenas administradores podem cadastrar produtos."}), 403

    dados = request.get_json()

    if not dados or not dados.get("nome"):
        return jsonify({"erro": "Informe o nome do produto."}), 400

    cadastrar_produto(
        dados["nome"],
        dados.get("descricao", ""),
        dados.get("preco", 0),
        dados.get("quantidade_estoque", 0)
    )

    return jsonify({"mensagem": "Produto cadastrado."}), 201


@estoque.route("/produtos/<int:produto_id>", methods=["GET"])
def consultar_produto(produto_id):
    if not logado():
        return jsonify({"erro": "Faça login primeiro."}), 401

    produto = buscar_produto(produto_id)

    if produto is None:
        return jsonify({"erro": "Produto não encontrado."}), 404

    return jsonify(produto), 200


@estoque.route("/produtos/<int:produto_id>", methods=["PUT"])
def editar_produto(produto_id):
    if not logado():
        return jsonify({"erro": "Faça login primeiro."}), 401

    if not administrador():
        return jsonify({"erro": "Apenas administradores podem editar produtos."}), 403

    dados = request.get_json()

    if not dados:
        return jsonify({"erro": "Envie os dados do produto."}), 400

    alterados = atualizar_produto(
        produto_id,
        dados.get("nome", ""),
        dados.get("descricao", ""),
        dados.get("preco", 0),
        dados.get("quantidade_estoque", 0)
    )

    if alterados == 0:
        return jsonify({"erro": "Produto não encontrado ou sem alterações."}), 404

    return jsonify({"mensagem": "Produto atualizado."}), 200


@estoque.route("/produtos/<int:produto_id>", methods=["DELETE"])
def remover_produto(produto_id):
    if not logado():
        return jsonify({"erro": "Faça login primeiro."}), 401

    if not administrador():
        return jsonify({"erro": "Apenas administradores podem excluir produtos."}), 403

    produto = buscar_produto(produto_id)

    if produto is None:
        return jsonify({"erro": "Produto não encontrado."}), 404

    try:
        excluidos = excluir_produto(produto_id)
    except Exception:
        return jsonify({
            "erro": "Não é possível excluir este produto. Verifique se ele possui movimentações."
        }), 400

    if excluidos == 0:
        return jsonify({"erro": "Produto não encontrado."}), 404

    return jsonify({"mensagem": "Produto excluído."}), 200


@estoque.route("/produtos/<int:produto_id>/entrada", methods=["POST"])
def entrada(produto_id):
    if not logado():
        return jsonify({"erro": "Faça login primeiro."}), 401

    dados = request.get_json() or {}
    quantidade = dados.get("quantidade", 0)

    if not isinstance(quantidade, int) or isinstance(quantidade, bool):
        return jsonify({"erro": "A quantidade deve ser um número inteiro."}), 400

    sucesso, mensagem = movimentar_estoque(
        produto_id, "entrada", quantidade, session["usuario_id"]
    )

    if not sucesso:
        return jsonify({"erro": mensagem}), 400

    return jsonify({"mensagem": mensagem}), 200


@estoque.route("/produtos/<int:produto_id>/saida", methods=["POST"])
def saida(produto_id):
    if not logado():
        return jsonify({"erro": "Faça login primeiro."}), 401

    dados = request.get_json() or {}
    quantidade = dados.get("quantidade", 0)

    if not isinstance(quantidade, int) or isinstance(quantidade, bool):
        return jsonify({"erro": "A quantidade deve ser um número inteiro."}), 400

    sucesso, mensagem = movimentar_estoque(
        produto_id, "saida", quantidade, session["usuario_id"]
    )

    if not sucesso:
        return jsonify({"erro": mensagem}), 400

    return jsonify({"mensagem": mensagem}), 200


@estoque.route("/movimentacoes", methods=["GET"])
def movimentacoes():
    if not logado():
        return jsonify({"erro": "Faça login primeiro."}), 401

    nome = request.args.get("nome", "")
    data = request.args.get("data", "")

    resultado = listar_movimentacoes(nome, data)

    return jsonify(resultado), 200
