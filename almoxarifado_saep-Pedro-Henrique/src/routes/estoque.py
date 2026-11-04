from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from src.config.db import conectar
from src.services.auth_service import login_obrigatorio
from src.services.estoque_service import registrar_movimentacao, EstoqueErro

estoque = Blueprint("estoque", __name__)

@estoque.route("/movimentacoes", methods=["GET", "POST"])
@login_obrigatorio
def movimentacoes():
    if request.method == "POST":
        try:
            registrar_movimentacao(request.form.get("produto_id"),
                                   request.form.get("quantidade"),
                                   request.form.get("tipo"),
                                   session["usuario"]["id"])
            flash("Movimentação registrada e estoque atualizado.", "sucesso")
            return redirect(url_for("estoque.movimentacoes"))
        except EstoqueErro as erro:
            flash(str(erro), "erro")
        except Exception:
            flash("Não foi possível registrar a movimentação. Tente novamente.", "erro")

    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, nome, quantidade_estoque FROM produtos ORDER BY nome")
        lista_produtos = cursor.fetchall()
        cursor.execute("""SELECT m.id, m.tipo, m.quantidade, m.data_hora, p.nome produto, u.nome usuario
                          FROM movimentacoes m JOIN produtos p ON p.id=m.produto_id
                          JOIN usuarios u ON u.id=m.usuario_id
                          ORDER BY m.data_hora DESC, m.id DESC LIMIT 100""")
        historico = cursor.fetchall()
        return render_template("movimentacoes.html", produtos=lista_produtos, historico=historico)
    finally:
        cursor.close()
        conexao.close()
