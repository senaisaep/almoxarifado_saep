import unittest
from datetime import date
from unittest.mock import MagicMock, patch
from src.routes.server import app
class ListagemProdutosTest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.patch = patch('src.routes.estoque.conectar')
        self.conectar = self.patch.start()
        self.addCleanup(self.patch.stop)
        self.conexao = self.conectar.return_value
        self.cursor = self.conexao.cursor.return_value
        self.cursor.fetchone.return_value = {'total': 21}
        self.cursor.fetchall.return_value = [{'id': 11, 'nome': 'Sabão'}]

    def test_paginacao_padrao(self):
        resposta = self.client.get('/produtos')
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json['pagina'], 1)
        self.assertEqual(resposta.json['total_paginas'], 3)
        self.assertEqual(self.cursor.execute.call_args.args[1], (10, 0))
        self.cursor.close.assert_called_once()
        self.conexao.close.assert_called_once()

    def test_filtros_combinados_e_segunda_pagina(self):
        resposta = self.client.get('/produtos?pagina=2&por_pagina=5&nome=Sabão&data_inicio=2026-11-01&data_fim=2026-11-04')
        self.assertEqual(resposta.status_code, 200)
        contagem, consulta = self.cursor.execute.call_args_list
        self.assertEqual(contagem.args[1], ('%Sabão%', date(2026, 11, 1), date(2026, 11, 5)))
        self.assertEqual(consulta.args[1], contagem.args[1] + (5, 5))
        self.assertIn('nome LIKE %s', consulta.args[0])
        self.assertIn('data_cadastro < %s', consulta.args[0])

    def test_data_exata_inclui_dia_inteiro(self):
        resposta = self.client.get('/produtos?data=2026-11-04')
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(self.cursor.execute.call_args.args[1], (date(2026, 11, 4), date(2026, 11, 5), 10, 0))

    def test_parametros_invalidos_nao_acessam_banco(self):
        for query in ('pagina=0', 'pagina=abc', 'por_pagina=101', 'por_pagina=0',
                      'data=2026-02-30', 'data=20261104', 'data=',
                      'data_inicio=2026-11-05&data_fim=2026-11-04',
                      'data=2026-11-04&data_inicio=2026-11-01'):
            with self.subTest(query=query):
                self.assertEqual(self.client.get('/produtos?' + query).status_code, 400)
        self.conectar.assert_not_called()

    def test_resultado_vazio(self):
        self.cursor.fetchone.return_value = {'total': 0}
        self.cursor.fetchall.return_value = []
        resposta = self.client.get('/produtos?pagina=99')
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json['produtos'], [])
        self.assertEqual(resposta.json['total_paginas'], 0)

    def test_nome_com_curingas_e_tratado_como_literal(self):
        self.client.get('/produtos', query_string={'nome': '10%_!'})
        self.assertEqual(self.cursor.execute.call_args.args[1][0], '%10!%!_!!%')

    def test_fecha_recursos_em_falha_sql(self):
        self.cursor.execute.side_effect = RuntimeError('falha simulada')
        with app.test_request_context('/produtos'):
            from src.routes.estoque import listar_produtos
            with self.assertRaises(RuntimeError):
                listar_produtos()
        self.cursor.close.assert_called_once()
        self.conexao.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
