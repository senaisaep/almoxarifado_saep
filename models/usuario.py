from src.config.db import conectar
from werkzeug.security import generate_password_hash, check_password_hash

def buscar_email(email):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
    usuario = cursor.fetchone()
    cursor.close()
    conexion.close()
    return usuario

def autenticar(email, senha):
    usuario = buscar_email(email)
    
    if usuario and check_password_hash(usuario["senha"], senha):
        return usuario
    return None
    
def cadastrar(nome, email, senha, tipo):
    conexao = conectar()
    cursor = conexao.cursor()
    
    cursor.execute("""INSERT INTO usuarios (nome, email, senha, tipo) VALUES (%s, %s, %s, %s)""",
                   (nome, email, generate_password_hash(senha), tipo))
    conexao.commit()
    cursor.close()
    conexao.close()
    
def listar():
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)
    
    cursor.execute("""SELECT id, nome, email, tipo FROM usuarios ORDER BY none""")
    
    dados = cursor.fetchall()
    cursor.close()
    conexao.close()
    return dados 

def excluir(id):
    conexao = conectar()
    cursor = conexao.cursor()
    
    cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
    conexao.commit()
    
    removidos = cursor.rowcount
    cursor.close()
    conexao.close()
    return removidos > 0