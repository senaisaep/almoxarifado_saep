from flask import Blueprint, g, jsonify, request

from src.security.decoradores import login_obrigatorio, requer_perfil
from src.security.perfis import ADMIN, ALMOXARIFE
from src.services import estoque_service
from src.utils.validacao import corpo_json

movimentacoes = Blueprint("movimentacoes", __name__, url_prefix="/movimentacoes")


@movimentacoes.route("", methods=["GET"])
@login_obrigatorio
def listar():
    return jsonify(estoque_service.listar_movimentacoes(request.args)), 200


@movimentacoes.route("/entrada", methods=["POST"])
@requer_perfil(ADMIN, ALMOXARIFE)
def registrar_entrada():
    dados = corpo_json(request)
    resultado = estoque_service.registrar_entrada(
        g.usuario["id"], dados.get("produto_id"), dados.get("quantidade")
    )
    return jsonify({"mensagem": "Entrada registrada com sucesso.", **resultado}), 201


@movimentacoes.route("/saida", methods=["POST"])
@requer_perfil(ADMIN, ALMOXARIFE)
def registrar_saida():
    dados = corpo_json(request)
    resultado = estoque_service.registrar_saida(
        g.usuario["id"], dados.get("produto_id"), dados.get("quantidade")
    )
    return jsonify({"mensagem": "Saída registrada com sucesso.", **resultado}), 201
