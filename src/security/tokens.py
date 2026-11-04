from datetime import datetime, timedelta, timezone

import jwt

from src.config import settings
from src.utils.erros import ErroApi


def gerar_token(usuario):
    agora = datetime.now(timezone.utc)
    payload = {
        "sub": str(usuario["id"]),
        "perfil": usuario["perfil"],
        "iat": agora,
        "exp": agora + timedelta(minutes=settings.jwt_expira_minutos()),
    }
    return jwt.encode(payload, settings.secret_key(), algorithm="HS256")


def decodificar_token(token):
    try:
        return jwt.decode(
            token,
            settings.secret_key(),
            algorithms=["HS256"],  # lista fixa: impede ataque "alg=none"
            options={"require": ["exp", "sub"]},
        )
    except jwt.ExpiredSignatureError:
        raise ErroApi("Sessão expirada. Faça login novamente.", 401)
    except jwt.InvalidTokenError:
        raise ErroApi("Token inválido.", 401)
