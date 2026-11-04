const API = "/api"; 

let pagina = 1, totalPaginas = 1;

function usuarioLogado() {
  try { return JSON.parse(localStorage.getItem("usuario") || "null"); }
  catch { return null; }
}

function sair() {
  localStorage.removeItem("token");
  localStorage.removeItem("usuario");
  window.location.href = "/app/login";
}


async function api(metodo, caminho, corpo) {
  const opcoes = { method: metodo, headers: { "Content-Type": "application/json" } };
  const token = localStorage.getItem("token");
  if (token) opcoes.headers["Authorization"] = "Bearer " + token;
  if (corpo !== undefined) opcoes.body = JSON.stringify(corpo);
  const resposta = await fetch(API + caminho, opcoes);
  const dados = await resposta.json().catch(() => null);
  if (!resposta.ok) {
    if (resposta.status === 401) sair();  
    throw { status: resposta.status, dados };
  }
  return dados;
}

function montarCabecalho() {
  const u = usuarioLogado();
  if (!u) { sair(); return; }
  document.getElementById("cabecalhoUsuario").innerHTML =
    `<small>${u.nome}</small>
     <span class="badge ${u.perfil}">${u.perfil}</span>
     <button class="secundario" id="botaoSair">Sair</button>`;
  document.getElementById("botaoSair").addEventListener("click", sair);
}

async function entrar() {
  const erro = document.getElementById("erroLogin");
  erro.textContent = "";
  try {
    const r = await api("POST", "/auth/login", {
      email: document.getElementById("email").value.trim(),
      senha: document.getElementById("senha").value,
    });
    localStorage.setItem("token", r.token);
    localStorage.setItem("usuario", JSON.stringify(r.usuario));
    window.location.href = "/app/produtos";
  } catch (e) {
    erro.textContent = (e.dados && e.dados.mensagem) || "Falha no login.";
  }
}

function mudarPagina(delta) {
  const nova = pagina + delta;
  if (nova >= 1 && nova <= totalPaginas) { pagina = nova; carregarProdutos(); }
}

async function carregarProdutos() {
  const filtro = document.getElementById("filtroNome").value.trim();
  try {
    const r = await api("GET",
      `/produtos?pagina=${pagina}&limite=10&nome=${encodeURIComponent(filtro)}`);
    totalPaginas = r.total_paginas || 1;
    document.getElementById("infoPagina").textContent =
      `Página ${pagina} de ${totalPaginas} (${r.total} produtos)`;

    const u = usuarioLogado();
    const podeExcluir = u && u.perfil === "admin";
    document.querySelector("#tabelaProdutos tbody").innerHTML = r.dados.map(p => `
      <tr>
        <td>${p.id}</td>
        <td><b>${p.nome}</b></td>
        <td>${p.descricao ?? ""}</td>
        <td class="num">R$ ${Number(p.preco).toFixed(2)}</td>
        <td class="num">${p.quantidade_estoque}</td>
        <td>${(p.data_cadastro || "").replace("T", " ").slice(0, 16)}</td>
        <td><div class="acoes">
          <button class="secundario" onclick="editarProduto(${p.id})">Editar</button>
          ${podeExcluir ? `<button class="vermelho" onclick="removerProduto(${p.id})">Excluir</button>` : ""}
          <button class="verde" onclick="movimentarRapido(${p.id})">Movimentar</button>
        </div></td>
      </tr>`).join("");
  } catch (e) {
    if (e.status !== 401) 
      document.getElementById("erroProdutos").textContent = "Erro ao carregar produtos.";
  }
}

async function cadastrarProduto() {
  const msg = document.getElementById("msgProduto");
  msg.className = "";
  try {
    const r = await api("POST", "/produtos", {
      nome: document.getElementById("pNome").value.trim(),
      descricao: document.getElementById("pDesc").value.trim(),
      preco: parseFloat(document.getElementById("pPreco").value),
      quantidade_estoque: parseInt(document.getElementById("pQtd").value),
    });
    msg.className = "ok";
    msg.textContent = r.mensagem;
    ["pNome", "pDesc", "pPreco", "pQtd"].forEach(id => document.getElementById(id).value = "");
    carregarProdutos();
  } catch (e) {
    msg.className = "erro";
    const detalhes = e.dados && e.dados.detalhes;
    msg.textContent = Array.isArray(detalhes) ? detalhes.join(". ") : (e.dados?.mensagem || "Erro ao cadastrar.");
  }
}

async function editarProduto(id) {
  const atual = await api("GET", `/produtos/${id}`);
  const nome = prompt("Nome:", atual.nome);
  if (nome === null) return;
  const descricao = prompt("Descrição:", atual.descricao ?? "");
  if (descricao === null) return;
  const preco = prompt("Preço:", atual.preco);
  if (preco === null) return;
  try {
    const r = await api("PUT", `/produtos/${id}`,
      { nome, descricao, preco: parseFloat(preco) });
    alert(r.mensagem);
    carregarProdutos();
  } catch (e) {
    alert((e.dados && e.dados.mensagem) || "Erro ao atualizar.");
  }
}

async function removerProduto(id) {
  if (!confirm(`Excluir o produto ${id}?`)) return;
  try {
    const r = await api("DELETE", `/produtos/${id}`);
    alert(r.mensagem);
    carregarProdutos();
  } catch (e) {
    alert((e.dados && e.dados.mensagem) || "Erro ao remover.");
  }
}

/* ================= MOVIMENTAÇÕES ================= */
function movimentarRapido(id) {
  const campo = document.getElementById("mProduto");
  campo.value = id;
  document.getElementById("mQtd").focus();
  campo.scrollIntoView({ behavior: "smooth" });
}

async function movimentar() {
  const msg = document.getElementById("msgMovimento");
  msg.className = "";
  try {
    const r = await api("POST", `/movimentacoes/${document.getElementById("mTipo").value}`, {
      produto_id: parseInt(document.getElementById("mProduto").value),
      quantidade: parseInt(document.getElementById("mQtd").value),
    });
    msg.className = "ok";
    msg.textContent = `${r.mensagem} Novo estoque: ${r.estoque_atual}`;
    carregarProdutos();
    carregarMovimentacoes();
  } catch (e) {
    msg.className = "erro";
    msg.textContent = (e.dados && e.dados.mensagem) || "Erro na movimentação.";
  }
}

async function carregarMovimentacoes() {
  try {
    const r = await api("GET", "/movimentacoes?pagina=1&limite=10");
    document.getElementById("tabelaMovs").innerHTML = r.dados.map(m => `
      <tr>
        <td>${(m.data_hora || "").replace("T", " ").slice(0, 16)}</td>
        <td>${m.produto ?? m.produto_id}</td>
        <td>${m.tipo}</td>
        <td class="num">${m.quantidade}</td>
        <td>${m.usuario ?? "-"}</td>
      </tr>`).join("");
  } catch (e) { /* silencioso */ }
}

function iniciarTelaProdutos() {
  montarCabecalho();
  carregarProdutos();
  carregarMovimentacoes();
}
