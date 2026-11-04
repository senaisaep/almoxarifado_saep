# Arquitetura do sistema

## Visão geral
API REST em Flask + MySQL, organizada em **camadas** com dependência em um só sentido
(rota → serviço → repositório → banco). Antes, regra de negócio e SQL ficavam juntas em
`routes/estoque.py`.

```
Cliente HTTP
    │  JSON + Authorization: Bearer <JWT>
    ▼
┌─────────────────────────────────────────────┐
│ routes/        HTTP: lê request, chama serviço, devolve JSON/status │
│ security/      @requer_perfil, JWT, hash de senha, matriz de perfis │
├─────────────────────────────────────────────┤
│ services/      REGRAS DE NEGÓCIO e transações                       │
│ utils/         validação de entrada, erros (ErroApi), paginação     │
├─────────────────────────────────────────────┤
│ repositories/  único lugar com SQL (sempre parametrizado)           │
│ config/        conexão MySQL, contexto transacional, settings       │
└─────────────────────────────────────────────┘
    ▼
MySQL (usuarios, produtos, movimentacoes)
```

## Estrutura de pastas
```
src/
  server.py              app factory, handlers de erro, cabeçalhos de segurança
  config/                db.py (conectar, transacao), settings.py (.env)
  routes/                auth.py, usuarios.py, produtos.py, movimentacoes.py
  services/              auth_service, usuario_service, produto_service, estoque_service
  repositories/          usuario_, produto_, movimentacao_repository
  security/              perfis.py, senhas.py, tokens.py, decoradores.py
  utils/                 erros.py, validacao.py
  scripts/criar_admin.py primeiro administrador
infra/                   bd.sql (banco novo), migracao_001_*.sql (banco existente)
tests/                   pytest (banco em memória)
docs/                    esta documentação
```

## Responsabilidades
| Camada | Pode | Não pode |
|---|---|---|
| Rota | validar formato do corpo, chamar 1 serviço, escolher status HTTP | conter SQL ou regra de negócio |
| Serviço | validar regras, abrir transação, lançar `ErroApi` | conhecer Flask/`request` |
| Repositório | executar SQL recebendo um cursor | decidir regra, abrir/fechar transação |

O serviço controla a transação (`with transacao() as cur`) e passa o cursor aos repositórios.
Assim várias operações viram **uma unidade atômica**.

## Fluxo da saída de estoque (regra principal)
```
POST /movimentacoes/saida {produto_id, quantidade}
  1. @requer_perfil(admin, almoxarife)  → 401/403
  2. valida inteiros positivos          → 400
  3. BEGIN
  4. SELECT ... FROM produtos WHERE id=? FOR UPDATE   (trava a linha)
  5. produto inexistente                → 404
  6. quantidade > saldo                 → EstoqueInsuficiente (422) → ROLLBACK
  7. UPDATE produtos SET quantidade_estoque = saldo - quantidade
  8. INSERT movimentacoes (produto, 'saida', quantidade, usuario_id)  ← data_hora = NOW() no banco
  9. COMMIT → 201 com movimentação (data_hora, responsável), saldo anterior e atual
```
Resposta de bloqueio (HTTP 422):
```json
{"mensagem": "Saída não permitida: estoque insuficiente. Disponível: 10, solicitado: 15.",
 "disponivel": 10, "solicitado": 15}
```
**Por que `FOR UPDATE`:** sem a trava, duas saídas simultâneas de 8 unidades com saldo 10 leem
ambas "10", ambas passam e o estoque fica em −6. Com a trava, a segunda espera a primeira e
lê saldo 2. Há ainda uma segunda barreira no banco: `CHECK (quantidade_estoque >= 0)`.

## Modelo de dados
- `usuarios(id, nome, email UNIQUE, senha_hash, perfil, ativo, tentativas_login, bloqueado_ate, data_cadastro)`
- `produtos(id, nome, descricao, preco, quantidade_estoque, data_cadastro)` + CHECKs ≥ 0
- `movimentacoes(id, produto_id FK, tipo ENUM('entrada','saida'), quantidade CHECK > 0, data_hora, usuario_id FK)`

Decisões: saldo só muda por movimentação (nada de `PUT` do saldo); usuário nunca é apagado
(só desativado) para preservar o histórico de responsáveis; produto com movimentação não é excluído.
O estoque inicial informado no cadastro gera uma movimentação de entrada.

## Endpoints
Todos exigem `Authorization: Bearer <token>`, exceto `/` e `/auth/login`.

| Método | Endpoint | Perfis | Descrição |
|---|---|---|---|
| POST | `/auth/login` | público | Login, devolve JWT |
| GET | `/auth/me` | todos | Dados do usuário logado |
| POST | `/auth/trocar-senha` | todos | Troca a própria senha |
| GET/POST | `/usuarios` | admin | Lista / cadastra usuário |
| GET/PUT/DELETE | `/usuarios/<id>` | admin | Consulta / edita / **desativa** |
| PUT | `/usuarios/<id>/senha` | admin | Redefine senha |
| GET | `/produtos` | todos | Lista paginada. Query: `pagina`, `por_pagina` (máx 100), `busca`, `estoque_max` |
| GET | `/produtos/<id>` | todos | Consulta |
| POST/PUT | `/produtos[/<id>]` | admin, almoxarife | Cadastra / atualiza (sem alterar saldo) |
| DELETE | `/produtos/<id>` | admin | Remove (só sem movimentações) |
| GET | `/movimentacoes` | todos | Lista paginada. Query: `tipo`, `produto_id`, `data_inicio`, `data_fim` (AAAA-MM-DD) |
| POST | `/movimentacoes/entrada` | admin, almoxarife | Registra entrada |
| POST | `/movimentacoes/saida` | admin, almoxarife | Registra saída (bloqueia se saldo insuficiente) |

Códigos usados: 200, 201, 400 (validação), 401 (sem/ inválido token), 403 (sem permissão),
404, 409 (conflito), 413, 422 (regra de negócio: estoque insuficiente), 423 (conta bloqueada), 500.
