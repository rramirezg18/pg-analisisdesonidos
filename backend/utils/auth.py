import os
import secrets

import jwt
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database import get_db
from models.user import Usuario
from utils.security import decodificar_token
import crud.usuario as crud_usuario

# Hace que Swagger muestre el botón "Authorize" para pegar el Bearer token.
bearer_scheme = HTTPBearer()

# Clave de administración para escribir el catálogo (marcas, modelos, modelos CNN).
# Si ADMIN_API_KEY está vacía, esas operaciones quedan deshabilitadas por completo.
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "")
admin_key_scheme = APIKeyHeader(name="X-Admin-Key", auto_error=False)

# Correos (separados por coma) con acceso al panel de investigación (/admin).
ADMIN_EMAILS = {
    e.strip().lower() for e in os.getenv("ADMIN_EMAILS", "").split(",") if e.strip()
}


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    """Valida el JWT del header Authorization y devuelve el usuario. -> 401 si falla."""
    try:
        payload = decodificar_token(credentials.credentials)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    sub = payload.get("sub")
    if sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token sin sujeto"
        )

    usuario = crud_usuario.get(db, int(sub))
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado"
        )
    return usuario


def requerir_admin(clave: str | None = Security(admin_key_scheme)) -> None:
    """Exige el header X-Admin-Key. -> 401 sin clave, 403 si es incorrecta o está deshabilitada."""
    if not clave:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Falta la clave de administración"
        )
    if not ADMIN_API_KEY or not secrets.compare_digest(clave, ADMIN_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Clave de administración inválida"
        )


def es_admin(usuario: Usuario) -> bool:
    return usuario.email.lower() in ADMIN_EMAILS


def requerir_usuario_admin(current: Usuario = Depends(get_current_user)) -> Usuario:
    """Exige un usuario autenticado cuyo correo esté en ADMIN_EMAILS. -> 403 si no."""
    if not es_admin(current):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Acceso solo para administradores"
        )
    return current
