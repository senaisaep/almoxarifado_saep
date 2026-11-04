from flask import Blueprint, request, jsonify
import mysql.connector

from src.config.db import conectar

estoque = Blueprint("estoque", __name__)

# Lógica de negócio e comandos SQL concentrados neste arquivo de rotas.


def _numero_positivo(valor):
    """Converte para inteiro positivo; retorna None se for inválido."""
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        return None
    return numero if numero > 0 else None


@estoque.route("/produtos", methods=["GET"])
def listar_produtos():
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM produtos ORDER BY id")
        dados = cursor.fetchall()
        return jsonify(dados), 200
    except mysql.connector.Error:
        return jsonify({"mensagem": "Erro ao consultar os produtos."}), 500
    finally:
        cursor.close()
        conexao.close()


@estoque.route("/produtos/<int:produto_id>", methods=["GET"])
def consultar_produto(produto_id):
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM produtos WHERE id = %s", (produto_id,))
        produto = cursor.fetchone()
    except mysql.connector.Error:
        return jsonify({"mensagem": "Erro ao consultar o produto."}), 500
    finally:
        cursor.close()
        conexao.close()
    if produto is None:
        return jsonify({"mensagem": "Produto não encontrado."}), 404
    return jsonify(produto), 200


@estoque.route("/produtos", methods=["POST"])
def cadastrar_produto():
    dados = request.get_json(silent=True) or {}
    if not dados.get("nome"):
        return jsonify({"mensagem": "O nome do produto é obrigatório."}), 400

    try:
        preco = float(dados.get("preco", 0))
        quantidade = int(dados.get("quantidade_estoque", 0))
    except (TypeError, ValueError):
        return jsonify({"mensagem": "Preço e quantidade devem ser números."}), 400
    if preco < 0 or quantidade < 0:
        return jsonify({"mensagem": "Preço e quantidade não podem ser negativos."}), 400

    conexao = conectar()
    cursor = conexao.cursor()
    try:
        cursor.execute(
            "INSERT INTO produtos (nome, descricao, preco, quantidade_estoque) VALUES (%s, %s, %s, %s)",
            (dados["nome"], dados.get("descricao", ""), preco, quantidade)
        )
        conexao.commit()
        novo_id = cursor.lastrowid
    except mysql.connector.Error:
        conexao.rollback()
        return jsonify({"mensagem": "Erro ao cadastrar o produto."}), 500
    finally:
        cursor.close()
        conexao.close()
    return jsonify({"mensagem": "Produto cadastrado.", "id": novo_id}), 201


@estoque.route("/produtos/<int:produto_id>", methods=["PUT"])
def atualizar_produto(produto_id):
    dados = request.get_json(silent=True) or {}
    conexao = conectar()
    cursor = conexao.cursor()
    try:
        cursor.execute(
            """UPDATE produtos
               SET nome=%s, descricao=%s, preco=%s, quantidade_estoque=%s
               WHERE id=%s""",
            (dados.get("nome"), dados.get("descricao", ""), dados.get("preco", 0),
             dados.get("quantidade_estoque", 0), produto_id)
        )
        conexao.commit()
        alterados = cursor.rowcount
    except mysql.connector.Error:
        conexao.rollback()
        return jsonify({"mensagem": "Erro ao atualizar o produto."}), 500
    finally:
        cursor.close()
        conexao.close()
    if alterados == 0:
        return jsonify({"mensagem": "Produto não encontrado ou sem alterações."}), 404
    return jsonify({"mensagem": "Produto atualizado."}), 200


@estoque.route("/produtos/<int:produto_id>", methods=["DELETE"])
def remover_produto(produto_id):
    conexao = conectar()
    cursor = conexao.cursor()
    try:
        cursor.execute("DELETE FROM produtos WHERE id=%s", (produto_id,))
        conexao.commit()
        removidos = cursor.rowcount
    except mysql.connector.Error as erro:
        conexao.rollback()
        if erro.errno == 1451:
            return jsonify({"mensagem": "Produto não pode ser removido: existem movimentações registradas para ele."}), 409
        return jsonify({"mensagem": "Erro ao remover o produto."}), 500
    finally:
        cursor.close()
        conexao.close()
    if removidos == 0:
        return jsonify({"mensagem": "Produto não encontrado."}), 404
    return jsonify({"mensagem": "Produto removido."}), 200


@estoque.route("/movimentacoes", methods=["GET"])
def listar_movimentacoes():
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)
    try:
        cursor.execute(
            """SELECT m.id, m.produto_id, p.nome AS produto, m.tipo, m.quantidade
               FROM movimentacoes m
               INNER JOIN produtos p ON p.id=m.produto_id
               ORDER BY m.id DESC"""
        )
        dados = cursor.fetchall()
        return jsonify(dados), 200
    except mysql.connector.Error:
        return jsonify({"mensagem": "Erro ao consultar as movimentações."}), 500
    finally:
        cursor.close()
        conexao.close()


@estoque.route("/movimentacoes/entrada", methods=["POST"])
def registrar_entrada():
    dados = request.get_json(silent=True) or {}
    produto_id = dados.get("produto_id")
    quantidade = _numero_positivo(dados.get("quantidade"))

    if not produto_id or quantidade is None:
        return jsonify({"mensagem": "Informe produto_id e quantidade maior que zero."}), 400

    conexao = conectar()
    cursor = conexao.cursor()
    try:
        cursor.execute("SELECT id FROM produtos WHERE id=%s", (produto_id,))
        if cursor.fetchone() is None:
            return jsonify({"mensagem": "Produto não encontrado."}), 404

        # INSERT e UPDATE na mesma transação: ou os dois acontecem, ou nenhum.
        cursor.execute(
            "INSERT INTO movimentacoes (produto_id, tipo, quantidade) VALUES (%s, 'entrada', %s)",
            (produto_id, quantidade)
        )
        cursor.execute(
            "UPDATE produtos SET quantidade_estoque=quantidade_estoque+%s WHERE id=%s",
            (quantidade, produto_id)
        )
        conexao.commit()
    except mysql.connector.Error:
        conexao.rollback()
        return jsonify({"mensagem": "Erro ao registrar a entrada."}), 500
    finally:
        cursor.close()
        conexao.close()
    return jsonify({"mensagem": "Entrada registrada com sucesso."}), 201
