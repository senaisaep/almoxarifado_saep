from functools import wraps

from flask import g, request

from src.services import auth_service
from src.utils.erros import ErroAPI


def login_obrigatorio(funcao):
    # Só deixa passar quem mandou o header "Authorization: Bearer <token>"
    # O usuário logado fica guardado em g.usuario para as rotas usarem
    @wraps(funcao)
    def interna(*args, **kwargs):
        partes = request.headers.get("Authorization", "").split()
        if len(partes) != 2 or partes[0].lower() != "bearer":
            raise ErroAPI("Envie o header 'Authorization: Bearer <token>'.", 401)
        g.usuario = auth_service.usuario_do_token(partes[1])
        return funcao(*args, **kwargs)
    return interna


def perfil_requerido(*perfis):
    # Usar logo abaixo de @login_obrigatorio. Ex.: @perfil_requerido("admin")
    def decorador(funcao):
        @wraps(funcao)
        def interna(*args, **kwargs):
            if g.usuario["perfil"] not in perfis:
                raise ErroAPI("Seu perfil não tem permissão para esta ação.", 403)
            return funcao(*args, **kwargs)
        return interna
    return decorador
