def test_listagem_paginada_e_filtros(client, banco, cenario, entrar):
    for i in range(14):
        banco.add_produto(f"Item {i:02d}", i)
    h = entrar("carla@teste.com")
    r = client.get("/produtos?por_pagina=5&pagina=2", headers=h).get_json()
    assert r["total"] == 15 and r["total_paginas"] == 3 and len(r["dados"]) == 5
    assert client.get("/produtos?busca=item 03", headers=h).get_json()["total"] == 1
    baixo = client.get("/produtos?estoque_max=2", headers=h).get_json()
    assert baixo["total"] == 3  # Item 00, 01, 02


def test_paginacao_invalida_retorna_400(client, cenario, entrar):
    h = entrar("carla@teste.com")
    assert client.get("/produtos?pagina=0", headers=h).status_code == 400
    assert client.get("/produtos?por_pagina=abc", headers=h).status_code == 400
    assert client.get("/produtos?estoque_max=-1", headers=h).status_code == 400


def test_por_pagina_tem_teto(client, cenario, entrar):
    r = client.get("/produtos?por_pagina=9999", headers=entrar("carla@teste.com")).get_json()
    assert r["por_pagina"] == 100


def test_cadastro_com_estoque_inicial_gera_movimentacao(client, banco, cenario, entrar):
    r = client.post("/produtos", headers=entrar("bruno@teste.com"),
                    json={"nome": "Vassoura", "preco": 12.5, "quantidade_estoque": 7})
    assert r.status_code == 201
    assert banco.movs[0]["tipo"] == "entrada" and banco.movs[0]["quantidade"] == 7
    assert banco.movs[0]["responsavel"] == "Bruno"


def test_cadastro_valida_campos(client, cenario, entrar):
    h = entrar("bruno@teste.com")
    for corpo in ({}, {"nome": ""}, {"nome": "X", "preco": -1},
                  {"nome": "X", "preco": "abc"}, {"nome": "X", "quantidade_estoque": -5}):
        assert client.post("/produtos", headers=h, json=corpo).status_code == 400, corpo


def test_put_nao_altera_saldo(client, banco, cenario, entrar):
    pid = cenario["produto"]
    r = client.put(f"/produtos/{pid}", headers=entrar("bruno@teste.com"),
                   json={"nome": "Novo nome", "preco": 9, "quantidade_estoque": 999})
    assert r.status_code == 200
    assert banco.produtos[pid]["nome"] == "Novo nome"
    assert banco.produtos[pid]["quantidade_estoque"] == 10


def test_remover_produto_com_movimentacao_e_bloqueado(client, banco, cenario, entrar):
    h = entrar("ana@teste.com")
    client.post("/movimentacoes/entrada", headers=h,
                json={"produto_id": cenario["produto"], "quantidade": 1})
    assert client.delete(f"/produtos/{cenario['produto']}", headers=h).status_code == 409
    novo = banco.add_produto("Sem uso", 0)
    assert client.delete(f"/produtos/{novo}", headers=h).status_code == 200


def test_listar_movimentacoes_com_filtro(client, cenario, entrar):
    h = entrar("bruno@teste.com")
    p = cenario["produto"]
    client.post("/movimentacoes/entrada", headers=h, json={"produto_id": p, "quantidade": 3})
    client.post("/movimentacoes/saida", headers=h, json={"produto_id": p, "quantidade": 2})
    todas = client.get("/movimentacoes", headers=h).get_json()
    assert todas["total"] == 2 and todas["dados"][0]["tipo"] == "saida"
    so_saidas = client.get("/movimentacoes?tipo=saida", headers=h).get_json()
    assert so_saidas["total"] == 1
    assert client.get("/movimentacoes?tipo=xyz", headers=h).status_code == 400
    assert client.get("/movimentacoes?data_inicio=04/11/2026", headers=h).status_code == 400
