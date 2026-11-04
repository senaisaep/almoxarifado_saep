from src.config import settings
from src.config.db import transacao
from src.repositories import usuario_repository as usuario_repo
from src.security.senhas import gerar_hash, verificar_senha
from src.security.tokens import decodificar_token, gerar_token
from src.utils.erros import ErroApi
from src.utils.validacao import senha_forte

# Hash descartável: gasta o mesmo tempo de CPU quando o e-mail não existe,
# evitando descobrir e-mails cadastrados pelo tempo de resposta.
_HASH_FALSO = gerar_hash("senha-descartavel-1")


def _dados_publicos(usuario):
    return {k: usuario[k] for k in ("id", "nome", "email", "perfil")}


def login(email, senha):
    email = (email or "").strip().lower() if isinstance(email, str) else ""
    if not email or not isinstance(senha, str) or not senha:
        raise ErroApi("Informe e-mail e senha.", 400)

    # Resultado decidido DENTRO da transação (para que a contagem de falhas seja
    # gravada) e o erro é lançado só DEPOIS do commit.
    with transacao() as cur:
        usuario = usuario_repo.buscar_por_email(cur, email)
        if usuario is None:
            verificar_senha(_HASH_FALSO, senha)
            resultado = "invalido"
        elif usuario["bloqueado"]:
            resultado = "bloqueado"
        else:
            if usuario["bloqueado_ate"]:  # bloqueio já expirou
                usuario_repo.zerar_falhas(cur, usuario["id"])
            if usuario["ativo"] and verificar_senha(usuario["senha_hash"], senha):
                usuario_repo.zerar_falhas(cur, usuario["id"])
                resultado = "ok"
            else:
                usuario_repo.registrar_falha(
                    cur,
                    usuario["id"],
                    settings.login_max_tentativas(),
                    settings.login_bloqueio_minutos(),
                )
                resultado = "invalido"

    if resultado == "bloqueado":
        raise ErroApi(
            "Conta temporariamente bloqueada por excesso de tentativas. "
            "Tente novamente mais tarde.",
            423,
        )
    if resultado != "ok":
        raise ErroApi("Credenciais inválidas.", 401)
    return {
        "token": gerar_token(usuario),
        "tipo": "Bearer",
        "expira_em_minutos": settings.jwt_expira_minutos(),
        "usuario": _dados_publicos(usuario),
    }


def usuario_do_token(token):
    """Valida o token E confere no banco se o usuário continua ativo,
    com o perfil atual (desativar/rebaixar vale imediatamente)."""
    payload = decodificar_token(token)
    try:
        usuario_id = int(payload["sub"])
    except (TypeError, ValueError):
        raise ErroApi("Token inválido.", 401)
    with transacao() as cur:
        usuario = usuario_repo.buscar_por_id(cur, usuario_id)
    if usuario is None or not usuario["ativo"]:
        raise ErroApi("Usuário inexistente ou inativo.", 401)
    return _dados_publicos(usuario)


def trocar_senha(usuario_id, senha_atual, nova_senha):
    senha_forte(nova_senha)
    with transacao() as cur:
        atual = usuario_repo.buscar_por_id(cur, usuario_id)
        completo = usuario_repo.buscar_por_email(cur, atual["email"])
        if not isinstance(senha_atual, str) or not verificar_senha(
            completo["senha_hash"], senha_atual
        ):
            erro = True
        else:
            erro = False
            usuario_repo.atualizar_senha(cur, usuario_id, gerar_hash(nova_senha))
    if erro:
        raise ErroApi("Senha atual incorreta.", 400)
