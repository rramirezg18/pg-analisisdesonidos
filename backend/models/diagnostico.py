from sqlalchemy import (
    Column,
    Integer,
    Text,
    Float,
    DateTime,
    ForeignKey,
    CheckConstraint,
    Index,
    func,
    text,
)

from database import Base


class Diagnostico(Base):
    __tablename__ = "diagnostico"

    id_diagnostico = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(
        Integer,
        ForeignKey("usuario.id_usuario", ondelete="CASCADE"),
        nullable=False,
    )
    id_modelo = Column(
        Integer,
        ForeignKey("modelo.id_modelo", ondelete="RESTRICT"),
        nullable=False,
    )
    id_modelo_cnn = Column(
        Integer,
        ForeignKey("modelo_cnn.id_modelo_cnn", ondelete="RESTRICT"),
        nullable=False,
    )
    anio = Column(Integer, nullable=False)
    kilometraje = Column(Integer, nullable=True)
    notas = Column(Text, nullable=True)
    espectrograma_ref = Column(Text, nullable=False)
    resultado = Column(Text, nullable=False)
    confianza = Column(Float, nullable=False)
    fecha_diagnostico = Column(
        DateTime, server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint("anio >= 1980 AND anio <= 2100", name="ck_diagnostico_anio"),
        CheckConstraint(
            "kilometraje IS NULL OR kilometraje >= 0",
            name="ck_diagnostico_kilometraje",
        ),
        CheckConstraint(
            "resultado IN ('normal', 'anomalia')",
            name="ck_diagnostico_resultado",
        ),
        CheckConstraint(
            "confianza >= 0 AND confianza <= 100", name="ck_diagnostico_confianza"
        ),
        Index(
            "idx_diagnostico_usuario_fecha",
            "id_usuario",
            text("fecha_diagnostico DESC"),
        ),
        Index("idx_diagnostico_modelo", "id_modelo"),
        Index("idx_diagnostico_modelo_cnn", "id_modelo_cnn"),
    )
