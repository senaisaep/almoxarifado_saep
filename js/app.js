const API_URL = "/api/produtos";

const form = document.querySelector("#produto-form");
const feedback = document.querySelector("#feedback");
const tabela = document.querySelector("#lista-produtos");
const pesquisa = document.querySelector("#pesquisa");
const cancelButton = document.querySelector("#cancel-button");

let produtos = [];

function mostrarFeedback(mensagem, erro = false) {
    feedback.textContent = mensagem;
    feedback.classList.toggle("error", erro);
}

function formatarPreco(valor) {
    return Number(valor).toLocaleString("pt-BR", {
        style: "currency",
        currency: "BRL"
    });
}

async function carregarProdutos() {
    try {
        const resposta = await fetch(API_URL);
        if (!resposta.ok) throw new Error("Não foi possível carregar os produtos.");
        produtos = await resposta.json();
        atualizarIndicadores();
        renderizarProdutos();
    } catch (erro) {
        tabela.innerHTML = `<tr><td colspan="5" class="empty">${erro.message}</td></tr>`;
    }
}

function atualizarIndicadores() {
    document.querySelector("#total-produtos").textContent = produtos.length;
    document.querySelector("#total-unidades").textContent = produtos.reduce(
        (total, produto) => total + Number(produto.quantidade_estoque), 0
    );
    document.querySelector("#estoque-baixo").textContent = produtos.filter(
        produto => Number(produto.quantidade_estoque) <= 5
    ).length;
}

function renderizarProdutos() {
    const termo = pesquisa.value.trim().toLowerCase();
    const filtrados = produtos.filter(produto =>
        produto.nome.toLowerCase().includes(termo)
    );

    if (filtrados.length === 0) {
        tabela.innerHTML = '<tr><td colspan="5" class="empty">Nenhum produto encontrado.</td></tr>';
        return;
    }

    tabela.innerHTML = filtrados.map(produto => {
        const estoqueBaixo = Number(produto.quantidade_estoque) <= 5;
        return `
            <tr>
                <td>${escaparHTML(produto.nome)}</td>
                <td>${formatarPreco(produto.preco)}</td>
                <td>${produto.quantidade_estoque}</td>
                <td><span class="pill ${estoqueBaixo ? "low" : ""}">${estoqueBaixo ? "Estoque baixo" : "Disponível"}</span></td>
                <td>
                    <button class="row-action" data-action="edit" data-id="${produto.id}">Editar</button>
                    <button class="row-action delete" data-action="delete" data-id="${produto.id}">Excluir</button>
                </td>
            </tr>
        `;
    }).join("");
}

function escaparHTML(valor) {
    return String(valor).replace(/[&<>"']/g, caractere => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
    })[caractere]);
}

function limparFormulario() {
    form.reset();
    document.querySelector("#produto-id").value = "";
    document.querySelector("#form-title").textContent = "Cadastrar produto";
    document.querySelector("#submit-button").textContent = "Salvar produto";
    cancelButton.classList.add("hidden");
}

form.addEventListener("submit", async evento => {
    evento.preventDefault();

    const id = document.querySelector("#produto-id").value;
    const dados = {
        nome: document.querySelector("#nome").value,
        descricao: document.querySelector("#descricao").value,
        preco: document.querySelector("#preco").value,
        quantidade_estoque: document.querySelector("#quantidade").value
    };

    const url = id ? `${API_URL}/${id}` : API_URL;
    const metodo = id ? "PUT" : "POST";

    try {
        const resposta = await fetch(url, {
            method: metodo,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(dados)
        });
        const resultado = await resposta.json();

        if (!resposta.ok) throw new Error(resultado.erro || "Erro ao salvar produto.");

        mostrarFeedback(resultado.mensagem);
        limparFormulario();
        await carregarProdutos();
    } catch (erro) {
        mostrarFeedback(erro.message, true);
    }
});

tabela.addEventListener("click", async evento => {
    const botao = evento.target.closest("button[data-action]");
    if (!botao) return;

    const produto = produtos.find(item => item.id === Number(botao.dataset.id));
    if (!produto) return;

    if (botao.dataset.action === "edit") {
        document.querySelector("#produto-id").value = produto.id;
        document.querySelector("#nome").value = produto.nome;
        document.querySelector("#descricao").value = produto.descricao || "";
        document.querySelector("#preco").value = produto.preco;
        document.querySelector("#quantidade").value = produto.quantidade_estoque;
        document.querySelector("#form-title").textContent = "Editar produto";
        document.querySelector("#submit-button").textContent = "Salvar alterações";
        cancelButton.classList.remove("hidden");
        document.querySelector("#cadastro").scrollIntoView({ behavior: "smooth" });
    }

    if (botao.dataset.action === "delete") {
        if (!confirm(`Deseja realmente excluir "${produto.nome}"?`)) return;

        try {
            const resposta = await fetch(`${API_URL}/${produto.id}`, { method: "DELETE" });
            const resultado = await resposta.json();
            if (!resposta.ok) throw new Error(resultado.erro || "Erro ao excluir produto.");
            mostrarFeedback(resultado.mensagem);
            await carregarProdutos();
        } catch (erro) {
            mostrarFeedback(erro.message, true);
        }
    }
});

cancelButton.addEventListener("click", limparFormulario);
pesquisa.addEventListener("input", renderizarProdutos);

carregarProdutos();
