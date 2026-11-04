# Plano de testes — saída de produtos

Endpoint testado: `POST /movimentacoes/saida`, autenticado como operador.
O banco é simulado nos testes automatizados; a data e hora da movimentação são
preenchidas pelo `DEFAULT CURRENT_TIMESTAMP` do MySQL.

## Cenário 1 — Saída com saldo suficiente

- **Pré-condições:** operador autenticado; produto 12 ativo com 10 unidades.
- **Dados de entrada:** `{"produto_id": 12, "quantidade": 4}`.
- **Passos:** executar o teste automatizado, que envia um POST autenticado para
  `/movimentacoes/saida`; verificar resposta, saldo, movimentação e confirmação.
- **Resultado esperado:** HTTP 201; saldo final de 6; uma saída de 4 registrada
  com o usuário responsável; transação confirmada.
- **Execução:** `python -m unittest -v tests.test_saida_produto.SaidaProdutoTests.test_cenario1_saida_com_saldo_suficiente`
- **Evidência:** [cenario1.txt](cenario1.txt)

## Cenário 2 — Saída maior que o saldo disponível

- **Pré-condições:** operador autenticado; produto 12 ativo com 2 unidades.
- **Dados de entrada:** `{"produto_id": 12, "quantidade": 3}`.
- **Passos:** executar o teste automatizado, que envia um POST autenticado para
  `/movimentacoes/saida`; verificar resposta, saldo, ausência de movimentação e
  ausência de confirmação da transação.
- **Resultado esperado:** HTTP 409; saldo continua em 2; nenhuma movimentação
  criada e transação não confirmada.
- **Execução:** `python -m unittest -v tests.test_saida_produto.SaidaProdutoTests.test_cenario2_saida_maior_que_saldo_disponivel`
- **Evidência:** [cenario2.txt](cenario2.txt)

## Cenário 3 — Saída igual ao saldo disponível

- **Pré-condições:** operador autenticado; produto 12 ativo com 5 unidades.
- **Dados de entrada:** `{"produto_id": 12, "quantidade": 5}`.
- **Passos:** executar o teste automatizado, que envia um POST autenticado para
  `/movimentacoes/saida`; verificar resposta, saldo zero, movimentação e
  confirmação.
- **Resultado esperado:** HTTP 201; saldo final de 0; uma saída de 5 registrada
  com o usuário responsável; transação confirmada.
- **Execução:** `python -m unittest -v tests.test_saida_produto.SaidaProdutoTests.test_cenario3_saida_igual_ao_saldo_disponivel`
- **Evidência:** [cenario3.txt](cenario3.txt)
