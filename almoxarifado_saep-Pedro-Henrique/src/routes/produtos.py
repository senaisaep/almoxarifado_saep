from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.config.db import conectar
from src.services.auth_service import login_obrigatorio, perfil_obrigatorio

produtos = Blueprint("produtos", __name__)

@produtos.route("/")
@login_obrigatorio
def dashboard():
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)
    try:
        cursor.execute("""SELECT COUNT(*) total, COALESCE(SUM(quantidade_estoque),0) unidades,
                          COALESCE(SUM(CASE WHEN quantidade_estoque <= 5 THEN 1 ELSE 0 END),0) baixo
                          FROM produtos""")
        resumo = cursor.fetchone()
        cursor.execute("""SELECT m.data_hora, m.tipo, m.quantidade, p.nome produto, u.nome usuario
                          FROM movimentacoes m JOIN produtos p ON p.id=m.produto_id
                          JOIN usuarios u ON u.id=m.usuario_id
                          ORDER BY m.data_hora DESC, m.id DESC LIMIT 5""")
        recentes = cursor.fetchall()
        return render_template("dashboard.html", resumo=resumo, recentes=recentes)
    finally:
        cursor.close()
        conexao.close()

@produtos.route("/produtos")
@login_obrigatorio
def listar():
    busca = request.args.get("busca", "").strip()
    data = request.args.get("data", "").strip()
    pagina = max(1, request.args.get("pagina", 1, type=int))
    por_pagina = 8
    condicoes, parametros = [], []
    if busca:
        condicoes.append("nome LIKE %s")
        parametros.append(f"%{busca}%")
    if data:
        condicoes.append("DATE(data_cadastro)=%s")
        parametros.append(data)
    where = " WHERE " + " AND ".join(condicoes) if condicoes else ""
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)
    try:
        cursor.execute(f"SELECT COUNT(*) total FROM produtos{where}", tuple(parametros))
        total = cursor.fetchone()["total"]
        cursor.execute(
            f"SELECT * FROM produtos{where} ORDER BY nome LIMIT %s OFFSET %s",
            tuple(parametros + [por_pagina, (pagina-1)*por_pagina])
        )
        itens = cursor.fetchall()
        return render_template("produtos.html", produtos=itens, busca=busca, data=data,
                               pagina=pagina, paginas=max(1, (total+por_pagina-1)//por_pagina),
                               total=total)
    finally:
        cursor.close()
        conexao.close()

@produtos.route("/produtos/novo", methods=["GET", "POST"])
@perfil_obrigatorio("operador", "administrador")
def novo():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        descricao = request.form.get("descricao", "").strip()
        try:
            preco = float(request.form.get("preco", "0").replace(",", "."))
            if not nome or preco < 0:
                raise ValueError
        except ValueError:
            flash("Confira os campos. Preço e quantidade não podem ser negativos.", "erro")
            return render_template("produto_form.html", produto=None)
        conexao = conectar()
        cursor = conexao.cursor()
        try:
            cursor.execute("INSERT INTO produtos (nome, descricao, preco, quantidade_estoque) VALUES (%s,%s,%s,0)",
                           (nome, descricao, preco))
            conexao.commit()
            flash("Produto cadastrado com sucesso.", "sucesso")
            return redirect(url_for("produtos.listar"))
        finally:
            cursor.close()
            conexao.close()
    return render_template("produto_form.html", produto=None)

@produtos.route("/produtos/<int:produto_id>/editar", methods=["GET", "POST"])
@perfil_obrigatorio("operador", "administrador")
def editar(produto_id):
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM produtos WHERE id=%s", (produto_id,))
        produto = cursor.fetchone()
        if not produto:
            flash("Produto não encontrado.", "erro")
            return redirect(url_for("produtos.listar"))
        if request.method == "POST":
            nome = request.form.get("nome", "").strip()
            descricao = request.form.get("descricao", "").strip()
            try:
                preco = float(request.form.get("preco", "0").replace(",", "."))
                if not nome or preco < 0:
                    raise ValueError
            except ValueError:
                flash("Confira os campos informados.", "erro")
                return render_template("produto_form.html", produto=produto)
            cursor.execute("""UPDATE produtos SET nome=%s, descricao=%s, preco=%s
                              WHERE id=%s""",
                           (nome, descricao, preco, produto_id))
            conexao.commit()
            flash("Produto atualizado.", "sucesso")
            return redirect(url_for("produtos.listar"))
        return render_template("produto_form.html", produto=produto)
    finally:
        cursor.close()
        conexao.close()

@produtos.route("/produtos/<int:produto_id>/excluir", methods=["POST"])
@perfil_obrigatorio("administrador")
def excluir(produto_id):
    conexao = conectar()
    cursor = conexao.cursor()
    try:
        cursor.execute("DELETE FROM produtos WHERE id=%s", (produto_id,))
        if cursor.rowcount == 0:
            flash("Produto não encontrado.", "erro")
        else:
            conexao.commit()
            flash("Produto excluído.", "sucesso")
    except Exception:
        conexao.rollback()
        flash("Não foi possível excluir: existem movimentações vinculadas a este produto.", "erro")
    finally:
        cursor.close()
        conexao.close()
    return redirect(url_for("produtos.listar"))
