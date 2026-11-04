import sqlite3
import os

from pathlib import Path
from werkzeug.security import generate_password_hash


# Caminho absoluto do banco de dados
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "estoque.db"


def conectar():
    conexao = sqlite3.connect(DB_PATH)
    conexao.row_factory = sqlite3.Row

    # Habilita integridade referencial
    conexao.execute("PRAGMA foreign_keys = ON")

    return conexao


def criar_banco():
    conexao = conectar()

    try:
        cursor = conexao.cursor()

        # ==========================
        # TABELA DE USUÁRIOS
        # ==========================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                login TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                perfil TEXT NOT NULL
                    CHECK(perfil IN ('admin', 'operador'))
            )
        """)

        # ==========================
        # TABELA DE PRODUTOS
        # ==========================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                descricao TEXT NOT NULL DEFAULT '',
                quantidade INTEGER NOT NULL DEFAULT 0
                    CHECK(quantidade >= 0),
                preco REAL NOT NULL
                    CHECK(preco >= 0),
                estoque_minimo INTEGER NOT NULL DEFAULT 0
                    CHECK(estoque_minimo >= 0),
                estoque_maximo INTEGER NOT NULL DEFAULT 999999
                    CHECK(estoque_maximo >= estoque_minimo)
            )
        """)

        # ==========================
        # TABELA DE MOVIMENTAÇÕES
        # ==========================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS movimentacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id INTEGER NOT NULL,
                tipo TEXT NOT NULL
                    CHECK(tipo IN ('entrada', 'saida')),
                quantidade INTEGER NOT NULL
                    CHECK(quantidade > 0),
                data_hora TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY(produto_id)
                    REFERENCES produtos(id)
                    ON DELETE RESTRICT
            )
        """)

        # ==========================
        # USUÁRIOS INICIAIS
        # ==========================

        cursor.execute("""
            INSERT OR IGNORE INTO usuarios
            (nome, login, senha, perfil)
            VALUES (?, ?, ?, ?)
        """, (
            "Administrador",
            "admin",
            generate_password_hash(
                os.getenv("ESTOQUE_ADMIN_PASSWORD", "123")
            ),
            "admin"
        ))

        cursor.execute("""
            INSERT OR IGNORE INTO usuarios
            (nome, login, senha, perfil)
            VALUES (?, ?, ?, ?)
        """, (
            "Operador",
            "operador",
            generate_password_hash(
                os.getenv("ESTOQUE_OPERATOR_PASSWORD", "123")
            ),
            "operador"
        ))

        conexao.commit()

        print("Banco de dados inicializado com sucesso!")

    except Exception:
        conexao.rollback()
        raise

    finally:
        conexao.close()


if __name__ == "__main__":
    criar_banco()