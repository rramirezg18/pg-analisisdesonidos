"""
Ejemplo de integración del CNN con FastAPI.
Adapta esto a tu estructura de routers/endpoints existente.
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from contextlib import asynccontextmanager
from cnn_service import CNNService

# Variable global para el servicio CNN (singleton)
cnn_service: CNNService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Carga el modelo CNN al arrancar la app."""
    global cnn_service
    cnn_service = CNNService(
        modelo_path="modelos/modelo_cnn_v1.keras",
        config_path="modelos/model_config.json"
    )
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/diagnosticos/analizar")
async def analizar_audio(
    audio: UploadFile = File(...),
    cilindraje: int = Form(...),
):
    """
    Recibe un archivo de audio + cilindraje → devuelve diagnóstico.
    
    Response:
        {
            "clase": "normal" | "anomalia",
            "confianza": 87.3,
            "valor_raw": 0.9365
        }
    """
    # Validar cilindraje
    if cilindraje not in [125, 150, 200]:
        raise HTTPException(400, "Cilindraje debe ser 125, 150 o 200")
    
    # Validar formato
    if audio.filename:
        ext = audio.filename.rsplit(".", 1)[-1].lower()
        if ext not in ["wav", "mp3", "m4a"]:
            raise HTTPException(400, f"Formato no soportado. Use: wav, mp3, m4a")
    
    # Leer audio
    audio_bytes = await audio.read()
    if len(audio_bytes) == 0:
        raise HTTPException(400, "Archivo de audio vacío")
    if len(audio_bytes) > 20 * 1024 * 1024:  # 20 MB
        raise HTTPException(400, "Archivo demasiado grande (máximo 20 MB)")
    
    # Ejecutar inferencia
    try:
        resultado = cnn_service.predecir(audio_bytes, cilindraje)
    except Exception as e:
        raise HTTPException(500, f"Error al procesar el audio: {str(e)}")
    
    return resultado
