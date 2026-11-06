"""Pruebas unitarias: funciones aisladas, sin HTTP.

El servicio CNN se construye sin cargar el modelo .keras (se usa un modelo falso
cuando hace falta), para probar solo la lógica de cada función.
"""

import io
import json
import os
from datetime import timedelta

import jwt
import numpy as np
import pytest
from PIL import Image
from pydantic import ValidationError

import services.diagnostico as service_diag
from conftest import generar_wav
from database import SessionLocal
from schemas.diagnostico import DiagnosticoCreate, DiagnosticoCreateIn
from services.cnn_service import AudioDemasiadoCorto, CNNService, _transcodificar_a_wav
from services.exceptions import NotFoundError
from utils.security import crear_token_acceso, decodificar_token, hash_token

CONFIG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "modelos", "model_config.json")


class ModeloFalso:
    """Sustituye al modelo Keras: devuelve siempre el valor indicado."""

    def __init__(self, valor):
        self.valor = valor

    def predict(self, entradas, verbose=0):
        return np.array([[self.valor]])


@pytest.fixture
def servicio():
    s = CNNService.__new__(CNNService)  # sin __init__: no carga TensorFlow/.keras
    s.config = json.load(open(CONFIG))
    s.mel_config = s.config["preprocesamiento_audio"]
    s.clases = s.config["clases"]
    s.input_shape = tuple(s.config["input_espectrograma"]["shape"])
    return s


# ---------- Servicio CNN: regla de clasificación ----------

@pytest.mark.unidad("CNNService.predecir")
@pytest.mark.parametrize(
    "raw,clase,confianza",
    [(0.9, "anomalia", 80.0), (0.1, "normal", 80.0), (0.5, "anomalia", 0.0), (1.0, "anomalia", 100.0), (0.0, "normal", 100.0)],
)
def test_ut01_regla_de_clasificacion(servicio, monkeypatch, raw, clase, confianza):
    """UT-01: umbral 0.5 y confianza = |raw - 0.5| * 200."""
    servicio.model = ModeloFalso(raw)
    monkeypatch.setattr(servicio, "_audio_a_espectrograma", lambda _: np.zeros((128, 173)))
    r = servicio.predecir(b"audio", 150)
    assert r["clase"] == clase
    assert r["confianza"] == pytest.approx(confianza)


@pytest.mark.unidad("CNNService._normalizar_cilindraje")
@pytest.mark.parametrize("cc,esperado", [(125, 0.0), (200, 1.0), (150, 1 / 3)])
def test_ut02_normalizacion_cilindraje(servicio, cc, esperado):
    """UT-02: cilindraje normalizado igual que en el entrenamiento: (cc - 125) / 75."""
    assert servicio._normalizar_cilindraje(cc) == pytest.approx(esperado)


# ---------- Servicio CNN: preprocesamiento ----------

@pytest.mark.unidad("CNNService._audio_a_espectrograma")
@pytest.mark.parametrize("segundos", [3.95, 4, 10])
def test_ut03_espectrograma_forma_y_rango(servicio, segundos):
    """UT-03: audios de 4 s o más (con el margen del codificador) dan la forma de la CNN, en [0, 1]."""
    mel = servicio._audio_a_espectrograma(generar_wav(segundos=segundos))
    assert mel.shape == servicio.input_shape[:2]
    assert mel.min() >= 0.0 and mel.max() <= 1.0


@pytest.mark.unidad("CNNService._audio_a_espectrograma")
def test_ut04_espectrograma_de_silencio(servicio):
    """UT-04: un audio en silencio no provoca división entre cero."""
    mel = servicio._audio_a_espectrograma(generar_wav(segundos=4, freq=0.0))
    assert not np.isnan(mel).any()


@pytest.mark.unidad("_transcodificar_a_wav")
def test_ut05_audio_corrupto(servicio):
    """UT-05: bytes que no son audio se rechazan con ValueError."""
    with pytest.raises(ValueError):
        _transcodificar_a_wav(b"esto no es un audio")


@pytest.mark.unidad("CNNService._audio_a_espectrograma")
@pytest.mark.parametrize("segundos", [1, 3.5])
def test_ut14_rechaza_audio_corto(servicio, segundos):
    """UT-14: un audio de menos de 4 s se rechaza en vez de rellenarse con silencio."""
    with pytest.raises(AudioDemasiadoCorto):
        servicio._audio_a_espectrograma(generar_wav(segundos=segundos))


@pytest.mark.unidad("CNNService._magma")
def test_ut06_colormap(servicio):
    """UT-06: el colormap respeta sus extremos y devuelve RGB de 8 bits."""
    rgb = servicio._magma(np.array([[0.0, 1.0]]))
    assert rgb.dtype == np.uint8 and rgb.shape == (1, 2, 3)
    assert tuple(rgb[0, 0]) == (0, 0, 4)
    assert tuple(rgb[0, 1]) == (252, 253, 191)


@pytest.mark.unidad("CNNService.generar_espectrograma_png")
def test_ut07_png_del_espectrograma(servicio, tmp_path):
    """UT-07: se genera un PNG válido de 256 px de alto."""
    destino = servicio.generar_espectrograma_png(generar_wav(segundos=4), str(tmp_path / "e.png"))
    img = Image.open(destino)
    assert img.format == "PNG" and img.height == 256


# ---------- Seguridad: JWT ----------

@pytest.mark.unidad("utils.security")
def test_ut08_token_ida_y_vuelta():
    """UT-08: el token firmado conserva el usuario (sub)."""
    assert decodificar_token(crear_token_acceso({"sub": "7"}))["sub"] == "7"


@pytest.mark.unidad("utils.security")
def test_ut09_token_expirado_o_alterado():
    """UT-09: un token expirado o con la firma alterada no se acepta."""
    with pytest.raises(jwt.ExpiredSignatureError):
        decodificar_token(crear_token_acceso({"sub": "7"}, expires_delta=timedelta(seconds=-1)))
    with pytest.raises(jwt.InvalidSignatureError):
        decodificar_token(crear_token_acceso({"sub": "7"})[:-2] + "xx")


@pytest.mark.unidad("utils.security")
def test_ut10_hash_token():
    """UT-10: el hash es determinista, SHA-256 en hexadecimal."""
    assert hash_token("abc") == hash_token("abc")
    assert len(hash_token("abc")) == 64 and hash_token("abc") != hash_token("abd")


# ---------- Validación de datos (schemas) ----------

VALIDO = dict(id_modelo=1, id_modelo_cnn=1, anio=2020, kilometraje=1000, espectrograma_ref="x.png", resultado="normal", confianza=50)


@pytest.mark.unidad("schemas.DiagnosticoCreateIn")
@pytest.mark.parametrize(
    "campo,valor",
    [("anio", 1979), ("anio", 2101), ("kilometraje", -1), ("confianza", 101), ("resultado", "dañado"), ("espectrograma_ref", "")],
)
def test_ut11_validacion_de_campos(campo, valor):
    """UT-11: valores fuera de rango o inválidos se rechazan."""
    with pytest.raises(ValidationError):
        DiagnosticoCreateIn(**{**VALIDO, campo: valor})


@pytest.mark.unidad("schemas.DiagnosticoCreateIn")
def test_ut12_datos_validos():
    """UT-12: los límites del rango se aceptan."""
    DiagnosticoCreateIn(**{**VALIDO, "anio": 1980, "kilometraje": 0, "confianza": 100})


# ---------- Servicio de diagnóstico ----------

@pytest.mark.unidad("services.diagnostico.crear")
@pytest.mark.parametrize("campo", ["id_usuario", "id_modelo", "id_modelo_cnn"])
def test_ut13_crear_con_referencia_inexistente(campo):
    """UT-13: crear un diagnóstico con usuario/modelo/CNN inexistente da NotFoundError (404), no error de BD."""
    db = SessionLocal()
    try:
        datos = DiagnosticoCreate(**{**VALIDO, "id_usuario": 1, campo: 9999})
        with pytest.raises(NotFoundError):
            service_diag.crear(db, datos)
    finally:
        db.close()
