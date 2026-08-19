from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
    Index,
)

from database import Base


class Modelo(Base):
    __tablename__ = "modelo"

    id_modelo = Column(Integer, primary_key=True, autoincrement=True)
    id_marca = Column(
        Integer,
        ForeignKey("marca.id_marca", ondelete="RESTRICT"),
        nullable=False,
    )
    nombre = Column(Text, nullable=False)
    cilindraje = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("id_marca", "nombre", name="uq_modelo_marca_nombre"),
        CheckConstraint(
            "cilindraje IN (125, 150, 200)", name="ck_modelo_cilindraje"
        ),
        Index("idx_modelo_marca", "id_marca"),
    )
