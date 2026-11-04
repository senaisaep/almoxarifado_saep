from flask import Blueprint, request, redirect, url_for, render_template, session
from werkzeug.security import check_password_hash

from models.usuarios import buscar_por_nome, criar_usuario

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login_route():
    if request.method == "POST":
        dados = request.get_json(silent=True) if request.is_json else request.form
        username = (dados.get("username", "") if dados else "").strip()
        senha = dados.get("senha") or dados.get("password", "") if dados else ""

        if not username or not senha:
            if request.is_json:
                return {"mensagem": "Usuário e senha são obrigatórios."}, 400
            return render_template("login.html", mensagem="Usuário e senha são obrigatórios."), 400

        usuario = buscar_por_nome(username)
        if not usuario or not check_password_hash(usuario["senha_hash"], senha):
            if request.is_json:
                return {"mensagem": "Usuário ou senha inválidos."}, 401
            return render_template("login.html", mensagem="Usuário ou senha inválidos."), 401

        session.clear()
        session["usuario_id"] = usuario["id"]
        session["usuario"] = usuario["username"]
        session["tipo"] = usuario["tipo"]
        session.permanent = True
        if request.is_json:
            return {"mensagem": "Autenticação realizada com sucesso.", "usuario": {
                "id": usuario["id"], "username": usuario["username"], "tipo": usuario["tipo"]
            }}, 200
        return redirect(url_for("produtos.produtos_route"))

    return render_template("login.html")


@auth_bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        dados = request.get_json(silent=True) if request.is_json else request.form
        username = (dados.get("username", "") if dados else "").strip()
        senha = dados.get("senha", dados.get("password", "")) if dados else ""
        tipo = (dados.get("tipo", "consulta") if dados else "consulta").strip()

        try:
            usuario = criar_usuario(username, senha, tipo)
        except ValueError as erro:
            if request.is_json:
                return {"mensagem": str(erro)}, 400
            return render_template("cadastro.html", mensagem=str(erro)), 400
        except Exception:
            if request.is_json:
                return {"mensagem": "Não foi possível cadastrar o usuário."}, 400
            return render_template("cadastro.html", mensagem="Não foi possível cadastrar o usuário."), 400

        if request.is_json:
            return {"mensagem": "Usuário cadastrado com sucesso.", "usuario": usuario}, 201

        session.clear()
        session["usuario_id"] = usuario["id"]
        session["usuario"] = usuario["username"]
        session["tipo"] = usuario["tipo"]
        session.permanent = True
        return redirect(url_for("produtos.produtos_route"))

    return render_template("cadastro.html")


@auth_bp.route("/usuarios", methods=["POST"])
def cadastrar_usuario():
    dados = request.get_json(silent=True) if request.is_json else request.form
    username = (dados.get("username", "") if dados else "").strip()
    senha = dados.get("senha") or dados.get("password", "") if dados else ""
    tipo = (dados.get("tipo", "consulta") if dados else "consulta").strip()

    try:
        usuario = criar_usuario(username, senha, tipo)
        return {"mensagem": "Usuário cadastrado com sucesso.", "usuario": usuario}, 201
    except ValueError as erro:
        return {"mensagem": str(erro)}, 400
    except Exception as erro:
        return {"mensagem": "Não foi possível cadastrar o usuário."}, 400


@auth_bp.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for("auth.login_route"))
