from flask import Blueprint, request, jsonify

sistema = Blueprint("sistema", __name__)

@sistema.route("/status", methods=["GET"])
def status():
    if request.method == "GET":
        return jsonify({"mensagem": "Sistema operacional."}), 200
    else:
        return jsonify({"mensagem": "Método não permitido."}), 405
