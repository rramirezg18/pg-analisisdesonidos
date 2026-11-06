"""Casos de prueba funcionales CP-01 a CP-10 (Tabla 16 del documento)."""

import os
import types
from datetime import timedelta
from urllib.parse import parse_qs, urlparse

import httpx
import pytest

import routers.auth as auth_router
from conftest import generar_wav
from utils.security import crear_token_acceso


# ---------- CU-01: Consultar información pública ----------

@pytest.mark.cu("CU-01")
def test_cp01_consulta_publica_sin_autenticacion(client):
    """CP-01: el catálogo de marcas y modelos es accesible sin token."""
    marcas = client.get("/marcas")
    modelos = client.get("/modelos")
    assert marcas.status_code == 200 and len(marcas.json()) > 0
    assert modelos.status_code == 200 and len(modelos.json()) > 0


# ---------- CU-02: Iniciar sesión (OAuth 2.0) ----------

def _github_falso(request: httpx.Request) -> httpx.Response:
    """Simula las respuestas de GitHub (token, perfil y correos)."""
    if request.url.path == "/login/oauth/access_token":
        return httpx.Response(200, json={"access_token": "gho_falso"})
    if request.url.path == "/user":
        return httpx.Response(200, json={"id": 999, "login": "tester", "name": "Tester", "email": "tester@test.com"})
    return httpx.Response(200, json=[])


@pytest.mark.cu("CU-02")
def test_cp02_login_github_oauth(client, monkeypatch):
    """CP-02: login con GitHub -> redirección con state, callback y JWT válido."""
    inicio = client.get("/auth/github/login", follow_redirects=False)
    assert inicio.status_code in (302, 307)
    assert inicio.headers["location"].startswith("https://github.com/login/oauth/authorize")
    state = parse_qs(urlparse(inicio.headers["location"]).query)["state"][0]
    assert inicio.cookies.get("oauth_state") == state

    # Solo se reemplaza el httpx que usa el router (no el del TestClient).
    monkeypatch.setattr(
        auth_router,
        "httpx",
        types.SimpleNamespace(Client=lambda **kw: httpx.Client(transport=httpx.MockTransport(_github_falso))),
    )
    callback = client.get(
        f"/auth/github/callback?code=abc&state={state}",
        headers={"Cookie": f"oauth_state={state}"},
        follow_redirects=False,
    )
    assert callback.status_code in (302, 307)
    destino = urlparse(callback.headers["location"])
    assert destino.path == "/auth/callback"
    # El token viaja en el fragmento (#), no en la query: no llega a los logs.
    assert "token" not in parse_qs(destino.query)
    token = parse_qs(destino.fragment)["token"][0]

    yo = client.get("/usuarios/me", headers={"Authorization": f"Bearer {token}"})
    assert yo.status_code == 200
    assert yo.json()["email"] == "tester@test.com"


@pytest.mark.cu("CU-02")
def test_cp03_rechazo_state_invalido(client):
    """CP-03: un callback con state distinto al de la cookie se rechaza (anti-CSRF)."""
    r = client.get(
        "/auth/github/callback?code=abc&state=manipulado",
        headers={"Cookie": "oauth_state=original"},
        follow_redirects=False,
    )
    assert r.status_code == 400


# ---------- CU-03: Cerrar sesión ----------

@pytest.mark.cu("CU-03")
def test_cp04_token_expirado_o_alterado_es_rechazado(client):
    """CP-04: tras cerrar sesión el token deja de servir.

    El cierre de sesión borra el token del navegador; en el servidor se verifica
    que un token expirado o alterado ya no da acceso.
    """
    expirado = crear_token_acceso({"sub": "1"}, expires_delta=timedelta(seconds=-1))
    r1 = client.get("/usuarios/me", headers={"Authorization": f"Bearer {expirado}"})
    r2 = client.get("/usuarios/me", headers={"Authorization": f"Bearer {expirado}x"})
    assert r1.status_code == 401
    assert r2.status_code == 401


# ---------- CU-04: Realizar diagnóstico ----------

@pytest.mark.cu("CU-04")
def test_cp05_registro_diagnostico_valido(client, headers_a, audio_wav, form_valido, tmp_dir):
    """CP-05: audio + datos válidos -> resultado del CNN, PNG generado y fila guardada."""
    r = client.post(
        "/diagnosticos/analizar",
        headers=headers_a,
        data=form_valido,
        files={"audio": ("motor.wav", audio_wav, "audio/wav")},
    )
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["resultado"] in ("normal", "anomalia")
    assert 0 <= d["confianza"] <= 100
    assert d["marca"] == "Honda" and d["modelo"] == "CG150" and d["cilindraje"] == 150
    assert os.path.isfile(os.path.join(tmp_dir, "data", d["espectrograma_ref"]))
    assert client.get(f"/media/{d['espectrograma_ref']}").status_code == 200


@pytest.mark.cu("CU-04")
def test_cp06_rechazo_formato_no_soportado(client, headers_a, form_valido):
    """CP-06: un archivo que no es audio se rechaza con 400."""
    r = client.post(
        "/diagnosticos/analizar",
        headers=headers_a,
        data=form_valido,
        files={"audio": ("documento.txt", b"esto no es audio", "text/plain")},
    )
    assert r.status_code == 400


@pytest.mark.cu("CU-04")
@pytest.mark.parametrize("segundos", [1, 3.5])
def test_cp06_rechazo_audio_corto(client, headers_a, form_valido, segundos):
    """CP-06: un audio de menos de 4 s se rechaza con 400 y un mensaje claro."""
    r = client.post(
        "/diagnosticos/analizar",
        headers=headers_a,
        data=form_valido,
        files={"audio": ("corto.wav", generar_wav(segundos=segundos), "audio/wav")},
    )
    assert r.status_code == 400
    assert "al menos 4 s" in r.json()["detail"]


@pytest.mark.cu("CU-04")
@pytest.mark.parametrize(
    "campo,valor",
    [("anio", "1800"), ("anio", "2500"), ("kilometraje", "-10")],
)
def test_cp07_rechazo_datos_fuera_de_rango(client, headers_a, audio_wav, form_valido, campo, valor):
    """CP-07: año o kilometraje fuera de rango -> error de validación (4xx), no 500."""
    datos = {**form_valido, campo: valor}
    r = client.post(
        "/diagnosticos/analizar",
        headers=headers_a,
        data=datos,
        files={"audio": ("motor.wav", audio_wav, "audio/wav")},
    )
    assert r.status_code in (400, 422), f"{campo}={valor} devolvió {r.status_code}"


# ---------- CU-05: Consultar historial ----------

@pytest.mark.cu("CU-05")
def test_cp08_historial_propio(client, headers_a, headers_b, audio_wav, form_valido):
    """CP-08: el historial solo contiene diagnósticos del usuario autenticado."""
    client.post(
        "/diagnosticos/analizar",
        headers=headers_b,
        data=form_valido,
        files={"audio": ("motor.wav", audio_wav, "audio/wav")},
    )
    hist_a = client.get("/diagnosticos/mis", headers=headers_a)
    hist_b = client.get("/diagnosticos/mis", headers=headers_b)
    assert hist_a.status_code == 200 and hist_b.status_code == 200
    assert len(hist_a.json()) >= 1 and len(hist_b.json()) >= 1
    assert all(d["id_usuario"] == 1 for d in hist_a.json())
    assert all(d["id_usuario"] == 2 for d in hist_b.json())


# ---------- CU-06: Ver detalle ----------

@pytest.mark.cu("CU-06")
def test_cp09_detalle_propio(client, headers_a):
    """CP-09: el usuario ve el detalle completo de su diagnóstico."""
    propio = client.get("/diagnosticos/mis", headers=headers_a).json()[0]
    r = client.get(f"/diagnosticos/{propio['id_diagnostico']}", headers=headers_a)
    assert r.status_code == 200
    assert r.json()["id_diagnostico"] == propio["id_diagnostico"]
    assert {"marca", "modelo", "cilindraje", "resultado", "confianza", "espectrograma_ref"} <= r.json().keys()


@pytest.mark.cu("CU-06")
def test_cp10_bloqueo_diagnostico_ajeno(client, headers_a, headers_b):
    """CP-10: el usuario A no puede ver un diagnóstico del usuario B."""
    ajeno = client.get("/diagnosticos/mis", headers=headers_b).json()[0]
    r = client.get(f"/diagnosticos/{ajeno['id_diagnostico']}", headers=headers_a)
    assert r.status_code == 403
    assert "resultado" not in r.json()
