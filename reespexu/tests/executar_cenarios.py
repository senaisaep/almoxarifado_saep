"""Executa os cenários do plano de testes (saída de produtos) contra a API
em execução e gera as evidências em docs/testes/cenarioX.txt.

Pré-requisitos:
  1. Banco recriado com infra/bd.sql (estado inicial conhecido).
  2. Servidor rodando:  python -m src.server
Uso:
  python -m tests.executar_cenarios            # usa http://127.0.0.1:5000
  python -m tests.executar_cenarios http://127.0.0.1:5000
"""
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5000").rstrip("/")
RAIZ = Path(__file__).resolve().parent.parent
PASTA_EVIDENCIAS = RAIZ / "docs" / "testes"
ARQUIVO_RESULTADOS = RAIZ / "docs" / "resultados_execucao.json"


def chamar(metodo, caminho, corpo=None, token=None, log=None):
    dados = json.dumps(corpo).encode() if corpo is not None else None
    req = urllib.request.Request(BASE + caminho, data=dados, method=metodo)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req) as resp:
            status, texto = resp.status, resp.read().decode()
    except urllib.error.HTTPError as erro:
        status, texto = erro.code, erro.read().decode()
    resposta = json.loads(texto) if texto else None
    if log is not None:
        log.append(f">>> {metodo} {caminho}")
        if corpo is not None:
            if "senha" in corpo:
                corpo = {**corpo, "senha": "********"}
            log.append(f"    corpo: {json.dumps(corpo, ensure_ascii=False)}")
        if token:
            log.append("    header: Authorization: Bearer <token>")
        log.append(f"<<< HTTP {status}")
        visivel = resposta
        if isinstance(resposta, dict) and "token" in resposta:
            visivel = {**resposta, "token": "<token omitido>"}
        log.append("    " + json.dumps(visivel, ensure_ascii=False, indent=2).replace("\n", "\n    "))
        log.append("")
    return status, resposta


def login(email, senha, log=None):
    status, corpo = chamar("POST", "/auth/login", {"email": email, "senha": senha}, log=log)
    assert status == 200, f"Login falhou: {corpo}"
    return corpo["token"]


def estoque(produto_id, token, log=None):
    _, produto = chamar("GET", f"/produtos/{produto_id}", token=token, log=log)
    return produto["quantidade_estoque"]


def total_movimentacoes(produto_id, token):
    _, r = chamar("GET", f"/movimentacoes?produto_id={produto_id}&tipo=saida", token=token)
    return r["total"]


def executar(numero, titulo, produto_id, quantidade, esperado, verificar):
    log = [
        f"EVIDÊNCIA - CENÁRIO {numero}: {titulo}",
        f"Executado em: {datetime.now():%d/%m/%Y %H:%M:%S}",
        f"API: {BASE}",
        "=" * 70, "",
        "[Passo 1] Login do operador", "",
    ]
    token = login("operador@almoxarifado.com", "operador123", log)

    log += ["[Passo 2] Consulta do saldo ANTES da saída", ""]
    antes = estoque(produto_id, token, log)
    movs_antes = total_movimentacoes(produto_id, token)

    log += [f"[Passo 3] Solicitação de saída de {quantidade} unidade(s)", ""]
    status, resposta = chamar(
        "POST", "/movimentacoes/saida",
        {"produto_id": produto_id, "quantidade": quantidade}, token, log)

    log += ["[Passo 4] Consulta do saldo DEPOIS da saída", ""]
    depois = estoque(produto_id, token, log)
    movs_depois = total_movimentacoes(produto_id, token)

    log += ["[Passo 5] Consulta do histórico de saídas do produto", ""]
    _, historico = chamar(
        "GET", f"/movimentacoes?produto_id={produto_id}&tipo=saida", token=token, log=log)

    obtido = {
        "status": status,
        "mensagem": resposta.get("mensagem"),
        "estoque_antes": antes,
        "estoque_depois": depois,
        "novas_movimentacoes": movs_depois - movs_antes,
        "ultima_movimentacao": historico["dados"][0] if historico["dados"] else None,
    }
    aprovado, comparacoes = verificar(obtido, esperado)

    log += ["=" * 70, "COMPARAÇÃO ESPERADO x OBTIDO"]
    log += [f"  {nome}: esperado={e!r} | obtido={o!r} -> {'OK' if ok else 'FALHOU'}"
            for nome, e, o, ok in comparacoes]
    log += ["", f"RESULTADO DO TESTE: {'APROVADO' if aprovado else 'REPROVADO'}"]

    arquivo = PASTA_EVIDENCIAS / f"cenario{numero}.txt"
    arquivo.write_text("\n".join(log) + "\n", encoding="utf-8")
    return {
        "numero": numero, "titulo": titulo, "produto_id": produto_id,
        "quantidade": quantidade, "esperado": esperado, "obtido": obtido,
        "comparacoes": [{"item": n, "esperado": e, "obtido": o, "ok": ok}
                        for n, e, o, ok in comparacoes],
        "aprovado": aprovado, "evidencia": f"docs/testes/{arquivo.name}",
        "executado_em": f"{datetime.now():%d/%m/%Y %H:%M:%S}",
    }


def comparar(obtido, esperado):
    itens = []
    for chave, valor_esperado in esperado.items():
        if chave == "usuario_ultima_saida":
            valor = (obtido["ultima_movimentacao"] or {}).get("usuario")
        elif chave == "tem_data_hora":
            valor = bool((obtido["ultima_movimentacao"] or {}).get("data_hora"))
        elif chave == "tipo_ultima_movimentacao":
            valor = (obtido["ultima_movimentacao"] or {}).get("tipo")
        else:
            valor = obtido[chave]
        itens.append((chave, valor_esperado, valor, valor == valor_esperado))
    return all(i[3] for i in itens), itens


CENARIOS = [
    (1, "Saída com quantidade MAIOR que o saldo disponível", 6, 20, {
        "status": 409,
        "mensagem": "Saída não permitida: estoque insuficiente. Disponível: 15. Solicitado: 20.",
        "estoque_depois": 15, "novas_movimentacoes": 0}),
    (2, "Saída com quantidade MENOR que o saldo disponível", 1, 10, {
        "status": 201, "estoque_antes": 40, "estoque_depois": 30, "novas_movimentacoes": 1}),
    (3, "Saída com quantidade IGUAL ao saldo disponível", 8, 12, {
        "status": 201, "estoque_antes": 12, "estoque_depois": 0, "novas_movimentacoes": 1}),
    (4, "Registro de data/hora e responsável na saída", 2, 5, {
        "status": 201, "estoque_depois": 20, "novas_movimentacoes": 1,
        "tipo_ultima_movimentacao": "saida", "usuario_ultima_saida": "Operador",
        "tem_data_hora": True}),
]

if __name__ == "__main__":
    PASTA_EVIDENCIAS.mkdir(parents=True, exist_ok=True)
    resultados = [executar(n, t, p, q, e, comparar) for n, t, p, q, e in CENARIOS]
    ARQUIVO_RESULTADOS.write_text(
        json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")
    for r in resultados:
        print(f"Cenário {r['numero']}: {'APROVADO' if r['aprovado'] else 'REPROVADO'} "
              f"-> {r['evidencia']}")
    sys.exit(0 if all(r["aprovado"] for r in resultados) else 1)
