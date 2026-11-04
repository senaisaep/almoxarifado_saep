from flask import request, render_template, render_template_string
from models.venda import Venda

def cdastrar():
    produto = request.form["produto"]
    quantidade = request.form["qtd"]
    preco = request.form["valor"]
    venda = Venda(produto=produto, quantidade=quantidade, preco=preco)
    id_venda = venda.salvar()
    return render_template_string("<h1> Venda {{id}} criada </h1>", id=id_venda)

def produtos():
    return render_template("produtos.html")

def listar():
    lista_vendas = Venda.listar()
    return render_template_string("<h1>Venda </h1> {{listar}}" ,listar=lista_vendas)

def apagar():
    produto_venda = request.args["produto"]
    Venda.apagar(produto_venda)
    return render_template_string("<h1> Excluido <h1>")
    