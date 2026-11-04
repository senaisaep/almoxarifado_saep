from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
from models import Usuario

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


# Modelos Pydantic

class UsuarioCreate(BaseModel):
    nome:   str
    login:  str
    perfil: str = "operador"


class UsuarioUpdate(BaseModel):
    nome:   Optional[str] = None
    login:  Optional[str] = None
    perfil: Optional[str] = None


# Função auxiliar

def get_or_404(usuario_id: int, db: Session) -> Usuario:
    Usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if Usuario is None:
        raise HTTPException(status_code=404, detail="Usuario não encontrado")
    return Usuario

# Rotas
@router.get("/")
def listar(db: Session = Depends(get_db)):
    return db.query(Usuario).all()


@router.get("/{usuario_id}")
def buscar(usuario_id: int, db: Session = Depends(get_db)):
    return get_or_404(usuario_id, db)


@router.post("/", status_code=201)
def criar(dados: UsuarioCreate, db: Session = Depends(get_db)):
    existente = db.query(Usuario).filter(Usuario.login == dados.login).first()
    if existente:
      raise HTTPException(status_code=409, detail="login já existe"
    )
    Usuario = Usuario(**dados.model_dump())
    db.add(Usuario)
    db.commit()
    db.refresh(Usuario)
    return Usuario

@router.put("/{usuario_id}")
def atualizar(usuario_id: int, dados: UsuarioUpdate, db: Session = Depends(get_db)):
   usuario = get_or_404(usuario_id, db)
   if dados.nome is not None: usuario.nome = dados.nome
   if dados.login is not None: usuario.login = dados.login
   if dados.perfil is not None: usuario.pefil = dados.perfil
   db.commmit()
   db.refresh()
   return usuario
    
@router.delete("/{usuario_id}")
def deletar(usuario_id: int, db: Session = Depends(get_db)):
    usuario = get_or_404(usuario_id, db)
    db.delete(usuario)

    try:
      db.commit()
    except Exception:
      db.rollback()
      raise HTTPException(status_code=409, detail="Não foi possivel remover o usuário")
    return {"mensagem": "Usuário removido com sucesso"}
   