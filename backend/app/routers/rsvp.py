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
from app.models.invitacion import Invitacion
from app.models.rsvp import Rsvp
from app.schemas.rsvp import (
    ResumenRsvp,
    RsvpCreadoOut,
    RsvpCreate,
    RsvpOut,
    RsvpUpdate,
)

router = APIRouter(tags=["rsvp"])


def _get_invitacion(token: str, db: Session) -> Invitacion:
    """Contra el token de la invitación, no el de la wishlist.

    Son links distintos a propósito: confirmar asistencia se hace desde
    la invitación, que se manda a los convidados de ese evento.
    """
    inv = db.query(Invitacion).filter(Invitacion.token == token).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Link no válido")
    return inv


@router.post(
    "/i/{invitacion_token}/rsvp",
    response_model=RsvpCreadoOut,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("10/minute")
def responder(
    request: Request,
    invitacion_token: str,
    body: RsvpCreate,
    db: Session = Depends(get_db),
):
    inv = _get_invitacion(invitacion_token, db)
    rsvp = Rsvp(
        invitacion_id=inv.id,
        nombre=body.nombre,
        asistira=body.asistira,
        cantidad=body.cantidad,
        comentario=body.comentario,
    )
    db.add(rsvp)
    db.commit()
    db.refresh(rsvp)
    return rsvp


@router.patch("/i/{invitacion_token}/rsvp/{token_edicion}", response_model=RsvpOut)
@limiter.limit("10/minute")
def cambiar_respuesta(
    request: Request,
    invitacion_token: str,
    token_edicion: str,
    body: RsvpUpdate,
    db: Session = Depends(get_db),
):
    """Cambia la propia respuesta en vez de crear otra.

    El token lo guarda el navegador al confirmar. Sin esto, quien cambiaba
    de opinión dejaba viva la respuesta vieja y sumaba una nueva, y en el
    admin aparecía dos veces.
    """
    inv = _get_invitacion(invitacion_token, db)
    rsvp = (
        db.query(Rsvp)
        .filter(Rsvp.token_edicion == token_edicion, Rsvp.invitacion_id == inv.id)
        .first()
    )
    if not rsvp:
        # Puede que el admin la haya borrado. El frontend lo toma como
        # señal para crear una nueva en vez de dejar a la persona trabada.
        raise HTTPException(status_code=404, detail="Esa respuesta ya no existe")

    cambios = body.model_dump(exclude_unset=True)
    if cambios.get("nombre") is not None:
        limpio = cambios["nombre"].strip()
        if not limpio:
            raise HTTPException(status_code=422, detail="Hace falta un nombre")
        rsvp.nombre = limpio
    if cambios.get("asistira") is not None:
        rsvp.asistira = cambios["asistira"]
    for campo in ("cantidad", "comentario"):
        if campo in cambios:
            setattr(rsvp, campo, (cambios[campo] or "").strip() or None)
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
