from datetime import datetime, timezone

from sqlalchemy.orm import Session

import crud.usuario as crud_usuario
from models.user import Usuario
from schemas.usuario import UsuarioCreate
from services.exceptions import NotFoundError


def listar(db: Session, skip: int = 0, limit: int = 100) -> list[Usuario]:
    return crud_usuario.get_all(db, skip, limit)


def obtener(db: Session, id_usuario: int) -> Usuario:
    usuario = crud_usuario.get(db, id_usuario)
    if usuario is None:
        raise NotFoundError(f"No existe el usuario {id_usuario}")
    return usuario


def login_oauth(db: Session, datos: UsuarioCreate) -> Usuario:
    """Corazón del login OAuth: busca al usuario por (proveedor, id externo).

    Si no existe lo crea; si ya existe actualiza su perfil y último acceso.
    Idempotente: llamarlo varias veces con la misma identidad no duplica.
    """
    usuario = crud_usuario.get_by_proveedor(
        db, datos.proveedor_oauth, datos.id_externo_proveedor
    )
    if usuario is None:
        return crud_usuario.create(db, Usuario(**datos.model_dump()))

    return crud_usuario.update(
        db,
        usuario,
        {
            "email": datos.email,
            "nombre": datos.nombre,
            "ultimo_acceso": datetime.now(timezone.utc),
        },
    )
