import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

NOMBRE_APP_DEFAULT = "Julia en Camino"


def _nuevo_share_token() -> str:
    return str(uuid.uuid4())


class WishlistConfig(Base):
    __tablename__ = "wishlist_config"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Dos links independientes a propósito: la wishlist se pasa solo a
    # quien pregunta qué hace falta, y la invitación se manda a todos los
    # convidados. Con un token compartido, invitar a alguien al shower
    # sería mostrarle también la lista de regalos.
    share_token: Mapped[str] = mapped_column(
        String(36), unique=True, default=_nuevo_share_token
    )
    invitacion_token: Mapped[str] = mapped_column(
        String(36), unique=True, default=_nuevo_share_token
    )
    nombre_app: Mapped[str] = mapped_column(String(100), default=NOMBRE_APP_DEFAULT)

    # Datos del baby shower, para el centro de la invitación. Van como
    # texto libre y no como fecha y hora reales: se escriben una vez y se
    # leen tal cual («Sábado 15 de noviembre», «de 4 a 7 de la tarde»),
    # así que tipar esto solo agregaría problemas de formato y zona
    # horaria sin ganar nada.
    evento_lugar: Mapped[str | None] = mapped_column(String(255), nullable=True)
    evento_fecha: Mapped[str | None] = mapped_column(String(100), nullable=True)
    evento_hora: Mapped[str | None] = mapped_column(String(100), nullable=True)
    evento_texto: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Aviso arriba del formulario: la fecha limite para confirmar, o por
    # donde mas se puede avisar. Va aparte del texto de la lamina porque
    # es una instruccion, no parte del dibujo.
    evento_aviso: Mapped[str | None] = mapped_column(String(500), nullable=True)
