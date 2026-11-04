from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
from models import Movimentacao, Produto, Usuario

router = APIRouter(prefix="/movimentacoes", tags=["Movimentacoes"])


# Modelos Pydantic

class MovimentacaoCreate(BaseModel):
    tipo:       str    # "entrada" ou "saida"
    quantidade: float
    observacao: Optional[str] = None
    produto_id: int
    usuario_id: int

# Função Auxiliar
def get_or_404(movimentacao_id: int, db: Session) -> Produto:
    m = db.query(Movimentacao).filter(Movimentacao.id == movimentacao_id).first()
    if not m: 
        raise HTTPException(status_code=404, detail="Movimentação não encontrada")
    return m


# Rotas

@router.get("/")
def listar(db: Session = Depends(get_db)):
    movimentacoes= db.query(Movimentacao).all()
    return movimentacoes

    # TODO: retorne todas as movimentações
    pass


@router.get("/{movimentacao_id}")
def buscar(movimentacao_id: int, db: Session = Depends(get_db)):
    movimentacao = get_or_404(db, Movimentacao, movimentacao_id)
    return movimentacao

    # TODO: busque a movimentação; 404 se não existir
    pass


@router.post("/", status_code=201)
def criar(dados: MovimentacaoCreate, db: Session = Depends(get_db)):

    produto = get_or_404(db, Produto, dados.produto_id)
    # TODO 1: verifique se produto_id existe → 404 "Produto não encontrado"
    usuario = get_or_404(db, Usuario, dados.usuario_id)
    # TODO 2: verifique se usuario_id existe → 404 "Usuário não encontrado"

    if dados.tipo == "saida":
        # Verifica se o estoque atual do produto é menor do que a quantidade que quer sair
        if produto.estoque < dados.quantidade:
            raise HTTPException(
                status_code=400,
                detail=f"Estoque insuficiente. Estoque atual: {produto.estoque}, Quantidade solicitada: {dados.quantidade}."
            )
        # Bônus: Se a saída for válida, você já pode abater do estoque do produto
        produto.estoque -= dados.quantidade

    elif dados.tipo == "entrada":
        # Bônus: Se for uma entrada, soma a quantidade ao estoque do produto
        produto.estoque += dados.quantidade
        # TODO 3 (DESAFIO): se tipo == "saida", verifique estoque suficiente → 400

    nova_movimentacao = Movimentacao(**dados.model_dump())

    db.add(nova_movimentacao)
    db.commit()
    db.refresh(nova_movimentacao)

    return nova_movimentacao

    # TODO 4: crie e salve a movimentação
    # pass
