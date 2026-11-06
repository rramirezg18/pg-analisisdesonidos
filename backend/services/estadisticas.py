"""Estadísticas del panel de investigación (preguntas OE1, OE2 y OE3 de la tesis).

Se traen las filas una sola vez y se agregan en Python: el volumen es de cientos
de diagnósticos, así que la claridad del cálculo pesa más que hacerlo en SQL.
"""

from collections import Counter
from datetime import date, datetime, time
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.diagnostico import Diagnostico
from models.evaluacion import EvaluacionUsuario
from models.modelo import Modelo
from models.modelo_cnn import ModeloCNN
from models.user import Usuario
from schemas.estadisticas import (
    ConfianzaUsuario,
    Conteo,
    DeteccionTemprana,
    Estadisticas,
    Exactitud,
    ExactitudVersion,
    GrupoDeteccion,
    MatrizConfusion,
    Resumen,
    Uso,
)


def _pct(parte: int, total: int) -> Optional[float]:
    return round(100 * parte / total, 1) if total else None


def _promedio(valores: list[float]) -> Optional[float]:
    return round(sum(valores) / len(valores), 2) if valores else None


def _ratio(num: int, den: int) -> Optional[float]:
    return round(num / den, 3) if den else None


def _coincide(diag: Diagnostico) -> bool:
    """El sistema acierta si coincide con el mecánico: sano <-> normal, leve/grave <-> anomalía."""
    real = "normal" if diag.veredicto_mecanico == "sano" else "anomalia"
    return diag.resultado == real


def _exactitud(validados: list, versiones: dict[int, ModeloCNN]) -> Exactitud:
    diags = [d for d, _, _ in validados]
    falla = [d for d in diags if d.veredicto_mecanico != "sano"]
    sanos = [d for d in diags if d.veredicto_mecanico == "sano"]
    vp = sum(d.resultado == "anomalia" for d in falla)
    fn = len(falla) - vp
    fp = sum(d.resultado == "anomalia" for d in sanos)
    vn = len(sanos) - fp
    coincidencias = vp + vn

    precision = _ratio(vp, vp + fp)
    sensibilidad = _ratio(vp, vp + fn)
    f1 = (
        round(2 * precision * sensibilidad / (precision + sensibilidad), 3)
        if precision and sensibilidad
        else None
    )

    por_version = []
    for id_cnn, cnn in sorted(versiones.items()):
        del_cnn = [d for d in diags if d.id_modelo_cnn == id_cnn]
        por_version.append(
            ExactitudVersion(
                version=cnn.version,
                exactitud_entrenamiento=cnn.exactitud_validacion,
                n=len(del_cnn),
                porcentaje=_pct(sum(_coincide(d) for d in del_cnn), len(del_cnn)),
            )
        )

    return Exactitud(
        n=len(diags),
        coincidencias=coincidencias,
        porcentaje=_pct(coincidencias, len(diags)),
        matriz=MatrizConfusion(vp=vp, fn=fn, fp=fp, vn=vn),
        precision=precision,
        sensibilidad=sensibilidad,
        especificidad=_ratio(vn, vn + fp),
        f1=f1,
        por_version=por_version,
    )


def _grupo(diags: list[Diagnostico]) -> GrupoDeteccion:
    detectados = sum(d.resultado == "anomalia" for d in diags)
    return GrupoDeteccion(
        n=len(diags),
        detectados=detectados,
        porcentaje=_pct(detectados, len(diags)),
        confianza_promedio=_promedio([d.confianza for d in diags]),
    )


def _deteccion_temprana(validados: list) -> DeteccionTemprana:
    diags = [d for d, _, _ in validados]
    return DeteccionTemprana(
        leve=_grupo([d for d in diags if d.veredicto_mecanico == "leve"]),
        grave=_grupo([d for d in diags if d.veredicto_mecanico == "grave"]),
        sin_sintomas=_grupo(
            [
                d
                for d in diags
                if d.veredicto_mecanico in ("leve", "grave") and d.notaba_sintomas == "no"
            ]
        ),
    )


def _confianza_usuario(filas: list) -> ConfianzaUsuario:
    con_eval = [(d, ev) for d, _, ev in filas if ev is not None]
    antes = [ev.confianza_antes for _, ev in con_eval]
    despues = [ev.confianza_despues for _, ev in con_eval]
    ayudo = Counter(ev.ayudo_decidir for _, ev in con_eval)
    validados = [(d, ev) for d, ev in con_eval if d.veredicto_mecanico is not None]

    return ConfianzaUsuario(
        n=len(con_eval),
        distribucion_antes=[antes.count(i) for i in range(1, 6)],
        distribucion_despues=[despues.count(i) for i in range(1, 6)],
        promedio_antes=_promedio(antes),
        promedio_despues=_promedio(despues),
        pct_alta_antes=_pct(sum(v >= 4 for v in antes), len(antes)),
        pct_alta_despues=_pct(sum(v >= 4 for v in despues), len(despues)),
        ayudo_si=ayudo["si"],
        ayudo_parcial=ayudo["parcial"],
        ayudo_no=ayudo["no"],
        promedio_despues_acierto=_promedio(
            [ev.confianza_despues for d, ev in validados if _coincide(d)]
        ),
        promedio_despues_fallo=_promedio(
            [ev.confianza_despues for d, ev in validados if not _coincide(d)]
        ),
    )


def _uso(filas: list) -> Uso:
    por_cc = Counter(cc for _, cc, _ in filas)
    por_mes = Counter(d.fecha_diagnostico.strftime("%Y-%m") for d, _, _ in filas)
    return Uso(
        por_cilindraje=[Conteo(etiqueta=f"{cc} cc", n=n) for cc, n in sorted(por_cc.items())],
        por_mes=[Conteo(etiqueta=mes, n=n) for mes, n in sorted(por_mes.items())],
    )


def calcular(
    db: Session,
    id_modelo_cnn: Optional[int] = None,
    desde: Optional[date] = None,
    hasta: Optional[date] = None,
) -> Estadisticas:
    q = (
        db.query(Diagnostico, Modelo.cilindraje, EvaluacionUsuario)
        .join(Modelo, Diagnostico.id_modelo == Modelo.id_modelo)
        .outerjoin(
            EvaluacionUsuario,
            EvaluacionUsuario.id_diagnostico == Diagnostico.id_diagnostico,
        )
    )
    if id_modelo_cnn is not None:
        q = q.filter(Diagnostico.id_modelo_cnn == id_modelo_cnn)
    if desde is not None:
        q = q.filter(Diagnostico.fecha_diagnostico >= datetime.combine(desde, time.min))
    if hasta is not None:
        q = q.filter(Diagnostico.fecha_diagnostico <= datetime.combine(hasta, time.max))
    filas = q.all()

    validados = [f for f in filas if f[0].veredicto_mecanico is not None]
    ids_cnn = {d.id_modelo_cnn for d, _, _ in validados}
    versiones = {
        c.id_modelo_cnn: c
        for c in db.query(ModeloCNN).filter(ModeloCNN.id_modelo_cnn.in_(ids_cnn))
    }

    return Estadisticas(
        resumen=Resumen(
            total_diagnosticos=len(filas),
            validados=len(validados),
            pendientes=len(filas) - len(validados),
            evaluaciones=sum(ev is not None for _, _, ev in filas),
            usuarios=db.query(func.count(Usuario.id_usuario)).scalar() or 0,
        ),
        exactitud=_exactitud(validados, versiones),
        deteccion_temprana=_deteccion_temprana(validados),
        confianza_usuario=_confianza_usuario(filas),
        uso=_uso(filas),
    )
