import json
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:5000"

def chamar(metodo, caminho, corpo=None, token=None):
    dados = json.dumps(corpo).encode() if corpo is not None else None
    req = urllib.request.Request(BASE + caminho, data=dados, method=metodo)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode() or "null")
    except urllib.error.HTTPError as erro:
        return erro.code, json.loads(erro.read().decode() or "null")

print("=== TESTES DE LOGIN (admin x operador) ===\n")

for nome, email, senha, esperado in [
    ("Login admin correto",     "admin@almoxarifado.com",    "admin123",     200),
    ("Login operador correto",  "operador@almoxarifado.com", "operador123",  200),
    ("Senha errada",            "admin@almoxarifado.com",    "errada",       401),
    ("E-mail inexistente",      "ninguem@x.com",             "admin123",     401),
]:
    status, r = chamar("POST", "/auth/login", {"email": email, "senha": senha})
    ok = status == esperado
    perfil = r.get("usuario", {}).get("perfil") if isinstance(r, dict) else None
    tem_token = isinstance(r, dict) and bool(r.get("token"))
    print(f"[{'OK' if ok else 'FALHOU'}] {nome}: HTTP {status} (esperado {esperado})"
          + (f" | perfil={perfil} token={tem_token}" if ok else f" | {r}"))

# guarda os tokens para os testes de permissão
_, admin = chamar("POST", "/auth/login", {"email": "admin@almoxarifado.com", "senha": "admin123"})
_, oper = chamar("POST", "/auth/login", {"email": "operador@almoxarifado.com", "senha": "operador123"})
t_admin, t_oper = admin["token"], oper["token"]

print("\n=== TOKEN / PERMISSÕES ===\n")

status, _ = chamar("GET", "/produtos")
print(f"[{'OK' if status == 401 else 'FALHOU'}] Sem token -> HTTP {status} (esperado 401)")

status, _ = chamar("GET", "/produtos", token="token_invalido")
print(f"[{'OK' if status == 401 else 'FALHOU'}] Token inválido -> HTTP {status} (esperado 401)")

status, _ = chamar("GET", "/produtos", token=t_oper)
print(f"[{'OK' if status == 200 else 'FALHOU'}] Operador consulta produtos -> HTTP {status} (esperado 200)")

status, _ = chamar("GET", "/produtos", token=t_admin)
print(f"[{'OK' if status == 200 else 'FALHOU'}] Admin consulta produtos -> HTTP {status} (esperado 200)")

status, r = chamar("DELETE", "/produtos/8", token=t_oper)
print(f"[{'OK' if status == 403 else 'FALHOU'}] Operador tenta DELETAR -> HTTP {status} (esperado 403) | {r}")

status, r = chamar("DELETE", "/produtos/8", token=t_admin)
print(f"[{'OK' if status in (200, 409) else 'FALHOU'}] Admin DELETA produto 8 -> HTTP {status} (esperado 200 ou 409) | {r}")

print("\nFim dos testes.")
