"""Límite de frecuencia (rate limiting) del análisis, que es costoso en CPU.

Ventana deslizante en memoria por usuario. Basta para un único proceso de
uvicorn, que es como se despliega la app; con varios workers haría falta Redis.
"""

import os
import threading
import time
from collections import defaultdict, deque

from fastapi import Depends, HTTPException, status

from models.user import Usuario
from utils.auth import get_current_user


class LimiteFrecuencia:
    def __init__(self, maximo: int, ventana_s: float):
        self.maximo = maximo
        self.ventana_s = ventana_s
        self._eventos: dict[int, deque] = defaultdict(deque)
        self._lock = threading.Lock()

    def registrar(self, clave: int) -> None:
        """Cuenta un evento para `clave`. Lanza 429 si ya alcanzó el máximo."""
        ahora = time.monotonic()
        with self._lock:
            eventos = self._eventos[clave]
            while eventos and ahora - eventos[0] >= self.ventana_s:
                eventos.popleft()
            if len(eventos) >= self.maximo:
                espera = int(self.ventana_s - (ahora - eventos[0])) + 1
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Demasiados análisis seguidos. Intenta de nuevo en {espera} s.",
                    headers={"Retry-After": str(espera)},
                )
            eventos.append(ahora)


limite_analisis = LimiteFrecuencia(
    maximo=int(os.getenv("ANALISIS_POR_MINUTO", "10")), ventana_s=60
)


def limitar_analisis(current: Usuario = Depends(get_current_user)) -> Usuario:
    """Autentica al usuario y cuenta un análisis contra su límite por minuto."""
    limite_analisis.registrar(current.id_usuario)
    return current
