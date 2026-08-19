from sqlalchemy.orm import Session

from models.modelo import Modelo


def get(db: Session, id_modelo: int) -> Modelo | None:
    return db.get(Modelo, id_modelo)


def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[Modelo]:
    return db.query(Modelo).offset(skip).limit(limit).all()


def get_by_marca(db: Session, id_marca: int) -> list[Modelo]:
    return db.query(Modelo).filter(Modelo.id_marca == id_marca).all()


def create(db: Session, modelo: Modelo) -> Modelo:
    db.add(modelo)
    db.commit()
    db.refresh(modelo)
    return modelo


def update(db: Session, modelo: Modelo, cambios: dict) -> Modelo:
    for campo, valor in cambios.items():
        setattr(modelo, campo, valor)
    db.commit()
    db.refresh(modelo)
    return modelo


def delete(db: Session, modelo: Modelo) -> None:
    db.delete(modelo)
    db.commit()
