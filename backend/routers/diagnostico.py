from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from database import get_db
from models.user import Usuario
from schemas.diagnostico import (
    AnalisisResultado,
    DiagnosticoCreate,
    DiagnosticoCreateIn,
    DiagnosticoRead,
)
from services.cnn_service import CNNService
from utils.auth import get_current_user
from utils.cnn import get_cnn_service
import services.diagnostico as service

router = APIRouter(prefix="/diagnosticos", tags=["Diagnosticos"])

FORMATOS_AUDIO = {"wav", "mp3", "m4a", "ogg", "webm"}
MAX_AUDIO_BYTES = 20 * 1024 * 1024  # 20 MB


@router.post("/analizar", response_model=AnalisisResultado)
async def analizar(
    audio: UploadFile = File(...),
    cilindraje: int = Form(...),
    current: Usuario = Depends(get_current_user),
    cnn: CNNService = Depends(get_cnn_service),
):
    """Audio + cilindraje -> inferencia del CNN. No persiste todavía."""
    if cilindraje not in (125, 150, 200):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Cilindraje debe ser 125, 150 o 200"
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

    try:
        return cnn.predecir(audio_bytes, cilindraje)
    except Exception:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "No se pudo procesar el audio. Verifica que sea una grabación válida.",
        )


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
