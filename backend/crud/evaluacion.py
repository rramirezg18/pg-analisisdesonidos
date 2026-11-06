from sqlalchemy.orm import Session

from models.evaluacion import EvaluacionUsuario


def get_by_diagnostico(db: Session, id_diagnostico: int) -> EvaluacionUsuario | None:
    return (
        db.query(EvaluacionUsuario)
        .filter(EvaluacionUsuario.id_diagnostico == id_diagnostico)
        .first()
    )


def create(db: Session, evaluacion: EvaluacionUsuario) -> EvaluacionUsuario:
    db.add(evaluacion)
    db.commit()
    db.refresh(evaluacion)
    return evaluacion
