"""Requisito central: saída maior que o saldo é bloqueada com mensagem clara."""


def _saida(client, headers, produto_id, quantidade):
    return client.post("/movimentacoes/saida", headers=headers,
                       json={"produto_id": produto_id, "quantidade": quantidade})


def test_saida_maior_que_saldo_e_bloqueada_com_mensagem_clara(client, banco, cenario, entrar):
    h = entrar("bruno@teste.com")
    r = _saida(client, h, cenario["produto"], 15)
    assert r.status_code == 422
    corpo = r.get_json()
    assert corpo["mensagem"] == (
        "Saída não permitida: estoque insuficiente. Disponível: 10, solicitado: 15."
    )
    assert corpo["disponivel"] == 10 and corpo["solicitado"] == 15
    # nada foi gravado e o saldo não mudou
    assert banco.produtos[cenario["produto"]]["quantidade_estoque"] == 10
    assert banco.movs == []
    assert banco.rollbacks >= 1


def test_saida_menor_que_saldo_e_registrada(client, banco, cenario, entrar):
    h = entrar("bruno@teste.com")
    r = _saida(client, h, cenario["produto"], 4)
    assert r.status_code == 201
    corpo = r.get_json()
    assert corpo["saldo_anterior"] == 10 and corpo["saldo_atual"] == 6
    assert banco.produtos[cenario["produto"]]["quantidade_estoque"] == 6
    assert len(banco.movs) == 1 and banco.movs[0]["tipo"] == "saida"


def test_saida_igual_ao_saldo_zera_o_estoque(client, banco, cenario, entrar):
    r = _saida(client, entrar("bruno@teste.com"), cenario["produto"], 10)
    assert r.status_code == 201
    assert banco.produtos[cenario["produto"]]["quantidade_estoque"] == 0


def test_saida_registra_data_hora_e_responsavel(client, cenario, entrar):
    r = _saida(client, entrar("bruno@teste.com"), cenario["produto"], 1)
    mov = r.get_json()["movimentacao"]
    assert mov["responsavel"] == "Bruno"
    assert mov["usuario_id"] == cenario["almox"]
    assert mov["data_hora"] == "2026-11-04 10:30:00"


def test_segunda_saida_apos_zerar_e_bloqueada(client, cenario, entrar):
    h = entrar("bruno@teste.com")
    assert _saida(client, h, cenario["produto"], 10).status_code == 201
    r = _saida(client, h, cenario["produto"], 1)
    assert r.status_code == 422
    assert "Disponível: 0, solicitado: 1" in r.get_json()["mensagem"]


def test_entrada_registra_responsavel_e_soma_saldo(client, banco, cenario, entrar):
    r = client.post("/movimentacoes/entrada", headers=entrar("ana@teste.com"),
                    json={"produto_id": cenario["produto"], "quantidade": 5})
    assert r.status_code == 201
    assert r.get_json()["saldo_atual"] == 15
    assert banco.movs[0]["usuario_id"] == cenario["admin"]


def test_saida_produto_inexistente(client, cenario, entrar):
    assert _saida(client, entrar("bruno@teste.com"), 999, 1).status_code == 404


def test_quantidade_invalida_e_rejeitada(client, cenario, entrar):
    h = entrar("bruno@teste.com")
    for invalida in (0, -3, "abc", 1.5, None, True):
        r = _saida(client, h, cenario["produto"], invalida)
        assert r.status_code == 400, invalida


def test_corpo_nao_json_retorna_400(client, cenario, entrar):
    r = client.post("/movimentacoes/saida", headers=entrar("bruno@teste.com"),
                    data="texto", content_type="text/plain")
    assert r.status_code == 400
