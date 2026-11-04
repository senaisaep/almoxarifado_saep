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
Antes da primeira execução, defina `ADMIN_USERNAME`, `ADMIN_PASSWORD` (mínimo
de 12 caracteres) e uma chave aleatória longa em `SECRET_KEY`. O primeiro
administrador é criado automaticamente na inicialização quando ainda não
existem usuários; a senha nunca é armazenada em texto puro.

## Execução
```bash
python -m src.server
```
API: `http://127.0.0.1:5000`

## Perfis e autenticação

Faça login em `POST /auth/login` com `{"usuario":"admin","senha":"..."}`.
Use o token retornado no cabeçalho `Authorization: Bearer <token>` nas demais
rotas. Os tokens expiram após 8 horas.

- **Operador (`operador`)**: consulta, insere e atualiza produtos; consulta o
  histórico e registra entradas e saídas. Não pode excluir produtos.
- **Administrador (`administrador`)**: todas as permissões do operador, além de
  excluir produtos e cadastrar usuários com qualquer um dos dois perfis.

Administradores criam usuários em `POST /usuarios`, enviando `nome`, `usuario`,
`senha` (mínimo de 12 caracteres) e `perfil` (`operador` ou `administrador`).
As senhas são armazenadas com hash seguro. A exclusão de produtos é lógica:
eles deixam de aparecer, mas o histórico é preservado.

## Endpoints

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/produtos` | Lista produtos paginados, com filtros opcionais `nome` e `data` |
| GET | `/produtos/<id>` | Consulta produto por ID |
| POST | `/produtos` | Cadastra produto |
| PUT | `/produtos/<id>` | Atualiza produto |
| DELETE | `/produtos/<id>` | Desativa produto (administrador) |
| GET | `/movimentacoes` | Lista movimentações |
| POST | `/movimentacoes/entrada` | Registra entrada |
| POST | `/movimentacoes/saida` | Registra saída |
| POST | `/auth/login` | Autentica usuário e retorna token |
| POST | `/usuarios` | Cadastra usuário (administrador) |

Todas as rotas, exceto `GET /` e `POST /auth/login`, exigem token. O histórico
de movimentações registra tipo, quantidade, data/hora e usuário responsável.
Alterações de estoque feitas pela atualização de produto e o estoque inicial
informado no cadastro também geram movimentações. Os registros iniciais do
script SQL aparecem como **Carga inicial**, pois não foram realizados por um
usuário autenticado.

A listagem aceita `pagina` (padrão `1`), `por_pagina` (padrão `10`, máximo `100`),
`nome` (busca parcial) e `data` no formato `AAAA-MM-DD`:
`GET /produtos?pagina=1&por_pagina=10&nome=detergente&data=2026-11-04`.
O resultado inclui os produtos e os totais de página.

## Organização e testes

A saída de produtos segue uma separação simples em camadas: a rota HTTP fica
em `Controle/produto_controle.py`, a regra de saldo em
`Controle/saida_servico.py` e as consultas/alterações SQL em
`Controle/produto_repositorio.py`. O plano e as evidências dos três cenários
estão em `docs/teste/`. Execute todos com:

```bash
python -m unittest -v tests.test_saida_produto
```

Exemplos (após obter o token):
```json
{"nome":"Detergente neutro","descricao":"Limpeza geral","preco":3.50,"quantidade_estoque":20}
```

```json
{"produto_id":1,"quantidade":10}
```

No exemplo de produto, o valor inicial de estoque produz uma entrada no
histórico atribuída ao usuário autenticado. O exemplo de movimentação é o corpo
de uma requisição para `/movimentacoes/entrada` ou `/movimentacoes/saida`.

> **Atenção:** `infra/bd.sql` recria as tabelas e apaga os dados existentes.
> Execute-o somente na configuração inicial ou após fazer backup.
