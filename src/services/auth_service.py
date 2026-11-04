from werkzeug.security import generate_password_hash, check_password_hash
from repositories import usuario_repository


def cadastrar(nome, email, senha):
    if not nome or not email or not senha:
        return False, "Preencha todos os campos."

    if usuario_repository.buscar_por_email(email):
        return False, "Este email já está cadastrado."

    total = usuario_repository.contar_usuarios()

    if total == 0:
        perfil = "admin"
    else:
        perfil = "operador"

    senha_hash = generate_password_hash(senha)

    usuario_repository.criar_usuario(
        nome,
        email,
        senha_hash,
        perfil
    )

    return True, "Usuário cadastrado com sucesso."


def fazer_login(email, senha):
    usuario = usuario_repository.buscar_por_email(email)

    if not usuario:
        return None

    senha_correta = check_password_hash(
        usuario["senha"],
        senha
    )

    if senha_correta:
        return usuario

    return None