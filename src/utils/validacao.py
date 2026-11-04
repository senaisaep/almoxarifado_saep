import re
from datetime import datetime
from decimal import Decimal, InvalidOperation

from src.utils.erros import ErroApi

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
POR_PAGINA_PADRAO = 10
POR_PAGINA_MAX = 100


def corpo_json(request):
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        raise ErroApi("Corpo da requisição deve ser um objeto JSON.", 400)
    return dados


def inteiro_positivo(valor, campo):
    if isinstance(valor, bool) or valor is None:
        raise ErroApi(f"{campo} deve ser um número inteiro maior que zero.", 400)
    if isinstance(valor, float) and not valor.is_integer():
        raise ErroApi(f"{campo} deve ser um número inteiro maior que zero.", 400)
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        raise ErroApi(f"{campo} deve ser um número inteiro maior que zero.", 400)
    if numero <= 0:
        raise ErroApi(f"{campo} deve ser um número inteiro maior que zero.", 400)
    return numero


def inteiro_nao_negativo(valor, campo):
    if valor in (0, "0"):
        return 0
    return inteiro_positivo(valor, campo)


def texto_obrigatorio(valor, campo, maximo):
    if not isinstance(valor, str) or not valor.strip():
        raise ErroApi(f"O campo {campo} é obrigatório.", 400)
    valor = valor.strip()
    if len(valor) > maximo:
        raise ErroApi(f"O campo {campo} aceita no máximo {maximo} caracteres.", 400)
    return valor


def texto_opcional(valor, campo, maximo=2000):
    if valor is None:
        return ""
    if not isinstance(valor, str):
        raise ErroApi(f"O campo {campo} deve ser texto.", 400)
    valor = valor.strip()
    if len(valor) > maximo:
        raise ErroApi(f"O campo {campo} aceita no máximo {maximo} caracteres.", 400)
    return valor


def preco_valido(valor):
    if isinstance(valor, bool) or valor is None:
        raise ErroApi("O campo preco deve ser um número maior ou igual a zero.", 400)
    try:
        numero = Decimal(str(valor)).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        raise ErroApi("O campo preco deve ser um número maior ou igual a zero.", 400)
    if numero < 0 or numero > Decimal("99999999.99"):
        raise ErroApi("O campo preco deve ser um número maior ou igual a zero.", 400)
    return numero


def email_valido(valor):
    email = texto_obrigatorio(valor, "email", 160).lower()
    if not _EMAIL.match(email):
        raise ErroApi("E-mail inválido.", 400)
    return email


def senha_forte(valor):
    if (
        not isinstance(valor, str)
        or len(valor) < 8
        or len(valor) > 128
        or not re.search(r"[A-Za-z]", valor)
        or not re.search(r"\d", valor)
    ):
        raise ErroApi(
            "Senha inválida: use de 8 a 128 caracteres, com letras e números.", 400
        )
    return valor


def data_iso(valor, campo):
    if not valor:
        return None
    try:
        return datetime.strptime(valor, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        raise ErroApi(f"{campo} deve estar no formato AAAA-MM-DD.", 400)


def paginacao(args):
    pagina = inteiro_positivo(args.get("pagina", 1), "pagina")
    por_pagina = inteiro_positivo(args.get("por_pagina", POR_PAGINA_PADRAO), "por_pagina")
    return pagina, min(por_pagina, POR_PAGINA_MAX)


def resposta_paginada(dados, total, pagina, por_pagina):
    return {
        "dados": dados,
        "pagina": pagina,
        "por_pagina": por_pagina,
        "total": total,
        "total_paginas": (total + por_pagina - 1) // por_pagina,
    }
