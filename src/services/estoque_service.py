from repositories import produto_repository
from repositories import movimentacao_repository


def listar_produtos(nome="", pagina=1):
    return produto_repository.listar_produtos(
        nome=nome,
        pagina=pagina,
        limite=10
    )


def cadastrar_produto(nome, descricao, quantidade, preco):
    try:
        quantidade = int(quantidade)
        preco = float(preco)
    except (ValueError, TypeError):
        return False, "Quantidade ou preço inválido."

    if not nome or preco < 0 or quantidade < 0:
        return False, "Confira os dados do produto."

    produto_repository.cadastrar_produto(
        nome, descricao, quantidade, preco
    )


    return True, "Produto cadastrado com sucesso."


def atualizar_produto(id, nome, descricao, preco):
    produto = produto_repository.buscar_produto(id)

    if not produto:
        return False, "Produto não encontrado."

    if not nome or preco < 0:
        return False, "Confira os dados do produto."

    produto_repository.atualizar_produto(
        id, nome, descricao, preco
    )

    return True, "Produto atualizado com sucesso."


def excluir_produto(id):
    produto = produto_repository.buscar_produto(id)

    if not produto:
        return False, "Produto não encontrado."

    movimentacoes = movimentacao_repository.listar_movimentacoes()

    for movimentacao in movimentacoes:
        if movimentacao["produto"] == produto["nome"]:
            return False, "Não é possível excluir produto com histórico de movimentações."

    produto_repository.excluir_produto(id)

    return True, "Produto excluído com sucesso."


def movimentar_estoque(produto_id, tipo, quantidade, usuario_id):
    return movimentacao_repository.registrar_movimentacao(
        produto_id, tipo, quantidade, usuario_id
    )