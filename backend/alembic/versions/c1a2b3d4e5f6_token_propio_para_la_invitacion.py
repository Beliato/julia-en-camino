"""token propio para la invitacion

Revision ID: c1a2b3d4e5f6
Revises: 7670faff6838
Create Date: 2026-08-29

La columna se agrega en tres pasos y no de una: la fila de config ya
existe en produccion, asi que hay que darle un token antes de exigir que
no sea nulo. gen_random_uuid() es volatil, de modo que el UPDATE genera
uno distinto por fila.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c1a2b3d4e5f6"
down_revision: Union[str, None] = "7670faff6838"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "wishlist_config",
        sa.Column("invitacion_token", sa.String(length=36), nullable=True),
    )
    op.execute(
        "UPDATE wishlist_config "
        "SET invitacion_token = gen_random_uuid()::text "
        "WHERE invitacion_token IS NULL"
    )
    op.alter_column("wishlist_config", "invitacion_token", nullable=False)
    op.create_unique_constraint(
        "uq_wishlist_config_invitacion_token",
        "wishlist_config",
        ["invitacion_token"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_wishlist_config_invitacion_token", "wishlist_config", type_="unique"
    )
    op.drop_column("wishlist_config", "invitacion_token")
