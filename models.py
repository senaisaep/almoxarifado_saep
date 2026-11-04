from sqlalchemy import Column, Integer, String, Float, ForeignKey
from database import Base


# TODO: Implemente os 3 modelos abaixo


# Tabela: usuarios
# Campos: id (PK), nome (String 100), login (String 50, unique), perfil (String 20)
class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String (100))
    login = Column(String (50), unique=True)
    perfil = Column(String(20))
    senha_hash = Column(String(250), nullable=False)

    # pass


# Tabela: produtos
# Campos: id (PK), nome (String 100), unidade (String 20),
#         quantidade_estoque (Float, default=0.0)
class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String (100))
    quantidade_estoque = Column(Float, default=0.0)
    unidade = Column(String(20))

    # pass


# Tabela: movimentacoes
# Campos: id (PK), tipo (String 10), quantidade (Float),
#         observacao (String 300, nullable), produto_id (FK), usuario_id (FK)
class Movimentacao(Base):
    __tablename__ = "movimentacoes"

    id = Column(Integer, primary_key=True, index=True)
    observacao = Column(String (300), nullable=True)
    quantidade = Column(Float)
    tipo = Column(String(20))
    produto_id = Column(Integer, ForeignKey("produtos.id"))
    uruario_id = Column(Integer, ForeignKey("usuarios.id"))

    # pass
