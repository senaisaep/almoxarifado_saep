"""Fixtures: banco em memória que substitui a camada de repositórios.

Assim testamos rotas + serviços + segurança sem MySQL. O SQL real é coberto
pelo plano de testes de integração (docs/PLANO_DE_TESTES.md).
"""
import os
from contextlib import contextmanager
from datetime import datetime

import pytest

os.environ["SECRET_KEY"] = "chave-de-teste-com-mais-de-trinta-e-dois-caracteres"
os.environ["LOGIN_MAX_TENTATIVAS"] = "3"

from src.repositories import movimentacao_repository as mov_repo  # noqa: E402
from src.repositories import produto_repository as produto_repo  # noqa: E402
from src.repositories import usuario_repository as usuario_repo  # noqa: E402
from src.security.senhas import gerar_hash  # noqa: E402
from src.server import create_app  # noqa: E402
from src.services import auth_service, estoque_service  # noqa: E402
from src.services import produto_service, usuario_service  # noqa: E402

SENHA = "Senha1234"
_HASH = gerar_hash(SENHA)  # calculado uma vez (PBKDF2 é lento de propósito)


class FakeBanco:
    def __init__(self):
        self.usuarios, self.produtos, self.movs = {}, {}, []
        self.commits = self.rollbacks = 0
        self._u = self._p = self._m = 0

    # -- helpers de teste
    def add_usuario(self, nome, perfil, ativo=True):
        self._u += 1
        self.usuarios[self._u] = {
            "id": self._u, "nome": nome, "email": f"{nome.lower()}@teste.com",
            "perfil": perfil, "ativo": 1 if ativo else 0, "data_cadastro": datetime.now(),
            "senha_hash": _HASH, "tentativas_login": 0, "bloqueado_ate": None,
            "bloqueado": False,
        }
        return self._u

    def add_produto(self, nome, estoque, preco=5.0):
        self._p += 1
        self.produtos[self._p] = {
            "id": self._p, "nome": nome, "descricao": "", "preco": preco,
            "quantidade_estoque": estoque, "data_cadastro": datetime.now(),
        }
        return self._p


def _publico(u):
    return {k: u[k] for k in ("id", "nome", "email", "perfil", "ativo", "data_cadastro")}


@pytest.fixture
def banco(monkeypatch):
    b = FakeBanco()

    @contextmanager
    def transacao_fake():
        snapshot = (
            {k: dict(v) for k, v in b.produtos.items()}, list(b.movs),
        )
        try:
            yield object()
            b.commits += 1
        except Exception:
            b.produtos, b.movs = snapshot  # rollback simulado
            b.rollbacks += 1
            raise

    for modulo in (auth_service, usuario_service, produto_service, estoque_service):
        monkeypatch.setattr(modulo, "transacao", transacao_fake)

    # ---- usuários
    monkeypatch.setattr(usuario_repo, "buscar_por_id",
        lambda c, i: _publico(b.usuarios[i]) if i in b.usuarios else None)
    monkeypatch.setattr(usuario_repo, "buscar_por_email",
        lambda c, e: next((u for u in b.usuarios.values() if u["email"] == e), None))
    monkeypatch.setattr(usuario_repo, "listar",
        lambda c: [_publico(u) for u in b.usuarios.values()])

    def inserir_usuario(c, nome, email, senha_hash, perfil):
        i = b.add_usuario(nome, perfil)
        b.usuarios[i].update(email=email, senha_hash=senha_hash)
        return i
    monkeypatch.setattr(usuario_repo, "inserir", inserir_usuario)
    monkeypatch.setattr(usuario_repo, "atualizar",
        lambda c, i, nome, perfil, ativo: b.usuarios[i].update(
            nome=nome, perfil=perfil, ativo=1 if ativo else 0))
    monkeypatch.setattr(usuario_repo, "atualizar_senha",
        lambda c, i, h: b.usuarios[i].update(senha_hash=h, tentativas_login=0, bloqueado=False))

    def falha(c, i, maximo, minutos):
        u = b.usuarios[i]
        u["tentativas_login"] += 1
        if u["tentativas_login"] >= maximo:
            u["bloqueado"], u["bloqueado_ate"] = True, datetime.now()
    monkeypatch.setattr(usuario_repo, "registrar_falha", falha)
    monkeypatch.setattr(usuario_repo, "zerar_falhas",
        lambda c, i: b.usuarios[i].update(tentativas_login=0, bloqueado=False, bloqueado_ate=None))

    # ---- produtos
    def filtrar(busca, estoque_max):
        itens = list(b.produtos.values())
        if busca:
            itens = [p for p in itens if busca.lower() in p["nome"].lower()]
        if estoque_max is not None:
            itens = [p for p in itens if p["quantidade_estoque"] <= estoque_max]
        return itens
    monkeypatch.setattr(produto_repo, "contar", lambda c, bu, em: len(filtrar(bu, em)))
    monkeypatch.setattr(produto_repo, "listar",
        lambda c, bu, em, lim, off: filtrar(bu, em)[off:off + lim])
    monkeypatch.setattr(produto_repo, "buscar_por_id", lambda c, i: b.produtos.get(i))
    monkeypatch.setattr(produto_repo, "buscar_para_atualizar",
        lambda c, i: dict(b.produtos[i]) if i in b.produtos else None)

    def inserir_produto(c, nome, descricao, preco, qtd):
        i = b.add_produto(nome, qtd, preco)
        b.produtos[i]["descricao"] = descricao
        return i
    monkeypatch.setattr(produto_repo, "inserir", inserir_produto)
    monkeypatch.setattr(produto_repo, "atualizar",
        lambda c, i, n, d, p: b.produtos[i].update(nome=n, descricao=d, preco=p))
    monkeypatch.setattr(produto_repo, "atualizar_saldo",
        lambda c, i, s: b.produtos[i].update(quantidade_estoque=s))
    monkeypatch.setattr(produto_repo, "remover", lambda c, i: b.produtos.pop(i))

    # ---- movimentações
    def inserir_mov(c, produto_id, tipo, qtd, usuario_id):
        b._m += 1
        b.movs.append({
            "id": b._m, "produto_id": produto_id,
            "produto": b.produtos[produto_id]["nome"], "tipo": tipo, "quantidade": qtd,
            "data_hora": datetime(2026, 11, 4, 10, 30, 0), "usuario_id": usuario_id,
            "responsavel": b.usuarios[usuario_id]["nome"],
        })
        return b._m
    monkeypatch.setattr(mov_repo, "inserir", inserir_mov)
    monkeypatch.setattr(mov_repo, "buscar_por_id",
        lambda c, i: next(m for m in b.movs if m["id"] == i))

    def filtrar_movs(f):
        return [m for m in b.movs
                if (not f["tipo"] or m["tipo"] == f["tipo"])
                and (not f["produto_id"] or m["produto_id"] == f["produto_id"])]
    monkeypatch.setattr(mov_repo, "contar", lambda c, f: len(filtrar_movs(f)))
    monkeypatch.setattr(mov_repo, "listar",
        lambda c, f, lim, off: filtrar_movs(f)[::-1][off:off + lim])
    monkeypatch.setattr(mov_repo, "contar_por_produto",
        lambda c, i: len([m for m in b.movs if m["produto_id"] == i]))
    return b


@pytest.fixture
def client(banco):
    app = create_app()
    app.testing = False  # exercita os handlers de erro como em produção
    return app.test_client()


@pytest.fixture
def entrar(client):
    """entrar(email) -> cabeçalho Authorization pronto."""
    def _entrar(email, senha=SENHA):
        r = client.post("/auth/login", json={"email": email, "senha": senha})
        assert r.status_code == 200, r.get_json()
        return {"Authorization": f"Bearer {r.get_json()['token']}"}
    return _entrar


@pytest.fixture
def cenario(banco):
    """Um usuário de cada perfil + produto com 10 unidades."""
    return {
        "admin": banco.add_usuario("Ana", "admin"),
        "almox": banco.add_usuario("Bruno", "almoxarife"),
        "consulta": banco.add_usuario("Carla", "consulta"),
        "produto": banco.add_produto("Detergente", 10),
    }
