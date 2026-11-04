from flask import Blueprint, request, jsonify, session, render_template, abort
from db import conectar

estoque = Blueprint("estoque", __name__)

@estoque.route("/home")
def home():
    return render_template("home.html")

@estoque.route("/produtos", methods=["GET"])
def listar_produtos():
    if session["usuario"]["permissao"] == "opr" or session["usuario"]["permissao"] == "adm":
        return render_template("produtos.html")
    else:
        abort(403)
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)
    cursor.execute("""SELECT * FROM produtos ORDER BY id""")
    dados = cursor.fetchall()
    cursor.close()
    conexao.close()
    return jsonify(dados), 200


@estoque.route("/produtos/<int:produto_id>", methods=["GET"])
def consultar_produto(produto_id):
    if session["usuario"]["permissao"] == "adm":
        return render_template("produtos.html")
    else:
        abort(403)
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)
    cursor.execute("""SELECT * FROM produtos WHERE id = ?""", (produto_id,))
    produto = cursor.fetchone()
    cursor.close()
    conexao.close()
    if produto is None:
        return jsonify({"mensagem": "Produto não encontrado."}), 404
    return jsonify(produto), 200


@estoque.route("/produtos", methods=["POST"])
def cadastrar_produto():
    if session["usuario"]["permissao"] == "opr" or session["usuario"]["permissao"] == "adm":
        return render_template("produtos.html")
    else:
        abort(403)
    dados = request.get_json(silent=True) or {}
    if not dados.get("nome"):
        return jsonify({"mensagem": "O nome do produto é obrigatório."}), 400

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        """INSERT INTO produtos (nome, descricao, preco, quantidade_estoque) VALUES (?,?,?,?)""",
        (dados["nome"], dados.get("descricao", ""), dados.get("preco", ""),
         dados.get("quantidade_estoque", ""))
    )
    conexao.commit()
    novo_id = cursor.lastrowid
    cursor.close()
    conexao.close()
    return jsonify({"mensagem": "Produto cadastrado.", "id": novo_id}), 201


@estoque.route("/produtos/<produto_id>", methods=["PUT"])
def atualizar_produto(produto_id):
    if session["usuario"]["permissao"] == "opr" or session["usuario"]["permissao"] == "adm":
        return render_template("produtos_id.html")
    else:
        abort(403)
    dados = request.get_json(silent=True) or {}
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        """UPDATE produtos
           SET nome=?, descricao=?, preco=?, quantidade_estoque=?
           WHERE id=?""",
        (dados.get("nome"), dados.get("descricao", ""), dados.get("preco", 0),
         dados.get("quantidade_estoque", ""), produto_id)
    )
    conexao.commit()
    alterados = cursor.rowcount
    cursor.close()
    conexao.close()
    if alterados == 0:
        return jsonify({"mensagem": "Produto não encontrado ou sem alterações."}), 404
    return jsonify({"mensagem": "Produto atualizado."}), 200


@estoque.route("/produtos/<produto_id>", methods=["DELETE"])
def remover_produto(produto_id):
    if session["usuario"]["permissao"] == "adm":
        return render_template("produtos_id.html")
    else:
        abort(403)
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""DELETE FROM produtos WHERE id=?""", (produto_id,))
    conexao.commit()
    removidos = cursor.rowcount
    cursor.close()
    conexao.close()
    if removidos == 0:
        return jsonify({"mensagem": "Produto não encontrado."}), 404
    return jsonify({"mensagem": "Produto removido."}), 200


@estoque.route("/movimentacoes", methods=["GET"])
def listar_movimentacoes():
    if session["usuario"]["permissao"] == "opr" or session["usuario"]["permissao"] == "adm":
        return render_template("movimentacoes.html")
    else:
        abort(403)
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)
    cursor.execute(
        """SELECT m.id, m.produto_id, p.nome AS produto, m.tipo, m.quantidade
           FROM movimentacoes m
           INNER JOIN produtos p ON p.id=m.produto_id
           ORDER BY m.id DESC"""
    )
    dados = cursor.fetchall()
    cursor.close()
    conexao.close()
    return jsonify(dados), 200


@estoque.route("/movimentacoes/entrada", methods=["POST"])
def registrar_entrada():
    if session["usuario"]["permissao"] == "opr" or session["usuario"]["permissao"] == "adm":
        return render_template("movimentacoes_entrada.html")
    else:
        abort(403)
    dados = request.get_json(silent=True) or {}
    produto_id = dados.get("produto_id")
    quantidade = dados.get("quantidade")

    if not produto_id or not quantidade or int(quantidade) <= 0:
        return jsonify({"mensagem": "Informe produto_id e quantidade maior que zero."}), 400

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        """INSERT INTO movimentacoes (produto_id, tipo, quantidade) VALUES (?, "entrada", ?)""",
        (produto_id, quantidade)
    )
    cursor.execute(
        """UPDATE produtos SET quantidade_estoque=quantidade_estoque+? WHERE id=?""",
        (quantidade, produto_id)
    )
    conexao.commit()
    cursor.close()
    conexao.close()
    return jsonify({"mensagem": "Entrada registrada com sucesso."}), 201
