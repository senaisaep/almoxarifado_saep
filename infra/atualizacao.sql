USE almoxarifado_saep;

ALTER TABLE movimentacoes
MODIFY tipo ENUM('entrada', 'saida') NOT NULL DEFAULT 'entrada';

ALTER TABLE movimentacoes
ADD data_movimentacao DATETIME DEFAULT CURRENT_TIMESTAMP,
ADD usuario_id INT;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha VARCHAR(100) NOT NULL,
    perfil ENUM('operador', 'administrador') NOT NULL
);

INSERT INTO usuarios (nome, email, senha, perfil)
VALUES ('Administrador', 'admin@teste.com', '123456', 'administrador');