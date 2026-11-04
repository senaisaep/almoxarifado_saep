from flask import Flask, jsonify
from src.routes.estoque import estoque
from src.routes.auth import auth
from src.routes.usuarios import usuarios
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.getenv("SECRET_KEY", "chave-do-sistema")

app.register_blueprint(estoque)
app.register_blueprint(auth)
app.register_blueprint(usuarios)


@app.route("/", methods=["GET"])
def inicio():
    return jsonify({
        "mensagem": "API do Sistema de Almoxarifado"
    }), 200


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=int(os.getenv("PORT", "5000")),
        debug=True
    )