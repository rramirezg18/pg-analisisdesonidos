from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import crud.modelo as crud_modelo
import crud.marca as crud_marca
from models.modelo import Modelo
from schemas.modelo import ModeloCreate
from services.exceptions import NotFoundError, ConflictError


def listar(db: Session, skip: int = 0, limit: int = 100) -> list[Modelo]:
    return crud_modelo.get_all(db, skip, limit)


def obtener(db: Session, id_modelo: int) -> Modelo:
    modelo = crud_modelo.get(db, id_modelo)
    if modelo is None:
        raise NotFoundError(f"No existe el modelo {id_modelo}")
    return modelo


def listar_por_marca(db: Session, id_marca: int) -> list[Modelo]:
    return crud_modelo.get_by_marca(db, id_marca)


def crear(db: Session, datos: ModeloCreate) -> Modelo:
    if crud_marca.get(db, datos.id_marca) is None:
        raise NotFoundError(f"No existe la marca {datos.id_marca}")
    try:
        return crud_modelo.create(db, Modelo(**datos.model_dump()))
    except IntegrityError:
        db.rollback()
        raise ConflictError(
            f"La marca {datos.id_marca} ya tiene un modelo '{datos.nombre}'"
        )
