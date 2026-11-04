from models.auth_models import buscar_por_login
from werkzeug.security import check_password_hash


def autenticar(login, senha):

    if not login or not senha:
        return None

    usuario = buscar_por_login(login)

    if usuario is None:
        return None

    senha_valida = check_password_hash(
        usuario["senha"],
        senha
    )

    if not senha_valida:
        return None

    return usuario