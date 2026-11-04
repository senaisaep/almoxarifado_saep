usuarios = {
    "Operador de Almoxarifado":{
        "senha": "123",
        "permissao": "opr",
    },
    "Administrador do Sistema":{
        "senha": "456",
        "permissao": "adm"
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