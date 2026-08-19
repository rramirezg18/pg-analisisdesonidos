from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ModeloCNNBase(BaseModel):
    version: str = Field(..., min_length=1)
    fecha_entrenamiento: datetime
    exactitud_validacion: float = Field(..., ge=0, le=100)
    archivo_pesos: str = Field(..., min_length=1)
    descripcion: Optional[str] = None
    activo: int = Field(0, ge=0, le=1)


class ModeloCNNCreate(ModeloCNNBase):
    pass


class ModeloCNNRead(ModeloCNNBase):
    model_config = ConfigDict(from_attributes=True)

    id_modelo_cnn: int
