-- Estado inicial do banco entregue pelo aplicador.
-- Não inclui usuários/perfis, data/hora ou responsável pela movimentação.

CREATE DATABASE IF NOT EXISTS almoxarifado_saep
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE almoxarifado_saep;

DROP TABLE IF EXISTS movimentacoes;
DROP TABLE IF EXISTS produtos;
DROP TABLE IF EXISTS usuarios;

CREATE TABLE produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    descricao TEXT,
    preco DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    quantidade_estoque INT NOT NULL DEFAULT 0,
    data_cadastro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    
);


CREATE TABLE usuarios(
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    cargo VARCHAR(150) NOT NULL
);

CREATE TABLE movimentacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    produto_id INT NOT NULL,
    tipo ENUM('entrada') NOT NULL DEFAULT 'entrada',
    quantidade INT NOT NULL,
    data_saida DATETIME NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    responsavel_saida VARCHAR(150) NOT NULL
    CONSTRAINT fk_movimentacoes_produtos
        FOREIGN KEY (produto_id) REFERENCES produtos(id)
);

INSERT INTO produtos (nome, descricao, preco, quantidade_estoque) VALUES
('Detergente neutro 500ml', 'Detergente líquido para limpeza geral', 3.50, 40),
('Água sanitária 1L', 'Alvejante para limpeza', 5.90, 25),
('Desinfetante lavanda 2L', 'Desinfetante perfumado', 8.75, 30),
('Sabão em pó 1kg', 'Sabão em pó para lavagem', 12.90, 18),
('Esponja multiuso', 'Esponja para limpeza de superfícies', 2.25, 60),
('Luva de borracha', 'Luva reutilizável para limpeza', 7.50, 15),
('Pano de chão', 'Pano de algodão', 6.00, 22),
('Álcool 70% 1L', 'Álcool para limpeza', 9.90, 12);

INSERT INTO movimentacoes (produto_id, tipo) VALUES
(1, 'entrada', 40), (2, 'entrada', 25), (3, 'entrada', 30),
(4, 'entrada', 18), (5, 'entrada', 60), (6, 'entrada', 15),
(7, 'entrada', 22), (8, 'entrada', 12);

INSERT INTO usuarios (nome, cargo) VALUES
( 'Maria', 'Administrador do sitema'),
('João', 'Operador de Almoxarifado');

