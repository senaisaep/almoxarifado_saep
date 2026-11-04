import os
from flask import Flask, redirect, url_for
from dotenv import load_dotenv
from src.routes.auth import auth
from src.routes.produtos import produtos
from src.routes.estoque import estoque
from src.routes.usuarios import usuarios

load_dotenv()

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.getenv("SECRET_KEY", "chave-local-trocar"),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax"
)
app.register_blueprint(auth)
app.register_blueprint(produtos)
app.register_blueprint(estoque)
app.register_blueprint(usuarios)

@app.route("/inicio")
def inicio():
    return redirect(url_for("produtos.dashboard"))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=False)
