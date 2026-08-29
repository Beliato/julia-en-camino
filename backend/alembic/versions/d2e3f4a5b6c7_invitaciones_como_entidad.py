"""invitaciones como entidad propia

Revision ID: d2e3f4a5b6c7
Revises: 80a44b49d94f
Create Date: 2026-08-29

La invitacion vivia dentro de wishlist_config, o sea que solo podia
existir una. Se mueve a su propia tabla para poder tener varias.

Lo delicado es no romper lo que ya esta afuera: si el link se compartio,
esa URL tiene que seguir funcionando. Por eso la primera fila hereda el
token y los datos que ya tenia la config, en vez de arrancar de cero. Y
las confirmaciones existentes se cuelgan de esa misma fila antes de que
la columna pase a obligatoria.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d2e3f4a5b6c7"
down_revision: Union[str, None] = "80a44b49d94f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_CAMPOS = ("lugar", "fecha", "hora", "texto", "aviso")


def upgrade() -> None:
    op.create_table(
        "invitaciones",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("token", sa.String(length=36), nullable=False),
        sa.Column("titulo", sa.String(length=150), nullable=False),
        sa.Column("lugar", sa.String(length=255), nullable=True),
        sa.Column("fecha", sa.String(length=100), nullable=True),
        sa.Column("hora", sa.String(length=100), nullable=True),
        sa.Column("texto", sa.String(length=500), nullable=True),
        sa.Column("aviso", sa.String(length=500), nullable=True),
        sa.Column("imagen_url", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token"),
    )

    # La invitación que ya existía se muda con su token intacto.
    columnas = ", ".join(_CAMPOS)
    origen = ", ".join(f"evento_{c}" for c in _CAMPOS)
    op.execute(
        f"INSERT INTO invitaciones (token, titulo, {columnas}, created_at) "
        f"SELECT invitacion_token, 'Baby shower', {origen}, NOW() "
        "FROM wishlist_config"
    )

    op.add_column("rsvps", sa.Column("invitacion_id", sa.Integer(), nullable=True))
    op.add_column("rsvps", sa.Column("comentario", sa.Text(), nullable=True))
    # Las confirmaciones que ya estaban son de esa única invitación.
    op.execute(
        "UPDATE rsvps SET invitacion_id = (SELECT MIN(id) FROM invitaciones) "
        "WHERE invitacion_id IS NULL"
    )
    # Si no habia ninguna invitacion, tampoco puede haber rsvps: el
    # DELETE es una red por si quedo alguno huerfano de pruebas.
    op.execute("DELETE FROM rsvps WHERE invitacion_id IS NULL")
    op.alter_column("rsvps", "invitacion_id", nullable=False)
    op.create_index("ix_rsvps_invitacion_id", "rsvps", ["invitacion_id"])
    op.create_foreign_key(
        "fk_rsvps_invitacion",
        "rsvps",
        "invitaciones",
        ["invitacion_id"],
        ["id"],
        ondelete="CASCADE",
    )

    for campo in _CAMPOS:
        op.drop_column("wishlist_config", f"evento_{campo}")
    op.drop_column("wishlist_config", "invitacion_token")


def downgrade() -> None:
    op.add_column(
        "wishlist_config",
        sa.Column("invitacion_token", sa.String(length=36), nullable=True),
    )
    for campo, largo in (
        ("lugar", 255),
        ("fecha", 100),
        ("hora", 100),
        ("texto", 500),
        ("aviso", 500),
    ):
        op.add_column(
            "wishlist_config",
            sa.Column(f"evento_{campo}", sa.String(length=largo), nullable=True),
        )

    # Vuelve la más vieja, que es la que tenía el token original.
    columnas = ", ".join(f"evento_{c} = i.{c}" for c in _CAMPOS)
    op.execute(
        "UPDATE wishlist_config SET invitacion_token = i.token, "
        f"{columnas} "
        "FROM (SELECT * FROM invitaciones ORDER BY id LIMIT 1) i"
    )
    op.execute(
        "UPDATE wishlist_config SET invitacion_token = gen_random_uuid()::text "
        "WHERE invitacion_token IS NULL"
    )
    op.alter_column("wishlist_config", "invitacion_token", nullable=False)
    op.create_unique_constraint(
        "uq_wishlist_config_invitacion_token",
        "wishlist_config",
        ["invitacion_token"],
    )

    op.drop_constraint("fk_rsvps_invitacion", "rsvps", type_="foreignkey")
    op.drop_index("ix_rsvps_invitacion_id", table_name="rsvps")
    op.drop_column("rsvps", "comentario")
    op.drop_column("rsvps", "invitacion_id")
    op.drop_table("invitaciones")
