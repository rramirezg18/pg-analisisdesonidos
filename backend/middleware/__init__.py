import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger("app")


def setup_middlewares(app: FastAPI, cors_origins: list[str]) -> None:
    """Registra los middlewares de la aplicación."""

    # CORS: permite que el frontend (otro origen en desarrollo) consuma la API.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Middleware propio: mide el tiempo de cada request y lo registra.
    @app.middleware("http")
    async def registrar_tiempo(request: Request, call_next):
        inicio = time.perf_counter()
        response = await call_next(request)
        duracion_ms = (time.perf_counter() - inicio) * 1000
        response.headers["X-Process-Time-ms"] = f"{duracion_ms:.2f}"
        logger.info(
            "%s %s -> %s (%.2f ms)",
            request.method,
            request.url.path,
            response.status_code,
            duracion_ms,
        )
        return response
