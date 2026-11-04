# Regras de login, token e cadastro de usuários
import os
from datetime import datetime, timedelta, timezone

import jwt
from mysql.connector.errors import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from src.config.db import transacao
from src.repositories import usuario_repository
from src.utils import validacao
from src.utils.erros import ErroAPI


def _gerar_token(usuario):
    payload = {
        "sub": str(usuario["id"]),
        "exp": datetime.now(timezone.utc) + timedelta(hours=8),
    }
    return jwt.encode(payload, os.getenv("JWT_SECRET"), algorithm="HS256")


def usuario_do_token(token):
    # Confere o token e busca o usuário no banco (usuário desativado perde o acesso na hora)
    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise ErroAPI("Token expirado. Faça login novamente.", 401)
    except jwt.InvalidTokenError:
        raise ErroAPI("Token inválido.", 401)

    with transacao() as cursor:
        usuario = usuario_repository.buscar_por_id(cursor, int(payload["sub"]))
    if usuario is None or not usuario["ativo"]:
        raise ErroAPI("Usuário inexistente ou inativo.", 401)
    return usuario


def login(dados):
    dados = validacao.exigir_json(dados)
    email = validacao.texto(dados.get("email"), "email").lower()
    senha = validacao.texto(dados.get("senha"), "senha")

    with transacao() as cursor:
        usuario = usuario_repository.buscar_por_email(cursor, email)

    # Mesma mensagem para e-mail inexistente e senha errada, para não dar pista a quem tenta invadir
    if usuario is None or not usuario["ativo"] or not check_password_hash(usuario["senha_hash"], senha):
        raise ErroAPI("E-mail ou senha incorretos.", 401)

    return {
        "token": _gerar_token(usuario),
        "usuario": {"id": usuario["id"], "nome": usuario["nome"], "perfil": usuario["perfil"]},
    }


def cadastrar(dados):
    dados = validacao.exigir_json(dados)
    nome = validacao.texto(dados.get("nome"), "nome", maximo=120)
    email = validacao.texto(dados.get("email"), "email", maximo=150).lower()
    senha = validacao.texto(dados.get("senha"), "senha")

    if "@" not in email:
        raise ErroAPI("E-mail inválido.")
    if len(senha) < 6:
        raise ErroAPI("A senha deve ter no mínimo 6 caracteres.")

    # Quem se cadastra sozinho sempre vira operador. O admin já vem criado no bd.sql
    try:
        with transacao() as cursor:
            return usuario_repository.inserir(
                cursor, nome, email, generate_password_hash(senha), "operador")
    except IntegrityError:
        raise ErroAPI("Já existe um usuário com este e-mail.", 409)
