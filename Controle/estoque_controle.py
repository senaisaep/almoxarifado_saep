import os
from contextlib import contextmanager
from decimal import Decimal, InvalidOperation
from functools import wraps

from dotenv import load_dotenv
from flask import Blueprint, g, jsonify, request
from itsdangerous import BadSignature, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash

from src.config.db import conectar

load_dotenv()
estoque = Blueprint("estoque", __name__)
_PERFIS = {"operador", "administrador"}
_TODOS = ("operador", "administrador")
_ADMIN = ("administrador",)
_TOKENS = URLSafeTimedSerializer(os.getenv("SECRET_KEY") or os.urandom(32))
_VALIDADE_TOKEN = 8 * 60 * 60

@contextmanager
def _banco(dicionario=False):
    conexao = conectar()
    cursor = conexao.cursor(dictionary=dicionario)
    try:
        yield conexao, cursor
    except Exception:
        conexao.rollback()
        raise
    finally:
        cursor.close()
        conexao.close()


def _json():
    dados = request.get_json(silent=True)
    return dados if isinstance(dados, dict) else None

def _erro(mensagem, status=400):
    return jsonify({"mensagem": mensagem}), status

def _quantidade(valor, aceitar_zero=False):
    if isinstance(valor, bool): return None
    try:
        numero = int(valor)
    except (TypeError, ValueError, OverflowError):
        return None
    minimo = 0 if aceitar_zero else 1
    return numero if str(numero) == str(valor).strip() and numero >= minimo else None

def _preco(valor):
    if isinstance(valor, bool): return None
    try:
        numero = Decimal(str(valor))
    except (InvalidOperation, ValueError, TypeError):
        return None
    return numero if numero.is_finite() and numero >= 0 else None


def _autenticar(token):
    try:
        usuario_id = _TOKENS.loads(token, max_age=_VALIDADE_TOKEN)
    except (BadSignature, TypeError):
        return None
    if not isinstance(usuario_id, int) or isinstance(usuario_id, bool): return None
    with _banco(True) as (_, cursor):
        cursor.execute(
            "SELECT id, nome, usuario, perfil FROM usuarios WHERE id=%s AND ativo=1",
            (usuario_id,),
        )
        return cursor.fetchone()

def _exigir_perfil(*perfis):
    def decorar(funcao):
        @wraps(funcao)
        def protegida(*args, **kwargs):
            esquema, _, token = request.headers.get("Authorization", "").partition(" ")
            if esquema.lower() != "bearer" or not token:
                return _erro("Autenticação obrigatória.", 401)
            g.usuario = _autenticar(token)
            if not g.usuario: return _erro("Token inválido ou usuário inativo.", 401)
            if g.usuario["perfil"] not in perfis: return _erro("Permissão insuficiente.", 403)
            return funcao(*args, **kwargs)
        return protegida
    return decorar


def _registrar_movimentacao(cursor, produto_id, tipo, quantidade):
    cursor.execute(
        "INSERT INTO movimentacoes "
        "(produto_id, tipo, quantidade, usuario_id, usuario_nome) "
        "VALUES (%s, %s, %s, %s, %s)",
        (produto_id, tipo, quantidade, g.usuario["id"], g.usuario["nome"]),
    )

def _atualizar(cursor, tabela, campos, valores, registro_id):
    atribuicoes = ", ".join(f"{campo}=%s" for campo in campos)
    cursor.execute(
        f"UPDATE {tabela} SET {atribuicoes} WHERE id=%s",
        (*valores, registro_id),
    )

def inicializar_administrador():
    with _banco() as (conexao, cursor):
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        if cursor.fetchone()[0]: return
        usuario = os.getenv("ADMIN_USERNAME", "").strip()
        senha = os.getenv("ADMIN_PASSWORD", "")
        if not usuario or len(senha) < 12:
            raise RuntimeError(
                "Defina ADMIN_USERNAME e ADMIN_PASSWORD (mínimo 12 caracteres) no .env."
            )
        cursor.execute(
            "INSERT INTO usuarios (nome, usuario, senha_hash, perfil) "
            "VALUES (%s, %s, %s, 'administrador')",
            (usuario, usuario, generate_password_hash(senha)),
        )
        conexao.commit()

# Login e criação de usuários
@estoque.post("/auth/login")
def login():
    dados = _json()
    if dados is None: return _erro("Envie um objeto JSON.")
    usuario, senha = dados.get("usuario"), dados.get("senha")
    if not isinstance(usuario, str) or not isinstance(senha, str):
        return _erro("Informe usuário e senha.")
    with _banco(True) as (_, cursor):
        cursor.execute(
            "SELECT id, nome, usuario, senha_hash, perfil FROM usuarios "
            "WHERE usuario=%s AND ativo=1",
            (usuario.strip(),),
        )
        conta = cursor.fetchone()
    if not conta or not check_password_hash(conta["senha_hash"], senha):
        return _erro("Usuário ou senha inválidos.", 401)
    campos = ("id", "nome", "usuario", "perfil")
    return jsonify({
        "token": _TOKENS.dumps(conta["id"]),
        "usuario": {campo: conta[campo] for campo in campos},
    })

@estoque.post("/usuarios")
@_exigir_perfil(*_ADMIN)
def cadastrar_usuario():
    dados = _json()
    if dados is None: return _erro("Envie um objeto JSON.")
    nome, usuario, senha, perfil = (dados.get(c) for c in ("nome", "usuario", "senha", "perfil"))
    if not all(isinstance(v, str) and v.strip() for v in (nome, usuario)):
        return _erro("Nome e usuário são obrigatórios.")
    if not isinstance(senha, str) or len(senha) < 12:
        return _erro("A senha deve ter ao menos 12 caracteres.")
    if not isinstance(perfil, str) or perfil not in _PERFIS:
        return _erro("Perfil inválido.")
    with _banco() as (conexao, cursor):
        cursor.execute(
            "INSERT INTO usuarios (nome, usuario, senha_hash, perfil) VALUES (%s, %s, %s, %s)",
            (nome.strip(), usuario.strip(), generate_password_hash(senha), perfil),
        )
        conexao.commit()
        return jsonify({"mensagem": "Usuário cadastrado.", "id": cursor.lastrowid}), 201

# Cadastro e consulta de produtos
@estoque.get("/produtos/<int:produto_id>")
@_exigir_perfil(*_TODOS)
def consultar_produto(produto_id):
    with _banco(True) as (_, cursor):
        cursor.execute("SELECT * FROM produtos WHERE id=%s AND ativo=1", (produto_id,))
        produto = cursor.fetchone()
    return jsonify(produto) if produto else _erro("Produto não encontrado.", 404)

@estoque.post("/produtos")
@_exigir_perfil(*_TODOS)
def cadastrar_produto():
    dados = _json()
    if dados is None: return _erro("Envie um objeto JSON.")
    nome, descricao = dados.get("nome"), dados.get("descricao", "")
    quantidade = _quantidade(dados.get("quantidade_estoque", 0), aceitar_zero=True)
    preco = _preco(dados.get("preco", 0))
    if not isinstance(nome, str) or not nome.strip():
        return _erro("O nome do produto é obrigatório.")
    if descricao is not None and not isinstance(descricao, str):
        return _erro("A descrição deve ser texto.")
    if quantidade is None or preco is None:
        return _erro("Preço ou quantidade inválidos.")
    with _banco() as (conexao, cursor):
        cursor.execute(
            "INSERT INTO produtos (nome, descricao, preco, quantidade_estoque) "
            "VALUES (%s, %s, %s, %s)",
            (nome.strip(), descricao, preco, quantidade),
        )
        produto_id = cursor.lastrowid
        if quantidade:
            _registrar_movimentacao(cursor, produto_id, "entrada", quantidade)
        conexao.commit()
    return jsonify({"mensagem": "Produto cadastrado.", "id": produto_id}), 201

@estoque.put("/produtos/<int:produto_id>")
@_exigir_perfil(*_TODOS)
def atualizar_produto(produto_id):
    dados = _json()
    permitidos = {"nome", "descricao", "preco", "quantidade_estoque"}
    if dados is None or not dados or not set(dados) <= permitidos:
        return _erro("Informe campos válidos para atualizar.")
    atualizacoes = {}
    for campo, valor in dados.items():
        if campo == "nome":
            if not isinstance(valor, str) or not valor.strip():
                return _erro("O nome do produto não pode ficar vazio.")
            valor = valor.strip()
        elif campo == "descricao":
            if valor is not None and not isinstance(valor, str):
                return _erro("A descrição deve ser texto.")
        elif campo == "preco":
            valor = _preco(valor)
            if valor is None:
                return _erro("Preço inválido.")
        else:
            valor = _quantidade(valor, aceitar_zero=True)
            if valor is None:
                return _erro("Quantidade inválida.")
        atualizacoes[campo] = valor
    with _banco(True) as (conexao, cursor):
        cursor.execute(
            "SELECT quantidade_estoque FROM produtos WHERE id=%s AND ativo=1 FOR UPDATE",
            (produto_id,),
        )
        produto = cursor.fetchone()
        if not produto:
            return _erro("Produto não encontrado.", 404)
        quantidade = atualizacoes.get("quantidade_estoque")
        if quantidade is not None:
            diferenca = quantidade - produto["quantidade_estoque"]
            if diferenca:
                tipo = "entrada" if diferenca > 0 else "saida"
                _registrar_movimentacao(cursor, produto_id, tipo, abs(diferenca))
        _atualizar(cursor, "produtos", atualizacoes, atualizacoes.values(), produto_id)
        conexao.commit()
    return jsonify({"mensagem": "Produto atualizado."})

@estoque.delete("/produtos/<int:produto_id>")
@_exigir_perfil(*_ADMIN)
def remover_produto(produto_id):
    with _banco() as (conexao, cursor):
        cursor.execute("UPDATE produtos SET ativo=0 WHERE id=%s AND ativo=1", (produto_id,))
        if not cursor.rowcount:
            return _erro("Produto não encontrado.", 404)
        conexao.commit()
    return jsonify({"mensagem": "Produto removido."})

# Histórico e movimentação do estoque
@estoque.get("/movimentacoes")
@_exigir_perfil(*_TODOS)
def listar_movimentacoes():
    with _banco(True) as (_, cursor):
        cursor.execute(
            """SELECT m.id, m.produto_id, p.nome AS produto, m.tipo, m.quantidade,
                      m.data_hora, m.usuario_id, m.usuario_nome AS responsavel
               FROM movimentacoes m JOIN produtos p ON p.id=m.produto_id
               ORDER BY m.id DESC"""
        )
        return jsonify(cursor.fetchall())

def _movimentar(tipo):
    dados = _json()
    if dados is None: return _erro("Envie um objeto JSON.")
    produto_id = _quantidade(dados.get("produto_id"))
    quantidade = _quantidade(dados.get("quantidade"))
    if produto_id is None or quantidade is None:
        return _erro("Informe produto_id e quantidade inteira maior que zero.")
    with _banco(True) as (conexao, cursor):
        cursor.execute(
            "SELECT quantidade_estoque FROM produtos WHERE id=%s AND ativo=1 FOR UPDATE",
            (produto_id,),
        )
        produto = cursor.fetchone()
        if not produto:
            return _erro("Produto não encontrado.", 404)
        if tipo == "saida" and produto["quantidade_estoque"] < quantidade:
            return _erro("Estoque insuficiente para essa saída.", 409)
        sinal = "+" if tipo == "entrada" else "-"
        cursor.execute(
            f"UPDATE produtos SET quantidade_estoque=quantidade_estoque{sinal}%s WHERE id=%s",
            (quantidade, produto_id),
        )
        _registrar_movimentacao(cursor, produto_id, tipo, quantidade)
        conexao.commit()
    return jsonify({"mensagem": f"{tipo.capitalize()} registrada com sucesso."}), 201

@estoque.post("/movimentacoes/entrada")
@_exigir_perfil(*_TODOS)
def registrar_movimentacao():
    return _movimentar("entrada")
