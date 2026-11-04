CREATE DATABASE IF NOT EXISTS almoxarifado_saep
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE almoxarifado_saep;

DROP TABLE IF EXISTS movimentacoes;
DROP TABLE IF EXISTS produtos;
DROP TABLE IF EXISTS usuarios;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    perfil ENUM('admin','operador') NOT NULL DEFAULT 'operador',
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    data_cadastro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    descricao TEXT,
    preco DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    quantidade_estoque INT NOT NULL DEFAULT 0,
    data_cadastro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_produtos_nome (nome),
    CONSTRAINT chk_produtos_preco CHECK (preco >= 0),
    CONSTRAINT chk_produtos_estoque CHECK (quantidade_estoque >= 0)
);

CREATE TABLE movimentacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    produto_id INT NOT NULL,
    usuario_id INT NULL,
    tipo ENUM('entrada','saida') NOT NULL DEFAULT 'entrada',
    quantidade INT NOT NULL,
    data_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_mov_data (data_hora),
    CONSTRAINT chk_mov_quantidade CHECK (quantidade > 0),
    CONSTRAINT fk_movimentacoes_produtos
        FOREIGN KEY (produto_id) REFERENCES produtos(id),
    CONSTRAINT fk_movimentacoes_usuarios
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
);

INSERT INTO usuarios (nome, email, senha_hash, perfil) VALUES
('Administrador', 'admin@almoxarifado.com',
 'pbkdf2:sha256:1000000$o5NkJohAdWfJP3Vu$5ee7ad69b680a74292c11149d54376d041324aff226375c8706244fc25317cc3', 'admin'),
('Operador', 'operador@almoxarifado.com',
 'pbkdf2:sha256:1000000$pCrcshpIWnrN3ApN$14d369200fc4ce13adb7ae13379109e2b22e1f3a613455cf39db85f20862dd9a', 'operador');

INSERT INTO produtos (nome, descricao, preco, quantidade_estoque) VALUES
('Detergente neutro 500ml', 'Detergente líquido para limpeza geral', 3.50, 40),
('Água sanitária 1L', 'Alvejante para limpeza', 5.90, 25),
('Desinfetante lavanda 2L', 'Desinfetante perfumado', 8.75, 30),
('Sabão em pó 1kg', 'Sabão em pó para lavagem', 12.90, 18),
('Esponja multiuso', 'Esponja para limpeza de superfícies', 2.25, 60),
('Luva de borracha', 'Luva reutilizável para limpeza', 7.50, 15),
('Pano de chão', 'Pano de algodão', 6.00, 22),
('Álcool 70% 1L', 'Álcool para limpeza', 9.90, 12);

INSERT INTO movimentacoes (produto_id, usuario_id, tipo, quantidade) VALUES
(1, 1, 'entrada', 40), (2, 1, 'entrada', 25), (3, 1, 'entrada', 30),
(4, 1, 'entrada', 18), (5, 1, 'entrada', 60), (6, 1, 'entrada', 15),
(7, 1, 'entrada', 22), (8, 1, 'entrada', 12);