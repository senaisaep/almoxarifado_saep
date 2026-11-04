# Versionamento (Git)

## Estratégia de branches
| Branch | Uso |
|---|---|
| `main` | Somente código estável/entregue. Cada release recebe uma **tag**. |
| `develop` | Integração do trabalho em andamento. |
| `feature/<assunto>` | Uma funcionalidade (ex.: `feature/saida-estoque`), criada a partir de `develop`. |
| `fix/<assunto>` | Correção de bug. |
| `hotfix/<assunto>` | Correção urgente a partir de `main`. |

Fluxo: `feature/*` → merge em `develop` (com revisão) → quando estável, merge `--no-ff` em `main` + tag.

## Mensagens de commit (Conventional Commits)
`tipo(escopo): descrição no imperativo/curta`

Tipos: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`.
Exemplos reais deste projeto:
```
feat(db): tabela usuarios, saida, data_hora e responsavel nas movimentacoes
feat(estoque): serviços de auth, usuários, produtos e entrada/saída transacional
refactor(arquitetura): camada de repositórios com SQL parametrizado
test: 33 testes (saída bloqueada, perfis, autenticação, produtos)
```
Regras: um commit = uma mudança lógica; nunca commitar `.env`, senhas ou `__pycache__`.

## Versão semântica (MAJOR.MINOR.PATCH)
| Tag | Conteúdo |
|---|---|
| `v0.1.0` | Projeto inicial entregue (CRUD de produtos + entrada) |
| `v1.0.0` | Camadas, usuários/perfis/JWT, saída com bloqueio, data/hora e responsável, paginação, testes |

MAJOR muda quando há quebra de contrato. Aqui houve: `GET /produtos` passou de lista para objeto
paginado (`{"dados": [...], "total": ...}`) e todas as rotas passaram a exigir token.

## Banco de dados também é versionado
- `infra/bd.sql`: estado completo (banco novo).
- `infra/migracao_NNN_*.sql`: scripts incrementais numerados para bancos já em uso.

## O que não entra no Git
`.gitignore` já exclui `.env`, `.venv/`, `__pycache__/`, `*.pyc`, `.pytest_cache/`. O arquivo
`.env.example` documenta as variáveis **sem valores reais**.

## Comandos do dia a dia
```bash
git checkout develop && git pull
git checkout -b feature/relatorio-estoque
git add src/services/relatorio_service.py tests/test_relatorio.py
git commit -m "feat(relatorio): lista produtos abaixo do estoque mínimo"
git push -u origin feature/relatorio-estoque      # abrir Pull Request para develop
# release:
git checkout main && git merge --no-ff develop -m "release: v1.1.0"
git tag -a v1.1.0 -m "Relatórios" && git push --follow-tags
```
