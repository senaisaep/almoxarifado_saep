from werkzeug.security import check_password_hash, generate_password_hash

# PBKDF2-SHA256 com sal aleatório por senha (compatível com qualquer build do Python)
_METODO = "pbkdf2:sha256:600000"


def gerar_hash(senha):
    return generate_password_hash(senha, method=_METODO)


def verificar_senha(senha_hash, senha):
    return check_password_hash(senha_hash, senha)
