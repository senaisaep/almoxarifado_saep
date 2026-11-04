from flask import Blueprint, g, jsonify, request

from src.services import estoque_service
from src.utils.auth import login_obrigatorio

movimentacoes = Blueprint("movimentacoes", __name__)


@movimentacoes.route("/movimentacoes", methods=["GET"])
@login_obrigatorio
def listar_movimentacoes():
    return jsonify(estoque_service.listar_movimentacoes(request.args)), 200


@movimentacoes.route("/movimentacoes/entrada", methods=["POST"])
@login_obrigatorio
def registrar_entrada():
    resultado = estoque_service.registrar_entrada(request.get_json(silent=True), g.usuario["id"])
    return jsonify({"mensagem": "Entrada registrada com sucesso.", **resultado}), 201


@movimentacoes.route("/movimentacoes/saida", methods=["POST"])
@login_obrigatorio
def registrar_saida():
    resultado = estoque_service.registrar_saida(request.get_json(silent=True), g.usuario["id"])
    return jsonify({"mensagem": "Saída registrada com sucesso.", **resultado}), 201
