from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.marca import MarcaCreate, MarcaRead
import services.marca as service

router = APIRouter(prefix="/marcas", tags=["Marcas"])


@router.get("", response_model=list[MarcaRead])
def listar(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return service.listar(db, skip, limit)


@router.get("/{id_marca}", response_model=MarcaRead)
def obtener(id_marca: int, db: Session = Depends(get_db)):
    return service.obtener(db, id_marca)


@router.post("", response_model=MarcaRead, status_code=status.HTTP_201_CREATED)
def crear(datos: MarcaCreate, db: Session = Depends(get_db)):
    return service.crear(db, datos)
