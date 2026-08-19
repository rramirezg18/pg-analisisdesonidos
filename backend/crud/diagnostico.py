from sqlalchemy.orm import Session

from models.diagnostico import Diagnostico


def get(db: Session, id_diagnostico: int) -> Diagnostico | None:
    return db.get(Diagnostico, id_diagnostico)


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
