import unittest
from contextlib import contextmanager
from unittest.mock import patch

from flask import Flask

from Controle.produto_controle import produtos


class CursorSimulado:
    def __init__(self, saldo):
        self.saldo = saldo
        self.movimentacoes = []
        self.consultas = []

    def execute(self, sql, parametros=()):
        self.consultas.append((sql, parametros))
        if sql.startswith("UPDATE produtos"):
            self.saldo -= parametros[0]
        elif sql.startswith("INSERT INTO movimentacoes"):
            self.movimentacoes.append(parametros)

    def fetchone(self):
        if self.saldo is None:
            return None
        return {"quantidade_estoque": self.saldo}

    def close(self):
        pass


class ConexaoSimulada:
    def __init__(self, cursor):
        self.cursor_simulado = cursor
        self.confirmada = False

    def cursor(self, dictionary=False):
        return self.cursor_simulado

    def commit(self):
        self.confirmada = True

    def rollback(self):
        pass

    def close(self):
        pass


class SaidaProdutoTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(produtos)
        self.cliente = self.app.test_client()
        self.usuario = {"id": 7, "nome": "Ana Operadora", "perfil": "operador"}
        self.cabecalho = {"Authorization": "Bearer token-de-teste"}

    def executar_saida(self, saldo, quantidade):
        cursor = CursorSimulado(saldo)
        conexao = ConexaoSimulada(cursor)

        @contextmanager
        def banco_simulado(dicionario=False):
            yield conexao, cursor

        dados = {"produto_id": 12, "quantidade": quantidade}
        with patch("Controle.estoque_controle._autenticar", return_value=self.usuario), \
             patch("Controle.produto_controle._banco", banco_simulado):
            resposta = self.cliente.post(
                "/movimentacoes/saida", json=dados, headers=self.cabecalho
            )
        return resposta, cursor, conexao

    def test_cenario1_saida_com_saldo_suficiente(self):
        resposta, cursor, conexao = self.executar_saida(saldo=10, quantidade=4)
        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(cursor.saldo, 6)
        self.assertEqual(cursor.movimentacoes, [(12, 4, 7, "Ana Operadora")])
        self.assertTrue(conexao.confirmada)

    def test_cenario2_saida_maior_que_saldo_disponivel(self):
        resposta, cursor, conexao = self.executar_saida(saldo=2, quantidade=3)
        self.assertEqual(resposta.status_code, 409)
        self.assertEqual(cursor.saldo, 2)
        self.assertEqual(cursor.movimentacoes, [])
        self.assertFalse(conexao.confirmada)

    def test_cenario3_saida_igual_ao_saldo_disponivel(self):
        resposta, cursor, conexao = self.executar_saida(saldo=5, quantidade=5)
        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(cursor.saldo, 0)
        self.assertEqual(cursor.movimentacoes, [(12, 5, 7, "Ana Operadora")])
        self.assertTrue(conexao.confirmada)


if __name__ == "__main__":
    unittest.main()
