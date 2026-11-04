from flask import Flask, jsonify, Blueprint, render_template
from estoque import estoque
from controllers.auth_controller import auth
from dotenv import load_dotenv
from db import conectar, criar_banco

load_dotenv()

app = Flask(__name__)

criar_banco()

app.register_blueprint(auth)
app.register_blueprint(estoque)

@app.errorhandler(403)
def erro_403(erro):
    return render_template(
        "erro403.html"
    ), 403

app.run(debug=True)
