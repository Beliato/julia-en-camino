from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Rsvp(Base):
    """Confirmación de asistencia al baby shower.

    Se guarda cada respuesta tal como llega, sin cuenta ni identidad: la
    invitación se comparte por el mismo link que la wishlist. Que alguien
    responda dos veces es posible y no se bloquea — corregirlo desde el
    admin es más simple que adivinar si «Ana» y «Ana Pérez» son la misma
    persona.
    """

    __tablename__ = "rsvps"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(255))
    asistira: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
