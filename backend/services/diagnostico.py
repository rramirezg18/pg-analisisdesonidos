from sqlalchemy.orm import Session

import crud.diagnostico as crud_diag
import crud.usuario as crud_usuario
import crud.modelo as crud_modelo
import crud.modelo_cnn as crud_cnn
from models.diagnostico import Diagnostico
from schemas.diagnostico import DiagnosticoCreate, DiagnosticoDetalle, DiagnosticoRead
from services.exceptions import NotFoundError


def _a_detalle(fila) -> DiagnosticoDetalle:
    diag, marca, modelo, cilindraje = fila
    return DiagnosticoDetalle(
        **DiagnosticoRead.model_validate(diag).model_dump(),
        marca=marca,
        modelo=modelo,
        cilindraje=cilindraje,
    )


def obtener(db: Session, id_diagnostico: int) -> Diagnostico:
    diag = crud_diag.get(db, id_diagnostico)
    if diag is None:
        raise NotFoundError(f"No existe el diagnóstico {id_diagnostico}")
    return diag


def obtener_detalle(db: Session, id_diagnostico: int) -> DiagnosticoDetalle:
    fila = crud_diag.get_detalle(db, id_diagnostico)
    if fila is None:
        raise NotFoundError(f"No existe el diagnóstico {id_diagnostico}")
    return _a_detalle(fila)


def historial_usuario(
    db: Session, id_usuario: int, skip: int = 0, limit: int = 100
) -> list[DiagnosticoDetalle]:
    if crud_usuario.get(db, id_usuario) is None:
        raise NotFoundError(f"No existe el usuario {id_usuario}")
    filas = crud_diag.get_detalle_by_usuario(db, id_usuario, skip, limit)
    return [_a_detalle(f) for f in filas]


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
