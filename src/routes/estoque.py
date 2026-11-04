from flask import Blueprint, request, jsonify, g
from src.config.db import conectar
from src.routes.auth import autenticar

estoque = Blueprint("estoque", __name__)


# LISTAR PRODUTOS COM PAGINAÇÃO E FILTROS
@estoque.route("/produtos", methods=["GET"])
@autenticar(["administrador", "operador"])
def listar_produtos():

    pagina = max(request.args.get("pagina", 1, type=int), 1)
    limite = min(max(request.args.get("limite", 10, type=int), 1), 100)
    nome = request.args.get("nome", "")
    data = request.args.get("data", "")

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    sql = "SELECT * FROM produtos WHERE 1=1"
    parametros = []

    if nome:
        sql += " AND nome LIKE %s"
        parametros.append(f"%{nome}%")

    if data:
        sql += " AND DATE(data_cadastro) = %s"
        parametros.append(data)

    cursor.execute(
        "SELECT COUNT(*) AS total FROM produtos WHERE 1=1"
        + (" AND nome LIKE %s" if nome else "")
        + (" AND DATE(data_cadastro) = %s" if data else ""),
        parametros
    )

    total = cursor.fetchone()["total"]

    sql += " ORDER BY id LIMIT %s OFFSET %s"
    parametros.extend([limite, (pagina - 1) * limite])

    cursor.execute(sql, parametros)
    dados = cursor.fetchall()

    cursor.close()
    conexao.close()

    return jsonify({
        "produtos": dados,
        "pagina": pagina,
        "limite": limite,
        "total": total
    }), 200


# CONSULTAR PRODUTO
@estoque.route("/produtos/<int:produto_id>", methods=["GET"])
@autenticar(["administrador", "operador"])
def consultar_produto(produto_id):

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM produtos WHERE id=%s",
        (produto_id,)
    )

    produto = cursor.fetchone()

    cursor.close()
    conexao.close()

    if not produto:
        return jsonify({"mensagem": "Produto não encontrado."}), 404

    return jsonify(produto), 200


# CADASTRAR PRODUTO
@estoque.route("/produtos", methods=["POST"])
@autenticar(["administrador", "operador"])
def cadastrar_produto():

    dados = request.get_json(silent=True) or {}

    if not dados.get("nome"):
        return jsonify({"mensagem": "O nome é obrigatório."}), 400

    quantidade = dados.get("quantidade_estoque", 0)

    if type(quantidade) is not int or quantidade < 0:
        return jsonify({"mensagem": "Quantidade inválida."}), 400

    conexao = conectar()
    cursor = conexao.cursor()

    try:
        cursor.execute(
            """INSERT INTO produtos
               (nome, descricao, preco, quantidade_estoque)
               VALUES (%s, %s, %s, %s)""",
            (
                dados["nome"],
                dados.get("descricao", ""),
                dados.get("preco", 0),
                quantidade
            )
        )

        produto_id = cursor.lastrowid

        if quantidade > 0:
            cursor.execute(
                """INSERT INTO movimentacoes
                   (produto_id, tipo, quantidade, usuario_id)
                   VALUES (%s, 'entrada', %s, %s)""",
                (produto_id, quantidade, g.usuario["id"])
            )

        conexao.commit()

    except Exception:
        conexao.rollback()
        return jsonify({"mensagem": "Erro ao cadastrar produto."}), 400

    finally:
        cursor.close()
        conexao.close()

    return jsonify({"mensagem": "Produto cadastrado.", "id": produto_id}), 201


# ATUALIZAR PRODUTO
@estoque.route("/produtos/<int:produto_id>", methods=["PUT"])
@autenticar(["administrador", "operador"])
def atualizar_produto(produto_id):

    dados = request.get_json(silent=True) or {}

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """UPDATE produtos
           SET nome=%s, descricao=%s, preco=%s
           WHERE id=%s""",
        (
            dados.get("nome"),
            dados.get("descricao", ""),
            dados.get("preco", 0),
            produto_id
        )
    )

    conexao.commit()
    alterados = cursor.rowcount

    cursor.close()
    conexao.close()

    if alterados == 0:
        return jsonify({"mensagem": "Produto não encontrado ou sem alterações."}), 404

    return jsonify({"mensagem": "Produto atualizado."}), 200


# EXCLUIR PRODUTO - SOMENTE ADMINISTRADOR
@estoque.route("/produtos/<int:produto_id>", methods=["DELETE"])
@autenticar(["administrador"])
def remover_produto(produto_id):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        "DELETE FROM produtos WHERE id=%s",
        (produto_id,)
    )

    conexao.commit()
    removidos = cursor.rowcount

    cursor.close()
    conexao.close()

    if removidos == 0:
        return jsonify({"mensagem": "Produto não encontrado."}), 404

    return jsonify({"mensagem": "Produto removido."}), 200


# LISTAR MOVIMENTAÇÕES
@estoque.route("/movimentacoes", methods=["GET"])
@autenticar(["administrador", "operador"])
def listar_movimentacoes():

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute(
        """SELECT m.id, m.produto_id, p.nome AS produto,
                  m.tipo, m.quantidade, m.data_hora,
                  u.nome AS responsavel
           FROM movimentacoes m
           INNER JOIN produtos p ON p.id=m.produto_id
           INNER JOIN usuarios u ON u.id=m.usuario_id
           ORDER BY m.id DESC"""
    )

    dados = cursor.fetchall()

    cursor.close()
    conexao.close()

    return jsonify(dados), 200


# REGISTRAR ENTRADA
@estoque.route("/movimentacoes/entrada", methods=["POST"])
@autenticar(["administrador", "operador"])
def registrar_entrada():

    dados = request.get_json(silent=True) or {}

    produto_id = dados.get("produto_id")
    quantidade = dados.get("quantidade")

    if type(produto_id) is not int or produto_id <= 0:
        return jsonify({"mensagem": "Produto inválido."}), 400

    if type(quantidade) is not int or quantidade <= 0:
        return jsonify({"mensagem": "Quantidade deve ser maior que zero."}), 400

    conexao = conectar()
    cursor = conexao.cursor()

    try:
        cursor.execute(
            """UPDATE produtos
               SET quantidade_estoque = quantidade_estoque + %s
               WHERE id = %s""",
            (quantidade, produto_id)
        )

        if cursor.rowcount == 0:
            conexao.rollback()
            return jsonify({"mensagem": "Produto não encontrado."}), 404

        cursor.execute(
            """INSERT INTO movimentacoes
               (produto_id, tipo, quantidade, usuario_id)
               VALUES (%s, 'entrada', %s, %s)""",
            (produto_id, quantidade, g.usuario["id"])
        )

        conexao.commit()

    except Exception:
        conexao.rollback()
        return jsonify({"mensagem": "Erro ao registrar entrada."}), 400

    finally:
        cursor.close()
        conexao.close()

    return jsonify({"mensagem": "Entrada registrada com sucesso."}), 201


# REGISTRAR SAÍDA
@estoque.route("/movimentacoes/saida", methods=["POST"])
@autenticar(["administrador", "operador"])
def registrar_saida():

    dados = request.get_json(silent=True) or {}

    produto_id = dados.get("produto_id")
    quantidade = dados.get("quantidade")

    if type(produto_id) is not int or produto_id <= 0:
        return jsonify({"mensagem": "Produto inválido."}), 400

    if type(quantidade) is not int or quantidade <= 0:
        return jsonify({"mensagem": "Quantidade deve ser maior que zero."}), 400

    conexao = conectar()
    cursor = conexao.cursor()

    try:
        cursor.execute(
            """UPDATE produtos
               SET quantidade_estoque = quantidade_estoque - %s
               WHERE id = %s AND quantidade_estoque >= %s""",
            (quantidade, produto_id, quantidade)
        )

        if cursor.rowcount == 0:
            cursor.execute(
                "SELECT quantidade_estoque FROM produtos WHERE id=%s",
                (produto_id,)
            )

            produto = cursor.fetchone()

            conexao.rollback()

            if produto is None:
                return jsonify({"mensagem": "Produto não encontrado."}), 404

            return jsonify({
                "mensagem": (
                    "Saída não permitida: estoque insuficiente. "
                    f"Disponível: {produto[0]}. Solicitado: {quantidade}."
                )
            }), 400

        cursor.execute(
            """INSERT INTO movimentacoes
               (produto_id, tipo, quantidade, usuario_id)
               VALUES (%s, 'saida', %s, %s)""",
            (produto_id, quantidade, g.usuario["id"])
        )

        conexao.commit()

    except Exception:
        conexao.rollback()
        return jsonify({"mensagem": "Erro ao registrar saída."}), 400

    finally:
        cursor.close()
        conexao.close()

    return jsonify({"mensagem": "Saída registrada com sucesso."}), 201


SERVER. PY
from flask import Flask, jsonify
from src.routes.estoque import estoque
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.register_blueprint(estoque)

@app.route("/", methods=["GET"])
def inicio():
    return jsonify({"mensagem": "API do Sistema de Almoxarifado"}), 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=True)




from flask import Blueprint, request, jsonify, g
from src.config.db import conectar
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import jwt
import os
from datetime import datetime, timedelta, timezone

auth = Blueprint("auth", __name__)

SECRET_KEY = os.getenv("SECRET_KEY", "chave-temporaria-trocar")


def gerar_token(usuario):
    payload = {
        "id": usuario["id"],
        "perfil": usuario["perfil"],
        "exp": datetime.now(timezone.utc) + timedelta(hours=8)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def autenticar(perfis=None):
    def decorador(funcao):
        @wraps(funcao)
        def verificar(*args, **kwargs):
            token = request.headers.get("Authorization", "")

            if not token.startswith("Bearer "):
                return jsonify({"mensagem": "Autenticação necessária."}), 401

            try:
                dados = jwt.decode(
                    token[7:],
                    SECRET_KEY,
                    algorithms=["HS256"]
                )
            except jwt.InvalidTokenError:
                return jsonify({"mensagem": "Token inválido ou expirado."}), 401

            conexao = conectar()
            cursor = conexao.cursor(dictionary=True)

            cursor.execute(
                "SELECT id, nome, email, perfil, ativo FROM usuarios WHERE id=%s",
                (dados["id"],)
            )
            usuario = cursor.fetchone()

            cursor.close()
            conexao.close()

            if not usuario or not usuario["ativo"]:
                return jsonify({"mensagem": "Usuário não encontrado ou inativo."}), 401

            if perfis and usuario["perfil"] not in perfis:
                return jsonify({"mensagem": "Você não tem permissão para esta operação."}), 403

            g.usuario = usuario
            return funcao(*args, **kwargs)

        return verificar
    return decorador


@auth.route("/auth/primeiro-admin", methods=["POST"])
def primeiro_admin():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("SELECT COUNT(*) FROM usuarios")
    total = cursor.fetchone()[0]

    if total > 0:
        cursor.close()
        conexao.close()
        return jsonify({"mensagem": "O administrador inicial já foi criado."}), 403

    dados = request.get_json(silent=True) or {}

    if not all(dados.get(campo) for campo in ["nome", "email", "senha"]):
        cursor.close()
        conexao.close()
        return jsonify({"mensagem": "Informe nome, email e senha."}), 400

    senha = generate_password_hash(dados["senha"])

    cursor.execute(
        """INSERT INTO usuarios (nome, email, senha_hash, perfil)
           VALUES (%s, %s, %s, 'administrador')""",
        (dados["nome"], dados["email"], senha)
    )

    conexao.commit()
    cursor.close()
    conexao.close()

    return jsonify({"mensagem": "Administrador criado com sucesso."}), 201


@auth.route("/auth/login", methods=["POST"])
def login():
    dados = request.get_json(silent=True) or {}

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM usuarios WHERE email=%s",
        (dados.get("email"),)
    )

    usuario = cursor.fetchone()

    cursor.close()
    conexao.close()

    if not usuario or not usuario["ativo"]:
        return jsonify({"mensagem": "Email ou senha inválidos."}), 401

    if not check_password_hash(usuario["senha_hash"], dados.get("senha", "")):
        return jsonify({"mensagem": "Email ou senha inválidos."}), 401

    return jsonify({
        "mensagem": "Login realizado com sucesso.",
        "token": gerar_token(usuario),
        "usuario": {
            "id": usuario["id"],
            "nome": usuario["nome"],
            "perfil": usuario["perfil"]
        }
    }), 200


@auth.route("/usuarios", methods=["POST"])
@autenticar(["administrador"])
def cadastrar_usuario():
    dados = request.get_json(silent=True) or {}

    if not all(dados.get(campo) for campo in ["nome", "email", "senha", "perfil"]):
        return jsonify({"mensagem": "Preencha todos os campos."}), 400

    if dados["perfil"] not in ["administrador", "operador"]:
        return jsonify({"mensagem": "Perfil inválido."}), 400

    senha = generate_password_hash(dados["senha"])

    conexao = conectar()
    cursor = conexao.cursor()

    try:
        cursor.execute(
            """INSERT INTO usuarios (nome, email, senha_hash, perfil)
               VALUES (%s, %s, %s, %s)""",
            (dados["nome"], dados["email"], senha, dados["perfil"])
        )
        conexao.commit()
    except Exception:
        conexao.rollback()
        return jsonify({"mensagem": "Não foi possível cadastrar. Verifique o email."}), 400
    finally:
        cursor.close()
        conexao.close()

    return jsonify({"mensagem": "Usuário cadastrado com sucesso."}), 201

