from datetime import date

from flask import Blueprint, g, jsonify, request

from Controle import saida_servico
from Controle.estoque_controle import (
    _TODOS,
    _banco,
    _erro,
    _exigir_perfil,
    _quantidade,
)

produtos = Blueprint("produtos", __name__)


@produtos.get("/produtos")
@_exigir_perfil(*_TODOS)
def listar_produtos():
    pagina = _quantidade(request.args.get("pagina", "1"))
    por_pagina = _quantidade(request.args.get("por_pagina", "10"))
    nome = request.args.get("nome", "").strip()
    data = request.args.get("data", "").strip()

    if pagina is None or por_pagina is None or por_pagina > 100:
        return _erro("Página inválida; por_pagina deve estar entre 1 e 100.")
    if data:
        try:
            data = date.fromisoformat(data).isoformat()
        except ValueError:
            return _erro("Data inválida. Use o formato AAAA-MM-DD.")

    filtros, parametros = ["ativo=1"], []
    if nome:
        filtros.append("nome LIKE %s")
        parametros.append(f"%{nome}%")
    if data:
        filtros.append("DATE(data_cadastro)=%s")
        parametros.append(data)
    where = " AND ".join(filtros)

    with _banco(True) as (_, cursor):
        cursor.execute(f"SELECT COUNT(*) AS total FROM produtos WHERE {where}", parametros)
        total = cursor.fetchone()["total"]
        cursor.execute(
            f"SELECT * FROM produtos WHERE {where} ORDER BY id LIMIT %s OFFSET %s",
            (*parametros, por_pagina, (pagina - 1) * por_pagina),
        )
        itens = cursor.fetchall()
    return jsonify({
        "produtos": itens,
        "pagina": pagina,
        "por_pagina": por_pagina,
        "total": total,
        "paginas": (total + por_pagina - 1) // por_pagina,
    })


@produtos.post("/movimentacoes/saida")
@_exigir_perfil(*_TODOS)
def registrar_saida():
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return _erro("Envie um objeto JSON.")
    produto_id = _quantidade(dados.get("produto_id"))
    quantidade = _quantidade(dados.get("quantidade"))
    if produto_id is None or quantidade is None:
        return _erro("Informe produto_id e quantidade inteira maior que zero.")

    with _banco() as (conexao, cursor):
        try:
            saida_servico.registrar_saida(cursor, produto_id, quantidade, g.usuario)
        except saida_servico.ProdutoNaoEncontrado:
            return _erro("Produto não encontrado.", 404)
        except saida_servico.EstoqueInsuficiente:
            return _erro("Estoque insuficiente para essa saída.", 409)
        conexao.commit()
    return jsonify({"mensagem": "Saída registrada com sucesso."}), 201