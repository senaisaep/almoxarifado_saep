from fastapi import FastAPI
from database import engine, Base
import models
from routers import auth_routes, usuarios, produtos, movimentacoes

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Loja Almoxarifado",
    description="Sistema de controle de estoque",
    version="1.0.0",
)

app.include_router(auth_routes.router)
app.include_router(usuarios.router)
app.include_router(produtos.router)
app.include_router(movimentacoes.router)

@app.get("/")
def raiz():
    return {"mensagem": "Loja Almoxarifado funcionando!"}