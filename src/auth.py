# Autenticação e autorização compartilhadas pela interface e pela API.
import os
import secrets
from datetime import timedelta
from flask import g, session, request, jsonify, redirect, url_for
from dotenv import load_dotenv
from models.usuarios import buscar_por_id
TIPOS = ("administrador", "operador", "consulta")


def configurar_seguranca(app):
    load_dotenv()
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY") or secrets.token_hex(32),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.getenv("COOKIE_SECURE", "0") == "1",
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
    )
    app.jinja_env.globals["csrf_token"] = csrf_token
    @app.before_request
    def proteger_rotas():
        g.usuario = None
        publicas = {"auth.login_route", "auth.cadastro"}
        if session.get("usuario_id"):
            g.usuario = buscar_por_id(session["usuario_id"])
            if not g.usuario:
                session.clear()
        if request.endpoint is None or request.endpoint == "static":
            return None
        if request.endpoint not in publicas:
            if not g.usuario:
                if not app.config.get("API") and request.method in ("GET", "HEAD"):
                    return redirect(url_for("auth.login_route"))
                return jsonify(mensagem="Autenticação obrigatória."), 401
            tipo = g.usuario["tipo"]
            if tipo not in TIPOS:
                return jsonify(mensagem="Tipo de usuário sem permissão."), 403
            if request.endpoint == "auth.cadastrar_usuario" or request.method == "DELETE":
                permitidos = ("administrador",)
            elif request.endpoint == "produtos.cadastrar_produto":
                permitidos = TIPOS
            elif request.method in ("POST", "PUT", "PATCH") and request.endpoint != "auth.logout":
                permitidos = ("administrador", "operador")
            else:
                permitidos = TIPOS
            if tipo not in permitidos:
                return jsonify(mensagem="Seu tipo de usuário não permite esta operação."), 403
        if request.endpoint in ("auth.login_route", "auth.cadastro"):
            return None
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            # JSON exige Content-Type application/json; formulários exigem token.
            if not request.is_json:
                enviado = request.form.get("csrf_token", "")
                esperado = session.get("csrf_token", "")
                if not esperado or not secrets.compare_digest(enviado, esperado):
                    return jsonify(mensagem="Token de formulário inválido. Recarregue a página."), 400
            elif g.usuario:
                enviado = request.headers.get("X-CSRF-Token", "")
                esperado = session.get("csrf_token", "")
                if not esperado or not secrets.compare_digest(enviado, esperado):
                    return jsonify(mensagem="Envie o token no cabeçalho X-CSRF-Token."), 400

def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    return session["csrf_token"]
