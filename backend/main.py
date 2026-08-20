import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from middleware import setup_middlewares
from services.cnn_service import CNNService
from services.exceptions import NotFoundError, ConflictError
from routers import auth, marca, usuario, modelo, modelo_cnn, diagnostico

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODELO_CNN_PATH = os.getenv("MODELO_CNN_PATH", "modelos/modelo_cnn_v1.keras")
MODELO_CNN_CONFIG = os.getenv("MODELO_CNN_CONFIG", "modelos/model_config.json")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cargar el modelo CNN una sola vez al arrancar (no en cada request).
    # Si falla, la app sigue viva pero /analizar responderá 503.
    try:
        app.state.cnn_service = CNNService(MODELO_CNN_PATH, MODELO_CNN_CONFIG)
    except Exception:
        app.state.cnn_service = None
        logger.exception("No se pudo cargar el modelo CNN")
    yield


app = FastAPI(
    title="API Análisis de Sonidos de Motores",
    root_path="/api",
    lifespan=lifespan,
)

# Orígenes permitidos para CORS (separados por coma en la variable de entorno).
cors_origins = os.getenv(
    "CORS_ORIGINS", "http://localhost,http://localhost:5173"
).split(",")
setup_middlewares(app, cors_origins=cors_origins)


# Excepciones de dominio -> códigos HTTP, en un solo lugar.
@app.exception_handler(NotFoundError)
async def manejar_no_encontrado(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(ConflictError)
async def manejar_conflicto(request: Request, exc: ConflictError):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


app.include_router(auth.router)
app.include_router(marca.router)
app.include_router(usuario.router)
app.include_router(modelo.router)
app.include_router(modelo_cnn.router)
app.include_router(diagnostico.router)


@app.get("/")
def read_root():
    return {"mensaje": "¡Backend estructurado profesionalmente!"}
