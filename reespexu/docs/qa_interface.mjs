export default async function run(page) {
  const resultado = { passos: [] };
  const loc = sel => page.locator(sel);

  // 1. Login como operador
  await loc('#email').fill('operador@almoxarifado.com');
  await loc('#senha').fill('operador123');
  await loc('#botaoEntrar').click();
  await page.waitForURL('**/app/produtos', { timeout: 5000 });
  await page.waitForTimeout(1000);
  resultado.passos.push({
    passo: 'login operador (redireciona para /app/produtos)',
    url: page.url(),
    perfil: await loc('#cabecalhoUsuario .badge').innerText(),
    produtosNaTabela: await loc('#tabelaProdutos tbody tr').count(),
  });

  // 2. Operador NÃO deve ver botão Excluir
  resultado.passos.push({
    passo: 'operador sem botão excluir',
    botoesExcluir: await loc('#tabelaProdutos button.vermelho').count()
  });

  // 3. Registrar entrada de 5 unidades do produto 5
  await loc('#mProduto').fill('5');
  await loc('#mQtd').fill('5');
  await page.selectOption('#mTipo', 'entrada');
  await page.getByRole('button', { name: 'Registrar movimentação' }).click();
  await page.waitForTimeout(800);
  resultado.passos.push({
    passo: 'entrada de estoque',
    mensagem: await loc('#msgMovimento').innerText()
  });

  // 4. Sair e logar como admin
  await page.evaluate(() => localStorage.clear());
  await page.goto('http://127.0.0.1:5000/app/login');
  await loc('#email').fill('admin@almoxarifado.com');
  await loc('#senha').fill('admin123');
  await loc('#botaoEntrar').click();
  await page.waitForURL('**/app/produtos', { timeout: 5000 });
  await page.waitForTimeout(1000);
  resultado.passos.push({
    passo: 'login admin',
    perfil: await loc('#cabecalhoUsuario .badge').innerText(),
    botoesExcluir: await loc('#tabelaProdutos button.vermelho').count()
  });

  // 5. Sem token -> tela de produtos deve voltar para o login
  await page.evaluate(() => localStorage.clear());
  await page.goto('http://127.0.0.1:5000/app/produtos');
  await page.waitForTimeout(500);
  resultado.passos.push({ passo: 'sem token redireciona ao login', urlFinal: page.url() });

  await page.screenshot({ path: 'C:/Users/3DSM/Documents/GitHub/almoxarifado_saep/reespexu/docs/interface_templates.png', fullPage: true });
  return resultado;
}
