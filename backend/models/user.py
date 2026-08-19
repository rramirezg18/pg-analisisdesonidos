from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    UniqueConstraint,
    CheckConstraint,
    func,
)

from database import Base


class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    proveedor_oauth = Column(Text, nullable=False)
    id_externo_proveedor = Column(Text, nullable=False)
    email = Column(Text, unique=True, nullable=False)
    nombre = Column(Text, nullable=True)
    fecha_registro = Column(DateTime, server_default=func.now(), nullable=False)
    ultimo_acceso = Column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "proveedor_oauth",
            "id_externo_proveedor",
            name="uq_usuario_proveedor_externo",
        ),
        CheckConstraint(
            "proveedor_oauth IN ('google', 'github')",
            name="ck_usuario_proveedor_oauth",
        ),
    )
