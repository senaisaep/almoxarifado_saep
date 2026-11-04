from flask import Blueprint, jsonify, render_template, request, session
from services import estoque_service, produto_service
from services.auth_service import requer_perfil


estoque_bp = Blueprint("estoque", __name__)


@estoque_bp.route("/estoque", methods=["GET"])
@requer_perfil()
def exibir_estoque():
    return render_template(
        "estoque.html",
        produtos=produto_service.listar_produtos(),
        movimentacoes=estoque_service.listar_movimentacoes(),
        nome=session.get("nome"),
        perfil=session.get("perfil"),
    )


@estoque_bp.route("/movimentacoes", methods=["GET"])
@requer_perfil()
def listar_movimentacoes():
    return jsonify(estoque_service.listar_movimentacoes()), 200


@estoque_bp.route("/movimentacoes/entrada", methods=["POST"])
@requer_perfil()
def registrar_entrada():
    return _registrar_movimentacao("entrada")


@estoque_bp.route("/movimentacoes/saida", methods=["POST"])
@requer_perfil()
def registrar_saida():
    return _registrar_movimentacao("saida")


def _registrar_movimentacao(tipo):
    resultado, status = estoque_service.registrar_movimentacao(
        request.get_json(silent=True) or {},
        tipo,
        session["usuario_id"],
    )
    if status != 201:
        return jsonify({"mensagem": resultado}), status
    return jsonify({"mensagem": "Movimentação registrada.", "id": resultado}), status