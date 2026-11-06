"""Casos de prueba del panel de investigación (CU-07 y CU-08).

Los diagnósticos se insertan directo en la BD con una versión de CNN propia,
y las estadísticas se piden filtradas por esa versión: así los diagnósticos
que crean las otras pruebas no alteran los números esperados.
"""

from datetime import datetime, timezone

import pytest

from database import SessionLocal
from models.diagnostico import Diagnostico
from models.modelo_cnn import ModeloCNN

# (veredicto del mecánico, resultado del sistema, ¿notaba síntomas?)
# 10 casos, 8 coincidencias -> 80 % de exactitud.
CASOS = [
    ("grave", "anomalia", "si"),
    ("grave", "anomalia", "si"),
    ("grave", "anomalia", "no"),
    ("leve", "anomalia", "no"),
    ("leve", "anomalia", "no"),
    ("leve", "normal", "no"),
    ("leve", "normal", "si"),
    ("sano", "normal", "no"),
    ("sano", "normal", "no"),
    ("sano", "normal", None),
]


@pytest.fixture(scope="module")
def escenario():
    """Crea una versión de CNN y los 10 diagnósticos de CASOS (el último sin validar aún)."""
    db = SessionLocal()
    cnn = ModeloCNN(
        version="v-panel-pruebas",
        fecha_entrenamiento=datetime.now(timezone.utc),
        exactitud_validacion=90.0,
        archivo_pesos="x.keras",
        activo=0,
    )
    db.add(cnn)
    db.flush()
    ids = []
    for i, (veredicto, resultado, sintomas) in enumerate(CASOS):
        d = Diagnostico(
            id_usuario=1,
            id_modelo=1,
            id_modelo_cnn=cnn.id_modelo_cnn,
            anio=2020,
            espectrograma_ref="espectrogramas/x.png",
            resultado=resultado,
            confianza=70.0 + i,
            notaba_sintomas=sintomas,
            # El último queda pendiente: lo valida la prueba del veredicto.
            veredicto_mecanico=veredicto if i < len(CASOS) - 1 else None,
        )
        db.add(d)
        db.flush()
        ids.append(d.id_diagnostico)
    db.commit()
    id_cnn = cnn.id_modelo_cnn
    db.close()
    return {"id_cnn": id_cnn, "ids": ids}


def _stats(client, headers, id_cnn):
    r = client.get(f"/admin/estadisticas?id_modelo_cnn={id_cnn}", headers=headers)
    assert r.status_code == 200
    return r.json()


# ---------- Acceso ----------

@pytest.mark.cu("CU-07")
def test_cp11_panel_solo_admin(client, headers_a):
    """CP-11: un usuario normal recibe 403 en todos los endpoints de /admin."""
    assert client.get("/admin/estadisticas", headers=headers_a).status_code == 403
    assert client.get("/admin/diagnosticos", headers=headers_a).status_code == 403
    r = client.patch(
        "/admin/diagnosticos/1/veredicto",
        json={"veredicto_mecanico": "sano"},
        headers=headers_a,
    )
    assert r.status_code == 403


@pytest.mark.cu("CU-07")
def test_cp12_me_indica_admin(client, headers_a, headers_admin):
    """CP-12: /usuarios/me indica si el usuario es admin (para mostrar el panel)."""
    assert client.get("/usuarios/me", headers=headers_a).json()["es_admin"] is False
    assert client.get("/usuarios/me", headers=headers_admin).json()["es_admin"] is True


# ---------- Validación del mecánico ----------

@pytest.mark.cu("CU-08")
def test_cp13_registrar_veredicto(client, headers_admin, escenario):
    """CP-13: el admin registra el veredicto del mecánico y el caso deja de estar pendiente."""
    pendiente = escenario["ids"][-1]
    pendientes = client.get("/admin/diagnosticos?estado=pendientes", headers=headers_admin)
    assert pendiente in [d["id_diagnostico"] for d in pendientes.json()]

    r = client.patch(
        f"/admin/diagnosticos/{pendiente}/veredicto",
        json={"veredicto_mecanico": "sano"},
        headers=headers_admin,
    )
    assert r.status_code == 204

    validados = client.get("/admin/diagnosticos?estado=validados&limit=500", headers=headers_admin).json()
    caso = next(d for d in validados if d["id_diagnostico"] == pendiente)
    assert caso["veredicto_mecanico"] == "sano" and caso["fecha_validacion"] is not None
    assert caso["email_usuario"] == "a@test.com"


@pytest.mark.cu("CU-08")
def test_cp14_veredicto_invalido(client, headers_admin, escenario):
    """CP-14: un veredicto fuera de sano/leve/grave se rechaza con 422."""
    r = client.patch(
        f"/admin/diagnosticos/{escenario['ids'][0]}/veredicto",
        json={"veredicto_mecanico": "regular"},
        headers=headers_admin,
    )
    assert r.status_code == 422


# ---------- Encuesta del usuario ----------

@pytest.mark.cu("CU-08")
def test_cp15_encuesta_confianza(client, headers_a, headers_b, escenario):
    """CP-15: solo el dueño evalúa su diagnóstico, una sola vez y con valores 1..5."""
    ids = escenario["ids"]
    encuesta = {"confianza_antes": 2, "confianza_despues": 4, "ayudo_decidir": "si"}

    assert client.post(f"/diagnosticos/{ids[0]}/evaluacion", json=encuesta, headers=headers_b).status_code == 403
    assert client.post(
        f"/diagnosticos/{ids[0]}/evaluacion", json={**encuesta, "confianza_antes": 6}, headers=headers_a
    ).status_code == 422
    assert client.post(f"/diagnosticos/{ids[0]}/evaluacion", json=encuesta, headers=headers_a).status_code == 201
    assert client.post(f"/diagnosticos/{ids[0]}/evaluacion", json=encuesta, headers=headers_a).status_code == 409

    # Dos encuestas más: una sobre un acierto y otra sobre un fallo del sistema (caso 6).
    client.post(
        f"/diagnosticos/{ids[1]}/evaluacion",
        json={"confianza_antes": 3, "confianza_despues": 5, "ayudo_decidir": "parcial"},
        headers=headers_a,
    )
    client.post(
        f"/diagnosticos/{ids[5]}/evaluacion",
        json={"confianza_antes": 4, "confianza_despues": 2, "ayudo_decidir": "no"},
        headers=headers_a,
    )


# ---------- Estadísticas (OE1, OE2, OE3) ----------

@pytest.mark.cu("CU-07")
def test_cp16_estadisticas_objetivos(client, headers_admin, escenario):
    """CP-16: los números del panel coinciden con el escenario conocido."""
    s = _stats(client, headers_admin, escenario["id_cnn"])

    assert s["resumen"]["total_diagnosticos"] == 10
    assert s["resumen"]["validados"] == 10 and s["resumen"]["pendientes"] == 0

    # OE1: 8 de 10 coincidencias.
    ex = s["exactitud"]
    assert (ex["n"], ex["coincidencias"], ex["porcentaje"]) == (10, 8, 80.0)
    assert ex["matriz"] == {"vp": 5, "fn": 2, "fp": 0, "vn": 3}
    assert ex["precision"] == 1.0 and ex["sensibilidad"] == round(5 / 7, 3)
    assert ex["por_version"] == [
        {"version": "v-panel-pruebas", "exactitud_entrenamiento": 90.0, "n": 10, "porcentaje": 80.0}
    ]

    # OE2: detecta 2 de 4 leves y 3 de 3 graves; 3 de las 4 fallas que el dueño no notaba.
    dt = s["deteccion_temprana"]
    assert (dt["leve"]["n"], dt["leve"]["detectados"], dt["leve"]["porcentaje"]) == (4, 2, 50.0)
    assert (dt["grave"]["n"], dt["grave"]["detectados"], dt["grave"]["porcentaje"]) == (3, 3, 100.0)
    assert (dt["sin_sintomas"]["n"], dt["sin_sintomas"]["detectados"]) == (4, 3)

    # OE3: 3 encuestas registradas en CP-15.
    cu = s["confianza_usuario"]
    assert cu["n"] == 3
    assert cu["distribucion_antes"] == [0, 1, 1, 1, 0]
    assert cu["distribucion_despues"] == [0, 1, 0, 1, 1]
    assert cu["pct_alta_antes"] == 33.3 and cu["pct_alta_despues"] == 66.7
    assert (cu["ayudo_si"], cu["ayudo_parcial"], cu["ayudo_no"]) == (1, 1, 1)
    assert cu["promedio_despues_acierto"] == 4.5 and cu["promedio_despues_fallo"] == 2.0

    assert s["uso"]["por_cilindraje"] == [{"etiqueta": "150 cc", "n": 10}]


@pytest.mark.cu("CU-07")
def test_cp17_estadisticas_sin_datos(client, headers_admin):
    """CP-17: sin casos, los porcentajes salen en null (no hay división entre cero)."""
    s = _stats(client, headers_admin, 99999)
    assert s["resumen"]["total_diagnosticos"] == 0
    assert s["exactitud"]["porcentaje"] is None
    assert s["deteccion_temprana"]["leve"]["porcentaje"] is None
    assert s["confianza_usuario"]["promedio_antes"] is None


@pytest.mark.cu("CU-04")
def test_cp18_analizar_guarda_sintomas(client, headers_a, audio_wav, form_valido):
    """CP-18: la respuesta '¿notaba algo raro?' se guarda junto al diagnóstico."""
    r = client.post(
        "/diagnosticos/analizar",
        files={"audio": ("motor.wav", audio_wav, "audio/wav")},
        data={**form_valido, "notaba_sintomas": "no"},
        headers=headers_a,
    )
    assert r.status_code == 200
    assert r.json()["notaba_sintomas"] == "no"
