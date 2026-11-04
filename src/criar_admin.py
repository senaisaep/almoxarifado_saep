from models.usuario import cadastrar, buscar_email

nome = input("Nome: ")
email = input("Email: ")
senha = input("Senha: ")

if buscar_email(email):
    print("Usuário já existe.")
else:
    cadastrar(nome, email, senha, "administrador")
    print("Administrador criado com sucesso!")
