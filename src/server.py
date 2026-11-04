from flask import Flask, jsonify
from src.routes.estoque import estoque
from src.routes.auth import auth
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.register_blueprint(estoque)
app.register_blueprint(auth)


@app.route("/", methods=["GET"])
def inicio():
    return jsonify({
        "mensagem": "API do Sistema de Almoxarifado funcionando!"
    }), 200


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=int(os.getenv("PORT", "5000")),
        debug=True
    )
