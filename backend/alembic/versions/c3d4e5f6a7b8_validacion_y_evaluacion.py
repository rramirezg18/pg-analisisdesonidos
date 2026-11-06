"""veredicto del mecánico en diagnostico + tabla evaluacion_usuario

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-11-05 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SQLite: batch mode para poder agregar los CHECK.
    with op.batch_alter_table("diagnostico") as batch_op:
        batch_op.add_column(sa.Column("notaba_sintomas", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("veredicto_mecanico", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("fecha_validacion", sa.DateTime(), nullable=True))
        batch_op.create_check_constraint(
            "ck_diagnostico_notaba_sintomas",
            "notaba_sintomas IS NULL OR notaba_sintomas IN ('si', 'no')",
        )
        batch_op.create_check_constraint(
            "ck_diagnostico_veredicto",
            "veredicto_mecanico IS NULL OR veredicto_mecanico IN ('sano', 'leve', 'grave')",
        )

    op.create_table(
        "evaluacion_usuario",
        sa.Column("id_evaluacion", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("id_diagnostico", sa.Integer(), nullable=False),
        sa.Column("confianza_antes", sa.Integer(), nullable=False),
        sa.Column("confianza_despues", sa.Integer(), nullable=False),
        sa.Column("ayudo_decidir", sa.Text(), nullable=False),
        sa.Column(
            "fecha_evaluacion",
            sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "confianza_antes BETWEEN 1 AND 5", name="ck_evaluacion_confianza_antes"
        ),
        sa.CheckConstraint(
            "confianza_despues BETWEEN 1 AND 5", name="ck_evaluacion_confianza_despues"
        ),
        sa.CheckConstraint(
            "ayudo_decidir IN ('si', 'parcial', 'no')", name="ck_evaluacion_ayudo"
        ),
        sa.ForeignKeyConstraint(
            ["id_diagnostico"], ["diagnostico.id_diagnostico"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id_evaluacion"),
        sa.UniqueConstraint("id_diagnostico"),
    )


def downgrade() -> None:
    op.drop_table("evaluacion_usuario")
    with op.batch_alter_table("diagnostico") as batch_op:
        batch_op.drop_constraint("ck_diagnostico_veredicto", type_="check")
        batch_op.drop_constraint("ck_diagnostico_notaba_sintomas", type_="check")
        batch_op.drop_column("fecha_validacion")
        batch_op.drop_column("veredicto_mecanico")
        batch_op.drop_column("notaba_sintomas")
