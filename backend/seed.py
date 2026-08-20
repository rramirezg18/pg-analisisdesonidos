"""Datos de catálogo (marcas, modelos y un modelo CNN base).

Reference data para que el frontend tenga opciones reales en los selects.
Idempotente: se puede correr varias veces sin duplicar.

Uso:  docker compose exec backend python seed.py
"""

from datetime import datetime, timezone

from database import SessionLocal
from models.marca import Marca
from models.modelo import Modelo
from models.modelo_cnn import ModeloCNN

MARCAS = ["Honda", "Yamaha", "Suzuki", "Bajaj"]

# (marca, nombre_modelo, cilindraje)
MODELOS = [
    ("Honda", "CG150", 150),
    ("Honda", "CB125F", 125),
    ("Yamaha", "YBR125", 125),
    ("Yamaha", "FZ150", 150),
    ("Suzuki", "GN125", 125),
    ("Bajaj", "Pulsar 200", 200),
]


def run() -> None:
    db = SessionLocal()
    try:
        marcas_por_nombre: dict[str, Marca] = {}
        for nombre in MARCAS:
            marca = db.query(Marca).filter(Marca.nombre == nombre).first()
            if marca is None:
                marca = Marca(nombre=nombre)
                db.add(marca)
                db.flush()
            marcas_por_nombre[nombre] = marca

        for nombre_marca, nombre_modelo, cc in MODELOS:
            marca = marcas_por_nombre[nombre_marca]
            existe = (
                db.query(Modelo)
                .filter(Modelo.id_marca == marca.id_marca, Modelo.nombre == nombre_modelo)
                .first()
            )
            if existe is None:
                db.add(
                    Modelo(id_marca=marca.id_marca, nombre=nombre_modelo, cilindraje=cc)
                )

        # Un modelo CNN base "activo" para que el flujo muestre la versión vigente.
        # exactitud/archivo son placeholders hasta que exista el entrenamiento real.
        if db.query(ModeloCNN).filter(ModeloCNN.activo == 1).first() is None:
            db.add(
                ModeloCNN(
                    version="v1.0",
                    fecha_entrenamiento=datetime.now(timezone.utc),
                    exactitud_validacion=0.0,
                    archivo_pesos="pendiente.keras",
                    descripcion="Modelo base pendiente de entrenamiento",
                    activo=1,
                )
            )

        db.commit()
        print("Seed OK:",
              db.query(Marca).count(), "marcas,",
              db.query(Modelo).count(), "modelos,",
              db.query(ModeloCNN).count(), "modelo_cnn")
    finally:
        db.close()


if __name__ == "__main__":
    run()
