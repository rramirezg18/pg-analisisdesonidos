from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.user import Usuario
from schemas.usuario import UsuarioCreate, UsuarioRead
from utils.auth import get_current_user
import services.usuario as service

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("", response_model=list[UsuarioRead])
def listar(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return service.listar(db, skip, limit)


# Devuelve el usuario autenticado a partir del JWT. Debe ir antes de /{id_usuario}.
@router.get("/me", response_model=UsuarioRead)
def yo(current: Usuario = Depends(get_current_user)):
    return current


@router.get("/{id_usuario}", response_model=UsuarioRead)
def obtener(id_usuario: int, db: Session = Depends(get_db)):
    return service.obtener(db, id_usuario)


# Punto de entrada del login OAuth: recibe la identidad ya verificada por el
# proveedor y crea o actualiza el usuario (upsert idempotente).
@router.post("/login-oauth", response_model=UsuarioRead)
def login_oauth(datos: UsuarioCreate, db: Session = Depends(get_db)):
    return service.login_oauth(db, datos)
