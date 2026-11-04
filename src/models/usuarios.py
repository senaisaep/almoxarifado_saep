usuarios = {
    "Almoxarifado": {
        "senha": "123",
        "permisao": "registrar_produto, retirar_produto, lista_produtos"
    },
    "ADM Sistema": {
        "senha": "456",
        "permisao": "relatorios"
    }
}

def autenticar(login, senha):
    if login in usuarios: 
        if usuarios[login]["senha"] == senha:
            return {
                "login": login,
                "permisao": usuarios[login]["permisao"]
            }
    return None