"""cantidad de personas en el rsvp

Revision ID: 1f737b6d04c9
Revises: 30cb19986102
Create Date: 2026-08-30 07:59:14.270771

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1f737b6d04c9"
down_revision: Union[str, None] = "30cb19986102"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # server_default para las invitaciones que ya existen: sin el,
    # agregar una columna not null sobre filas cargadas falla. Se quita
    # despues para que el valor lo ponga el modelo y no la base.
    op.add_column(
        "invitaciones",
        sa.Column(
            "pide_cantidad",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.alter_column("invitaciones", "pide_cantidad", server_default=None)
    op.add_column("rsvps", sa.Column("cantidad", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("rsvps", "cantidad")
    op.drop_column("invitaciones", "pide_cantidad")
