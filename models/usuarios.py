usuarios = {
    "Maria":{
        "senha": "123",
        "permissao": "sistema"
    },
    "João":{
        "senha": "456",
        "permissao":"almoxarifado"
    }
}
def auntenticar(login, senha):
    if login in usuarios:
        if usuarios[login]["senha"] == senha:
            return {
                "login": login,
                "permissao": usuarios[login]["permissao"]
            }