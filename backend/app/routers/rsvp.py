"""Confirmación de asistencia al baby shower.

El envío es público —lo hace quien tiene el link compartido, sin cuenta—
así que va con el mismo límite de tasa que las reservas. La consulta y el
borrado son solo del admin.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_admin
from app.core.ratelimit import limiter
from app.models.admin import Admin
from app.models.rsvp import Rsvp
from app.models.wishlist_config import WishlistConfig
from app.schemas.rsvp import ResumenRsvp, RsvpCreate, RsvpOut

router = APIRouter(tags=["rsvp"])


def _validar_token(share_token: str, db: Session) -> None:
    config = (
        db.query(WishlistConfig)
        .filter(WishlistConfig.share_token == share_token)
        .first()
    )
    if not config:
        raise HTTPException(status_code=404, detail="Link no válido")


@router.post(
    "/w/{share_token}/rsvp",
    response_model=RsvpOut,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("10/minute")
def responder(
    request: Request,
    share_token: str,
    body: RsvpCreate,
    db: Session = Depends(get_db),
):
    _validar_token(share_token, db)
    rsvp = Rsvp(nombre=body.nombre, asistira=body.asistira)
    db.add(rsvp)
    db.commit()
    db.refresh(rsvp)
    return rsvp


@router.get("/rsvps", response_model=ResumenRsvp)
def listar_rsvps(
    db: Session = Depends(get_db),
    _: Admin = Depends(get_current_admin),
):
    respuestas = db.query(Rsvp).order_by(Rsvp.created_at.desc()).all()
    return ResumenRsvp(
        asisten=sum(1 for r in respuestas if r.asistira),
        no_asisten=sum(1 for r in respuestas if not r.asistira),
        respuestas=respuestas,
    )


@router.delete("/rsvps/{rsvp_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_rsvp(
    rsvp_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(get_current_admin),
):
    """Para limpiar duplicados o una respuesta cargada por error."""
    rsvp = db.query(Rsvp).filter(Rsvp.id == rsvp_id).first()
    if not rsvp:
        raise HTTPException(status_code=404, detail="Respuesta no encontrada")
    db.delete(rsvp)
    db.commit()
