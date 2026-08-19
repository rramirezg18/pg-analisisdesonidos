from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class UsuarioBase(BaseModel):
    proveedor_oauth: Literal["google", "github"]
    id_externo_proveedor: str = Field(..., min_length=1)
    email: str = Field(..., min_length=3)
    nombre: Optional[str] = None


# DTO de entrada: lo que llega tras el login OAuth para crear/actualizar el usuario.
class UsuarioCreate(UsuarioBase):
    pass


# DTO de salida: lo que la API devuelve (incluye id y campos gestionados por la BD).
class UsuarioRead(UsuarioBase):
    model_config = ConfigDict(from_attributes=True)

    id_usuario: int
    fecha_registro: datetime
    ultimo_acceso: Optional[datetime] = None
