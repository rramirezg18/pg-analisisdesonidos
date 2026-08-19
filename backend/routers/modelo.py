from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.modelo import ModeloCreate, ModeloRead
import services.modelo as service

router = APIRouter(prefix="/modelos", tags=["Modelos"])


@router.get("", response_model=list[ModeloRead])
def listar(
    id_marca: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    if id_marca is not None:
        return service.listar_por_marca(db, id_marca)
    return service.listar(db, skip, limit)


@router.get("/{id_modelo}", response_model=ModeloRead)
def obtener(id_modelo: int, db: Session = Depends(get_db)):
    return service.obtener(db, id_modelo)


@router.post("", response_model=ModeloRead, status_code=status.HTTP_201_CREATED)
def crear(datos: ModeloCreate, db: Session = Depends(get_db)):
    return service.crear(db, datos)
