# Sistema de Almoxarifado - Projeto inicial SAEP

## Tecnologias
Python, Flask e MySQL.

## Banco de dados
Execute `infra/bd.sql` no MySQL Workbench. O script cria o banco `almoxarifado_saep`, as tabelas e registros iniciais.

## Instalação
```bash
python -m venv .venv
```
Windows: `.venv\\Scripts\\activate`
Linux/macOS: `source .venv/bin/activate`

```bash
pip install -r requirements.txt
```

Copie `.env.example` para `.env` e informe os dados de conexão com o MySQL.

## Execução
```bash
python -m src.server
```
API: `http://127.0.0.1:5000`

## Endpoints existentes

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/produtos` | Lista todos, sem paginação/filtros |
| GET | `/produtos/<id>` | Consulta produto por ID |
| POST | `/produtos` | Cadastra produto |
| PUT | `/produtos/<id>` | Atualiza produto |
| DELETE | `/produtos/<id>` | Remove produto |
| GET | `/movimentacoes` | Lista movimentações |
| POST | `/movimentacoes/entrada` | Registra entrada |

Exemplo de produto:
```json
{"nome":"Detergente neutro","descricao":"Limpeza geral","preco":3.50,"quantidade_estoque":20}
```

Exemplo de entrada:
```json
{"produto_id":1,"quantidade":10}
```

## Limitações do projeto inicial
- Não possui cadastro/login de usuários, autenticação, autorização ou perfis.
- Não possui paginação nem filtros na listagem de produtos.
- As movimentações não armazenam data/hora nem usuário responsável.
- Somente a entrada de estoque está implementada; saída não está implementada.
- A lógica de negócio e os comandos SQL estão concentrados em `src/routes/estoque.py`.
- O estudante deverá reorganizar o código em camadas e implementar os requisitos da avaliação.
 