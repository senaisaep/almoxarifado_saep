
from src.config.db import conectar


def listar(nome="", data="", pagina=1, limite=10):
    con = conectar()
    cur = con.cursor(dictionary=True)

    filtros = ["ativo = TRUE"]
    valores = []

    if nome:
        filtros.append("nome LIKE %s")
        valores.append(f"%{nome}%")

    if data:
        filtros.append("DATE(data_cadastro) = %s")
        valores.append(data)

    where = " WHERE " + " AND ".join(filtros) if filtros else ""

    cur.execute(
        f"SELECT COUNT(*) AS total FROM produtos {where}",
        valores
    )
    total = cur.fetchone()["total"]

    cur.execute(f"""
        SELECT * FROM produtos
        {where}
        ORDER BY id DESC
        LIMIT %s OFFSET %s
    """, valores + [limite, (pagina - 1) * limite])

    produtos = cur.fetchall()
    cur.close()
    con.close()

    return produtos, total


def buscar(id):
    con = conectar()
    cur = con.cursor(dictionary=True)

    cur.execute("""SELECT * FROM produtos WHERE id = %s AND ativo = TRUE""", (id,))
    produto = cur.fetchone()

    cur.close()
    con.close()
    return produto


def cadastrar(nome, descricao, preco, quantidade):
    con = conectar()
    cur = con.cursor()

    cur.execute("""
        INSERT INTO produtos
        (nome, descricao, preco, quantidade_estoque)
        VALUES (%s, %s, %s, %s)
    """, (nome, descricao, preco, quantidade))

    novo_id = cur.lastrowid

    con.commit()
    cur.close()
    con.close()

    return novo_id


def atualizar(id, nome, descricao, preco):
    con = conectar()
    cur = con.cursor()

    cur.execute("""
        UPDATE produtos
        SET nome = %s, descricao = %s, preco = %s
        WHERE id = %s
    """, (nome, descricao, preco, id))

    con.commit()
    alterados = cur.rowcount
    cur.close()
    con.close()

    return alterados


def excluir(id):
    con = conectar()
    cur = con.cursor()

    cur.execute("""UPDATE produtos SET ativo = FALSE WHERE id = %s AND ativo = TRUE""", (id,))

    con.commit()
    removidos = cur.rowcount
    cur.close()
    con.close()

    return removidos


def buscar_por_nome(nome):
    con = conectar()
    cur = con.cursor(dictionary=True)

    cur.execute("""
        SELECT * FROM produtos
        WHERE nome = %s
        ORDER BY id DESC
        LIMIT 1
    """, (nome,))

    dados = cur.fetchone()
    cur.close()
    con.close()
    return dados
