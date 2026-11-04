from flask import session

USUARIOS = {
    "admin": {
        "senha": "admin123",
        "permissoes": ["estoque", "relatorios", "admin"],
    },
    "estoque": {
        "senha": "estoque123",
        "permissoes": ["estoque"],
    },
    "relatorios": {
        "senha": "relatorio123",
        "permissoes": ["relatorios"],
    },
}


def autenticar_usuario(usuario, senha):
    dados = USUARIOS.get(usuario)
    if not dados or dados["senha"] != senha:
        return False

    session["usuario"] = {
        "nome": usuario,
        "permissao": dados["permissoes"][0],
        "permissoes": dados["permissoes"],
    }
    return True


def usuario_logado():
    return "usuario" in session


def possui_permissao(*permissoes):
    usuario = session.get("usuario")
    if not usuario:
        return False

    permissoes_usuario = set(usuario.get("permissoes", []))
    return any(permissao in permissoes_usuario for permissao in permissoes)


def logout():
    session.clear()
