import os
from datetime import datetime
from decimal import Decimal

from dotenv import load_dotenv
from flask import Flask, jsonify

from src.routes.auth import auth
from src.routes.movimentacoes import movimentacoes
from src.routes.produtos import produtos
from src.utils.erros import ErroAPI
from src.web import web

load_dotenv()

if not os.getenv("JWT_SECRET"):
    raise RuntimeError("Defina JWT_SECRET no arquivo .env (veja .env.example).")

app = Flask(__name__)
app.json.ensure_ascii = False  # mostra acentos normalmente no JSON


def converter(objeto):
    # O JSON não conhece Decimal nem datas, então convertemos aqui
    if isinstance(objeto, Decimal):
        return float(objeto)
    if isinstance(objeto, datetime):
        return objeto.isoformat()
    raise TypeError(f"Tipo não serializável: {type(objeto)}")


app.json.default = converter

app.register_blueprint(auth)
app.register_blueprint(produtos)
app.register_blueprint(movimentacoes)
app.register_blueprint(web)


@app.route("/", methods=["GET"])
def inicio():
    return jsonify({"mensagem": "API do Sistema de Almoxarifado"}), 200


@app.errorhandler(ErroAPI)
def tratar_erro(erro):
    corpo = {"mensagem": erro.mensagem}
    if erro.detalhes:
        corpo["detalhes"] = erro.detalhes
    return jsonify(corpo), erro.status


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")),
            debug=os.getenv("FLASK_DEBUG") == "1")
