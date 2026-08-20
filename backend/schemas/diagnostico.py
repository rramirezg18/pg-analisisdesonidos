from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


# Lo que envía el cliente. El id_usuario NO va aquí: se toma del JWT.
class DiagnosticoCreateIn(BaseModel):
    id_modelo: int
    id_modelo_cnn: int
    anio: int = Field(..., ge=1980, le=2100)
    kilometraje: Optional[int] = Field(None, ge=0)
    notas: Optional[str] = None
    audio_ref: str = Field(..., min_length=1)
    resultado: Literal["normal", "anomalia"]
    confianza: float = Field(..., ge=0, le=100)


# DTO interno completo (con el id_usuario ya resuelto) que recibe el service.
class DiagnosticoCreate(DiagnosticoCreateIn):
    id_usuario: int


class DiagnosticoRead(DiagnosticoCreateIn):
    model_config = ConfigDict(from_attributes=True)

    id_usuario: int
    id_diagnostico: int
    fecha_diagnostico: datetime


# Resultado que devuelve la inferencia del CNN (sin persistir todavía).
class AnalisisResultado(BaseModel):
    clase: Literal["normal", "anomalia"]
    confianza: float = Field(..., ge=0, le=100)
    valor_raw: float
