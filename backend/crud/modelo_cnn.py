from sqlalchemy.orm import Session

from models.modelo_cnn import ModeloCNN


def get(db: Session, id_modelo_cnn: int) -> ModeloCNN | None:
    return db.get(ModeloCNN, id_modelo_cnn)


def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[ModeloCNN]:
    return db.query(ModeloCNN).offset(skip).limit(limit).all()


def get_activo(db: Session) -> ModeloCNN | None:
    return db.query(ModeloCNN).filter(ModeloCNN.activo == 1).first()


def create(db: Session, modelo_cnn: ModeloCNN) -> ModeloCNN:
    db.add(modelo_cnn)
    db.commit()
    db.refresh(modelo_cnn)
    return modelo_cnn


def update(db: Session, modelo_cnn: ModeloCNN, cambios: dict) -> ModeloCNN:
    for campo, valor in cambios.items():
        setattr(modelo_cnn, campo, valor)
    db.commit()
    db.refresh(modelo_cnn)
    return modelo_cnn


def delete(db: Session, modelo_cnn: ModeloCNN) -> None:
    db.delete(modelo_cnn)
    db.commit()
