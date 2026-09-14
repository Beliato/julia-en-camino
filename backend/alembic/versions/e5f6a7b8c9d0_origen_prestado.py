"""origen prestado

Revision ID: e5f6a7b8c9d0
Revises: 1f737b6d04c9
Create Date: 2026-09-13

Agrega PRESTADO a los dos enums de origen.

Los enums de Postgres tienen dos reglas que muerden aca:

1. ALTER TYPE ... ADD VALUE no se puede usar en la misma transaccion que
   lo agrega. Como esta migracion solo agrega el valor y no inserta
   filas con el, corre bien dentro de la transaccion de Alembic en PG 12+.

2. No existe forma de quitar un valor de un enum. El downgrade tiene que
   reconstruir el tipo entero, y eso solo es seguro si ninguna fila usa
   PRESTADO: convertir un prestamo en regalo o en compra seria mentir
   sobre algo que hay que devolver. Por eso aborta si encuentra alguna.
"""

from typing import Sequence, Union

from alembic import op

revision: str = "e5f6a7b8c9d0"
down_revision: Union[str, None] = "1f737b6d04c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE origenregalo ADD VALUE IF NOT EXISTS 'PRESTADO'")
    op.execute("ALTER TYPE origenadquisicion ADD VALUE IF NOT EXISTS 'PRESTADO'")


def _rehacer_enum(
    tipo: str, valores: list[str], usos: list[tuple[str, str, str | None]]
) -> None:
    """Reconstruye un enum sin PRESTADO, moviendo las columnas que lo usan.

    El DEFAULT de la columna hay que sacarlo antes y reponerlo despues:
    quedaria apuntando al tipo viejo y Postgres no lo castea solo
    ("default for column ... cannot be cast automatically"). Se descubrio
    corriendo el downgrade de verdad, no leyendo el codigo.
    """
    etiquetas = ", ".join(f"'{v}'" for v in valores)
    op.execute(f"ALTER TYPE {tipo} RENAME TO {tipo}_viejo")
    op.execute(f"CREATE TYPE {tipo} AS ENUM ({etiquetas})")
    for tabla, columna, default in usos:
        if default:
            op.execute(f"ALTER TABLE {tabla} ALTER COLUMN {columna} DROP DEFAULT")
        op.execute(
            f"ALTER TABLE {tabla} ALTER COLUMN {columna} "
            f"TYPE {tipo} USING {columna}::text::{tipo}"
        )
        if default:
            op.execute(
                f"ALTER TABLE {tabla} ALTER COLUMN {columna} "
                f"SET DEFAULT '{default}'::{tipo}"
            )
    op.execute(f"DROP TYPE {tipo}_viejo")


def downgrade() -> None:
    conexion = op.get_bind()
    for tabla, columna in (("regalos", "origen"), ("items", "origen_adquisicion")):
        pendientes = conexion.exec_driver_sql(
            f"SELECT COUNT(*) FROM {tabla} WHERE {columna}::text = 'PRESTADO'"
        ).scalar()
        if pendientes:
            raise RuntimeError(
                f"Hay {pendientes} fila(s) en {tabla} con origen PRESTADO. "
                "No se puede volver atras sin inventar que fueron regalo o "
                "compra. Resolvelas a mano antes de bajar esta migracion."
            )

    _rehacer_enum(
        "origenregalo", ["REGALO", "NOSOTROS"], [("regalos", "origen", "REGALO")]
    )
    _rehacer_enum(
        "origenadquisicion",
        ["NOSOTROS", "REGALO"],
        [("items", "origen_adquisicion", None)],
    )
