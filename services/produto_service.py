from models import estoque_models


def exigir_admin(usuario):
    if usuario is None or usuario["perfil"] != "admin":
        raise PermissionError(
            "Acesso permitido somente para administradores."
        )


def validar_produto(nome, descricao, quantidade, preco,
                    estoque_minimo, estoque_maximo):

    if not nome or not nome.strip():
        raise ValueError("O nome do produto é obrigatório.")

    if not isinstance(quantidade, int) or isinstance(quantidade, bool):
        raise ValueError("A quantidade deve ser um número inteiro.")

    if not isinstance(estoque_minimo, int) or isinstance(estoque_minimo, bool):
        raise ValueError("O estoque mínimo deve ser inteiro.")

    if not isinstance(estoque_maximo, int) or isinstance(estoque_maximo, bool):
        raise ValueError("O estoque máximo deve ser inteiro.")

    if quantidade < 0:
        raise ValueError("A quantidade não pode ser negativa.")

    if estoque_minimo < 0:
        raise ValueError("O estoque mínimo não pode ser negativo.")

    if estoque_maximo < estoque_minimo:
        raise ValueError("O estoque máximo deve ser maior que o mínimo.")

    if quantidade < 0 or quantidade > estoque_maximo:
        raise ValueError("Quantidade fora dos limites do estoque.")

    if not isinstance(preco, (int, float)) or isinstance(preco, bool):
        raise ValueError("O preço deve ser numérico.")

    if preco < 0:
        raise ValueError("O preço não pode ser negativo.")

    if not isinstance(descricao, str):
        raise ValueError("Descrição inválida.")


def inserir_produto(
    usuario,
    nome,
    descricao,
    quantidade,
    preco,
    estoque_minimo=0,
    estoque_maximo=999999
):
    exigir_admin(usuario)

    validar_produto(
        nome, descricao, quantidade, preco,
        estoque_minimo, estoque_maximo
    )

    return estoque_models.inserir_produto(
        nome.strip(),
        descricao,
        quantidade,
        preco,
        estoque_minimo,
        estoque_maximo
    )


def listar_produtos():
    return estoque_models.buscar_produtos()


def buscar_produto(produto_id):
    produto = estoque_models.buscar_por_id(produto_id)

    if produto is None:
        raise ValueError("Produto não encontrado.")

    return produto


def atualizar_produto(
    usuario,
    produto_id,
    nome,
    descricao,
    quantidade,
    preco,
    estoque_minimo,
    estoque_maximo
):
    exigir_admin(usuario)

    buscar_produto(produto_id)

    validar_produto(
        nome, descricao, quantidade, preco,
        estoque_minimo, estoque_maximo
    )

    return estoque_models.atualizar_produto(
        produto_id,
        nome.strip(),
        descricao,
        quantidade,
        preco,
        estoque_minimo,
        estoque_maximo
    )


def deletar_produto(usuario, produto_id):
    exigir_admin(usuario)

    buscar_produto(produto_id)

    return estoque_models.deletar_produto(produto_id)