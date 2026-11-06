from typing import Optional

from pydantic import BaseModel


# Respuesta del panel de investigación. Los porcentajes van de 0 a 100 y son
# None cuando todavía no hay casos para calcularlos (n = 0).


class Resumen(BaseModel):
    total_diagnosticos: int
    validados: int
    pendientes: int
    evaluaciones: int
    usuarios: int


# Matriz de confusión con "anomalía" como clase positiva.
class MatrizConfusion(BaseModel):
    vp: int  # mecánico: falla   / sistema: anomalía
    fn: int  # mecánico: falla   / sistema: normal
    fp: int  # mecánico: sano    / sistema: anomalía
    vn: int  # mecánico: sano    / sistema: normal


class ExactitudVersion(BaseModel):
    version: str
    exactitud_entrenamiento: float
    n: int
    porcentaje: Optional[float]


# OE1: coincidencias entre el sistema y el mecánico.
class Exactitud(BaseModel):
    n: int
    coincidencias: int
    porcentaje: Optional[float]
    matriz: MatrizConfusion
    precision: Optional[float]
    sensibilidad: Optional[float]  # recall
    especificidad: Optional[float]
    f1: Optional[float]
    por_version: list[ExactitudVersion]


class GrupoDeteccion(BaseModel):
    n: int
    detectados: int
    porcentaje: Optional[float]
    confianza_promedio: Optional[float]  # confianza del modelo en esos casos


# OE2: ¿detecta los problemas leves igual que los graves?
class DeteccionTemprana(BaseModel):
    leve: GrupoDeteccion
    grave: GrupoDeteccion
    # Casos con falla real en los que el usuario NO notaba nada raro.
    sin_sintomas: GrupoDeteccion


# OE3: confianza del usuario antes (solo mecánico) y después (con el sistema).
class ConfianzaUsuario(BaseModel):
    n: int
    distribucion_antes: list[int]  # conteo de respuestas 1..5
    distribucion_despues: list[int]
    promedio_antes: Optional[float]
    promedio_despues: Optional[float]
    pct_alta_antes: Optional[float]  # % que respondió 4 o 5
    pct_alta_despues: Optional[float]
    ayudo_si: int
    ayudo_parcial: int
    ayudo_no: int
    promedio_despues_acierto: Optional[float]
    promedio_despues_fallo: Optional[float]


class Conteo(BaseModel):
    etiqueta: str
    n: int


class Uso(BaseModel):
    por_cilindraje: list[Conteo]
    por_mes: list[Conteo]


class Estadisticas(BaseModel):
    resumen: Resumen
    exactitud: Exactitud
    deteccion_temprana: DeteccionTemprana
    confianza_usuario: ConfianzaUsuario
    uso: Uso
