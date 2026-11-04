from datetime import datetime

from src.repositories import movimentacao_repository, produto_repository


def validar_quantidade(quantidade):
    try:
        valor = int(quantidade)
    except (TypeError, ValueError):
        raise ValueError("A quantidade deve ser um número inteiro.")

    if valor <= 0:
        raise ValueError("A quantidade deve ser maior que zero.")

    return valor


def validar_responsavel(responsavel):
    valor = str(responsavel or "Sistema").strip()
    return valor or "Sistema"


def listar_movimentacoes():
    return movimentacao_repository.listar()


def registrar_entrada(produto_id, quantidade, responsavel, produto_repo=produto_repository, movimentacao_repo=movimentacao_repository):
    produto = produto_repo.buscar_por_id(produto_id)
    if produto is None:
        raise LookupError("Produto não encontrado.")

    quantidade_validada = validar_quantidade(quantidade)
    responsavel_validado = validar_responsavel(responsavel)
    saldo_atual = int(produto["quantidade_estoque"])
    novo_saldo = saldo_atual + quantidade_validada

    produto_repo.atualizar_quantidade(produto_id, novo_saldo)

    dados = {
        "produto_id": produto_id,
        "tipo": "entrada",
        "quantidade": quantidade_validada,
        "responsavel": responsavel_validado,
        "data_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    return movimentacao_repo.criar(dados)


def registrar_saida(produto_id, quantidade, responsavel, produto_repo=produto_repository, movimentacao_repo=movimentacao_repository):
    produto = produto_repo.buscar_por_id(produto_id)
    if produto is None:
        raise LookupError("Produto não encontrado.")

    quantidade_validada = validar_quantidade(quantidade)
    responsavel_validado = validar_responsavel(responsavel)
    saldo_disponivel = int(produto["quantidade_estoque"])

    if quantidade_validada > saldo_disponivel:
        raise ValueError(
            f"Saida não permitida: estoque insuficiente. Disponivel: {saldo_disponivel}. Solicitado: {quantidade_validada}."
        )

    novo_saldo = saldo_disponivel - quantidade_validada
    produto_repo.atualizar_quantidade(produto_id, novo_saldo)

    dados = {
        "produto_id": produto_id,
        "tipo": "saida",
        "quantidade": quantidade_validada,
        "responsavel": responsavel_validado,
        "data_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    return movimentacao_repo.criar(dados)
