import sqlite3

def conectar():
    conexao = sqlite3.connect("estoque.db")
    return conexao

def criar_banco():
   conexao = conectar()
   cursor = conexao.cursor()

   cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            login TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            perfil TEXT NOT NULL
        )
    """)
   
   cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            preco TEXT NOT NULL,
            quantidade_estoque TEXT NOT NULL,
            data_cadastro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
   
   cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimentacoes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id TEXT NOT NULL,
            tipo TEXT NOT NULL,
            quantidade TEXT NOT NULL,
            data_hora TEXT NOT NULL,
            FOREIGN KEY(produto_id) REFERENCES produtos(id)
        )
    """)
   
   cursor.execute("""
        INSERT OR IGNORE INTO usuarios(
        nome, login, senha, perfil) VALUES(
        ?,?,?,?)
    """, (
        "Administrador",
        "admin",
        "123",
        "Administrador"
    ))

   cursor.execute("""
        INSERT OR IGNORE INTO usuarios(
        nome, login, senha, perfil) VALUES(
        ?,?,?,?) 
    """, (
        "Operador",
        "operador",
        "123",
        "Operador"
    ))

   cursor.execute("""
           INSERT OR IGNORE INTO produtos(
           nome, descricao, preco, quantidade_estoque) VALUES(
           ?,?,?,?) 
       """, (
            "Detergente neutro 500ml", 
            "Detergente líquido para limpeza geral",
            "3.50", 
            "40"
        ))
   
   cursor.execute("""
            INSERT OR IGNORE INTO movimentacoes(
            produto_id, tipo, quantidade) VALUES(
            ?,?,?) 
        """, (
            "1", 
            "entrada",
            "40"
        ))
   conexao.commit()
   cursor.close()
   conexao.close()
   
criar_banco()

