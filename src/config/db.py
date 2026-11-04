import logging
import os
from contextlib import contextmanager
from pathlib import Path

import mysql.connector
from mysql.connector import pooling
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("almoxarifado.db")

_pool = None


def obter_configuracao():
    """Retorna os parâmetros de conexão a partir das variáveis de ambiente."""
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", "almoxarifado_saep"),
        "charset": "utf8mb4",
        "use_unicode": True,
        "connect_timeout": 5,
    }


def _obter_pool():
    global _pool
    if _pool is None:
        cfg = obter_configuracao()
        try:
            _pool = pooling.MySQLConnectionPool(
                pool_name="almoxarifado_pool",
                pool_size=5,
                pool_reset_session=True,
                **cfg,
            )
        except Exception as e:
            logger.debug("Pool de conexões não inicializado (%s). Conexões serão abertas sob demanda.", e)
            _pool = False
    return _pool if _pool is not False else None


def conectar():
    """Abre conexão com o MySQL, utilizando o pool de conexões quando disponível."""
    cfg = obter_configuracao()
    pool = _obter_pool()
    if pool:
        try:
            return pool.get_connection()
        except Exception as e:
            logger.warning("Falha ao obter conexão do pool (%s). Tentando conexão direta.", e)

    try:
        return mysql.connector.connect(**cfg)
    except mysql.connector.Error as err:
        msg = (
            f"Erro ao conectar ao MySQL ({cfg['host']}:{cfg['port']}, banco='{cfg['database']}', usuário='{cfg['user']}'): {err}. "
            "Verifique se o serviço MySQL está ativo e se os dados no arquivo .env estão corretos."
        )
        logger.error(msg)
        raise RuntimeError(msg) from err


@contextmanager
def transacao():
    """Abre conexão + cursor e controla a transação.

    Commit ao sair normalmente; rollback se qualquer exceção ocorrer dentro
    do bloco. É a base da atomicidade das operações de estoque.
    """
    conexao = conectar()
    conexao.autocommit = False
    cursor = conexao.cursor(dictionary=True)
    try:
        yield cursor
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        try:
            conexao.close()
        except Exception:
            pass


def testar_conexao():
    """Testa se a conexão com o banco de dados está operacional.

    Retorna uma tupla (sucesso: bool, mensagem: str).
    """
    try:
        with transacao() as cur:
            cur.execute("SELECT 1 AS status")
            cur.fetchone()
            return True, "Conexão com o banco de dados estabelecida com sucesso."
    except Exception as e:
        return False, str(e)


def inicializar_banco(caminho_sql=None):
    """Cria banco e tabelas caso não existam a partir do script SQL."""
    if caminho_sql is None:
        raiz = Path(__file__).resolve().parent.parent.parent
        caminho_sql = raiz / "infra" / "bd.sql"

    if not Path(caminho_sql).exists():
        raise FileNotFoundError(f"Arquivo de inicialização SQL não encontrado: {caminho_sql}")

    cfg = obter_configuracao()
    banco_nome = cfg["database"]

    # Conecta sem banco para garantir que ele existe
    cfg_sem_banco = dict(cfg)
    cfg_sem_banco.pop("database", None)
    conn = mysql.connector.connect(**cfg_sem_banco)
    cursor = conn.cursor()
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{banco_nome}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute(f"USE `{banco_nome}`")

        with open(caminho_sql, "r", encoding="utf-8") as f:
            script = f.read()

        for comando in script.split(";"):
            comando = comando.strip()
            if comando and not comando.upper().startswith("USE "):
                cursor.execute(comando)
        conn.commit()
        return True, f"Banco '{banco_nome}' inicializado com sucesso."
    finally:
        cursor.close()
        conn.close()
