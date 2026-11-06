"""Pruebas no funcionales CP-NF-01 a CP-NF-05 (Tabla 20 del documento).

CP-NF-06 (compatibilidad con navegadores) es manual y no se automatiza aquí.
"""

import json
import os
import statistics
import time

import pytest

import utils.limite as limite
from conftest import generar_wav
from database import SQLALCHEMY_DATABASE_URL
from models.user import Usuario

REPETICIONES = int(os.getenv("PERF_REPETICIONES", "10"))
LIMITE_SEGUNDOS = 10.0  # RNF-01


@pytest.mark.cu("RNF-01")
@pytest.mark.parametrize("segundos_audio", [4, 10])
def test_cpnf01_rendimiento_diagnostico(client, headers_a, form_valido, tmp_dir, segundos_audio):
    """CP-NF-01: el diagnóstico responde en menos de 10 s (audios de 4 a 10 s)."""
    audio = generar_wav(segundos=segundos_audio)
    tiempos = []
    for _ in range(REPETICIONES):
        inicio = time.perf_counter()
        r = client.post(
            "/diagnosticos/analizar",
            headers=headers_a,
            data=form_valido,
            files={"audio": ("motor.wav", audio, "audio/wav")},
        )
        tiempos.append(time.perf_counter() - inicio)
        assert r.status_code == 200, r.text

    tiempos.sort()
    resumen = {
        "audio_segundos": segundos_audio,
        "repeticiones": REPETICIONES,
        "tiempos_s": [round(t, 3) for t in tiempos],
        "promedio_s": round(statistics.mean(tiempos), 3),
        "p95_s": round(tiempos[min(len(tiempos) - 1, int(0.95 * len(tiempos)))], 3),
        "max_s": round(max(tiempos), 3),
        "limite_s": LIMITE_SEGUNDOS,
    }
    destino = os.getenv("RESULTADOS_DIR")
    if destino:
        os.makedirs(destino, exist_ok=True)
        with open(os.path.join(destino, f"rendimiento_{segundos_audio}s.json"), "w") as f:
            json.dump(resumen, f, indent=2)

    assert max(tiempos) < LIMITE_SEGUNDOS


@pytest.mark.cu("RNF-05")
def test_cpnf02_no_se_almacena_audio_ni_contrasena(client, headers_a, audio_wav, form_valido, tmp_dir):
    """CP-NF-02: tras analizar solo quedan PNG en disco y el usuario no tiene contraseña."""
    r = client.post(
        "/diagnosticos/analizar",
        headers=headers_a,
        data=form_valido,
        files={"audio": ("motor.wav", audio_wav, "audio/wav")},
    )
    assert r.status_code == 200
    extensiones_audio = (".wav", ".mp3", ".m4a", ".ogg", ".webm")
    for raiz, _, archivos in os.walk(tmp_dir):
        for nombre in archivos:
            assert not nombre.lower().endswith(extensiones_audio), os.path.join(raiz, nombre)
    columnas = {c.name for c in Usuario.__table__.columns}
    assert not any("pass" in c or "contra" in c for c in columnas)


@pytest.mark.cu("RNF-06")
@pytest.mark.parametrize(
    "metodo,ruta",
    [
        ("get", "/usuarios/me"),
        ("get", "/diagnosticos/mis"),
        ("get", "/diagnosticos/1"),
        ("post", "/diagnosticos/analizar"),
        ("post", "/marcas"),
        ("post", "/modelos"),
        ("post", "/modelos-cnn"),
        ("patch", "/modelos-cnn/1/activar"),
    ],
)
def test_cpnf03_rutas_protegidas_exigen_token(client, metodo, ruta):
    """CP-NF-03: sin token (o sin clave de administración), las rutas protegidas responden 401/403."""
    r = getattr(client, metodo)(ruta)
    assert r.status_code in (401, 403)


@pytest.mark.cu("RNF-06")
def test_cpnf03_catalogo_exige_clave_admin(client, headers_a):
    """CP-NF-03: un usuario normal no altera el catálogo; con la clave de administración sí."""
    nueva = {"nombre": "Yamaha"}
    assert client.post("/marcas", json=nueva, headers=headers_a).status_code == 401
    assert client.post("/marcas", json=nueva, headers={"X-Admin-Key": "incorrecta"}).status_code == 403
    assert client.post("/marcas", json=nueva, headers={"X-Admin-Key": "clave-admin-pruebas"}).status_code == 201


@pytest.mark.cu("RNF-06")
@pytest.mark.parametrize("ruta", ["/docs", "/redoc", "/openapi.json"])
def test_cpnf03_documentacion_no_expuesta(client, ruta):
    """CP-NF-03: Swagger/OpenAPI no se publican salvo con HABILITAR_DOCS=true."""
    assert client.get(ruta).status_code == 404


@pytest.mark.cu("RNF-06")
def test_cpnf03_limite_de_analisis(client, headers_b, audio_wav, form_valido, monkeypatch):
    """CP-NF-03: superar el límite de análisis por minuto responde 429 sin correr el CNN."""
    monkeypatch.setattr(limite, "limite_analisis", limite.LimiteFrecuencia(maximo=2, ventana_s=60))
    codigos = [
        client.post(
            "/diagnosticos/analizar",
            headers=headers_b,
            data=form_valido,
            files={"audio": ("motor.wav", audio_wav, "audio/wav")},
        ).status_code
        for _ in range(3)
    ]
    assert codigos == [200, 200, 429]


@pytest.mark.cu("RNF-07")
def test_cpnf04_usuario_no_accede_a_datos_de_otro(client, headers_a):
    """CP-NF-04: el usuario A no puede leer los datos personales del usuario B."""
    r = client.get("/usuarios/2", headers=headers_a)
    assert r.status_code in (401, 403, 404), "GET /usuarios/{id} expone datos de otro usuario"
    lista = client.get("/usuarios")
    assert lista.status_code in (401, 403, 404), "GET /usuarios lista a todos los usuarios sin autenticación"


@pytest.mark.cu("RNF-14")
def test_cpnf05_base_de_datos_sin_servidor_dedicado():
    """CP-NF-05: la persistencia usa SQLite embebido (sin servidor de BD)."""
    assert SQLALCHEMY_DATABASE_URL.startswith("sqlite")
