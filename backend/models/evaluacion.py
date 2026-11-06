from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    ForeignKey,
    CheckConstraint,
    func,
)

from database import Base


# Encuesta del usuario sobre un diagnóstico (OE3: confianza percibida).
# Una por diagnóstico: confianza antes (solo con el mecánico) vs después
# (con el respaldo del sistema), en escala Likert de 1 a 5.
class EvaluacionUsuario(Base):
    __tablename__ = "evaluacion_usuario"

    id_evaluacion = Column(Integer, primary_key=True, autoincrement=True)
    id_diagnostico = Column(
        Integer,
        ForeignKey("diagnostico.id_diagnostico", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    confianza_antes = Column(Integer, nullable=False)
    confianza_despues = Column(Integer, nullable=False)
    ayudo_decidir = Column(Text, nullable=False)
    fecha_evaluacion = Column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "confianza_antes BETWEEN 1 AND 5", name="ck_evaluacion_confianza_antes"
        ),
        CheckConstraint(
            "confianza_despues BETWEEN 1 AND 5", name="ck_evaluacion_confianza_despues"
        ),
        CheckConstraint(
            "ayudo_decidir IN ('si', 'parcial', 'no')", name="ck_evaluacion_ayudo"
        ),
    )
