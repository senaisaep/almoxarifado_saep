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
    # Busca o usuário no banco pelo ID
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=404, 
            detail=f"Usuário com ID {usuario_id} não encontrado."
        )
    return usuario


# Rotas

@router.get("/")
def listar(db: Session = Depends(get_db)):
    # Retorna todos os usuários
    usuarios = db.query(Usuario).all()
    return usuarios


@router.get("/{usuario_id}")
def buscar(usuario_id: int, db: Session = Depends(get_db)):
    # Usa a função auxiliar get_or_404
    usuario = get_or_404(usuario_id, db)
    return usuario


@router.post("/", status_code=201)
def criar(dados: UsuarioCreate, db: Session = Depends(get_db)):
    # Verifica se o login já existe no banco (Evita duplicados)
    login_existente = db.query(Usuario).filter(Usuario.login == dados.login).first()
    if login_existente:
        raise HTTPException(
            status_code=409, 
            detail="O login informado já está cadastrado."
        )
    
    # Cria e salva o usuário
    novo_usuario = Usuario(**dados.model_dump())
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario


@router.put("/{usuario_id}")
def atualizar(usuario_id: int, dados: UsuarioUpdate, db: Session = Depends(get_db)):
    # Busca o usuário existente ou lança 404
    usuario_existente = get_or_404(usuario_id, db)
    
    # Extrai apenas os campos que foram enviados na requisição
    dados_atualizacao = dados.model_dump(exclude_unset=True)
    
    # Atualiza apenas os campos enviados
    for chave, valor in dados_atualizacao.items():
        setattr(usuario_existente, chave, valor)
        
    db.commit()
    db.refresh(usuario_existente)
    return usuario_existente


@router.delete("/{usuario_id}")
def deletar(usuario_id: int, db: Session = Depends(get_db)):
    # Busca o usuário existente ou lança 404
    usuario = get_or_404(usuario_id, db)
    
    # Deleta do banco e confirma
    db.delete(usuario)
    db.commit()
    return {"message": f"Usuário com ID {usuario_id} deletado com sucesso."}


# # Função auxiliar

# def get_or_404(usuario_id: int, db: Session) -> Usuario:
#     # TODO: busque o usuário no banco; se não existir, raise HTTPException 404
#     pass


# # Rotas

# @router.get("/")
# def listar(db: Session = Depends(get_db)):
#     # TODO: retorne todos os usuários
#     pass


# @router.get("/{usuario_id}")
# def buscar(usuario_id: int, db: Session = Depends(get_db)):
#     # TODO: use get_or_404
#     pass


# @router.post("/", status_code=201)
# def criar(dados: UsuarioCreate, db: Session = Depends(get_db)):
#     # TODO: verifique se o login já existe → 409
#     # TODO: crie e salve o usuário
#     pass


# @router.put("/{usuario_id}")
# def atualizar(usuario_id: int, dados: UsuarioUpdate, db: Session = Depends(get_db)):
#     # TODO: use get_or_404; atualize apenas os campos enviados
#     pass


# @router.delete("/{usuario_id}")
# def deletar(usuario_id: int, db: Session = Depends(get_db)):
#     # TODO: use get_or_404; delete e retorne mensagem de confirmação
#     pass
