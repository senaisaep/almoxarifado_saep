import src.security.tokens as tokens


def test_login_ok_retorna_token_sem_expor_hash(client, cenario):
    r = client.post("/auth/login", json={"email": "ana@teste.com", "senha": "Senha1234"})
    assert r.status_code == 200
    corpo = r.get_json()
    assert corpo["tipo"] == "Bearer" and corpo["usuario"]["perfil"] == "admin"
    assert "senha_hash" not in str(corpo)


def test_login_senha_errada_e_email_inexistente_tem_mesma_mensagem(client, cenario):
    a = client.post("/auth/login", json={"email": "ana@teste.com", "senha": "errada123"})
    b = client.post("/auth/login", json={"email": "ninguem@teste.com", "senha": "errada123"})
    assert a.status_code == b.status_code == 401
    assert a.get_json() == b.get_json()


def test_bloqueio_apos_tentativas_excessivas(client, cenario):
    for _ in range(3):
        client.post("/auth/login", json={"email": "ana@teste.com", "senha": "errada123"})
    r = client.post("/auth/login", json={"email": "ana@teste.com", "senha": "Senha1234"})
    assert r.status_code == 423


def test_usuario_inativo_nao_entra(client, banco):
    banco.add_usuario("Dora", "consulta", ativo=False)
    r = client.post("/auth/login", json={"email": "dora@teste.com", "senha": "Senha1234"})
    assert r.status_code == 401


def test_rotas_exigem_token(client, cenario):
    for metodo, rota in [("get", "/produtos"), ("get", "/movimentacoes"),
                         ("post", "/movimentacoes/saida"), ("get", "/usuarios")]:
        assert getattr(client, metodo)(rota).status_code == 401, rota


def test_token_invalido_adulterado_ou_expirado(client, cenario, monkeypatch):
    assert client.get("/produtos", headers={"Authorization": "Bearer lixo"}).status_code == 401
    monkeypatch.setattr(tokens.settings, "jwt_expira_minutos", lambda: -1)
    r = client.post("/auth/login", json={"email": "ana@teste.com", "senha": "Senha1234"})
    expirado = {"Authorization": f"Bearer {r.get_json()['token']}"}
    r = client.get("/produtos", headers=expirado)
    assert r.status_code == 401 and "expirada" in r.get_json()["mensagem"]


def test_usuario_desativado_perde_acesso_mesmo_com_token_valido(client, banco, cenario, entrar):
    h = entrar("bruno@teste.com")
    assert client.get("/produtos", headers=h).status_code == 200
    banco.usuarios[cenario["almox"]]["ativo"] = 0
    assert client.get("/produtos", headers=h).status_code == 401


def test_perfil_consulta_le_mas_nao_altera(client, cenario, entrar):
    h = entrar("carla@teste.com")
    assert client.get("/produtos", headers=h).status_code == 200
    assert client.get("/movimentacoes", headers=h).status_code == 200
    assert client.post("/movimentacoes/saida", headers=h,
                       json={"produto_id": cenario["produto"], "quantidade": 1}).status_code == 403
    assert client.post("/movimentacoes/entrada", headers=h,
                       json={"produto_id": cenario["produto"], "quantidade": 1}).status_code == 403
    assert client.post("/produtos", headers=h, json={"nome": "X"}).status_code == 403


def test_almoxarife_nao_remove_produto_nem_gerencia_usuarios(client, cenario, entrar):
    h = entrar("bruno@teste.com")
    assert client.delete(f"/produtos/{cenario['produto']}", headers=h).status_code == 403
    assert client.get("/usuarios", headers=h).status_code == 403
    assert client.post("/usuarios", headers=h, json={}).status_code == 403


def test_admin_cria_usuario_e_novo_usuario_loga(client, cenario, entrar):
    h = entrar("ana@teste.com")
    r = client.post("/usuarios", headers=h, json={
        "nome": "Edu", "email": "Edu@Teste.com", "senha": "OutraSenha9", "perfil": "almoxarife"})
    assert r.status_code == 201
    r = client.post("/auth/login", json={"email": "edu@teste.com", "senha": "OutraSenha9"})
    assert r.status_code == 200


def test_cadastro_de_usuario_valida_dados(client, cenario, entrar):
    h = entrar("ana@teste.com")
    base = {"nome": "Edu", "email": "edu@teste.com", "senha": "OutraSenha9", "perfil": "consulta"}
    for alteracao in ({"senha": "curta1"}, {"senha": "somenteletras"}, {"email": "invalido"},
                      {"perfil": "root"}, {"nome": "  "}):
        r = client.post("/usuarios", headers=h, json={**base, **alteracao})
        assert r.status_code == 400, alteracao
    assert client.post("/usuarios", headers=h, json={**base, "email": "ana@teste.com"}).status_code == 409


def test_admin_nao_pode_se_desativar_nem_rebaixar(client, cenario, entrar):
    h = entrar("ana@teste.com")
    uid = cenario["admin"]
    assert client.delete(f"/usuarios/{uid}", headers=h).status_code == 400
    assert client.put(f"/usuarios/{uid}", headers=h, json={"perfil": "consulta"}).status_code == 400


def test_admin_desativa_outro_usuario(client, banco, cenario, entrar):
    r = client.delete(f"/usuarios/{cenario['consulta']}", headers=entrar("ana@teste.com"))
    assert r.status_code == 200 and banco.usuarios[cenario["consulta"]]["ativo"] == 0


def test_trocar_senha(client, cenario, entrar):
    h = entrar("carla@teste.com")
    assert client.post("/auth/trocar-senha", headers=h,
                       json={"senha_atual": "errada", "nova_senha": "NovaSenha77"}).status_code == 400
    assert client.post("/auth/trocar-senha", headers=h,
                       json={"senha_atual": "Senha1234", "nova_senha": "fraca"}).status_code == 400
    assert client.post("/auth/trocar-senha", headers=h,
                       json={"senha_atual": "Senha1234", "nova_senha": "NovaSenha77"}).status_code == 200
    assert client.post("/auth/login", json={"email": "carla@teste.com", "senha": "NovaSenha77"}).status_code == 200


def test_erro_interno_nao_vaza_detalhes(client, cenario, entrar, monkeypatch):
    from src.services import produto_service
    h = entrar("ana@teste.com")
    def explode(*a, **k): raise RuntimeError("SELECT secreto FROM tabela")
    monkeypatch.setattr(produto_service, "listar", explode)
    r = client.get("/produtos", headers=h)
    assert r.status_code == 500 and "SELECT" not in r.get_data(as_text=True)


def test_cabecalhos_de_seguranca(client):
    r = client.get("/")
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["X-Frame-Options"] == "DENY"
