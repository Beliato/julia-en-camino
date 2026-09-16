import enum
from datetime import UTC, datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.regalo import OrigenRegalo


class EstadoItem(str, enum.Enum):
    NECESITADO = "NECESITADO"
    RESERVADO = "RESERVADO"
    ADQUIRIDO = "ADQUIRIDO"


class OrigenAdquisicion(str, enum.Enum):
    NOSOTROS = "NOSOTROS"
    REGALO = "REGALO"
    # Prestado por alguien: resuelve la necesidad igual que lo demás, así
    # que cuenta como adquirido, pero el objeto no es de ellos y en algún
    # momento hay que devolverlo.
    PRESTADO = "PRESTADO"


class Prioridad(str, enum.Enum):
    URGENTE = "URGENTE"
    NORMAL = "NORMAL"
    PUEDE_ESPERAR = "PUEDE_ESPERAR"


class RangoPrecio(str, enum.Enum):
    BAJO = "BAJO"
    MEDIO = "MEDIO"
    ALTO = "ALTO"


class Etapa(str, enum.Enum):
    CUALQUIERA = "CUALQUIERA"
    RECIEN_NACIDO = "RECIEN_NACIDO"
    M0_3 = "M0_3"
    M3_6 = "M3_6"
    # El viejo M6_12 se partió en dos: entre los 6 y los 12 meses el bebé
    # cambia de talla y de habilidades demasiado como para que una sola
    # etiqueta sirva al buscar qué sacar de la caja.
    M6_9 = "M6_9"
    M9_12 = "M9_12"
    A1_2 = "A1_2"
    A2_MAS = "A2_MAS"


class Item(Base):
    __tablename__ = "items"
    __table_args__ = (
        CheckConstraint("cantidad >= 1", name="ck_items_cantidad_positiva"),
        CheckConstraint(
            "cantidad_recibida >= 0 AND cantidad_recibida <= cantidad",
            name="ck_items_recibida_valida",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(255))
    descripcion: Mapped[str | None] = mapped_column(String(1000))
    amazon_link: Mapped[str | None] = mapped_column(String(2000))
    cantidad: Mapped[int] = mapped_column(Integer, default=1)
    cantidad_recibida: Mapped[int] = mapped_column(Integer, default=0)
    prioridad: Mapped[Prioridad] = mapped_column(
        Enum(Prioridad), default=Prioridad.NORMAL
    )
    rango_precio: Mapped[RangoPrecio | None] = mapped_column(Enum(RangoPrecio))
    categoria_id: Mapped[int | None] = mapped_column(
        ForeignKey("categorias.id", ondelete="SET NULL")
    )
    # Derivado de cantidad/cantidad_recibida/reservas activas — ver
    # recalcular_estado(). Se persiste para poder filtrar e indexar.
    estado: Mapped[EstadoItem] = mapped_column(
        Enum(EstadoItem), default=EstadoItem.NECESITADO, index=True
    )
    origen_adquisicion: Mapped[OrigenAdquisicion | None] = mapped_column(
        Enum(OrigenAdquisicion)
    )
    etapa: Mapped[Etapa] = mapped_column(Enum(Etapa), default=Etapa.CUALQUIERA)
    caja_id: Mapped[int | None] = mapped_column(
        ForeignKey("cajas_almacenamiento.id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    caja = relationship("CajaAlmacenamiento")
    categoria = relationship("Categoria")
    fotos = relationship(
        "FotoItem",
        back_populates="item",
        cascade="all, delete-orphan",
        order_by="FotoItem.orden",
    )
    reservas = relationship(
        "Reserva", back_populates="item", cascade="all, delete-orphan"
    )
    regalos = relationship(
        "Regalo",
        back_populates="item",
        cascade="all, delete-orphan",
        order_by="Regalo.fecha",
    )

    @property
    def personas(self) -> list[str]:
        """Quiénes regalaron este objeto, sin repetir y sin los vacíos."""
        vistos: list[str] = []
        for r in self.regalos:
            if r.persona and r.persona not in vistos:
                vistos.append(r.persona)
        return vistos

    @property
    def prestamos_pendientes(self) -> int:
        """Cuántos préstamos de este objeto siguen sin devolver.

        Devolver no libera la unidad ni revive la necesidad: el objeto ya
        cumplió su función y revivirlo lo publicaría de nuevo en la lista
        pública. Este contador es lo que distingue "nos lo prestaron y lo
        tenemos" de "ya lo devolvimos".
        """
        return sum(
            1
            for r in self.regalos
            if r.origen == OrigenRegalo.PRESTADO and r.devuelto_en is None
        )

    @property
    def reservas_activas(self) -> int:
        """Cuántas unidades están reservadas. Solo el número: los nombres
        viven en Reserva y no salen de ahí hasta recibir cada unidad."""
        return sum(1 for r in self.reservas if r.released_at is None)


class FotoItem(Base):
    __tablename__ = "fotos_item"

    id: Mapped[int] = mapped_column(primary_key=True)
    item_id: Mapped[int] = mapped_column(
        ForeignKey("items.id", ondelete="CASCADE"), index=True
    )
    url: Mapped[str] = mapped_column(String(2000))
    orden: Mapped[int] = mapped_column(Integer, default=0)

    item = relationship("Item", back_populates="fotos")
