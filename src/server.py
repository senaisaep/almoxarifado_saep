import os
import sys
from pathlib import Path

from flask import Flask, jsonify, send_from_directory
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.routes.movimentacoes import movimentacoes
from src.routes.produtos import produtos

load_dotenv(ROOT_DIR / ".env")

STATIC_DIR = ROOT_DIR / "frontend"
app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path="/")

app.register_blueprint(produtos)
app.register_blueprint(movimentacoes)

@app.get("/")
def inicio():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return send_from_directory(str(STATIC_DIR), "index.html")
    return jsonify({"status": "online", "sistema": "Almoxarifado SAEP"}), 200

@app.get("/api/status")
def status():
    return jsonify({"status": "online", "sistema": "Almoxarifado SAEP"}), 200

@app.errorhandler(404)
def rota_nao_encontrada(erro):
    if (STATIC_DIR / "index.html").exists():
        return jsonify({"erro": "Rota não encontrada."}), 404
    return jsonify({"erro": "Recurso não encontrado."}), 404

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=int(os.getenv("PORT", "5000")),
        debug=True
    )