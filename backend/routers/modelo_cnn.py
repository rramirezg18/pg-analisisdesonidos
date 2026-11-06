from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from utils.auth import requerir_admin
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


# Escritura del catálogo: solo con la clave de administración (X-Admin-Key).
@router.post(
    "",
    response_model=ModeloCNNRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(requerir_admin)],
)
def crear(datos: ModeloCNNCreate, db: Session = Depends(get_db)):
    return service.crear(db, datos)


@router.patch(
    "/{id_modelo_cnn}/activar",
    response_model=ModeloCNNRead,
    dependencies=[Depends(requerir_admin)],
)
def activar(id_modelo_cnn: int, db: Session = Depends(get_db)):
    return service.activar(db, id_modelo_cnn)
