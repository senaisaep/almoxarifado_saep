from flask import Flask, jsonify
from Controle.estoque_controle import estoque, inicializar_administrador
from Controle.produto_controle import produtos
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.register_blueprint(estoque)
app.register_blueprint(produtos)

@app.route("/", methods=["GET"])
def inicio():
    return jsonify({"mensagem": "API do Sistema de Almoxarifado"}), 200

if __name__ == "__main__":
    inicializar_administrador()
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=True)
