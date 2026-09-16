"""devolucion de prestamos

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-09-15

Agrega regalos.devuelto_en: la fecha en que le devolvimos el objeto a
quien lo presto. Nulo mientras siga en casa.

Va nullable y sin default a proposito. Nulo no es "falta el dato": es el
estado normal de todo lo que todavia no se devolvio, y de todo lo que no
es un prestamo. Un booleano "devuelto" habria perdido la fecha, que es lo
unico que despues sirve para saber cuanto hace que lo tenemos.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f6a7b8c9d0e1"
down_revision: Union[str, None] = "e5f6a7b8c9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("regalos", sa.Column("devuelto_en", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("regalos", "devuelto_en")
