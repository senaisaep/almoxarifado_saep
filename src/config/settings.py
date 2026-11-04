import os

from dotenv import load_dotenv

load_dotenv()


def _inteiro(nome, padrao):
    try:
        return int(os.getenv(nome, padrao))
    except ValueError:
        return int(padrao)


def secret_key():
    chave = os.getenv("SECRET_KEY", "")
    if len(chave) < 32:
        raise RuntimeError(
            "SECRET_KEY ausente ou curta demais (mínimo 32 caracteres). "
            "Defina no arquivo .env."
        )
    return chave


def jwt_expira_minutos():
    return _inteiro("JWT_EXPIRA_MINUTOS", "60")


def login_max_tentativas():
    return _inteiro("LOGIN_MAX_TENTATIVAS", "5")


def login_bloqueio_minutos():
    return _inteiro("LOGIN_BLOQUEIO_MINUTOS", "15")
