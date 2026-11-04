import sqlite3
from pathlib import Path

from werkzeug.security import generate_password_hash


DATABASE_PATH = Path(__file__).resolve().with_name("almoxarifado.db")


SCHEMA = """
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    login TEXT NOT NULL UNIQUE,
    senha TEXT NOT NULL,
    perfil TEXT NOT NULL CHECK (perfil IN ('Administrador', 'Operador'))
);

CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT NOT NULL DEFAULT '',
    preco REAL NOT NULL DEFAULT 0 CHECK (preco >= 0),
    quantidade_estoque INTEGER NOT NULL DEFAULT 0 CHECK (quantidade_estoque >= 0),
    data_cadastro TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS movimentacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL REFERENCES produtos(id),
    tipo TEXT NOT NULL CHECK (tipo IN ('entrada', 'saida')),
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
    data_hora TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

PRODUTOS_INICIAIS = (
    ("Detergente neutro 500ml", "Detergente líquido para limpeza geral", 3.50, 40),
    ("Água sanitária 1L", "Alvejante para limpeza", 5.90, 25),
    ("Desinfetante lavanda 2L", "Desinfetante perfumado", 8.75, 30),
    ("Sabão em pó 1kg", "Sabão em pó para lavagem", 12.90, 18),
    ("Esponja multiuso", "Esponja para limpeza de superfícies", 2.25, 60),
    ("Luva de borracha", "Luva reutilizável para limpeza", 7.50, 15),
    ("Pano de chão", "Pano de algodão", 6.00, 22),
    ("Álcool 70% 1L", "Álcool para limpeza", 9.90, 12),
)

USUARIOS_INICIAIS = (
    ("Administrador", "admin", "123", "Administrador"),
    ("Operador", "operador", "456", "Operador"),
)


def conectar():
    conexao = sqlite3.connect(DATABASE_PATH, timeout=10)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def inicializar_banco():
    conexao = conectar()
    try:
        conexao.executescript(SCHEMA)
        conexao.executemany(
            """INSERT INTO produtos (nome, descricao, preco, quantidade_estoque)
               SELECT ?, ?, ?, ?
               WHERE NOT EXISTS (
                   SELECT 1 FROM produtos WHERE nome = ? COLLATE NOCASE
               )""",
            (
                (nome, descricao, preco, quantidade, nome)
                for nome, descricao, preco, quantidade in PRODUTOS_INICIAIS
            ),
        )
        conexao.executemany(
            """INSERT OR IGNORE INTO usuarios (nome, login, senha, perfil)
               VALUES (?, ?, ?, ?)""",
            (
                (nome, login, generate_password_hash(senha), perfil)
                for nome, login, senha, perfil in USUARIOS_INICIAIS
            ),
        )
        conexao.commit()
    finally:
        conexao.close()
