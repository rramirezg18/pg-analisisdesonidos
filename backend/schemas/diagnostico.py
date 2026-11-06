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
    espectrograma_ref: str = Field(..., min_length=1)
    resultado: Literal["normal", "anomalia"]
    confianza: float = Field(..., ge=0, le=100)
    # ¿El usuario ya notaba algo raro en la moto? (se pregunta antes del resultado)
    notaba_sintomas: Optional[Literal["si", "no"]] = None


# DTO interno completo (con el id_usuario ya resuelto) que recibe el service.
class DiagnosticoCreate(DiagnosticoCreateIn):
    id_usuario: int


class DiagnosticoRead(DiagnosticoCreateIn):
    model_config = ConfigDict(from_attributes=True)

    id_usuario: int
    id_diagnostico: int
    fecha_diagnostico: datetime


# Lectura enriquecida con los nombres de marca/modelo para mostrar en la UI
# (historial y detalle) sin que el frontend tenga que resolver cada id.
class DiagnosticoDetalle(DiagnosticoRead):
    marca: str
    modelo: str
    cilindraje: int


# Vista del admin: incluye el veredicto del mecánico y quién hizo el diagnóstico.
class DiagnosticoAdmin(DiagnosticoDetalle):
    email_usuario: str
    veredicto_mecanico: Optional[Literal["sano", "leve", "grave"]] = None
    fecha_validacion: Optional[datetime] = None
    tiene_evaluacion: bool


# Lo que registra el admin tras la revisión del mecánico (null = quitar veredicto).
class VeredictoUpdate(BaseModel):
    veredicto_mecanico: Optional[Literal["sano", "leve", "grave"]]


# Resultado que devuelve la inferencia del CNN (uso interno del servicio).
class AnalisisResultado(BaseModel):
    clase: Literal["normal", "anomalia"]
    confianza: float = Field(..., ge=0, le=100)
    valor_raw: float
