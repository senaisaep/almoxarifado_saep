# Funções que conferem os dados que chegam na API.
# Se algo estiver errado, levantam ErroAPI (resposta 400).
import math
from datetime import datetime

from src.utils.erros import ErroAPI


def exigir_json(corpo):
    # O corpo da requisição precisa ser um objeto JSON, tipo {"nome": "..."}
    if not isinstance(corpo, dict):
        raise ErroAPI("Envie um corpo JSON válido.")
    return corpo


def texto(valor, campo, obrigatorio=True, maximo=None):
    if valor is None or str(valor).strip() == "":
        if obrigatorio:
            raise ErroAPI(f"O campo '{campo}' é obrigatório.")
        return ""
    valor = str(valor).strip()
    if maximo and len(valor) > maximo:
        raise ErroAPI(f"O campo '{campo}' aceita no máximo {maximo} caracteres.")
    return valor


def inteiro(valor, campo, minimo=0):
    try:
        if isinstance(valor, bool) or float(valor) != int(float(valor)):
            raise ValueError
        numero = int(float(valor))
    except (ValueError, TypeError):
        raise ErroAPI(f"O campo '{campo}' deve ser um número inteiro.")
    if numero < minimo:
        raise ErroAPI(f"O campo '{campo}' deve ser maior ou igual a {minimo}.")
    return numero


def preco(valor, campo="preco"):
    try:
        numero = float(valor)
        if isinstance(valor, bool) or not math.isfinite(numero):
            raise ValueError
    except (ValueError, TypeError):
        raise ErroAPI(f"O campo '{campo}' deve ser um número.")
    if numero < 0:
        raise ErroAPI(f"O campo '{campo}' não pode ser negativo.")
    return round(numero, 2)


def data(valor, campo, fim_do_dia=False):
    # Aceita "2026-11-04". Se for a data final, vale até 23:59:59 daquele dia
    if not valor:
        return None
    try:
        resultado = datetime.strptime(valor.strip(), "%Y-%m-%d")
    except ValueError:
        raise ErroAPI(f"O campo '{campo}' deve estar no formato AAAA-MM-DD.")
    if fim_do_dia:
        resultado = resultado.replace(hour=23, minute=59, second=59)
    return resultado


def paginacao(args):
    pagina = inteiro(args.get("pagina", 1), "pagina", minimo=1)
    limite = inteiro(args.get("limite", 10), "limite", minimo=1)
    if limite > 100:
        raise ErroAPI("O campo 'limite' aceita no máximo 100.")
    offset = (pagina - 1) * limite  # ex.: página 3 com limite 10 pula os 20 primeiros
    return pagina, limite, offset


def montar_pagina(dados, total, pagina, limite):
    total_paginas = (total + limite - 1) // limite  # divisão arredondando para cima
    return {"dados": dados, "pagina": pagina, "limite": limite,
            "total": total, "total_paginas": total_paginas}
