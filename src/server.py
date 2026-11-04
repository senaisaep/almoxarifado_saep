from flask import Flask, jsonify
from config.db import Conectar, Criar_tabelas
from routes.estoque import estoque
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.register_blueprint(estoque)

@app.route("/", methods=["GET"])
def inicio():
    return jsonify({"mensagem": "API do Sistema de Almoxarifado"}), 200

if __name__ == "__main__":
    Conectar()
    Criar_tabelas()
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=True)