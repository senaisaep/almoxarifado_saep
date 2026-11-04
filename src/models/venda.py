from database import conectar

class Venda:
    def __init__(self, produto, quantidade, preco):
        self.produto = produto
        self.quantidade = quantidade
        self.preco = preco

    def salvar(self):
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute(""" INSERT INTO venda (produto, quantidade, preco)VALUES (?, ?, ?)""",(self.produto, self.quantidade, self.preco))
        conexao.commit()
        lastrowid = cursor.lastrowid
        cursor.close()
        conexao.close()
        return lastrowid

    def listar():
            conexao = conectar()
            cursor = conexao.cursor()
            cursor.execute( """SELECT * FROM venda""")
            lista_vendas = cursor.fetchall()
            cursor.close()
            conexao.close()
            return lista_vendas
    
    def apagar(produto):
        conexao = conectar()
        cursor = conexao.cursor()
        sql = (f"DELETE FROM venda WHERE produto = %s", (produto,))
        conexao.commit()
        cursor.close()
        conexao.close()