from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from src.config.db import conectar
from src.services.auth_service import perfil_obrigatorio

usuarios = Blueprint("usuarios", __name__)

@usuarios.route("/usuarios", methods=["GET", "POST"])
@perfil_obrigatorio("administrador")
def gerenciar():
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)
    try:
        if request.method == "POST":
            nome = request.form.get("nome", "").strip()
            email = request.form.get("email", "").strip().lower()
            senha = request.form.get("senha", "")
            perfil = request.form.get("perfil", "")
            if not nome or not email or len(senha) < 8 or perfil not in ("operador", "administrador"):
                flash("Preencha os campos. A senha deve ter pelo menos 8 caracteres.", "erro")
            else:
                try:
                    cursor.execute("INSERT INTO usuarios (nome,email,senha_hash,perfil) VALUES (%s,%s,%s,%s)",
                                   (nome,email,generate_password_hash(senha),perfil))
                    conexao.commit()
                    flash("Usuário cadastrado.", "sucesso")
                except Exception:
                    conexao.rollback()
                    flash("Não foi possível cadastrar. Verifique se o e-mail já está em uso.", "erro")
        cursor.execute("SELECT id,nome,email,perfil,ativo FROM usuarios ORDER BY nome")
        return render_template("usuarios.html", usuarios=cursor.fetchall())
    finally:
        cursor.close()
        conexao.close()
