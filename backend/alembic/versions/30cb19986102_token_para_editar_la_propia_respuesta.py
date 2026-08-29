"""token para editar la propia respuesta

Revision ID: 30cb19986102
Revises: d2e3f4a5b6c7
Create Date: 2026-08-29

Tres pasos y no uno: puede haber respuestas cargadas, asi que primero se
crea la columna nullable, despues se le da un token distinto a cada fila
—gen_random_uuid() es volatil, de modo que el UPDATE no repite— y recien
entonces se exige not null y unico.

La constraint va con nombre explicito: sin el, el downgrade no tiene como
referenciarla.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "30cb19986102"
down_revision: Union[str, None] = "d2e3f4a5b6c7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "rsvps", sa.Column("token_edicion", sa.String(length=36), nullable=True)
    )
    op.execute(
        "UPDATE rsvps SET token_edicion = gen_random_uuid()::text "
        "WHERE token_edicion IS NULL"
    )
    op.alter_column("rsvps", "token_edicion", nullable=False)
    op.create_unique_constraint("uq_rsvps_token_edicion", "rsvps", ["token_edicion"])


def downgrade() -> None:
    op.drop_constraint("uq_rsvps_token_edicion", "rsvps", type_="unique")
    op.drop_column("rsvps", "token_edicion")
