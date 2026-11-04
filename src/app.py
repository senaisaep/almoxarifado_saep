from flask import Flask, jsonify, render_template
from src.routes.estoque import estoque
from dotenv import load_dotenv
from flask import Flask, render_template
from config.autenticacao_controller import autentic
from controllers.venda_controller import cadastrar, lista
from config.sistema_controller import sistema


app = Flask(__name__)
app.secret_key = "chave-secreta"
app.register_blueprint(autentic)
app.register_blueprint(sistema)
@app.errorhandler(403)# handler lidar
def erro_403(erro):
    return render_template("erro403.html"), 403
app.run(debug=True)

@app.route("/", methods=["GET"])
def inicio():
    return jsonify({"mensagem": "API do Sistema de Almoxarifado"}), 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=True)
