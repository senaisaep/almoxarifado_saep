import re
from datetime import datetime

import pytest

from src.services import movimentacao_service


class FakeProdutoRepository:
    def __init__(self, produto):
        self.produto = produto

    def buscar_por_id(self, produto_id):
        if self.produto["id"] == produto_id:
            return self.produto
        return None

    def atualizar_quantidade(self, produto_id, quantidade):
        self.produto["quantidade_estoque"] = quantidade


class FakeMovimentacaoRepository:
    def __init__(self):
        self.movimentos = []

    def criar(self, dados):
        movimento = {"id": len(self.movimentos) + 1, **dados}
        self.movimentos.append(movimento)
        return movimento


def test_cenario_1_saida_bloqueada_quando_saldo_insuficiente():
    produto = {"id": 1, "quantidade_estoque": 5}
    fake_produto_repo = FakeProdutoRepository(produto)
    fake_movimento_repo = FakeMovimentacaoRepository()

    with pytest.raises(ValueError, match=r"Saida não permitida: estoque insuficiente"):
        movimentacao_service.registrar_saida(
            1,
            7,
            "Maria",
            produto_repo=fake_produto_repo,
            movimentacao_repo=fake_movimento_repo,
        )

    assert produto["quantidade_estoque"] == 5
    assert fake_movimento_repo.movimentos == []


def test_cenario_2_saida_registrada_quando_quantidade_igual_ou_menor_ao_saldo():
    produto = {"id": 2, "quantidade_estoque": 10}
    fake_produto_repo = FakeProdutoRepository(produto)
    fake_movimento_repo = FakeMovimentacaoRepository()

    movimento = movimentacao_service.registrar_saida(
        2,
        4,
        "João",
        produto_repo=fake_produto_repo,
        movimentacao_repo=fake_movimento_repo,
    )

    assert movimento["tipo"] == "saida"
    assert movimento["quantidade"] == 4
    assert produto["quantidade_estoque"] == 6
    assert fake_movimento_repo.movimentos[0]["responsavel"] == "João"


def test_cenario_3_saida_registra_data_hora_e_responsavel():
    produto = {"id": 3, "quantidade_estoque": 12}
    fake_produto_repo = FakeProdutoRepository(produto)
    fake_movimento_repo = FakeMovimentacaoRepository()

    movimento = movimentacao_service.registrar_saida(
        3,
        2,
        "Ana",
        produto_repo=fake_produto_repo,
        movimentacao_repo=fake_movimento_repo,
    )

    assert movimento["responsavel"] == "Ana"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", movimento["data_hora"])
    datetime.strptime(movimento["data_hora"], "%Y-%m-%d %H:%M:%S")
    assert produto["quantidade_estoque"] == 10
