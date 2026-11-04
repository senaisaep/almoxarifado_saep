import logging
import os
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path

# Garante que a raiz do projeto esteja no sys.path mesmo ao executar diretamente 'python src/server.py'
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from flask import Flask, jsonify, request
from flask.json.provider import DefaultJSONProvider

from src.routes.auth import auth
from src.routes.movimentacoes import movimentacoes
from src.routes.produtos import produtos
from src.routes.usuarios import usuarios
from src.utils.erros import ErroApi

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("almoxarifado")


class JsonProvider(DefaultJSONProvider):
    ensure_ascii = False  # acentos legíveis nas mensagens

    @staticmethod
    def default(o):
        if isinstance(o, datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(o, Decimal):
            return float(o)
        return DefaultJSONProvider.default(o)


def create_app():
    app = Flask(__name__)
    app.json = JsonProvider(app)
    app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024  # 1 MB por requisição

    for blueprint in (auth, usuarios, produtos, movimentacoes):
        app.register_blueprint(blueprint)

    @app.route("/", methods=["GET"])
    def inicio():
        return jsonify({"mensagem": "API do Sistema de Almoxarifado", "versao": "1.0.0"}), 200

    @app.route("/health", methods=["GET"])
    def health():
        from src.config.db import testar_conexao
        banco_ok, msg = testar_conexao()
        status_code = 200 if banco_ok else 503
        return jsonify({
            "status": "ok" if banco_ok else "erro",
            "banco": "conectado" if banco_ok else "desconectado",
            "mensagem": msg,
            "versao": "1.0.0",
        }), status_code

    @app.before_request
    def preflight_cors():
        if request.method == "OPTIONS":
            resposta = jsonify({"status": "ok"})
            resposta.headers["Access-Control-Allow-Origin"] = "*"
            resposta.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            resposta.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            return resposta, 200

    @app.errorhandler(ErroApi)
    def erro_api(erro):
        return jsonify({"mensagem": erro.mensagem, **erro.extra}), erro.status

    @app.errorhandler(404)
    def nao_encontrado(_):
        return jsonify({"mensagem": "Recurso não encontrado."}), 404

    @app.errorhandler(405)
    def metodo_nao_permitido(_):
        return jsonify({"mensagem": "Método não permitido."}), 405

    @app.errorhandler(413)
    def corpo_grande(_):
        return jsonify({"mensagem": "Requisição grande demais."}), 413

    @app.errorhandler(Exception)
    def erro_inesperado(erro):
        # Detalhes (SQL, stack) vão só para o log, nunca para o cliente.
        logger.exception("Erro inesperado: %s", erro)
        return jsonify({"mensagem": "Erro interno do servidor."}), 500

    @app.after_request
    def cabecalhos_seguranca(resposta):
        resposta.headers["X-Content-Type-Options"] = "nosniff"
        resposta.headers["X-Frame-Options"] = "DENY"
        resposta.headers["Cache-Control"] = "no-store"
        resposta.headers["Access-Control-Allow-Origin"] = "*"
        resposta.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        resposta.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        return resposta

    return app


app = create_app()

if __name__ == "__main__":
    from src.config.db import testar_conexao
    ok, msg = testar_conexao()
    if ok:
        logger.info("Banco de dados MySQL conectado com sucesso.")
    else:
        logger.warning("Aviso de banco: %s", msg)

    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    logger.info("Iniciando servidor em http://%s:%d (debug=%s)", host, port, debug)

    app.run(
        host=host,
        port=port,
        debug=debug,
    )
