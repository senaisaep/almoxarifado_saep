# Sistema de Almoxarifado - SAEP (v1.0.0)

API em **Python, Flask e MySQL** com camadas (rota → serviço → repositório), usuários com perfis,
autenticação JWT e controle de estoque com entrada e saída.

## Documentação
- [Arquitetura](docs/ARQUITETURA.md) · [Versionamento](docs/VERSIONAMENTO.md)
- [Usuários, perfis e segurança](docs/SEGURANCA.md) · [Plano de testes](docs/PLANO_DE_TESTES.md)

## Instalação
```bash
python -m venv .venv
```
Windows: `.venv\Scripts\activate` · Linux/macOS: `source .venv/bin/activate`
```bash
pip install -r requirements.txt
```
1. Copie `.env.example` para `.env`; informe os dados do MySQL e gere a `SECRET_KEY`:
   `python -c "import secrets; print(secrets.token_urlsafe(48))"`
2. **Banco novo:** execute `infra/bd.sql` no MySQL Workbench.
   **Banco da v0.1.0 com dados:** execute `infra/migracao_001_usuarios_saida.sql` (uma vez).
3. Crie o primeiro administrador: `python -m src.scripts.criar_admin`

## Execução e testes
```bash
python -m src.server     # http://127.0.0.1:5000
pytest                   # não precisa de MySQL
```

## Uso rápido
```bash
# login
curl -X POST localhost:5000/auth/login -H "Content-Type: application/json" \
     -d '{"email":"admin@exemplo.com","senha":"SuaSenha123"}'
# use o token retornado:
curl -X POST localhost:5000/movimentacoes/saida -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" -d '{"produto_id":1,"quantidade":5}'
```

### Saída de estoque
- `quantidade <= saldo` → **201**, saldo atualizado, movimentação com `data_hora` e `responsavel`.
- `quantidade > saldo` → **422**, nada é gravado:
```json
{"mensagem":"Saída não permitida: estoque insuficiente. Disponível: 10, solicitado: 15.",
 "disponivel":10,"solicitado":15}
```

## Perfis
| Perfil | Pode |
|---|---|
| `admin` | Tudo (inclui usuários e exclusão de produtos) |
| `almoxarife` | Ver, cadastrar/editar produtos, registrar entradas e saídas |
| `consulta` | Somente leitura |

## Endpoints
Lista completa com perfis e parâmetros em [docs/ARQUITETURA.md](docs/ARQUITETURA.md#endpoints).
Resumo: `/auth/*`, `/usuarios`, `/produtos` (paginado, filtros `busca` e `estoque_max`),
`/movimentacoes` (filtros `tipo`, `produto_id`, `data_inicio`, `data_fim`),
`/movimentacoes/entrada`, `/movimentacoes/saida`.

## Mudanças em relação à v0.1.0 (quebram compatibilidade)
- Todas as rotas (exceto `/` e `/auth/login`) exigem `Authorization: Bearer <token>`.
- `GET /produtos` agora retorna `{"dados": [...], "pagina", "por_pagina", "total", "total_paginas"}`.
- `PUT /produtos/<id>` não altera mais `quantidade_estoque` (use entrada/saída).
- Movimentações guardam `data_hora` e responsável; `tipo` aceita `saida`.
