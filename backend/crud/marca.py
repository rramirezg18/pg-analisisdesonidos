from sqlalchemy.orm import Session

from models.marca import Marca


def get(db: Session, id_marca: int) -> Marca | None:
    return db.get(Marca, id_marca)


def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[Marca]:
    return db.query(Marca).offset(skip).limit(limit).all()


def create(db: Session, marca: Marca) -> Marca:
    db.add(marca)
    db.commit()
    db.refresh(marca)
    return marca


def update(db: Session, marca: Marca, cambios: dict) -> Marca:
    for campo, valor in cambios.items():
        setattr(marca, campo, valor)
    db.commit()
    db.refresh(marca)
    return marca


def delete(db: Session, marca: Marca) -> None:
    db.delete(marca)
    db.commit()
