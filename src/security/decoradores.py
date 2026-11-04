from functools import wraps

from flask import g, request

from src.security.perfis import PERFIS
from src.services import auth_service
from src.utils.erros import ErroApi


def _autenticar():
    partes = request.headers.get("Authorization", "").split()
    if len(partes) != 2 or partes[0].lower() != "bearer":
        raise ErroApi("Autenticação necessária.", 401)
    g.usuario = auth_service.usuario_do_token(partes[1])


def requer_perfil(*perfis):
    def decorador(funcao):
        @wraps(funcao)
        def interno(*args, **kwargs):
            _autenticar()
            if g.usuario["perfil"] not in perfis:
                raise ErroApi(
                    "Acesso negado: seu perfil não tem permissão para esta operação.",
                    403,
                )
            return funcao(*args, **kwargs)

        return interno

    return decorador


login_obrigatorio = requer_perfil(*PERFIS)
