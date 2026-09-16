"""etapas 6-9 y 9-12

Revision ID: a7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-09-15

Parte la etapa M6_12 en dos: M6_9 y M9_12.

Se hace con RENAME VALUE y no agregando M6_9 desde cero, porque asi las
filas que hoy dicen M6_12 se conservan solas: pasan a M6_9 sin UPDATE. El
criterio es que 6-9 es el tramo mas probable de lo que ya estaba cargado
(la ropa y los juguetes se compran para ya, no para dentro de medio ano),
pero es una suposicion: lo que en realidad era de 9-12 hay que moverlo a
mano desde el admin.

M9_12 se agrega con AFTER 'M6_9' para que el orden del enum siga siendo el
orden cronologico. Sin eso quedaria al final, despues de A2_MAS, y
cualquier ORDER BY etapa mentiria.

Igual que en la migracion de PRESTADO: ADD VALUE corre bien dentro de la
transaccion de Alembic en PG 12+ mientras no se inserten filas con el
valor nuevo en la misma transaccion, y no hay forma de quitar un valor de
un enum, asi que el downgrade reconstruye el tipo entero.
"""

from typing import Sequence, Union

from alembic import op

revision: str = "a7b8c9d0e1f2"
down_revision: Union[str, None] = "f6a7b8c9d0e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# El orden importa: es el que queda grabado en el tipo de Postgres.
ETAPAS_VIEJAS = [
    "CUALQUIERA",
    "RECIEN_NACIDO",
    "M0_3",
    "M3_6",
    "M6_12",
    "A1_2",
    "A2_MAS",
]


def upgrade() -> None:
    op.execute("ALTER TYPE etapa RENAME VALUE 'M6_12' TO 'M6_9'")
    op.execute("ALTER TYPE etapa ADD VALUE IF NOT EXISTS 'M9_12' AFTER 'M6_9'")


def downgrade() -> None:
    # Volver a juntar los dos tramos en uno no inventa nada: 9-12 esta
    # contenido en 6-12. Lo que se pierde es el detalle, no la verdad.
    op.execute("UPDATE items SET etapa = 'M6_9' WHERE etapa = 'M9_12'")
    op.execute("ALTER TYPE etapa RENAME VALUE 'M6_9' TO 'M6_12'")

    etiquetas = ", ".join(f"'{v}'" for v in ETAPAS_VIEJAS)
    op.execute("ALTER TYPE etapa RENAME TO etapa_viejo")
    op.execute(f"CREATE TYPE etapa AS ENUM ({etiquetas})")
    # El DEFAULT hay que sacarlo antes del cast y reponerlo despues:
    # quedaria apuntando al tipo viejo y Postgres no lo castea solo.
    op.execute("ALTER TABLE items ALTER COLUMN etapa DROP DEFAULT")
    op.execute(
        "ALTER TABLE items ALTER COLUMN etapa TYPE etapa USING etapa::text::etapa"
    )
    op.execute("ALTER TABLE items ALTER COLUMN etapa SET DEFAULT 'CUALQUIERA'::etapa")
    op.execute("DROP TYPE etapa_viejo")
