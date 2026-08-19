from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import crud.modelo_cnn as crud_cnn
from models.modelo_cnn import ModeloCNN
from schemas.modelo_cnn import ModeloCNNCreate
from services.exceptions import NotFoundError, ConflictError


def listar(db: Session, skip: int = 0, limit: int = 100) -> list[ModeloCNN]:
    return crud_cnn.get_all(db, skip, limit)


def obtener(db: Session, id_modelo_cnn: int) -> ModeloCNN:
    cnn = crud_cnn.get(db, id_modelo_cnn)
    if cnn is None:
        raise NotFoundError(f"No existe el modelo CNN {id_modelo_cnn}")
    return cnn


def obtener_activo(db: Session) -> ModeloCNN:
    cnn = crud_cnn.get_activo(db)
    if cnn is None:
        raise NotFoundError("No hay ningún modelo CNN activo")
    return cnn


def crear(db: Session, datos: ModeloCNNCreate) -> ModeloCNN:
    # Regla de negocio: solo un CNN activo a la vez. Si el nuevo entra como
    # activo, primero desactivamos el que estuviera activo.
    if datos.activo == 1:
        _desactivar_actual(db)
    try:
        return crud_cnn.create(db, ModeloCNN(**datos.model_dump()))
    except IntegrityError:
        db.rollback()
        raise ConflictError(f"Ya existe un modelo CNN con versión '{datos.version}'")


def activar(db: Session, id_modelo_cnn: int) -> ModeloCNN:
    """Marca este CNN como el activo y desactiva cualquier otro."""
    cnn = obtener(db, id_modelo_cnn)
    _desactivar_actual(db)
    return crud_cnn.update(db, cnn, {"activo": 1})


def _desactivar_actual(db: Session) -> None:
    actual = crud_cnn.get_activo(db)
    if actual is not None:
        crud_cnn.update(db, actual, {"activo": 0})
