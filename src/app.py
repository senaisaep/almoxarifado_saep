import os

from dotenv import load_dotenv
from flask import Flask

from routes.estoque import estoque
from routes.sistema import sistema

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "almoxarifado-secret")
app.register_blueprint(sistema)
app.register_blueprint(estoque)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=True)
