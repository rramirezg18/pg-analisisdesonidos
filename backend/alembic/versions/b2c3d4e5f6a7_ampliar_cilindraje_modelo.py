"""ampliar cilindrajes permitidos en modelo (155, 160, 180, 190)

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-10-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SQLite no permite ALTER sobre CHECK: batch mode recrea la tabla.
    with op.batch_alter_table("modelo") as batch_op:
        batch_op.drop_constraint("ck_modelo_cilindraje", type_="check")
        batch_op.create_check_constraint(
            "ck_modelo_cilindraje",
            "cilindraje IN (125, 150, 155, 160, 180, 190, 200)",
        )


def downgrade() -> None:
    with op.batch_alter_table("modelo") as batch_op:
        batch_op.drop_constraint("ck_modelo_cilindraje", type_="check")
        batch_op.create_check_constraint(
            "ck_modelo_cilindraje", "cilindraje IN (125, 150, 200)"
        )
