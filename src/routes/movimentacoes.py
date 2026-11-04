from flask import Blueprint, jsonify, request

from src.services import movimentacao_service

movimentacoes = Blueprint("movimentacoes", __name__, url_prefix="/api")


@movimentacoes.get("/movimentacoes")
def listar():
    return jsonify(movimentacao_service.listar_movimentacoes()), 200


@movimentacoes.post("/movimentacoes/entrada")
def registrar_entrada():
    dados = request.get_json(silent=True) or {}
    try:
        movimentacao = movimentacao_service.registrar_entrada(
            dados.get("produto_id"),
            dados.get("quantidade"),
            dados.get("responsavel")
        )
        return jsonify({"mensagem": "Entrada registrada.", "movimentacao": movimentacao}), 201
    except LookupError as erro:
        return jsonify({"erro": str(erro)}), 404
    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 400


@movimentacoes.post("/movimentacoes/saida")
def registrar_saida():
    dados = request.get_json(silent=True) or {}
    try:
        movimentacao = movimentacao_service.registrar_saida(
            dados.get("produto_id"),
            dados.get("quantidade"),
            dados.get("responsavel")
        )
        return jsonify({"mensagem": "Saida registrada.", "movimentacao": movimentacao}), 201
    except LookupError as erro:
        return jsonify({"erro": str(erro)}), 404
    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 400
