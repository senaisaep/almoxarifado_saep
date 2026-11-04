# Plano de implementação de testes

## Objetivos
Garantir que (1) a saída nunca deixe o estoque negativo, (2) só perfis autorizados operem,
(3) toda movimentação seja rastreável, (4) entradas inválidas sejam rejeitadas.

## Pirâmide
| Nível | O que cobre | Ferramenta | Situação |
|---|---|---|---|
| Unitário / regra de negócio | serviços, validações | pytest + repositórios em memória (`tests/conftest.py`) | **Implementado** |
| API (rota → serviço → segurança) | status HTTP, JSON, perfis, JWT | pytest + `app.test_client()` | **Implementado** |
| Integração com MySQL | SQL real, FKs, CHECKs, `FOR UPDATE`, migração | pytest com banco de teste `almoxarifado_saep_test` | **Planejado** (fase 2) |
| Manual / aceitação | roteiro no Postman/Insomnia | coleção de requests | **Planejado** |

Executar: `pytest` (ou `pytest -k saida`). Os testes não precisam de MySQL.

## Casos já automatizados (33)
**Saída de estoque** (`tests/test_saida_estoque.py`)
| # | Cenário | Esperado |
|---|---|---|
| S1 | Saldo 10, saída 15 | 422; mensagem "Saída não permitida: estoque insuficiente. Disponível: 10, solicitado: 15."; saldo continua 10; nenhuma movimentação gravada; rollback |
| S2 | Saldo 10, saída 4 | 201; saldo 6; 1 movimentação `saida` |
| S3 | Saldo 10, saída 10 (igual) | 201; saldo 0 |
| S4 | Após zerar, saída 1 | 422 "Disponível: 0, solicitado: 1" |
| S5 | Saída registrada | `data_hora` preenchida e `responsavel`/`usuario_id` do usuário logado |
| S6 | Entrada | soma ao saldo; registra responsável |
| S7 | Produto inexistente | 404 |
| S8 | Quantidade 0, negativa, texto, decimal, nula, booleana | 400 |
| S9 | Corpo não JSON | 400 |

**Autenticação e perfis** (`tests/test_auth_perfis.py`): login ok sem expor hash; mesma resposta para e-mail
inexistente/senha errada; bloqueio após N falhas (423); usuário inativo; rotas sem token (401); token lixo/expirado;
usuário desativado perde acesso com token válido; `consulta` não escreve (403); `almoxarife` não exclui produto nem gere
usuários; admin cria usuário e ele loga; validação de cadastro (senha fraca, e-mail, perfil, duplicado 409);
admin não se desativa/rebaixa; troca de senha; erro 500 sem vazar SQL; cabeçalhos de segurança.

**Produtos e movimentações** (`tests/test_produtos.py`): paginação e filtros (`busca`, `estoque_max`), parâmetros inválidos,
teto de `por_pagina`, estoque inicial gera entrada, validação de cadastro, `PUT` não altera saldo, exclusão bloqueada
com movimentações, filtros de movimentações.

## Fase 2 — integração com MySQL (a implementar)
Preparação: criar `almoxarifado_saep_test` com `infra/bd.sql`; `DB_NAME` de teste via variável; limpar tabelas entre testes.
| # | Teste | Por que importa |
|---|---|---|
| I1 | **Concorrência**: 2 threads, saldo 10, cada uma saída de 8 | Exatamente 1 sucesso e 1 `422`; saldo final 2. Prova o `FOR UPDATE` |
| I2 | `INSERT` direto com `quantidade_estoque = -1` | Banco recusa (CHECK) |
| I3 | `data_hora` automática | Preenchida pelo `DEFAULT CURRENT_TIMESTAMP` |
| I4 | FK `usuario_id` inexistente | Banco recusa |
| I5 | `registrar_falha` no SQL real | Bloqueia exatamente na N-ésima tentativa |
| I6 | Migração 001 sobre dump do banco v0.1.0 | Dados preservados; movimentações antigas com usuário 1 |
| I7 | `LIKE` com `%`, `'` e `;` na busca | Sem erro nem injeção |

## Fase 3 — qualidade contínua
- Cobertura: `pytest --cov=src` (meta ≥ 85% em `services/` e `security/`).
- Executar `pytest` antes de cada merge em `develop` (hook `pre-push` ou CI no repositório).
- Todo bug corrigido ganha um teste que o reproduz antes do `fix`.

## Roteiro manual (aceitação)
1. Rodar `bd.sql`, `criar_admin`, subir a API.
2. Login admin → criar usuários `almoxarife` e `consulta`.
3. Como `almoxarife`: entrada de 10 → saída de 15 (**deve bloquear com a mensagem**) → saída de 4 (ok) → `GET /movimentacoes` mostra data/hora e responsável.
4. Como `consulta`: tentar saída → 403.
5. Desativar o `almoxarife` → o token dele passa a dar 401.
