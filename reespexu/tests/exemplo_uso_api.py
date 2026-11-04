"""Exemplo de uso das APIs de LOGIN e PRODUTOS do sistema de almoxarifado.

Demonstra, em código reutilizável:
  1. POST /auth/login  -> recebe o token (admin e operador)
  2. GET  /produtos    -> listar com paginação e filtro (requer token)
  3. GET  /produtos/<id>      -> consultar um produto
  4. POST /produtos           -> cadastrar (requer token)
  5. PUT  /produtos/<id>      -> atualizar (requer token)
  6. DELETE /produtos/<id>    -> remover (SÓ admin)

Pré-requisitos:
  - Banco criado com infra/bd.sql
  - Servidor rodando:  python -m src.server
Uso:
  python -m tests.exemplo_uso_api
"""
import json
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:5000"


# ----------------------------------------------------------------------
# Função genérica: chama qualquer endpoint da API
# ----------------------------------------------------------------------
def chamar(metodo, caminho, corpo=None, token=None):
    """Faz uma requisição HTTP à API e devolve (status, resposta_json)."""
    dados = json.dumps(corpo).encode() if corpo is not None else None
    req = urllib.request.Request(BASE + caminho, data=dados, method=metodo)
    req.add_header("Content-Type", "application/json")
    if token:  # todas as rotas (menos login/cadastro) exigem o token
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as erro:
        return erro.code, json.loads(erro.read().decode() or "null")


# ----------------------------------------------------------------------
# 1. LOGIN  (POST /auth/login)
# ----------------------------------------------------------------------
def login(email, senha):
    status, r = chamar("POST", "/auth/login", {"email": email, "senha": senha})
    if status != 200:
        raise RuntimeError(f"Login falhou ({status}): {r}")
    print(f"[LOGIN] {email} -> perfil={r['usuario']['perfil']}, id={r['usuario']['id']}")
    return r["token"]


# ----------------------------------------------------------------------
# 2-6. PRODUTOS
# ----------------------------------------------------------------------
def listar_produtos(token, pagina=1, limite=10, nome=None):
    """GET /produtos — lista paginada; filtros opcionais: nome, data_inicio, data_fim."""
    qs = f"?pagina={pagina}&limite={limite}"
    if nome:
        qs += f"&nome={nome}"
    return chamar("GET", "/produtos" + qs, token=token)


def consultar_produto(token, produto_id):
    return chamar("GET", f"/produtos/{produto_id}", token=token)


def cadastrar_produto(token, nome, preco, quantidade, descricao=""):
    """POST /produtos — qualquer usuário logado pode cadastrar."""
    corpo = {"nome": nome, "preco": preco,
             "quantidade_estoque": quantidade, "descricao": descricao}
    return chamar("POST", "/produtos", corpo, token=token)


def atualizar_produto(token, produto_id, campos):
    """PUT /produtos/<id> — campos: nome, descricao e/ou preco."""
    return chamar("PUT", f"/produtos/{produto_id}", campos, token=token)


def remover_produto(token, produto_id):
    """DELETE /produtos/<id> — SOMENTE o perfil admin."""
    return chamar("DELETE", f"/produtos/{produto_id}", token=token)


# ----------------------------------------------------------------------
# Demonstração completa
# ----------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("EXEMPLO DE USO DAS APIS — LOGIN E PRODUTOS")
    print("=" * 60)

    # --- login dos dois perfis ---
    print("\n--- 1. LOGIN ---")
    token_admin = login("admin@almoxarifado.com", "admin123")
    token_oper = login("operador@almoxarifado.com", "operador123")

    # --- listar produtos (com filtro por nome) ---
    print("\n--- 2. LISTAR PRODUTOS (filtro nome=deter) ---")
    status, lista = listar_produtos(token_oper, nome="deter")
    print(f"HTTP {status} | total={lista['total']} | dados={lista['dados']}")

    # --- consultar um produto ---
    print("\n--- 3. CONSULTAR PRODUTO 1 ---")
    status, produto = consultar_produto(token_oper, 1)
    print(f"HTTP {status} | {produto}")

    # --- cadastrar produto (operador), com estoque zero para poder deletar depois ---
    print("\n--- 4. CADASTRAR PRODUTO ---")
    status, r = cadastrar_produto(
        token_oper, "Produto de exemplo", 9.90, 0, "Criado pelo exemplo_uso_api")
    print(f"HTTP {status} | {r}")
    novo_id = r["id"]

    # --- atualizar o produto criado ---
    print("\n--- 5. ATUALIZAR PRODUTO ---")
    status, r = atualizar_produto(token_oper, novo_id, {"preco": 12.50})
    print(f"HTTP {status} | {r}")

    # --- operador tenta deletar (deve dar 403) ---
    print("\n--- 6a. OPERADOR tenta DELETE (esperado 403) ---")
    status, r = remover_produto(token_oper, novo_id)
    print(f"HTTP {status} | {r}")

    # --- admin deleta o produto criado (200; daria 409 se o produto tivesse movimentações) ---
    print("\n--- 6b. ADMIN deleta (esperado 200) ---")
    status, r = remover_produto(token_admin, novo_id)
    print(f"HTTP {status} | {r}")

    print("\nFim do exemplo.")
