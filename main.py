from fastapi import FastAPI
from database import engine, Base
# import models  # IMPORTANTE: importar antes do create_all

# TODO: importe os routers aqui
from routers import usuarios, produtos, movimentacoes

app = FastAPI(
    title="API de Almoxarifado",
    description="Sistema de controle de estoque - Almoxarifado SAEP",
    version="1.0.0",
)

# Cria as tabelas no banco
Base.metadata.create_all(bind=engine)

# TODO: monte os routers no app
app.include_router(usuarios.router)
app.include_router(produtos.router)
app.include_router(movimentacoes.router)


@app.get("/")
def raiz():
    return {"mensagem": "API de Almoxarifado funcionando!"}
