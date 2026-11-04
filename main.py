from flask import Flask
from controller.sistema_controller import cadastrar

app = Flask(__name__)

@app.route("/sistema_usuarios", methods=["POST"])
def salvar_sistema_usuarios():
    return cadastrar()

app.run(debug=True)