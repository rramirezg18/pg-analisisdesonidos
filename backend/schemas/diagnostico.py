from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class DiagnosticoBase(BaseModel):
    id_usuario: int
    id_modelo: int
    id_modelo_cnn: int
    anio: int = Field(..., ge=1980, le=2100)
    kilometraje: Optional[int] = Field(None, ge=0)
    notas: Optional[str] = None
    audio_ref: str = Field(..., min_length=1)
    resultado: Literal["normal", "anomalia"]
    confianza: float = Field(..., ge=0, le=100)


class DiagnosticoCreate(DiagnosticoBase):
    pass


class DiagnosticoRead(DiagnosticoBase):
    model_config = ConfigDict(from_attributes=True)

    id_diagnostico: int
    fecha_diagnostico: datetime
