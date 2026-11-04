usuarios = {
    "operador": {
        "senha": "op123",
        "permissao": "produtos"
    },
    "administrador": {
        "senha": "adm123",
        "permissao": "movimentacoes"
    }
}

def autenticar(login, senha):
    if login in usuarios:
        if usuarios[login]["senha"] == senha:
            return {
                "login": login,
                "permissao": usuarios[login]["permissao"]
            }
        return None