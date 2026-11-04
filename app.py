from pathlib import Path
from flask import Flask

from controllers.auth_controller import auth_bp
from controllers.produto_controller import produto_bp

BASE_DIR = Path(__file__).resolve().parent

app = Flask(
    __name__,
    template_folder=BASE_DIR / "templates",
    static_folder=BASE_DIR / "static"
)

app.secret_key = "troque-por-uma-chave-segura"

app.register_blueprint(auth_bp)
app.register_blueprint(produto_bp)


if __name__ == "__main__":
    app.run(debug=True)