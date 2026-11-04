ususario = {
    "Operador de Almoxarifado":{
        "senha": "12345",
        "permissao": "produtos",
        "ipc": "1"
    },
    "Administrador": {
        "senha": "09876",
        "permissao": "estoque",
        "ipc": "9"
    },
    "Assistente":{
        "senha": "123",
        "permissao": "catalogo",
        "ipc": "2"
    }
}
def autenticacao(loguin, senha, ipc):
    if loguin in ususario [loguin]["senha"]["ipc"] == senha:
        return {
            "loguin": loguin,
            "permissao": ususario[loguin]["permissao"]
        }
    return None