"""Fixtures compartidas de las pruebas.

Las pruebas corren contra una BD SQLite TEMPORAL y una carpeta de media temporal,
nunca contra la base de producción. El modelo CNN es el real (backend/modelos).
"""

import io
import math
import os
import struct
import sys
import tempfile
import wave
from datetime import datetime, timezone

import pytest

# Las variables de entorno deben fijarse ANTES de importar la app,
# porque database.py y los routers las leen al importarse.
_TMP = tempfile.mkdtemp(prefix="motorscan_test_")
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP}/test.db"
os.environ["MEDIA_DIR"] = f"{_TMP}/data"
os.environ["ESPECTROGRAMAS_DIR"] = f"{_TMP}/data/espectrogramas"
os.environ["SECRET_KEY"] = "clave-solo-para-pruebas"
os.environ["FRONTEND_URL"] = "http://frontend.test"
os.environ["ADMIN_API_KEY"] = "clave-admin-pruebas"
os.environ["ADMIN_EMAILS"] = "admin@test.com"
os.environ["HABILITAR_DOCS"] = "false"
# Límite alto: CP-NF-01 hace 20 análisis seguidos con el mismo usuario.
os.environ["ANALISIS_POR_MINUTO"] = "1000"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient  # noqa: E402

from database import Base, SessionLocal, engine  # noqa: E402
from main import app  # noqa: E402
from models.marca import Marca  # noqa: E402
from models.modelo import Modelo  # noqa: E402
from models.modelo_cnn import ModeloCNN  # noqa: E402
from models.user import Usuario  # noqa: E402
from utils.security import crear_token_acceso  # noqa: E402


@pytest.fixture(scope="session")
def tmp_dir():
    return _TMP


@pytest.fixture(scope="session", autouse=True)
def datos_base():
    """Crea el esquema y el catálogo mínimo: 1 marca, 1 modelo, CNN activo, 2 usuarios y 1 admin."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    marca = Marca(nombre="Honda")
    db.add(marca)
    db.flush()
    db.add(Modelo(id_marca=marca.id_marca, nombre="CG150", cilindraje=150))
    db.add(
        ModeloCNN(
            version="v1.0-sintetico",
            fecha_entrenamiento=datetime.now(timezone.utc),
            exactitud_validacion=0.0,
            archivo_pesos="modelo_cnn_v1.keras",
            activo=1,
        )
    )
    db.add(Usuario(proveedor_oauth="github", id_externo_proveedor="1", email="a@test.com", nombre="Usuario A"))
    db.add(Usuario(proveedor_oauth="github", id_externo_proveedor="2", email="b@test.com", nombre="Usuario B"))
    db.add(Usuario(proveedor_oauth="google", id_externo_proveedor="3", email="admin@test.com", nombre="Admin"))
    db.commit()
    db.close()
    yield


@pytest.fixture(scope="session")
def client():
    # El context manager ejecuta el lifespan -> carga el modelo CNN real.
    with TestClient(app) as c:
        yield c


def _headers(id_usuario: int) -> dict:
    return {"Authorization": f"Bearer {crear_token_acceso({'sub': str(id_usuario)})}"}


@pytest.fixture
def headers_a():
    return _headers(1)


@pytest.fixture
def headers_b():
    return _headers(2)


@pytest.fixture
def headers_admin():
    return _headers(3)


def generar_wav(segundos: float = 4.0, sr: int = 22050, freq: float = 120.0) -> bytes:
    """WAV mono 16 bits: tono base + armónicos, imitando un motor en ralentí."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        muestras = bytearray()
        for i in range(int(segundos * sr)):
            t = i / sr
            v = 0.5 * math.sin(2 * math.pi * freq * t) + 0.25 * math.sin(2 * math.pi * 2 * freq * t)
            muestras += struct.pack("<h", int(v * 32767 * 0.8))
        w.writeframes(bytes(muestras))
    return buf.getvalue()


@pytest.fixture(scope="session")
def audio_wav():
    return generar_wav()


@pytest.fixture
def form_valido():
    return {"id_modelo": "1", "anio": "2020", "kilometraje": "15000", "notas": "prueba"}
