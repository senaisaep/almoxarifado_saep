  
CREATE DATABASE IF NOT EXISTS almoxarifado_saep
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE almoxarifado_saep;

DROP TABLE IF EXISTS movimentacoes;
DROP TABLE IF EXISTS produtos;
DROP TABLE IF EXISTS usuarios;

-- TABELA DE USUARIOS
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    perfil ENUM('administrador', 'operador') NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    data_cadastro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- TABELA DE PRODUTOS
CREATE TABLE produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    descricao TEXT,
    preco DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    quantidade_estoque INT NOT NULL DEFAULT 0,
    data_cadastro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- TABELA DE MOVIMENTACOES
CREATE TABLE movimentacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    produto_id INT NOT NULL,
    usuario_id INT NOT NULL,
    tipo ENUM('entrada', 'saida') NOT NULL,
    quantidade INT NOT NULL,
    data_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_mov_produto
        FOREIGN KEY (produto_id) REFERENCES produtos(id),

    CONSTRAINT fk_mov_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- PRODUTOS INICIAIS
INSERT INTO produtos
(nome, descricao, preco, quantidade_estoque)
VALUES
('Detergente neutro 500ml', 'Detergente líquido para limpeza geral', 3.50, 40),
('Água sanitária 1L', 'Alvejante para limpeza', 5.90, 25),
('Desinfetante lavanda 2L', 'Desinfetante perfumado', 8.75, 30),
('Sabão em pó 1kg', 'Sabão em pó para lavagem', 12.90, 18),
('Esponja multiuso', 'Esponja para limpeza de superfícies', 2.25, 60),
('Luva de borracha', 'Luva reutilizável para limpeza', 7.50, 15),
('Pano de chão', 'Pano de algodão', 6.00, 22),
('Álcool 70% 1L', 'Álcool para limpeza', 9.90, 12);
