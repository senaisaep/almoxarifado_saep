from flask import Flask
from dotenv import load_dotenv
import os

from routes.auth import auth_bp
from routes.estoque import estoque_bp

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv(
    "SECRET_KEY",
    "chave_secreta_do_projeto"
)

app.register_blueprint(auth_bp)
app.register_blueprint(estoque_bp)


@app.route("/")
def inicio():
    return {
        "mensagem": "Sistema de Almoxarifado funcionando!"
    }


if __name__ == "__main__":
    app.run(debug=True)