
# Conexão com o banco de dados e responsável por criar as tabelas
import sqlite3

def Conectar():
    # Conectando ao banco de dados
    conexao = sqlite3.connect('almoxarifado.db')
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def Criar_tabelas():
    conexao = Conectar()
    cursor = conexao.cursor()

    query_sql = """
        DROP TABLE IF EXISTS movimentacoes;
        DROP TABLE IF EXISTS produtos;

        CREATE TABLE produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome VARCHAR(120) NOT NULL,
            descricao TEXT,
            preco DECIMAL(10,2) NOT NULL DEFAULT 0.00,
            quantidade_estoque INTEGER NOT NULL DEFAULT 0,
            data_cadastro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL,
            tipo TEXT NOT NULL DEFAULT 'entrada'
                CHECK (tipo IN ('entrada')),
            quantidade INTEGER NOT NULL,

            CONSTRAINT fk_movimentacoes_produtos
                FOREIGN KEY (produto_id) REFERENCES produtos(id)
        );
    """

    query_sql_insert = """
        INSERT INTO produtos (nome, descricao, preco, quantidade_estoque) VALUES
        ('Detergente neutro 500ml', 'Detergente líquido para limpeza geral', 3.50, 40),
        ('Água sanitária 1L', 'Alvejante para limpeza', 5.90, 25),
        ('Desinfetante lavanda 2L', 'Desinfetante perfumado', 8.75, 30),
        ('Sabão em pó 1kg', 'Sabão em pó para lavagem', 12.90, 18),
        ('Esponja multiuso', 'Esponja para limpeza de superfícies', 2.25, 60),
        ('Luva de borracha', 'Luva reutilizável para limpeza', 7.50, 15),
        ('Pano de chão', 'Pano de algodão', 6.00, 22),
        ('Álcool 70% 1L', 'Álcool para limpeza', 9.90, 12);

        INSERT INTO movimentacoes (produto_id, tipo, quantidade) VALUES
        (1, 'entrada', 40), (2, 'entrada', 25), (3, 'entrada', 30),
        (4, 'entrada', 18), (5, 'entrada', 60), (6, 'entrada', 15),
        (7, 'entrada', 22), (8, 'entrada', 12);
    """

    cursor.executescript(query_sql)

    conexao.commit()
    cursor.close()
    conexao.close()
