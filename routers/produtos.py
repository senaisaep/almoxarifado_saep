from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
from models import Produto

router = APIRouter(prefix="/produtos", tags=["Produtos"])


# Modelos Pydantic

class ProdutoCreate(BaseModel):
    nome:               str
    unidade:            str
    quantidade_estoque: float = 0.0


class ProdutoUpdate(BaseModel):
    nome:               Optional[str]   = None
    unidade:            Optional[str]   = None
    quantidade_estoque: Optional[float] = None


# Função auxiliar

def get_or_404(produto_id: int, db: Session) -> Produto:
    p = db.query(Produto).filter(Produto.id == produto_id).first()
    if not p: 
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return p 


    # TODO: busque o produto no banco; se não existir, raise HTTPException 404
    # pass


# Rotas

@router.get("/")
def listar(db: Session = Depends(get_db)):
    produtos = db.query(Produto).all()
    return produtos

    # TODO: retorne todos os produtos
    pass


@router.get("/{produto_id}")
def buscar(produto_id: int, db: Session = Depends(get_db)):
    produto = get_or_404(db, Produto, produto_id)
    return produto

    # TODO: use get_or_404
    pass


@router.post("/", status_code=201)
def criar(dados: ProdutoCreate, db: Session = Depends(get_db)):
    novo_produto = Produto(**dados.model_dump())

    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto) # Atualiza o objeto com o ID gerado pelo banco
    return novo_produto


    # TODO: crie e salve o produto
    pass


@router.put("/{produto_id}")
def atualizar(produto_id: int, dados: ProdutoUpdate, db: Session = Depends(get_db)):
 produto_existente = get_or_404(db, Produto, produto_id)
    
    # Extrai apenas os campos que o cliente explicitamente enviou na requisição
    # (Evita sobrescrever campos omitidos com valores padrões ou nulos)
 dados_atualizacao = dados.model_dump(exclude_unset=True)
    
 for chave, valor in dados_atualizacao.items():
        setattr(produto_existente, chave, valor)
        
 db.commit()
 db.refresh(produto_existente)
 return produto_existente

    
    # TODO: use get_or_404; atualize apenas os campos enviados
    # pass


@router.delete("/{produto_id}")
def deletar(produto_id: int, db: Session = Depends(get_db)):
    produto = get_or_404(db, Produto, produto_id)

    db.delete(produto)
    db.commit()
    
    return {"message": f"Produto com ID {produto_id} deletado com sucesso."}    
    # TODO: use get_or_404; delete e retorne mensagem de confirmação
    # pass
