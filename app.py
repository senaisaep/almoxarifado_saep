import os
import secrets
from pathlib import Path

from flask import Flask, redirect

from controllers.auth_controller import auth_bp
from controllers.estoque_controller import estoque_bp
from controllers.produto_controller import produto_bp
from infra.database import inicializar_banco


def criar_app():
    app = Flask(
        __name__,
        template_folder=str(Path(__file__).resolve().with_name("templates")),
    )
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY") or secrets.token_hex(32),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )
    app.register_blueprint(auth_bp)
    app.register_blueprint(estoque_bp)
    app.register_blueprint(produto_bp)

    @app.get("/")
    def inicio():
        return redirect("/login")

    inicializar_banco()
    return app


app = criar_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)