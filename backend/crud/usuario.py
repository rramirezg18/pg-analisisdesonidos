from sqlalchemy.orm import Session

from models.user import Usuario


def get(db: Session, id_usuario: int) -> Usuario | None:
    return db.get(Usuario, id_usuario)


def get_by_email(db: Session, email: str) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.email == email).first()


def get_by_proveedor(
    db: Session, proveedor_oauth: str, id_externo_proveedor: str
) -> Usuario | None:
    return (
        db.query(Usuario)
        .filter(
            Usuario.proveedor_oauth == proveedor_oauth,
            Usuario.id_externo_proveedor == id_externo_proveedor,
        )
        .first()
    )


def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[Usuario]:
    return db.query(Usuario).offset(skip).limit(limit).all()


def create(db: Session, usuario: Usuario) -> Usuario:
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def update(db: Session, usuario: Usuario, cambios: dict) -> Usuario:
    for campo, valor in cambios.items():
        setattr(usuario, campo, valor)
    db.commit()
    db.refresh(usuario)
    return usuario


def delete(db: Session, usuario: Usuario) -> None:
    db.delete(usuario)
    db.commit()
