# Almoxarifado SAEP

Sistema web de controle de materiais desenvolvido com Python, Flask e MySQL.

## Requisitos
- Python 3.10 ou superior
- MySQL 8+
- Navegador atualizado

## Instalação
1. Extraia o projeto.
2. Crie o banco executando `infra/bd.sql` no MySQL Workbench.
3. Crie e ative o ambiente virtual:
   - Windows: `python -m venv .venv` e `.venv\Scripts\activate`
   - Linux/macOS: `python3 -m venv .venv` e `source .venv/bin/activate`
4. Instale as dependências: `pip install -r requirements.txt`
5. Copie `.env.example` para `.env` e informe os dados do MySQL e uma SECRET_KEY própria.
6. Crie o primeiro administrador (veja abaixo).
7. Inicie: `python -m src.server`
8. Acesse `http://127.0.0.1:5000/login`.

## Criar o primeiro administrador
No terminal, com o ambiente virtual ativado, execute:
`python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('SuaSenhaForte'))"`
Copie o hash retornado e execute no MySQL:
`INSERT INTO usuarios (nome,email,senha_hash,perfil) VALUES ('Administrador','admin@empresa.com','COLE_O_HASH_AQUI','administrador');`
Altere o e-mail e a senha para valores seus. Não use uma senha real em trabalhos compartilhados.

## Funcionalidades
- Autenticação e sessão de usuário.
- Perfis operador e administrador.
- Produtos com cadastro, edição, consulta, exclusão restrita e paginação.
- Filtro por nome e data de cadastro.
- Entradas e saídas com atualização transacional do saldo.
- Bloqueio de saída acima do estoque, com saldo disponível e solicitado na mensagem.
- Histórico com data/hora e usuário responsável.

## Organização
- `routes/`: recebe as requisições e monta as páginas.
- `services/`: autenticação e regras de negócio do estoque.
- `config/`: conexão com o banco.
- `templates/`: páginas HTML reutilizáveis.
- `static/`: CSS e JavaScript.
- `infra/`: estrutura SQL do banco.
- `docs/`: plano e registro de testes.

## Observações
- O banco entregue originalmente não tinha usuários nem saídas. O script desta versão cria as tabelas necessárias.
- O sistema usa transação e bloqueio da linha do produto (`FOR UPDATE`) para proteger o saldo durante movimentações simultâneas.
- Antes de publicar na internet, configure HTTPS, `SECRET_KEY` forte, credenciais seguras e proteção CSRF. Esta entrega está preparada para execução local e avaliação, não para publicação sem essas medidas.
