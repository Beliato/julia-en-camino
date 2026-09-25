"""placeholders del rsvp

Revision ID: b8c9d0e1f2a3
Revises: a7b8c9d0e1f2
Create Date: 2026-09-25

Agrega los tres ejemplos en gris del formulario de confirmacion, uno por
campo de texto. El desplegable de asistencia no lleva porque sus opciones
ya son las etiquetas.

Van nullable y sin default: nulo significa "usa el de la app", que es lo
que ya veian todas las invitaciones existentes. Asi ninguna cambia de
aspecto al aplicar esta migracion, y el default vive en un solo lugar
—el frontend— en vez de quedar copiado en cada fila de la base.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b8c9d0e1f2a3"
down_revision: Union[str, None] = "a7b8c9d0e1f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

COLUMNAS = ("placeholder_nombre", "placeholder_cantidad", "placeholder_comentario")


def upgrade() -> None:
    for columna in COLUMNAS:
        op.add_column(
            "invitaciones", sa.Column(columna, sa.String(length=150), nullable=True)
        )


def downgrade() -> None:
    for columna in COLUMNAS:
        op.drop_column("invitaciones", columna)
