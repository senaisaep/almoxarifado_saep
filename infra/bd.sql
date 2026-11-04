-- Almoxarifado SAEP - versão 1.0.0
-- Cria banco, tabelas (com usuários/perfis, data/hora e responsável nas
-- movimentações) e dados iniciais.
-- O administrador NÃO é criado aqui (evita senha padrão no repositório):
--   python -m src.scripts.criar_admin

CREATE DATABASE IF NOT EXISTS almoxarifado_saep
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE almoxarifado_saep;

DROP TABLE IF EXISTS movimentacoes;
DROP TABLE IF EXISTS produtos;
DROP TABLE IF EXISTS usuarios;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    email VARCHAR(160) NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    perfil ENUM('admin','almoxarife','consulta') NOT NULL DEFAULT 'consulta',
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    tentativas_login INT NOT NULL DEFAULT 0,
    bloqueado_ate DATETIME NULL,
    data_cadastro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_usuarios_email UNIQUE (email)
);

CREATE TABLE produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    descricao TEXT,
    preco DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    quantidade_estoque INT NOT NULL DEFAULT 0,
    data_cadastro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_produtos_nome (nome),
    -- Última barreira: o banco também impede saldo/preço negativos (MySQL >= 8.0.16)
    CONSTRAINT ck_produtos_preco CHECK (preco >= 0),
    CONSTRAINT ck_produtos_estoque CHECK (quantidade_estoque >= 0)
);

CREATE TABLE movimentacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    produto_id INT NOT NULL,
    tipo ENUM('entrada','saida') NOT NULL DEFAULT 'entrada',
    quantidade INT NOT NULL,
    data_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    usuario_id INT NOT NULL,
    INDEX idx_mov_data (data_hora),
    INDEX idx_mov_produto (produto_id),
    CONSTRAINT ck_mov_quantidade CHECK (quantidade > 0),
    CONSTRAINT fk_movimentacoes_produtos
        FOREIGN KEY (produto_id) REFERENCES produtos(id),
    CONSTRAINT fk_movimentacoes_usuarios
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- Usuário técnico (inativo, sem login possível) dono da carga inicial.
INSERT INTO usuarios (id, nome, email, senha_hash, perfil, ativo) VALUES
(1, 'Sistema (carga inicial)', 'sistema@almoxarifado.local', '!sem-login', 'consulta', 0);

INSERT INTO produtos (nome, descricao, preco, quantidade_estoque) VALUES
('Detergente neutro 500ml', 'Detergente líquido para limpeza geral', 3.50, 40),
('Água sanitária 1L', 'Alvejante para limpeza', 5.90, 25),
('Desinfetante lavanda 2L', 'Desinfetante perfumado', 8.75, 30),
('Sabão em pó 1kg', 'Sabão em pó para lavagem', 12.90, 18),
('Esponja multiuso', 'Esponja para limpeza de superfícies', 2.25, 60),
('Luva de borracha', 'Luva reutilizável para limpeza', 7.50, 15),
('Pano de chão', 'Pano de algodão', 6.00, 22),
('Álcool 70% 1L', 'Álcool para limpeza', 9.90, 12);

INSERT INTO movimentacoes (produto_id, tipo, quantidade, usuario_id) VALUES
(1, 'entrada', 40, 1), (2, 'entrada', 25, 1), (3, 'entrada', 30, 1),
(4, 'entrada', 18, 1), (5, 'entrada', 60, 1), (6, 'entrada', 15, 1),
(7, 'entrada', 22, 1), (8, 'entrada', 12, 1);
