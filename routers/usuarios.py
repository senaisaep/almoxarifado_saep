from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
from models import Usuario

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

class UsuarioCreate(BaseModel):
    nome:   str
    login:  str
    perfil: str

class UsuarioUpdate(BaseModel):
    nome:   Optional[str] = None
    login:  Optional[str] = None
    perfil: Optional[str] = None

def get_or_404(usuario_id: int, db: Session) -> Usuario:
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado!")
    return usuario

@router.get("/")
def listar(db: Session = Depends(get_db)):
    return db.query(Usuario).all()

@router.get("/{usuario_id}")
def buscar(usuario_id: int, db: Session = Depends(get_db)):
    return get_or_404(usuario_id, db)

@router.post("/", status_code=201)
def criar(dados: UsuarioCreate, db: Session = Depends(get_db)):
    usuario_existente = db.query(Usuario).filter(Usuario.login == dados.login).first()
    if usuario_existente:
        raise HTTPException(status_code=409, detail="Login foi duplicado!")
    usuario = Usuario(
        nome = dados.nome,
        login = dados.login,
        perfil = dados.perfil,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario

@router.put("/{usuario_id}")
def atualizar(usuario_id: int, dados: UsuarioUpdate, db: Session = Depends(get_db)):
    usuario = get_or_404(usuario_id, db)

    usuario.nome = dados.nome
    usuario.login = dados.login
    usuario.perfil = dados.perfil
    db.commit()
    db.refresh(usuario)
    return usuario

@router.delete("/{usuario_id}")
def deletar(usuario_id: int, db: Session = Depends(get_db)):
    usuario = get_or_404(usuario_id, db)

    db.delete(usuario)
    db.commit()
    return{"mensagem": "Usuário não existir!"}