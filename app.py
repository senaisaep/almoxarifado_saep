from flask import Flask
from controllers.auth_controller import auth_bp
from controllers.sistema_controller import sistema
from controllers.protutos_controller import produtos_bp
from src.auth import configurar_seguranca
from src.routes.estoque import estoque

app = Flask(__name__)

app.secret_key = "chavesegura"
configurar_seguranca(app)

app.register_blueprint(auth_bp)
app.register_blueprint(sistema)
app.register_blueprint(produtos_bp)
app.register_blueprint(estoque)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
