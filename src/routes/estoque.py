
from flask import Blueprint, request, jsonify, session
from functools import wraps
from models import produto
from models import movimentacao
from models import usuario

estoque = Blueprint("estoque", __name__)


# VERIFICAÇÃO DE LOGIN
def login_obrigatorio(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "usuario_id" not in session:
            return jsonify({"erro": "Faça login."}), 401
        return func(*args, **kwargs)
    return wrapper


# VERIFICAÇÃO DE ADMINISTRADOR
def admin_obrigatorio(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "usuario_id" not in session:
            return jsonify({"erro": "Faça login."}), 401

        if session.get("tipo") != "administrador":
            return jsonify({"erro": "Acesso permitido somente ao administrador."}), 403

        return func(*args, **kwargs)
    return wrapper


# LOGIN
@estoque.route("/login", methods=["POST"])
def login():
    dados = request.get_json(silent=True) or request.form

    user = usuario.autenticar(
        dados.get("email", ""),
        dados.get("senha", "")
    )

    if not user:
        return jsonify({"erro": "Email ou senha incorretos."}), 401

    session.clear()
    session["usuario_id"] = user["id"]
    session["tipo"] = user["tipo"]
    session["nome"] = user["nome"]

    return jsonify({
        "mensagem": "Login realizado.",
        "usuario": {
            "id": user["id"],
            "nome": user["nome"],
            "tipo": user["tipo"]
        }
    })


# LOGOUT
@estoque.route("/logout", methods=["POST"])
@login_obrigatorio
def logout():
    session.clear()
    return jsonify({"mensagem": "Logout realizado."})


# LISTAR PRODUTOS COM FILTROS E PAGINAÇÃO
@estoque.route("/produtos", methods=["GET"])
@login_obrigatorio
def listar_produtos():
    nome = request.args.get("nome", "")
    data = request.args.get("data", "")
    pagina = max(1, request.args.get("pagina", 1, type=int))

    dados, total = produto.listar(nome, data, pagina)

    return jsonify({
        "produtos": dados,
        "pagina": pagina,
        "total": total,
        "paginas": (total + 9) // 10
    })


# CONSULTAR PRODUTO
@estoque.route("/produtos/<int:produto_id>", methods=["GET"])
@login_obrigatorio
def consultar_produto(produto_id):
    dados = produto.buscar(produto_id)

    if not dados:
        return jsonify({"erro": "Produto não encontrado."}), 404

    return jsonify(dados)


# CADASTRAR PRODUTO
@estoque.route("/produtos", methods=["POST"])
@login_obrigatorio
def cadastrar_produto():
    dados = request.get_json(silent=True) or {}

    nome = dados.get("nome", "").strip()
    descricao = dados.get("descricao", "")
    
    try:
        preco = float(dados.get("preco", 0))
        quantidade = int(dados.get("quantidade_estoque", 0))

        if preco < 0 or quantidade < 0:
            raise ValueError()

    except (ValueError, TypeError):
        return jsonify({"erro": "Preço ou quantidade inválidos."}), 400

    if not nome:
        return jsonify({"erro": "Nome obrigatório."}), 400

    # O produto começa com saldo zero.
    # A quantidade inicial é registrada como entrada.
    novo_id = produto.cadastrar(nome, descricao, preco, 0)

    if quantidade > 0:
        sucesso, mensagem = movimentacao.registrar(
            novo_id,
            session["usuario_id"],
            "entrada",
            quantidade
        )

        if not sucesso:
            return jsonify({"erro": mensagem}), 400

    return jsonify({
        "mensagem": "Produto cadastrado.",
        "id": novo_id
    }), 201


# ATUALIZAR PRODUTO
@estoque.route("/produtos/<int:produto_id>", methods=["PUT"])
@login_obrigatorio
def atualizar_produto(produto_id):
    dados = request.get_json(silent=True) or {}

    nome = dados.get("nome", "").strip()
    descricao = dados.get("descricao", "")

    try:
        preco = float(dados.get("preco", 0))
        if preco < 0:
            raise ValueError()
    except (ValueError, TypeError):
        return jsonify({"erro": "Preço inválido."}), 400

    if not nome:
        return jsonify({"erro": "Nome obrigatório."}), 400

    if not produto.buscar(produto_id):
        return jsonify({"erro": "Produto não encontrado."}), 404

    produto.atualizar(produto_id, nome, descricao, preco)

    return jsonify({"mensagem": "Produto atualizado."})


# EXCLUIR PRODUTO - SOMENTE ADMINISTRADOR
@estoque.route("/produtos/<int:produto_id>", methods=["DELETE"])
@admin_obrigatorio
def remover_produto(produto_id):
    try:
        removidos = produto.excluir(produto_id)

        if not removidos:
            return jsonify({"erro": "Produto não encontrado."}), 404

        return jsonify({"mensagem": "Produto removido."})

    except Exception:
        return jsonify({
            "erro": "Não é possível excluir produto com movimentações registradas."
        }), 409


# REGISTRAR ENTRADA
@estoque.route("/movimentacoes/entrada", methods=["POST"])
@login_obrigatorio
def registrar_entrada():
    return registrar_movimento("entrada")


# REGISTRAR SAÍDA
@estoque.route("/movimentacoes/saida", methods=["POST"])
@login_obrigatorio
def registrar_saida():
    return registrar_movimento("saida")


# FUNÇÃO COMPARTILHADA DE MOVIMENTAÇÃO
def registrar_movimento(tipo):
    dados = request.get_json(silent=True) or {}

    try:
        produto_id = int(dados.get("produto_id"))
        quantidade = int(dados.get("quantidade"))
    except (ValueError, TypeError):
        return jsonify({"erro": "Dados inválidos."}), 400

    sucesso, mensagem = movimentacao.registrar(
        produto_id,
        session["usuario_id"],
        tipo,
        quantidade
    )

    if not sucesso:
        return jsonify({"erro": mensagem}), 400

    return jsonify({"mensagem": mensagem}), 201


# CONSULTAR HISTÓRICO
@estoque.route("/movimentacoes", methods=["GET"])
@login_obrigatorio
def listar_movimentacoes():
    return jsonify(movimentacao.listar())


# CADASTRAR USUÁRIO - SOMENTE ADMINISTRADOR
@estoque.route("/usuarios", methods=["POST"])
@admin_obrigatorio
def cadastrar_usuario():
    dados = request.get_json(silent=True) or {}

    nome = dados.get("nome", "").strip()
    email = dados.get("email", "").strip()
    senha = dados.get("senha", "")
    tipo = dados.get("tipo", "")

    if not nome or not email or not senha:
        return jsonify({"erro": "Preencha todos os campos."}), 400

    if tipo not in ("operador", "administrador"):
        return jsonify({"erro": "Perfil inválido."}), 400

    if usuario.buscar_email(email):
        return jsonify({"erro": "Email já cadastrado."}), 409

    usuario.cadastrar(nome, email, senha, tipo)

    return jsonify({"mensagem": "Usuário cadastrado."}), 201


# LISTAR USUÁRIOS - SOMENTE ADMINISTRADOR
@estoque.route("/usuarios", methods=["GET"])
@admin_obrigatorio
def listar_usuarios():
    return jsonify(usuario.listar())


# EXCLUIR USUÁRIO - SOMENTE ADMINISTRADOR
@estoque.route("/usuarios/<int:id>", methods=["DELETE"])
@admin_obrigatorio
def excluir_usuario(id):
    if id == session["usuario_id"]:
        return jsonify({"erro": "Não pode excluir o próprio usuário."}), 400

    try:
        if not usuario.excluir(id):
            return jsonify({"erro": "Usuário não encontrado."}), 404

        return jsonify({"mensagem": "Usuário excluído."})

    except Exception:
        return jsonify({
            "erro": "Usuário possui movimentações registradas."
        }), 409
