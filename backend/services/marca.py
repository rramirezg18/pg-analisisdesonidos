from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import crud.marca as crud_marca
from models.marca import Marca
from schemas.marca import MarcaCreate
from services.exceptions import NotFoundError, ConflictError


def listar(db: Session, skip: int = 0, limit: int = 100) -> list[Marca]:
    return crud_marca.get_all(db, skip, limit)


def obtener(db: Session, id_marca: int) -> Marca:
    marca = crud_marca.get(db, id_marca)
    if marca is None:
        raise NotFoundError(f"No existe la marca {id_marca}")
    return marca


def crear(db: Session, datos: MarcaCreate) -> Marca:
    try:
        return crud_marca.create(db, Marca(**datos.model_dump()))
    except IntegrityError:
        db.rollback()
        raise ConflictError(f"Ya existe una marca con nombre '{datos.nombre}'")
