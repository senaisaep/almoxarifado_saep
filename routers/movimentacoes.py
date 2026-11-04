from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
from auth import usuario_logado
from models import Movimentacao, Produto, Usuario as ModelUsuario

router = APIRouter(prefix="/movimentacoes", tags=["Movimentacoes"])

class MovimentacaoCreate(BaseModel):
    tipo: str
    quantidade: float
    observacao: Optional[str] = None
    produto_id: int
    usuario_id: int

@router.get("/")
def listar(db: Session = Depends(get_db), atual: ModelUsuario = Depends(usuario_logado)):
    return db.query(Movimentacao).all()

@router.get("/{movimentacao_id}")
def buscar(movimentacao_id: int, db: Session = Depends(get_db)):
    movimentacao = db.query(Movimentacao).filter(Movimentacao.id == movimentacao_id).first()
    if not movimentacao:
        raise HTTPException(status_code=404, detail="Movimentação não encontrada!")
    return movimentacao

@router.post("/", status_code=201)
def criar(dados: MovimentacaoCreate, db: Session = Depends(get_db), atual: ModelUsuario = Depends(usuario_logado)):
    produto = db.query(Produto).filter(Produto.id == dados.produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado!")

    usuario = db.query(Usuario).filter(Usuario.id == dados.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado!")

    tipo_lower = dados.tipo.lower()

    if tipo_lower == "saida":
        if produto.quantidade < dados.quantidade:
            raise HTTPException(status_code=400, detail="Estoque insuficiente!")
        produto.quantidade -= dados.quantidade
    elif tipo_lower == "entrada":
        produto.quantidade += dados.quantidade
    else:
        raise HTTPException(status_code=400, detail="Tipo de movimentação inválido! Use entrada ou saida!")

    movimentacao = Movimentacao(
        tipo=dados.tipo,
        quantidade=dados.quantidade,
        observacao=dados.observacao,
        produto_id=dados.produto_id,
        usuario_id=dados.usuario_id
    )
    
    db.add(movimentacao)
    db.commit()
    db.refresh(movimentacao)
    
    return movimentacao