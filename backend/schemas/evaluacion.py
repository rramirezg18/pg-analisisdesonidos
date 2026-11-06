from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# Encuesta del usuario (OE3). Escala: 1 nada, 2 poca, 3 regular, 4 bastante, 5 mucha.
class EvaluacionCreate(BaseModel):
    # "¿Qué tanta confianza tiene al autorizar una reparación solo con lo que dice el mecánico?"
    confianza_antes: int = Field(..., ge=1, le=5)
    # "Con el respaldo de este diagnóstico, ¿qué tanta confianza tiene para autorizarla?"
    confianza_despues: int = Field(..., ge=1, le=5)
    # "¿El resultado le ayudó a decidir?"
    ayudo_decidir: Literal["si", "parcial", "no"]


class EvaluacionRead(EvaluacionCreate):
    model_config = ConfigDict(from_attributes=True)

    id_evaluacion: int
    id_diagnostico: int
    fecha_evaluacion: datetime
