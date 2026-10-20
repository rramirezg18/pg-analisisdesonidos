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

MARCAS = [
    "Honda", "Yamaha", "Suzuki", "Bajaj", "TVS", "Hero", "Italika",
    "Haojue", "Keeway", "Kymco", "AKT",
]

# (marca, nombre_modelo, cilindraje)
# Modelos de 125 a 200 cc de uso común en Guatemala. El cilindraje es el nominal
# comercial (la BD admite 125, 150, 155, 160, 180, 190 o 200).
MODELOS = [
    ("Honda", "CG125", 125),
    ("Honda", "CB125F", 125),
    ("Honda", "XR125L", 125),
    ("Honda", "CG150", 150),
    ("Honda", "XR150L", 150),
    ("Honda", "CB160F", 160),
    ("Honda", "XR190L", 190),
    ("Honda", "CB190R", 190),
    ("Yamaha", "YBR125", 125),
    ("Yamaha", "XTZ125", 125),
    ("Yamaha", "FZ150", 150),
    ("Yamaha", "XTZ150", 150),
    ("Yamaha", "NMAX 155", 155),
    ("Yamaha", "R15", 155),
    ("Suzuki", "GN125", 125),
    ("Suzuki", "EN125", 125),
    ("Suzuki", "Gixxer 155", 155),
    ("Bajaj", "Discover 125", 125),
    ("Bajaj", "Boxer 150", 150),
    ("Bajaj", "Pulsar 150", 150),
    ("Bajaj", "Pulsar N160", 160),
    ("Bajaj", "Pulsar NS160", 160),
    ("Bajaj", "Pulsar 180", 180),
    ("Bajaj", "Pulsar 200", 200),
    ("Bajaj", "Pulsar NS200", 200),
    ("TVS", "Raider 125", 125),
    ("TVS", "Stryker 125", 125),
    ("TVS", "Apache RTR 150", 150),
    ("TVS", "Apache RTR 160 4V", 160),
    ("TVS", "Apache RTR 180", 180),
    ("TVS", "Apache RTR 200 4V", 200),
    ("Hero", "Glamour 125", 125),
    ("Hero", "Ignitor 125", 125),
    ("Hero", "Hunk 150", 150),
    ("Hero", "Hunk 160R", 160),
    ("Hero", "Xtreme 160R", 160),
    ("Hero", "Xpulse 200", 200),
    ("Italika", "FT125", 125),
    ("Italika", "FT150", 150),
    ("Italika", "DM150", 150),
    ("Italika", "DM200", 200),
    ("Italika", "Vort-X 200", 200),
    ("Haojue", "HJ125-7", 125),
    ("Haojue", "DK150", 150),
    ("Haojue", "NK150", 150),
    ("Haojue", "DR160", 160),
    ("Keeway", "RKS 150", 150),
    ("Keeway", "Superlight 200", 200),
    ("Kymco", "Agility 125", 125),
    ("Kymco", "Like 150i", 150),
    ("AKT", "NKD 125", 125),
    ("AKT", "CR4 125", 125),
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
