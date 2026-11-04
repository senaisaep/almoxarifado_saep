import os
from contextlib import contextmanager

import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def conectar():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "almoxarifado_saep"),
    )


@contextmanager
def transacao():
    # Uso: with transacao() as cursor: ...
    # Tudo dentro do "with" é uma transação só: se der erro, desfaz tudo (rollback);
    # se der certo, grava (commit). No fim, a conexão é sempre fechada.
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)
    try:
        yield cursor
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        cursor.close()
        conexao.close()
