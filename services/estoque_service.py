from repositories import estoque_repository


def listar_movimentacoes():
    return estoque_repository.listar_movimentacoes()


def registrar_movimentacao(dados, tipo, usuario_id):
    if not isinstance(dados, dict):
        return "Envie os dados em formato JSON.", 400
    if tipo not in ("entrada", "saida"):
        return "Tipo de movimentação inválido.", 400

    produto_id = dados.get("produto_id")
    quantidade = dados.get("quantidade")
    if (
        not isinstance(produto_id, int)
        or isinstance(produto_id, bool)
        or produto_id <= 0
        or not isinstance(quantidade, int)
        or isinstance(quantidade, bool)
        or quantidade <= 0
        or quantidade > 2147483647
    ):
        return "Informe produto_id e quantidade inteira maior que zero.", 400

    return estoque_repository.registrar_movimentacao(
        produto_id,
        quantidade,
        tipo,
        usuario_id,
    )