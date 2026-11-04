from functools import wraps
from flask import session, redirect, url_for, flash
from werkzeug.security import check_password_hash

def autenticar(email, senha):
    from src.config.db import conectar
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, nome, email, senha_hash, perfil, ativo FROM usuarios WHERE email=%s",
            (email,)
        )
        usuario = cursor.fetchone()
        if not usuario or not usuario["ativo"]:
            return None
        if not check_password_hash(usuario["senha_hash"], senha):
            return None
        return {k: usuario[k] for k in ("id", "nome", "email", "perfil")}
    finally:
        cursor.close()
        conexao.close()

def login_obrigatorio(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "usuario" not in session:
            flash("Entre com seu usuário para continuar.", "aviso")
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)
    return wrapper

def perfil_obrigatorio(*perfis):
    def decorador(func):
        @wraps(func)
        @login_obrigatorio
        def wrapper(*args, **kwargs):
            if session["usuario"]["perfil"] not in perfis:
                flash("Seu perfil não tem permissão para realizar esta ação.", "erro")
                return redirect(url_for("produtos.listar"))
            return func(*args, **kwargs)
        return wrapper
    return decorador
