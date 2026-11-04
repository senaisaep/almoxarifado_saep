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


# Tratamento global de erros: respostas JSON em vez de traceback HTML.
@app.errorhandler(404)
def rota_nao_encontrada(_erro):
    return jsonify({"mensagem": "Rota não encontrada."}), 404


@app.errorhandler(405)
def metodo_nao_permitido(_erro):
    return jsonify({"mensagem": "Método não permitido para esta rota."}), 405


@app.errorhandler(500)
def erro_interno(_erro):
    return jsonify({"mensagem": "Erro interno do servidor."}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=True)
