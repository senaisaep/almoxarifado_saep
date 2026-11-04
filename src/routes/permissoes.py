from functools import wraps
from flask import session, jsonify


def login_obrigatorio(funcao):
    @wraps(funcao)
    def verificar(*args, **kwargs):
        if "usuario_id" not in session:
            return jsonify({"erro": "Faça login primeiro."}), 401

        return funcao(*args, **kwargs)

    return verificar


def administrador_obrigatorio(funcao):
    @wraps(funcao)
    def verificar(*args, **kwargs):
        if "usuario_id" not in session:
            return jsonify({"erro": "Faça login primeiro."}), 401

        if session.get("perfil") != "admin":
            return jsonify({"erro": "Acesso permitido somente ao administrador."}), 403

        return funcao(*args, **kwargs)

    return verificar