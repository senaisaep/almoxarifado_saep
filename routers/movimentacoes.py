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


# Rotas

@router.get("/")
def listar(db: Session = Depends(get_db)):
    return db.query(Movimentacao).all()
    


@router.get("/{movimentacao_id}")
def buscar(movimentacao_id: int, db: Session = Depends(get_db)):
    movimentacao = db.query(movimentacao).filter(movimentacao.id == movimentacao_id).first()
    if movimentacao is None:
            raise HTTPException(status_code=404, detail="Usuario não movimentação não encontrada")
    return movimentacao

@router.post("/", status_code=201)
def criar(dados: MovimentacaoCreate, db: Session = Depends(get_db)):
      movimentacao = db.query(movimentacao).filter(movimentacao.id == dados.movimentacao_id).first()
      if movimentacao is None:
       raise HTTPException(status_code=404, detail="movimentação já existe"
)
      movimentacao = movimentacao(**dados.model_dump())
      db.add(movimentacao)
      db.commit()
      db.refresh(movimentacao)
      return movimentacao
    
    