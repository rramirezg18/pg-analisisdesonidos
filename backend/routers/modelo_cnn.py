from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.modelo_cnn import ModeloCNNCreate, ModeloCNNRead
import services.modelo_cnn as service

router = APIRouter(prefix="/modelos-cnn", tags=["Modelos CNN"])


@router.get("", response_model=list[ModeloCNNRead])
def listar(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return service.listar(db, skip, limit)


# Debe declararse antes de /{id_modelo_cnn} para que "activo" no se lea como id.
@router.get("/activo", response_model=ModeloCNNRead)
def obtener_activo(db: Session = Depends(get_db)):
    return service.obtener_activo(db)


@router.get("/{id_modelo_cnn}", response_model=ModeloCNNRead)
def obtener(id_modelo_cnn: int, db: Session = Depends(get_db)):
    return service.obtener(db, id_modelo_cnn)


@router.post("", response_model=ModeloCNNRead, status_code=status.HTTP_201_CREATED)
def crear(datos: ModeloCNNCreate, db: Session = Depends(get_db)):
    return service.crear(db, datos)


@router.patch("/{id_modelo_cnn}/activar", response_model=ModeloCNNRead)
def activar(id_modelo_cnn: int, db: Session = Depends(get_db)):
    return service.activar(db, id_modelo_cnn)
