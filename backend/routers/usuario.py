from fastapi import APIRouter, Depends

from models.user import Usuario
from schemas.usuario import UsuarioMe, UsuarioRead
from utils.auth import es_admin, get_current_user

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


# Devuelve el usuario autenticado a partir del JWT. Es la única lectura de
# usuarios expuesta: no se listan ni se consultan datos de otros usuarios (RNF-07).
# El alta/actualización de usuarios ocurre solo en el callback OAuth (routers/auth.py).
@router.get("/me", response_model=UsuarioMe)
def yo(current: Usuario = Depends(get_current_user)):
    return UsuarioMe(
        **UsuarioRead.model_validate(current).model_dump(), es_admin=es_admin(current)
    )
