import mysql.connector

from src.config.db import transacao
from src.repositories import usuario_repository as usuario_repo
from src.security.perfis import PERFIS
from src.security.senhas import gerar_hash
from src.utils.erros import ErroApi
from src.utils.validacao import email_valido, senha_forte, texto_obrigatorio


def _perfil_valido(perfil):
    if perfil not in PERFIS:
        raise ErroApi(f"Perfil inválido. Use: {', '.join(PERFIS)}.", 400)
    return perfil


def listar():
    with transacao() as cur:
        return usuario_repo.listar(cur)


def consultar(usuario_id):
    with transacao() as cur:
        usuario = usuario_repo.buscar_por_id(cur, usuario_id)
    if usuario is None:
        raise ErroApi("Usuário não encontrado.", 404)
    return usuario


def criar(dados):
    nome = texto_obrigatorio(dados.get("nome"), "nome", 120)
    email = email_valido(dados.get("email"))
    senha_forte(dados.get("senha"))
    perfil = _perfil_valido(dados.get("perfil", "consulta"))
    senha_hash = gerar_hash(dados["senha"])
    try:
        with transacao() as cur:
            if usuario_repo.buscar_por_email(cur, email):
                raise ErroApi("Já existe usuário com este e-mail.", 409)
            return usuario_repo.inserir(cur, nome, email, senha_hash, perfil)
    except mysql.connector.IntegrityError:
        raise ErroApi("Já existe usuário com este e-mail.", 409)


def atualizar(usuario_id, dados, usuario_logado_id):
    with transacao() as cur:
        atual = usuario_repo.buscar_por_id(cur, usuario_id)
        if atual is None:
            raise ErroApi("Usuário não encontrado.", 404)
        nome = texto_obrigatorio(dados.get("nome", atual["nome"]), "nome", 120)
        perfil = _perfil_valido(dados.get("perfil", atual["perfil"]))
        ativo = dados.get("ativo", bool(atual["ativo"]))
        if not isinstance(ativo, bool):
            raise ErroApi("O campo ativo deve ser true ou false.", 400)
        if usuario_id == usuario_logado_id and (
            perfil != atual["perfil"] or not ativo
        ):
            raise ErroApi(
                "Você não pode alterar o próprio perfil nem desativar a própria conta.",
                400,
            )
        usuario_repo.atualizar(cur, usuario_id, nome, perfil, ativo)


def redefinir_senha(usuario_id, nova_senha):
    senha_forte(nova_senha)
    senha_hash = gerar_hash(nova_senha)
    with transacao() as cur:
        if usuario_repo.buscar_por_id(cur, usuario_id) is None:
            raise ErroApi("Usuário não encontrado.", 404)
        usuario_repo.atualizar_senha(cur, usuario_id, senha_hash)


def desativar(usuario_id, usuario_logado_id):
    """Não há exclusão física: movimentações guardam o responsável (auditoria)."""
    if usuario_id == usuario_logado_id:
        raise ErroApi("Você não pode desativar a própria conta.", 400)
    with transacao() as cur:
        atual = usuario_repo.buscar_por_id(cur, usuario_id)
        if atual is None:
            raise ErroApi("Usuário não encontrado.", 404)
        usuario_repo.atualizar(cur, usuario_id, atual["nome"], atual["perfil"], False)
