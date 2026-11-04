usuarios = {
    "OperadorAl":{
        "senha": "operador123",
        "permissao": "operar"
    },
    "AdmAl":{
        "senha": "adm123",
        "permissao": "adm"
    }
}
def autenticar(login, senha):
    if login in usuarios:
        if usuarios[login]["senha"]==senha:
            return {
                "login": login,
                "permissao": usuarios[login]["permissao"]
            }
    return None