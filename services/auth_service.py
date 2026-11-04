from functools import wraps

from flask import jsonify, redirect, session
from werkzeug.security import check_password_hash

from repositories.usuario_repository import buscar_usuario_por_login


def autenticar_usuario(login, senha):
    usuario = buscar_usuario_por_login(login)
    if usuario is None:
        return None

    return usuario if check_password_hash(usuario["senha"], senha) else None


def requer_perfil(*perfis):
    def decorador(funcao):
        @wraps(funcao)
        def verificar_permissao(*args, **kwargs):
            if "usuario_id" not in session:
                return redirect("/login")
            if perfis and session.get("perfil") not in perfis:
                return jsonify({"mensagem": "Permissão insuficiente."}), 403
            return funcao(*args, **kwargs)

        return verificar_permissao

    return decorador
