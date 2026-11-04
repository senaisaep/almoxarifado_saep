# Almoxarifado

Aplicação local para controlar usuários, produtos e movimentações de estoque.
Todos os dados ficam em `almoxarifado.db`, criado automaticamente; não precisa
de MySQL nem de configurar um arquivo `.env`.
Na primeira inicialização, o sistema também cadastra os oito produtos iniciais
com seus saldos antigos, sem duplicá-los nem sobrescrever alterações futuras.

## Iniciar

```powershell
python -m pip install -r requirements.txt
python app.py
```

Abra <http://127.0.0.1:5000> e entre com uma das contas iniciais:

| Perfil | Login | Senha |
|---|---|---|
| Administrador | `admin` | `123` |
| Operador | `operador` | `456` |

O administrador pode cadastrar usuários, produtos e movimentar o estoque.
Operadores podem consultar produtos e registrar entradas e saídas. O saldo
inicial de um produto também é registrado como uma entrada.

As senhas são armazenadas como hashes no SQLite. Altere as senhas padrão antes
de disponibilizar o sistema a outras pessoas.

## Testes

```powershell
python -m unittest discover -s tests -v
```

## Estrutura

- `app.py`: inicializa e executa o Flask.
- `infra/database.py`: cria e conecta ao banco SQLite local.
- `controllers/`: rotas HTTP.
- `repositories/`: consultas e transações do banco.
- `services/`: validações e regras de negócio.
- `templates/`: páginas do sistema.
