from fastapi import FastAPI
from database import engine, Base
from routers import usuarios, produtos, movimentacoes

# TODO: importe os routers aqui from routers import usuarios, produtos, movimentacoes

app = FastAPI(
    title="API de Almoxarifado",
    description="Sistema de controle de estoque - Simulado SAEP",
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
