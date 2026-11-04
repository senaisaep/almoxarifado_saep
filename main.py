from flask import Flask, jsonify, render_template
from controllers.estoque_controller import estoque
from controllers.auth_controller import auth

app = Flask(__name__)

app.secret_key = "chave-secreta"

app.register_blueprint(estoque)

app.register_blueprint(auth)

@app.route("/", methods=["GET"])
def inicio():
    return jsonify({"mensagem": "API do Sistema de Almoxarifado"}), 200

@app.errorhandler(403)
def erro_403(erro):
    return render_template(
        "erro403.html"
    ), 403

app.run(debug=True)