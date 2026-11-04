# Sistema de Almoxarifado - SAEP

API REST em Python, Flask e MySQL, organizada em camadas.

## Estrutura

```
src/
├── server.py          # cria o app, registra as rotas e trata erros
├── config/db.py       # conexão e transação com o MySQL
├── routes/            # camada HTTP: recebe o pedido e devolve JSON
├── services/          # regras de negócio e validações
├── repositories/      # único lugar com comandos SQL
└── utils/             # login por token, validações e classe de erro
tests/test_api.py            # testes automatizados (pytest)
tests/executar_cenarios.py   # executa os cenários do plano e gera as evidências
docs/plano_testes.docx       # plano de testes (saída de produtos)
docs/testes/cenarioX.txt     # evidências de cada cenário
resultados.docx              # resultados: esperado x obtido
```

Fluxo de um pedido: `rota -> service -> repository -> banco`.

## Banco de dados
Execute `infra/bd.sql` no MySQL Workbench. Usuários de teste (troque as senhas fora de ambiente de teste):

| E-mail | Senha | Perfil |
|---|---|---|
| admin@almoxarifado.com | admin123 | admin |
| operador@almoxarifado.com | operador123 | operador |

## Instalação e execução
```bash
python -m venv .venv
.venv\Scripts\activate          # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```
Copie `.env.example` para `.env` e preencha a senha do MySQL e o `JWT_SECRET`. Depois:
```bash
python -m src.server
```
API em `http://127.0.0.1:5000`.

## Perfis e permissões
- **Operador**: consulta, insere e atualiza. Não deleta.
- **Administrador**: consulta, insere, atualiza e deleta.
- Todas as rotas, menos cadastro e login, exigem o header `Authorization: Bearer <token>`.

## Endpoints

| Método | Endpoint | Quem acessa | Descrição |
|---|---|---|---|
| POST | `/auth/cadastro` | público | Cadastra usuário (sempre como operador) |
| POST | `/auth/login` | público | Retorna o token |
| GET | `/produtos` | logado | Lista com paginação e filtros |
| GET | `/produtos/<id>` | logado | Consulta um produto |
| POST | `/produtos` | logado | Cadastra produto |
| PUT | `/produtos/<id>` | logado | Atualiza nome, descrição e/ou preço |
| DELETE | `/produtos/<id>` | admin | Remove (409 se tiver movimentações) |
| GET | `/movimentacoes` | logado | Lista com paginação (`produto_id`, `tipo`) |
| POST | `/movimentacoes/entrada` | logado | Registra entrada |
| POST | `/movimentacoes/saida` | logado | Registra saída |

Filtros de produtos: `GET /produtos?pagina=1&limite=10&nome=sab&data_inicio=2026-11-01&data_fim=2026-11-30`

Resposta paginada: `{"dados":[...],"pagina":1,"limite":10,"total":8,"total_paginas":1}`

Exemplo de produto: `{"nome":"Detergente neutro","descricao":"Limpeza geral","preco":3.50,"quantidade_estoque":20}`
Exemplo de entrada/saída: `{"produto_id":1,"quantidade":10}`

## Regra da saída de estoque
A saída só é registrada se a quantidade for menor ou igual ao saldo. Senão retorna **409**:
```json
{"mensagem":"Saída não permitida: estoque insuficiente. Disponível: 15. Solicitado: 20.","detalhes":{"disponivel":15,"solicitado":20}}
```
Toda movimentação guarda a data/hora e o usuário responsável.

## Testes
```bash
pip install pytest
pytest -v
```
Os testes gravam dados no banco: use um banco de teste e rode `infra/bd.sql` de novo para resetar.

Cenários do plano de testes (banco recém-criado e servidor rodando):
```bash
python -m tests.executar_cenarios
```

## Versionamento (Git)
```bash
git checkout -b nome.sobrenome
git add .
git commit -m "Implementa camadas, login, saída de estoque, filtros e testes"
git push -u origin nome.sobrenome
```
Depois, no GitHub, abra um Pull Request da sua branch para a `main`.
