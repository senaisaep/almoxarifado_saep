import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from werkzeug.security import generate_password_hash

import infra.database as database
from app import app
from repositories import estoque_repository, produto_repository, usuario_repository


class AlmoxarifadoTestes(unittest.TestCase):
    def setUp(self):
        self.pasta_temporaria = tempfile.TemporaryDirectory()
        patcher = patch(
            "infra.database.DATABASE_PATH",
            Path(self.pasta_temporaria.name) / "teste.db",
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self.pasta_temporaria.cleanup)
        database.inicializar_banco()
        app.config.update(TESTING=True, SECRET_KEY="chave-de-teste")
        self.cliente = app.test_client()

    def criar_usuario(self, perfil="Administrador", login="teste-admin"):
        return usuario_repository.criar_usuario(
            "Usuário de teste",
            login,
            generate_password_hash("senha-segura-123"),
            perfil,
        )

    def test_produtos_antigos_sao_criados_e_inicializacao_nao_altera_saldos(self):
        produtos = produto_repository.listar_produtos()
        saldos = {produto["nome"]: produto["quantidade_estoque"] for produto in produtos}

        self.assertEqual(len(produtos), 8)
        self.assertEqual(saldos["Detergente neutro 500ml"], 40)
        self.assertEqual(saldos["Água sanitária 1L"], 25)
        self.assertEqual(saldos["Álcool 70% 1L"], 12)

        conexao = database.conectar()
        try:
            conexao.execute(
                "UPDATE produtos SET quantidade_estoque=7 "
                "WHERE nome='Detergente neutro 500ml'"
            )
            conexao.commit()
        finally:
            conexao.close()

        database.inicializar_banco()
        produtos = produto_repository.listar_produtos()
        saldos = {produto["nome"]: produto["quantidade_estoque"] for produto in produtos}

        self.assertEqual(len(produtos), 8)
        self.assertEqual(saldos["Detergente neutro 500ml"], 7)

    def entrar(self, perfil="Administrador"):
        usuario_id = self.criar_usuario(perfil)
        with self.cliente.session_transaction() as sessao:
            sessao.update(
                usuario_id=usuario_id,
                nome="Usuário de teste",
                perfil=perfil,
            )
        return usuario_id

    def test_login_valida_senha_e_rejeita_senha_incorreta(self):
        incorreta = self.cliente.post(
            "/login", data={"login": "admin", "senha": "errada"}
        )
        correta = self.cliente.post("/login", data={"login": "admin", "senha": "123"})

        self.assertEqual(incorreta.status_code, 401)
        self.assertEqual(correta.status_code, 302)
        self.assertEqual(correta.headers["Location"], "/estoque")
        self.assertEqual(self.cliente.get("/estoque").status_code, 200)

    def test_contas_iniciais_tem_senhas_hash_e_perfis_corretos(self):
        database.inicializar_banco()
        admin = usuario_repository.buscar_usuario_por_login("admin")
        operador = usuario_repository.buscar_usuario_por_login("operador")

        self.assertEqual(usuario_repository.contar_usuarios(), 2)
        self.assertEqual(admin["perfil"], "Administrador")
        self.assertEqual(operador["perfil"], "Operador")
        self.assertTrue(admin["senha"].startswith("scrypt:"))
        self.assertTrue(operador["senha"].startswith("scrypt:"))

    def test_produto_movimentacoes_e_saldo_funcionam_no_sqlite(self):
        self.entrar()
        cadastrado = self.cliente.post(
            "/produtos",
            json={
                "nome": "Papel toalha",
                "descricao": "Pacote",
                "preco": 12.5,
                "quantidade_estoque": 5,
            },
        )
        produto_id = cadastrado.get_json()["id"]
        produto = self.cliente.get(f"/produtos/{produto_id}").get_json()

        saida = self.cliente.post(
            "/movimentacoes/saida",
            json={"produto_id": produto_id, "quantidade": 3},
        )
        insuficiente = self.cliente.post(
            "/movimentacoes/saida",
            json={"produto_id": produto_id, "quantidade": 3},
        )
        movimentos = estoque_repository.listar_movimentacoes()

        self.assertEqual(cadastrado.status_code, 201)
        self.assertEqual(produto["quantidade_estoque"], 5)
        self.assertEqual(saida.status_code, 201)
        self.assertEqual(insuficiente.status_code, 400)
        self.assertEqual(
            produto_repository.buscar_produto(produto_id)["quantidade_estoque"],
            2,
        )
        self.assertEqual(len(movimentos), 2)
        self.assertTrue(all(movimento["responsavel"] == "Usuário de teste"
                            for movimento in movimentos))
        self.assertTrue(all(movimento["tipo"] in ("entrada", "saida")
                            for movimento in movimentos))

    def test_operador_pode_consultar_mas_nao_gerenciar(self):
        login = self.cliente.post(
            "/login", data={"login": "operador", "senha": "456"}
        )

        pagina = self.cliente.get("/estoque")
        cadastro = self.cliente.post("/produtos", json={"nome": "Produto"})
        cadastro_usuario = self.cliente.post(
            "/usuarios",
            json={
                "nome": "Outro usuário",
                "login": "outro",
                "senha": "senha-segura-123",
                "perfil": "Operador",
            },
        )

        self.assertEqual(login.status_code, 302)
        self.assertEqual(pagina.status_code, 200)
        self.assertEqual(cadastro.status_code, 403)
        self.assertEqual(cadastro_usuario.status_code, 403)
        self.assertNotIn(b'id="novo-produto"', pagina.data)

    def test_atualizar_e_remover_produto_respeitam_movimentacoes(self):
        usuario_id = self.entrar()
        produto_id = produto_repository.cadastrar_produto(
            "Produto", "", 2, 0, usuario_id
        )

        atualizado = self.cliente.put(
            f"/produtos/{produto_id}",
            json={"nome": "Produto atualizado", "descricao": "", "preco": 3},
        )
        removido = self.cliente.delete(f"/produtos/{produto_id}")

        self.assertEqual(atualizado.status_code, 200)
        self.assertEqual(removido.status_code, 200)

    def test_produto_com_movimentacao_nao_pode_ser_removido(self):
        usuario_id = self.entrar()
        produto_id = produto_repository.cadastrar_produto(
            "Produto", "", 2, 1, usuario_id
        )

        resposta = self.cliente.delete(f"/produtos/{produto_id}")

        self.assertEqual(resposta.status_code, 409)

    def test_usuario_cadastrado_pelo_admin_consegue_entrar(self):
        login_admin = self.cliente.post(
            "/login", data={"login": "admin", "senha": "123"}
        )
        cadastro = self.cliente.post(
            "/usuarios",
            json={
                "nome": "Operador",
                "login": "novo-operador",
                "senha": "senha-do-operador",
                "perfil": "Operador",
            },
        )
        self.cliente.post("/logout")
        login = self.cliente.post(
            "/login",
            data={"login": "novo-operador", "senha": "senha-do-operador"},
        )

        self.assertEqual(cadastro.status_code, 201)
        self.assertEqual(login_admin.status_code, 302)
        self.assertEqual(login.status_code, 302)
        self.assertEqual(self.cliente.get("/estoque").status_code, 200)


if __name__ == "__main__":
    unittest.main()
