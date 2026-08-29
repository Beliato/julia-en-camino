from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class RsvpCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=255)
    asistira: bool
    # Mensaje para Julia, para leerle después.
    comentario: str | None = Field(default=None, max_length=2000)

    @field_validator("nombre")
    @classmethod
    def nombre_no_vacio(cls, v: str) -> str:
        limpio = v.strip()
        if not limpio:
            raise ValueError("Hace falta un nombre")
        return limpio

    @field_validator("comentario")
    @classmethod
    def comentario_vacio_es_nada(cls, v: str | None) -> str | None:
        return (v or "").strip() or None


class RsvpOut(BaseModel):
    id: int
    invitacion_id: int
    nombre: str
    asistira: bool
    comentario: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class ResumenRsvp(BaseModel):
    """Lo que se ve de un vistazo en el admin."""

    asisten: int
    no_asisten: int
    respuestas: list[RsvpOut]
