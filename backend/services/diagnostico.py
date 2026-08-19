from sqlalchemy.orm import Session

import crud.diagnostico as crud_diag
import crud.usuario as crud_usuario
import crud.modelo as crud_modelo
import crud.modelo_cnn as crud_cnn
from models.diagnostico import Diagnostico
from schemas.diagnostico import DiagnosticoCreate
from services.exceptions import NotFoundError


def obtener(db: Session, id_diagnostico: int) -> Diagnostico:
    diag = crud_diag.get(db, id_diagnostico)
    if diag is None:
        raise NotFoundError(f"No existe el diagnóstico {id_diagnostico}")
    return diag


def historial_usuario(
    db: Session, id_usuario: int, skip: int = 0, limit: int = 100
) -> list[Diagnostico]:
    if crud_usuario.get(db, id_usuario) is None:
        raise NotFoundError(f"No existe el usuario {id_usuario}")
    return crud_diag.get_by_usuario(db, id_usuario, skip, limit)


def crear(db: Session, datos: DiagnosticoCreate) -> Diagnostico:
    # Verificamos las tres FKs antes de insertar para dar un error claro
    # (404) en vez de un IntegrityError genérico de la BD.
    if crud_usuario.get(db, datos.id_usuario) is None:
        raise NotFoundError(f"No existe el usuario {datos.id_usuario}")
    if crud_modelo.get(db, datos.id_modelo) is None:
        raise NotFoundError(f"No existe el modelo {datos.id_modelo}")
    if crud_cnn.get(db, datos.id_modelo_cnn) is None:
        raise NotFoundError(f"No existe el modelo CNN {datos.id_modelo_cnn}")

    return crud_diag.create(db, Diagnostico(**datos.model_dump()))
