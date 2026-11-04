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
    perfil: str  # "admin" ou "operador"


class UsuarioUpdate(BaseModel):
    nome:   Optional[str] = None
    login:  Optional[str] = None
    perfil: Optional[str] = None


# Função auxiliar

def get_or_404(usuario_id: int, db: Session) -> Usuario:
    u = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Usuario não encontrado")
    # TODO: busque o usuário no banco; se não existir, raise HTTPException 404
    # pass


# Rotas

@router.get("/")
def listar(db: Session = Depends(get_db)):
    usuarios = db.query(Usuario).all()
    return usuarios
    # TODO: retorne todos os usuários
    # pass


@router.get("/{usuario_id}")
def buscar(usuario_id: int, db: Session = Depends(get_db)):
    usuario = get_or_404(db, Usuario, usuario_id)
    return usuario
    # TODO: use get_or_404
    pass


@router.post("/", status_code=201)
def criar(dados: UsuarioCreate, db: Session = Depends(get_db)):
    novo_usuario = Usuario(**dados.model_dump())

    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario
    # TODO: verifique se o login já existe → 409
    # TODO: crie e salve o usuário
    # pass


@router.put("/{usuario_id}")
def atualizar(usuario_id: int, dados: UsuarioUpdate, db: Session = Depends(get_db)):
    usuario_existente = get_or_404(db, Usuario, usuario_id)

    dados_atualizacao = dados.model_dump(exclude_unset = True)

    for chave, valor in dados_atualizacao.items():
        setattr(usuario_existente, chave, valor)

        db.commit()
        db.refresh(usuario_existente)
        return usuario_existente
    # TODO: use get_or_404; atualize apenas os campos enviados
    # pass


@router.delete("/{usuario_id}")
def deletar(usuario_id: int, db: Session = Depends(get_db)):
    usuario = get_or_404(db, Usuario, usuario_id)

    db.delete(usuario)
    db.commit()
    db.refresh()
    # TODO: use get_or_404; delete e retorne mensagem de confirmação
    # pass
