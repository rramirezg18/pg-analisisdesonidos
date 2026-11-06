from datetime import date
from typing import Literal, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import services.diagnostico as service_diag
import services.estadisticas as service_stats
from database import get_db
from schemas.diagnostico import DiagnosticoAdmin, VeredictoUpdate
from schemas.estadisticas import Estadisticas
from utils.auth import requerir_usuario_admin

# Panel de investigación: solo usuarios cuyo correo esté en ADMIN_EMAILS.
router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(requerir_usuario_admin)],
)


@router.get("/estadisticas", response_model=Estadisticas)
def estadisticas(
    id_modelo_cnn: Optional[int] = None,
    desde: Optional[date] = None,
    hasta: Optional[date] = None,
    db: Session = Depends(get_db),
):
    return service_stats.calcular(db, id_modelo_cnn, desde, hasta)


@router.get("/diagnosticos", response_model=list[DiagnosticoAdmin])
def listar_diagnosticos(
    estado: Optional[Literal["pendientes", "validados"]] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return service_diag.listar_admin(db, estado, skip, limit)


# Registra lo que dijo el mecánico al revisar la moto (sano, leve o grave).
@router.patch("/diagnosticos/{id_diagnostico}/veredicto", status_code=204)
def registrar_veredicto(
    id_diagnostico: int,
    datos: VeredictoUpdate,
    db: Session = Depends(get_db),
):
    service_diag.registrar_veredicto(db, id_diagnostico, datos.veredicto_mecanico)
