"""Testes automatizados (usam o MySQL do .env e gravam dados no banco).
Use um banco de teste e rode infra/bd.sql de novo para resetar.

    pip install pytest
    pytest -v
"""
import os
import uuid

import pytest

os.environ.setdefault("JWT_SECRET", "segredo-de-teste")

from src.server import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    return app.test_client()


def login(client, email, senha):
    r = client.post("/auth/login", json={"email": email, "senha": senha})
    assert r.status_code == 200
    return {"Authorization": "Bearer " + r.get_json()["token"]}


@pytest.fixture(scope="module")
def admin(client):
    return login(client, "admin@almoxarifado.com", "admin123")


@pytest.fixture(scope="module")
def operador(client):
    return login(client, "operador@almoxarifado.com", "operador123")


def novo_produto(client, headers, estoque=10):
    r = client.post("/produtos", headers=headers, json={
        "nome": "Teste " + uuid.uuid4().hex[:8], "preco": 4.5, "quantidade_estoque": estoque})
    assert r.status_code == 201
    return r.get_json()["id"]


def test_login_e_rotas_privadas(client):
    assert client.post("/auth/login", json={"email": "x@x.com", "senha": "errada"}).status_code == 401
    assert client.get("/produtos").status_code == 401
    assert client.get("/produtos", headers={"Authorization": "Bearer lixo"}).status_code == 401


def test_cadastro_cria_sempre_operador(client):
    email = uuid.uuid4().hex[:8] + "@teste.com"
    corpo = {"nome": "Novo", "email": email, "senha": "abc123", "perfil": "admin"}
    assert client.post("/auth/cadastro", json=corpo).status_code == 201
    assert client.post("/auth/cadastro", json=corpo).status_code == 409  # e-mail repetido
    token = login(client, email, "abc123")
    # operador não deleta, então se virou admin esse DELETE passaria
    assert client.delete("/produtos/1", headers=token).status_code == 403


def test_operador_consulta_insere_atualiza_mas_nao_deleta(client, operador, admin):
    pid = novo_produto(client, operador, estoque=0)
    assert client.get(f"/produtos/{pid}", headers=operador).status_code == 200
    assert client.put(f"/produtos/{pid}", headers=operador, json={"preco": 9.99}).status_code == 200
    assert client.get(f"/produtos/{pid}", headers=operador).get_json()["preco"] == 9.99
    assert client.delete(f"/produtos/{pid}", headers=operador).status_code == 403
    assert client.delete(f"/produtos/{pid}", headers=admin).status_code == 200


def test_validacoes_de_produto(client, admin):
    assert client.post("/produtos", headers=admin, json={}).status_code == 400
    assert client.post("/produtos", headers=admin, json={"nome": "A", "preco": -1}).status_code == 400
    assert client.post("/produtos", headers=admin, json={"nome": "A", "quantidade_estoque": 1.5}).status_code == 400
    pid = novo_produto(client, admin, estoque=0)
    assert client.put(f"/produtos/{pid}", headers=admin, json={"quantidade_estoque": 50}).status_code == 400


def test_entrada_e_saida(client, admin, operador):
    pid = novo_produto(client, admin, estoque=10)

    r = client.post("/movimentacoes/entrada", headers=operador, json={"produto_id": pid, "quantidade": 5})
    assert r.status_code == 201 and r.get_json()["estoque_atual"] == 15

    r = client.post("/movimentacoes/saida", headers=operador, json={"produto_id": pid, "quantidade": 7})
    assert r.status_code == 201 and r.get_json()["estoque_atual"] == 8

    # saída maior que o estoque: bloqueia e não muda nada
    r = client.post("/movimentacoes/saida", headers=operador, json={"produto_id": pid, "quantidade": 9})
    assert r.status_code == 409
    assert r.get_json()["mensagem"] == "Saída não permitida: estoque insuficiente. Disponível: 8. Solicitado: 9."
    assert client.get(f"/produtos/{pid}", headers=admin).get_json()["quantidade_estoque"] == 8

    assert client.post("/movimentacoes/saida", headers=operador, json={"produto_id": pid, "quantidade": 0}).status_code == 400
    assert client.post("/movimentacoes/entrada", headers=operador, json={"produto_id": 999999, "quantidade": 1}).status_code == 404


def test_movimentacao_registra_usuario_e_data(client, admin, operador):
    pid = novo_produto(client, admin, estoque=0)
    client.post("/movimentacoes/entrada", headers=operador, json={"produto_id": pid, "quantidade": 3})
    r = client.get(f"/movimentacoes?produto_id={pid}&tipo=entrada", headers=admin).get_json()
    assert r["total"] == 1
    assert r["dados"][0]["usuario"] == "Operador" and "T" in r["dados"][0]["data_hora"]
    assert client.get("/movimentacoes?tipo=xyz", headers=admin).status_code == 400


def test_paginacao_e_filtros_de_produtos(client, admin):
    r = client.get("/produtos?limite=3&pagina=1", headers=admin).get_json()
    assert len(r["dados"]) <= 3 and r["total"] >= 8
    assert r["total_paginas"] == -(-r["total"] // 3)

    r = client.get("/produtos?nome=detergente", headers=admin).get_json()
    assert r["total"] >= 1 and all("detergente" in p["nome"].lower() for p in r["dados"])

    assert client.get("/produtos?data_inicio=2999-01-01", headers=admin).get_json()["total"] == 0
    assert client.get("/produtos?data_inicio=2000-01-01&data_fim=2999-12-31", headers=admin).get_json()["total"] >= 8
    assert client.get("/produtos?data_inicio=ontem", headers=admin).status_code == 400
    assert client.get("/produtos?limite=1000", headers=admin).status_code == 400
    assert client.get("/produtos?pagina=0", headers=admin).status_code == 400
