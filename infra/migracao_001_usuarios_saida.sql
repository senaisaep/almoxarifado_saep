-- Migração para quem JÁ possui o banco da versão 0.1.0 com dados.
-- Execute UMA vez. (Em banco novo, use apenas infra/bd.sql.)
USE almoxarifado_saep;

CREATE TABLE IF NOT EXISTS usuarios (
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

INSERT IGNORE INTO usuarios (id, nome, email, senha_hash, perfil, ativo) VALUES
(1, 'Sistema (carga inicial)', 'sistema@almoxarifado.local', '!sem-login', 'consulta', 0);

-- Movimentações antigas ficam atribuídas ao usuário técnico (id 1).
ALTER TABLE movimentacoes
  MODIFY tipo ENUM('entrada','saida') NOT NULL DEFAULT 'entrada',
  ADD COLUMN data_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ADD COLUMN usuario_id INT NOT NULL DEFAULT 1,
  ADD INDEX idx_mov_data (data_hora),
  ADD INDEX idx_mov_produto (produto_id),
  ADD CONSTRAINT fk_movimentacoes_usuarios
      FOREIGN KEY (usuario_id) REFERENCES usuarios(id);

ALTER TABLE movimentacoes ALTER COLUMN usuario_id DROP DEFAULT;

ALTER TABLE movimentacoes ADD CONSTRAINT ck_mov_quantidade CHECK (quantidade > 0);
ALTER TABLE produtos ADD CONSTRAINT ck_produtos_preco CHECK (preco >= 0);
ALTER TABLE produtos ADD CONSTRAINT ck_produtos_estoque CHECK (quantidade_estoque >= 0);
ALTER TABLE produtos ADD INDEX idx_produtos_nome (nome);
