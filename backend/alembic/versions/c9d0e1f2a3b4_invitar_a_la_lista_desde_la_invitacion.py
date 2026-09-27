"""invitar a la lista desde la invitacion

Revision ID: c9d0e1f2a3b4
Revises: b8c9d0e1f2a3
Create Date: 2026-09-27

Agrega invitaciones.texto_regalos: el parrafo que invita a mirar la lista
de regalos, al pie de la pagina de la invitacion.

Nullable y sin default. Nulo no es "falta el dato": es "esta invitacion
no menciona la lista", que era el comportamiento hasta ahora y el que
conservan todas las filas existentes. Ademas hace de interruptor del
bloque entero, incluido el boton que lleva a la lista.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c9d0e1f2a3b4"
down_revision: Union[str, None] = "b8c9d0e1f2a3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "invitaciones", sa.Column("texto_regalos", sa.String(length=500), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("invitaciones", "texto_regalos")
