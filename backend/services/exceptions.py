"""Excepciones de dominio.

Los services las lanzan sin saber nada de HTTP; el router las traduce a
códigos de estado (404, 409, etc.).
"""


class ServiceError(Exception):
    pass


class NotFoundError(ServiceError):
    """La entidad solicitada no existe."""


class ConflictError(ServiceError):
    """Viola una regla de unicidad o integridad."""
