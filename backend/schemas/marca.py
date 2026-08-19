from pydantic import BaseModel, ConfigDict, Field


class MarcaBase(BaseModel):
    nombre: str = Field(..., min_length=1)


class MarcaCreate(MarcaBase):
    pass


class MarcaRead(MarcaBase):
    model_config = ConfigDict(from_attributes=True)

    id_marca: int
