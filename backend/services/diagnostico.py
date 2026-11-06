from sqlalchemy.orm import Session

from datetime import datetime, timezone

import crud.diagnostico as crud_diag
import crud.evaluacion as crud_eval
import crud.usuario as crud_usuario
import crud.modelo as crud_modelo
import crud.modelo_cnn as crud_cnn
from models.diagnostico import Diagnostico
from models.evaluacion import EvaluacionUsuario
from schemas.diagnostico import (
    DiagnosticoAdmin,
    DiagnosticoCreate,
    DiagnosticoDetalle,
    DiagnosticoRead,
)
from schemas.evaluacion import EvaluacionCreate
from services.exceptions import ConflictError, NotFoundError


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


def evaluar(db: Session, id_diagnostico: int, datos: EvaluacionCreate) -> EvaluacionUsuario:
    """Guarda la encuesta del usuario. Solo se permite una por diagnóstico."""
    obtener(db, id_diagnostico)
    if crud_eval.get_by_diagnostico(db, id_diagnostico) is not None:
        raise ConflictError("Este diagnóstico ya fue evaluado")
    return crud_eval.create(
        db, EvaluacionUsuario(id_diagnostico=id_diagnostico, **datos.model_dump())
    )


def listar_admin(
    db: Session, estado: str | None = None, skip: int = 0, limit: int = 100
) -> list[DiagnosticoAdmin]:
    filas = crud_diag.get_detalle_admin(db, estado, skip, limit)
    return [
        DiagnosticoAdmin(
            **_a_detalle((diag, marca, modelo, cc)).model_dump(),
            email_usuario=email,
            veredicto_mecanico=diag.veredicto_mecanico,
            fecha_validacion=diag.fecha_validacion,
            tiene_evaluacion=id_eval is not None,
        )
        for diag, marca, modelo, cc, email, id_eval in filas
    ]


def registrar_veredicto(
    db: Session, id_diagnostico: int, veredicto: str | None
) -> Diagnostico:
    diag = obtener(db, id_diagnostico)
    return crud_diag.update(
        db,
        diag,
        {
            "veredicto_mecanico": veredicto,
            "fecha_validacion": datetime.now(timezone.utc) if veredicto else None,
        },
    )
