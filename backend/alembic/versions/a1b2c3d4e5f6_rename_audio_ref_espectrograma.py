"""renombrar audio_ref a espectrograma_ref

Revision ID: a1b2c3d4e5f6
Revises: 13c6d5cbb9f2
Create Date: 2026-08-19 04:10:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "13c6d5cbb9f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SQLite requiere batch mode para renombrar columnas.
    with op.batch_alter_table("diagnostico") as batch_op:
        batch_op.alter_column("audio_ref", new_column_name="espectrograma_ref")


def downgrade() -> None:
    with op.batch_alter_table("diagnostico") as batch_op:
        batch_op.alter_column("espectrograma_ref", new_column_name="audio_ref")
