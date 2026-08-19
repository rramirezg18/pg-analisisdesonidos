from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ModeloBase(BaseModel):
    id_marca: int
    nombre: str = Field(..., min_length=1)
    cilindraje: Literal[125, 150, 200]


class ModeloCreate(ModeloBase):
    pass


class ModeloRead(ModeloBase):
    model_config = ConfigDict(from_attributes=True)

    id_modelo: int
