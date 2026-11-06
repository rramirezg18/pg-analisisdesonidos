from sqlalchemy.orm import Session

from models.diagnostico import Diagnostico
from models.evaluacion import EvaluacionUsuario
from models.marca import Marca
from models.modelo import Modelo
from models.user import Usuario


def get(db: Session, id_diagnostico: int) -> Diagnostico | None:
    return db.get(Diagnostico, id_diagnostico)


# Filas del diagnóstico enriquecidas con nombre de marca/modelo y cilindraje,
# para el historial y el detalle. Devuelve tuplas (Diagnostico, marca, modelo, cc).
def _query_detalle(db: Session):
    return (
        db.query(Diagnostico, Marca.nombre, Modelo.nombre, Modelo.cilindraje)
        .join(Modelo, Diagnostico.id_modelo == Modelo.id_modelo)
        .join(Marca, Modelo.id_marca == Marca.id_marca)
    )


def get_detalle(db: Session, id_diagnostico: int):
    return (
        _query_detalle(db)
        .filter(Diagnostico.id_diagnostico == id_diagnostico)
        .first()
    )


def get_detalle_by_usuario(
    db: Session, id_usuario: int, skip: int = 0, limit: int = 100
):
    return (
        _query_detalle(db)
        .filter(Diagnostico.id_usuario == id_usuario)
        .order_by(Diagnostico.fecha_diagnostico.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


# Listado del admin: tuplas (Diagnostico, marca, modelo, cc, email, id_evaluacion).
# estado: "pendientes" (sin veredicto), "validados" o None (todos).
def get_detalle_admin(
    db: Session, estado: str | None = None, skip: int = 0, limit: int = 100
):
    q = (
        db.query(
            Diagnostico,
            Marca.nombre,
            Modelo.nombre,
            Modelo.cilindraje,
            Usuario.email,
            EvaluacionUsuario.id_evaluacion,
        )
        .join(Modelo, Diagnostico.id_modelo == Modelo.id_modelo)
        .join(Marca, Modelo.id_marca == Marca.id_marca)
        .join(Usuario, Diagnostico.id_usuario == Usuario.id_usuario)
        .outerjoin(
            EvaluacionUsuario,
            EvaluacionUsuario.id_diagnostico == Diagnostico.id_diagnostico,
        )
    )
    if estado == "pendientes":
        q = q.filter(Diagnostico.veredicto_mecanico.is_(None))
    elif estado == "validados":
        q = q.filter(Diagnostico.veredicto_mecanico.is_not(None))
    return (
        q.order_by(Diagnostico.fecha_diagnostico.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[Diagnostico]:
    return db.query(Diagnostico).offset(skip).limit(limit).all()


# Historial de un usuario, mas reciente primero (usa idx_diagnostico_usuario_fecha).
def get_by_usuario(
    db: Session, id_usuario: int, skip: int = 0, limit: int = 100
) -> list[Diagnostico]:
    return (
        db.query(Diagnostico)
        .filter(Diagnostico.id_usuario == id_usuario)
        .order_by(Diagnostico.fecha_diagnostico.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create(db: Session, diagnostico: Diagnostico) -> Diagnostico:
    db.add(diagnostico)
    db.commit()
    db.refresh(diagnostico)
    return diagnostico


def update(db: Session, diagnostico: Diagnostico, cambios: dict) -> Diagnostico:
    for campo, valor in cambios.items():
        setattr(diagnostico, campo, valor)
    db.commit()
    db.refresh(diagnostico)
    return diagnostico


def delete(db: Session, diagnostico: Diagnostico) -> None:
    db.delete(diagnostico)
    db.commit()
