sistema_usuarios = {
    "operador":{
        "permissao": "consultar"
    },
    "admin":{
        "permissao": "consultar"
    }
}
def autenticar(login):
    if login in sistema_usuarios:
        return{
            "permissao": sistema_usuarios["login"]["permissao"]
        }