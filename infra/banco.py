import sqlite3

def conectar():
    conexao = sqlite3.connect("almoxarifado_saep")
    return conexao

def criar_banco():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            login TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            perfil TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            valor REAL NOT NULL,
            quantidade INTEGER NOT NULL,
            estoque_minimo INTEGER NOT NULL,
            estoque_maximo INTEGER NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            data_hora TEXT NOT NULL,
            FOREIGN KEY(produto_id) REFERENCES produtos(id)
        )
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO usuarios
        (nome, login, senha, perfil)
        VALUES (?, ?, ?, ?)
    """, (
        "Administrador",
        "admin",
        "123",
        "Administrador"
    ))

    cursor.execute("""
        INSERT OR IGNORE INTO usuarios
        (nome, login, senha, perfil)
        VALUES (?, ?, ?, ?)
    """, (
        "Operador",
        "operador",
        "123",
        "Operador"
    ))

    conexao.commit()
    cursor.close()
    conexao.close()

criar_banco()