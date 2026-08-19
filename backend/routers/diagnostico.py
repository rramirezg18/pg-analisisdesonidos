from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.user import Usuario
from schemas.diagnostico import DiagnosticoCreate, DiagnosticoCreateIn, DiagnosticoRead
from utils.auth import get_current_user
import services.diagnostico as service

router = APIRouter(prefix="/diagnosticos", tags=["Diagnosticos"])


@router.post("", response_model=DiagnosticoRead, status_code=status.HTTP_201_CREATED)
def crear(
    datos: DiagnosticoCreateIn,
    current: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # El id_usuario sale del token, no del body: nadie crea diagnósticos a nombre de otro.
    completo = DiagnosticoCreate(**datos.model_dump(), id_usuario=current.id_usuario)
    return service.crear(db, completo)


# Historial del usuario autenticado. Debe ir antes de /{id_diagnostico}.
@router.get("/mis", response_model=list[DiagnosticoRead])
def mis_diagnosticos(
    skip: int = 0,
    limit: int = 100,
    current: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.historial_usuario(db, current.id_usuario, skip, limit)


@router.get("/{id_diagnostico}", response_model=DiagnosticoRead)
def obtener(
    id_diagnostico: int,
    current: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    diag = service.obtener(db, id_diagnostico)
    if diag.id_usuario != current.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes ver diagnósticos de otro usuario",
        )
    return diag
