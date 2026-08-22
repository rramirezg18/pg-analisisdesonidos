import logging
import os
import uuid
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

import crud.modelo as crud_modelo
import crud.modelo_cnn as crud_cnn
import services.diagnostico as service
from database import get_db
from models.user import Usuario
from schemas.diagnostico import DiagnosticoCreate, DiagnosticoDetalle
from services.cnn_service import CNNService
from utils.auth import get_current_user
from utils.cnn import get_cnn_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/diagnosticos", tags=["Diagnosticos"])

FORMATOS_AUDIO = {"wav", "mp3", "m4a", "ogg", "webm"}
MAX_AUDIO_BYTES = 20 * 1024 * 1024  # 20 MB

# Carpeta donde se guardan los PNG de los espectrogramas (dentro del volumen data).
ESPECTROGRAMAS_DIR = os.getenv("ESPECTROGRAMAS_DIR", "data/espectrogramas")


@router.post("/analizar", response_model=DiagnosticoDetalle)
async def analizar(
    audio: UploadFile = File(...),
    id_modelo: int = Form(...),
    anio: int = Form(...),
    kilometraje: Optional[int] = Form(None),
    notas: Optional[str] = Form(None),
    current: Usuario = Depends(get_current_user),
    cnn: CNNService = Depends(get_cnn_service),
    db: Session = Depends(get_db),
):
    """Audio + datos de la moto -> inferencia del CNN + persistencia.

    En la BD se guarda la IMAGEN del espectrograma (PNG), nunca el audio.
    """
    modelo = crud_modelo.get(db, id_modelo)
    if modelo is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No existe el modelo indicado")

    cnn_activo = crud_cnn.get_activo(db)
    if cnn_activo is None:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, "No hay modelo CNN activo"
        )

    ext = (audio.filename or "").rsplit(".", 1)[-1].lower()
    if ext not in FORMATOS_AUDIO:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Formato no soportado. Usa: {', '.join(sorted(FORMATOS_AUDIO))}",
        )

    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Archivo de audio vacío")
    if len(audio_bytes) > MAX_AUDIO_BYTES:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Archivo demasiado grande (máx. 20 MB)"
        )

    # El cilindraje que entra al modelo sale del modelo de moto, no del cliente.
    cilindraje = modelo.cilindraje

    try:
        resultado = cnn.predecir(audio_bytes, cilindraje)
    except Exception:
        logger.exception("Falló la inferencia del CNN")
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "No se pudo procesar el audio. Verifica que sea una grabación válida.",
        )

    # Genera y guarda el PNG del espectrograma. El nombre es un UUID (no adivinable).
    os.makedirs(ESPECTROGRAMAS_DIR, exist_ok=True)
    nombre_png = f"{uuid.uuid4().hex}.png"
    ruta_absoluta = os.path.join(ESPECTROGRAMAS_DIR, nombre_png)
    try:
        cnn.generar_espectrograma_png(audio_bytes, ruta_absoluta)
    except Exception:
        logger.exception("Falló la generación del espectrograma PNG")
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "No se pudo generar el espectrograma del audio.",
        )

    datos = DiagnosticoCreate(
        id_usuario=current.id_usuario,
        id_modelo=id_modelo,
        id_modelo_cnn=cnn_activo.id_modelo_cnn,
        anio=anio,
        kilometraje=kilometraje,
        notas=notas,
        espectrograma_ref=f"espectrogramas/{nombre_png}",
        resultado=resultado["clase"],
        confianza=resultado["confianza"],
    )
    creado = service.crear(db, datos)
    return service.obtener_detalle(db, creado.id_diagnostico)


# Historial del usuario autenticado. Debe ir antes de /{id_diagnostico}.
@router.get("/mis", response_model=list[DiagnosticoDetalle])
def mis_diagnosticos(
    skip: int = 0,
    limit: int = 100,
    current: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.historial_usuario(db, current.id_usuario, skip, limit)


@router.get("/{id_diagnostico}", response_model=DiagnosticoDetalle)
def obtener(
    id_diagnostico: int,
    current: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    detalle = service.obtener_detalle(db, id_diagnostico)
    if detalle.id_usuario != current.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes ver diagnósticos de otro usuario",
        )
    return detalle
