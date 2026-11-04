from datetime import date, timedelta
from flask import Blueprint, request, jsonify
from src.config.db import conectar

estoque = Blueprint("estoque", __name__)

# Lógica de negócio e comandos SQL concentrados neste arquivo de rotas.

@estoque.route("/produtos", methods=["GET"])
def listar_produtos():
    try:
        pagina = int(request.args.get("pagina", "1"))
        por_pagina = int(request.args.get("por_pagina", "10"))
        if pagina < 1 or not 1 <= por_pagina <= 100:
            raise ValueError
    except ValueError:
        return jsonify({"mensagem": "pagina deve ser positiva e por_pagina deve estar entre 1 e 100."}), 400
    try:
        datas = {}
        for campo in ("data", "data_inicio", "data_fim"):
            valor = request.args.get(campo)
            if valor is not None:
                if len(valor) != 10 or valor[4] != "-" or valor[7] != "-":
                    raise ValueError
                datas[campo] = date.fromisoformat(valor)
        if "data" in datas and len(datas) > 1:
            raise ValueError
        inicio = datas.get("data", datas.get("data_inicio"))
        fim = datas.get("data", datas.get("data_fim"))
        if inicio and fim and inicio > fim:
            raise ValueError
        fim_exclusivo = fim + timedelta(days=1) if fim else None
    except (ValueError, OverflowError):
        return jsonify({"mensagem": "Use datas válidas no formato AAAA-MM-DD: data ou data_inicio/data_fim, em ordem cronológica."}), 400
    filtros = []
    parametros = []
    nome = request.args.get("nome", "").strip()
    if nome:
        # Trata os caracteres especiais do LIKE como texto literal.
        nome = nome.replace("!", "!!").replace("%", "!%").replace("_", "!_")
        filtros.append("nome LIKE %s ESCAPE '!'")
        parametros.append(f"%{nome}%")
    if inicio:
        filtros.append("data_cadastro >= %s")
        parametros.append(inicio)
    if fim_exclusivo:
        filtros.append("data_cadastro < %s")
        parametros.append(fim_exclusivo)
    where = " WHERE " + " AND ".join(filtros) if filtros else ""

    conexao = conectar()
    cursor = None
    try:
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) AS total FROM produtos" + where, tuple(parametros))
        total = cursor.fetchone()["total"]
        cursor.execute(
            "SELECT * FROM produtos" + where + " ORDER BY id LIMIT %s OFFSET %s",
            tuple(parametros + [por_pagina, (pagina - 1) * por_pagina])
        )
        dados = cursor.fetchall()
    finally:
        try:
            if cursor is not None:
                cursor.close()
        finally:
            conexao.close()

    return jsonify({
        "produtos": dados,
        "pagina": pagina,
        "por_pagina": por_pagina,
        "total": total,
        "total_paginas": (total + por_pagina - 1) // por_pagina
    }), 200


@estoque.route("/produtos/<int:produto_id>", methods=["GET"])
def consultar_produto(produto_id):
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)
    cursor.execute("SELECT * FROM produtos WHERE id = %s", (produto_id,))
    produto = cursor.fetchone()
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

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "INSERT INTO produtos (nome, descricao, preco, quantidade_estoque) VALUES (%s, %s, %s, %s)",
        (dados["nome"], dados.get("descricao", ""), dados.get("preco", 0),
         dados.get("quantidade_estoque", 0))
    )
    conexao.commit()
    novo_id = cursor.lastrowid
    cursor.close()
    conexao.close()
    return jsonify({"mensagem": "Produto cadastrado.", "id": novo_id}), 201


@estoque.route("/produtos/<int:produto_id>", methods=["PUT"])
def atualizar_produto(produto_id):
    dados = request.get_json(silent=True) or {}
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        """UPDATE produtos
           SET nome=%s, descricao=%s, preco=%s, quantidade_estoque=%s
           WHERE id=%s""",
        (dados.get("nome"), dados.get("descricao", ""), dados.get("preco", 0),
         dados.get("quantidade_estoque", 0), produto_id)
    )
    conexao.commit()
    alterados = cursor.rowcount
    cursor.close()
    conexao.close()
    if alterados == 0:
        return jsonify({"mensagem": "Produto não encontrado ou sem alterações."}), 404
    return jsonify({"mensagem": "Produto atualizado."}), 200


@estoque.route("/produtos/<int:produto_id>", methods=["DELETE"])
def remover_produto(produto_id):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM produtos WHERE id=%s", (produto_id,))
    conexao.commit()
    removidos = cursor.rowcount
    cursor.close()
    conexao.close()
    if removidos == 0:
        return jsonify({"mensagem": "Produto não encontrado."}), 404
    return jsonify({"mensagem": "Produto removido."}), 200


@estoque.route("/movimentacoes", methods=["GET"])
def listar_movimentacoes():
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
    dados = request.get_json(silent=True) or {}
    produto_id = dados.get("produto_id")
    quantidade = dados.get("quantidade")

    if not produto_id or not quantidade or int(quantidade) <= 0:
        return jsonify({"mensagem": "Informe produto_id e quantidade maior que zero."}), 400

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "INSERT INTO movimentacoes (produto_id, tipo, quantidade) VALUES (%s, 'entrada', %s)",
        (produto_id, int(quantidade))
    )
    cursor.execute(
        "UPDATE produtos SET quantidade_estoque=quantidade_estoque+%s WHERE id=%s",
        (int(quantidade), produto_id)
    )
    conexao.commit()
    cursor.close()
    conexao.close()
    return jsonify({"mensagem": "Entrada registrada com sucesso."}), 201


@estoque.route("/movimentacoes/saida", methods=["POST"])
def registrar_saida():
    dados = request.get_json(silent=True) or {}
    produto_id = dados.get("produto_id")
    quantidade = dados.get("quantidade")

    try:
        produto_id = int(produto_id)
        quantidade = int(quantidade)
    except (TypeError, ValueError):
        return jsonify({
            "mensagem": "Informe produto_id e quantidade maior que zero."
        }), 400

    if produto_id <= 0 or quantidade <= 0:
        return jsonify({
            "mensagem": "Informe produto_id e quantidade maior que zero."
        }), 400

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, quantidade_estoque FROM produtos WHERE id=%s FOR UPDATE",
            (produto_id,),
        )
        produto = cursor.fetchone()

        if produto is None:
            conexao.rollback()
            return jsonify({"mensagem": "Produto não encontrado."}), 404

        disponivel = int(produto["quantidade_estoque"])
        if quantidade > disponivel:
            conexao.rollback()
            return jsonify({
                "mensagem": (
                    "Saída não permitida: estoque insuficiente. "
                    f"Disponível {disponivel}. Solicitado {quantidade}."
                )
            }), 400

        cursor.execute(
            "INSERT INTO movimentacoes (produto_id, tipo, quantidade) VALUES (%s, 'saida', %s)",
            (produto_id, quantidade),
        )
        cursor.execute(
            "UPDATE produtos SET quantidade_estoque=quantidade_estoque-%s WHERE id=%s",
            (quantidade, produto_id),
        )
        conexao.commit()
        return jsonify({
            "mensagem": "Saída registrada com sucesso.",
            "disponivel": disponivel - quantidade,
        }), 201
    except Exception:
        conexao.rollback()
        raise
    finally:
        cursor.close()
        conexao.close()
