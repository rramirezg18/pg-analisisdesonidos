from sqlalchemy import (
    Column,
    Integer,
    Text,
    Float,
    DateTime,
    CheckConstraint,
    Index,
    text,
)

from database import Base


class ModeloCNN(Base):
    __tablename__ = "modelo_cnn"

    id_modelo_cnn = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(Text, unique=True, nullable=False)
    fecha_entrenamiento = Column(DateTime, nullable=False)
    exactitud_validacion = Column(Float, nullable=False)
    archivo_pesos = Column(Text, nullable=False)
    descripcion = Column(Text, nullable=True)
    activo = Column(Integer, nullable=False, server_default=text("0"))

    __table_args__ = (
        CheckConstraint(
            "exactitud_validacion >= 0 AND exactitud_validacion <= 100",
            name="ck_modelo_cnn_exactitud",
        ),
        CheckConstraint("activo IN (0, 1)", name="ck_modelo_cnn_activo"),
        # Solo un ModeloCNN puede estar activo a la vez (índice único parcial).
        Index(
            "idx_modelo_cnn_activo_unico",
            "activo",
            unique=True,
            sqlite_where=text("activo = 1"),
        ),
    )
