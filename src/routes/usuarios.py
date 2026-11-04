from flask import Blueprint, request, jsonify, session
from src.config.db import conectar

usuarios = Blueprint("usuarios", __name__)


@usuarios.route("/usuarios", methods=["GET"])
def listar_usuarios():
    if "usuario_id" not in session:
        return jsonify({"erro": "Faça login primeiro."}), 401

    if session.get("perfil") != "administrador":
        return jsonify({"erro": "Acesso permitido apenas ao administrador."}), 403

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, nome, email, perfil
        FROM usuarios
    """)

    resultado = cursor.fetchall()

    cursor.close()
    conexao.close()

    return jsonify(resultado), 200


@usuarios.route("/usuarios", methods=["POST"])
def criar_usuario():
    if "usuario_id" not in session:
        return jsonify({"erro": "Faça login primeiro."}), 401

    if session.get("perfil") != "administrador":
        return jsonify({"erro": "Apenas administradores podem criar usuários."}), 403

    dados = request.get_json() or {}

    nome = dados.get("nome")
    email = dados.get("email")
    senha = dados.get("senha")
    perfil = dados.get("perfil")

    if not nome or not email or not senha:
        return jsonify({"erro": "Preencha nome, email e senha."}), 400

    if perfil not in ["operador", "administrador"]:
        return jsonify({"erro": "Perfil inválido."}), 400

    conexao = conectar()
    cursor = conexao.cursor()

    try:
        cursor.execute("""
            INSERT INTO usuarios (nome, email, senha, perfil)
            VALUES (%s, %s, %s, %s)
        """, (nome, email, senha, perfil))

        conexao.commit()

    except Exception:
        conexao.rollback()
        return jsonify({"erro": "Não foi possível cadastrar. Verifique se o email já existe."}), 400

    finally:
        cursor.close()
        conexao.close()

    return jsonify({"mensagem": "Usuário cadastrado."}), 201