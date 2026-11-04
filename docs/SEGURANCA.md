# Usuários, perfis e segurança de dados

## Autenticação
- **Login** por e-mail + senha → JWT (HS256) com `sub`, `perfil`, `iat`, `exp` (padrão 60 min).
- O algoritmo é fixado na validação (`algorithms=["HS256"]`), bloqueando tokens `alg=none`.
- A cada requisição o usuário é **reconsultado no banco**: se foi desativado ou mudou de perfil,
  vale imediatamente, sem esperar o token expirar.
- `SECRET_KEY` vem do `.env` (mínimo 32 caracteres); a aplicação se recusa a emitir tokens sem ela.
- Não existe auto-cadastro público: só o admin cria contas (evita criar conta com perfil alto).
- Primeiro admin: `python -m src.scripts.criar_admin` (senha digitada oculta; nada de senha padrão no SQL).

## Senhas
- Armazenadas com **PBKDF2-SHA256, 600 mil iterações, sal aleatório** (`senha_hash`); nunca em texto puro.
- Política: 8–128 caracteres, com letras e números.
- Mensagem de erro de login é a mesma para "e-mail inexistente" e "senha errada"; um hash falso é
  verificado quando o e-mail não existe (resposta com tempo parecido) → não dá para listar e-mails.
- **Bloqueio**: 5 falhas seguidas (`LOGIN_MAX_TENTATIVAS`) bloqueiam a conta por 15 min (`LOGIN_BLOQUEIO_MINUTOS`); HTTP 423.
- A API nunca devolve `senha_hash`.

## Perfis e permissões
| Ação | admin | almoxarife | consulta |
|---|:--:|:--:|:--:|
| Ver produtos e movimentações | ✔ | ✔ | ✔ |
| Registrar entrada / saída | ✔ | ✔ | ✘ |
| Cadastrar / editar produto | ✔ | ✔ | ✘ |
| Excluir produto | ✔ | ✘ | ✘ |
| Gerenciar usuários e perfis | ✔ | ✘ | ✘ |
| Trocar a própria senha | ✔ | ✔ | ✔ |

Princípio do menor privilégio; regra aplicada no servidor por `@requer_perfil(...)` (esconder botão
no front não é segurança). Perfil novo por padrão = `consulta`. O admin não pode desativar nem
rebaixar a si mesmo (evita ficar sem administrador).

## Proteção dos dados
| Ameaça | Controle |
|---|---|
| SQL Injection | 100% das consultas parametrizadas (`%s`); filtros montados com colunas fixas |
| Dados inválidos | Validação central (`utils/validacao.py`): tipos, limites, e-mail, datas, inteiros positivos |
| Estoque negativo / corrida | Transação + `SELECT … FOR UPDATE` + `CHECK (quantidade_estoque >= 0)` |
| Adulteração do saldo | `PUT /produtos` ignora `quantidade_estoque`; só entrada/saída movimentam |
| Falta de rastreabilidade | Toda movimentação guarda `data_hora` (banco) e `usuario_id`; usuários só são desativados |
| Vazamento de erros | Handler global: detalhes só no log; cliente recebe "Erro interno do servidor." |
| Segredos no Git | `.env` ignorado; `.env.example` sem valores reais |
| Abuso de payload | `MAX_CONTENT_LENGTH` = 1 MB; `per_page` limitado a 100 |
| Debug em produção | `FLASK_DEBUG=0` por padrão (antes `debug=True` fixo) |
| Cabeçalhos | `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Cache-Control: no-store` |

## Recomendações para produção (fora do escopo do código)
- Servir atrás de **HTTPS** (proxy reverso) e rodar com gunicorn/waitress, não com o servidor de desenvolvimento.
- Usuário MySQL **dedicado** com permissão só no banco `almoxarifado_saep` (não usar `root`).
- Rate limiting por IP no proxy (o bloqueio de conta já protege por usuário).
- Backups periódicos do banco; rotação da `SECRET_KEY` (invalida todos os tokens).
