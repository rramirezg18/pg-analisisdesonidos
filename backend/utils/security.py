"""Helpers de seguridad: firma de JWT y hashing.

En una app con login OAuth lo que realmente se "cifra"/firma es el JWT que tú
emites tras validar la identidad del proveedor. La clave sale de SECRET_KEY.
"""

import hashlib
import os
from datetime import datetime, timedelta, timezone

import jwt

SECRET_KEY = os.getenv("SECRET_KEY", "CAMBIAME-usa-un-valor-aleatorio-largo")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


def crear_token_acceso(
    datos: dict, expires_delta: timedelta | None = None
) -> str:
    """Firma un JWT. `datos` suele incluir el id del usuario (claim 'sub')."""
    to_encode = datos.copy()
    expira = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expira})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)


def decodificar_token(token: str) -> dict:
    """Verifica la firma y la expiración. Lanza jwt.PyJWTError si es inválido."""
    return jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])


def hash_token(valor: str) -> str:
    """SHA-256 en hex. Para guardar tokens opacos (p. ej. refresh) sin texto plano."""
    return hashlib.sha256(valor.encode("utf-8")).hexdigest()
