from fastapi import HTTPException, Request, status

from services.cnn_service import CNNService


def get_cnn_service(request: Request) -> CNNService:
    """Inyecta el CNNService cargado en el lifespan (singleton en app.state)."""
    servicio: CNNService | None = getattr(request.app.state, "cnn_service", None)
    if servicio is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El modelo CNN no está disponible.",
        )
    return servicio
