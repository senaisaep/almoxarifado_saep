CREATE DATABASE IF NOT EXISTS almoxarifado_saep
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE almoxarifado_saep;

CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    email VARCHAR(160) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    perfil ENUM('operador','administrador') NOT NULL DEFAULT 'operador',
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    data_cadastro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    descricao TEXT,
    preco DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    quantidade_estoque INT NOT NULL DEFAULT 0,
    data_cadastro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS movimentacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    produto_id INT NOT NULL,
    tipo ENUM('entrada','saida') NOT NULL,
    quantidade INT NOT NULL,
    usuario_id INT NOT NULL,
    data_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_mov_produto FOREIGN KEY (produto_id) REFERENCES produtos(id),
    CONSTRAINT fk_mov_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

INSERT INTO produtos (nome, descricao, preco, quantidade_estoque)
SELECT dados.nome, dados.descricao, dados.preco, dados.quantidade
FROM (
    SELECT 'Detergente neutro 500ml' nome, 'Detergente líquido para limpeza geral' descricao, 3.50 preco, 40 quantidade
    UNION ALL SELECT 'Água sanitária 1L', 'Alvejante para limpeza', 5.90, 25
    UNION ALL SELECT 'Desinfetante lavanda 2L', 'Desinfetante perfumado', 8.75, 30
    UNION ALL SELECT 'Sabão em pó 1kg', 'Sabão em pó para lavagem', 12.90, 18
    UNION ALL SELECT 'Esponja multiuso', 'Esponja para limpeza de superfícies', 2.25, 60
    UNION ALL SELECT 'Luva de borracha', 'Luva reutilizável para limpeza', 7.50, 15
    UNION ALL SELECT 'Pano de chão', 'Pano de algodão', 6.00, 22
    UNION ALL SELECT 'Álcool 70% 1L', 'Álcool para limpeza', 9.90, 12
) dados
WHERE NOT EXISTS (SELECT 1 FROM produtos LIMIT 1);
