from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core import intentos_login
from app.core.database import get_db
from app.core.deps import get_current_admin
from app.core.ratelimit import limiter
from app.core.security import create_access_token, verify_password
from app.models.admin import Admin
from app.schemas.auth import AdminOut, LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
# Freno grueso. Detrás del proxy de Railway esto es un balde global y no
# uno por IP — ver app/core/intentos_login.py —, así que va holgado: el
# freno que de verdad aísla al atacante es el de por email, abajo.
@limiter.limit("20/minute")
def login(request: Request, body: LoginRequest, db: Session = Depends(get_db)):
    email = body.email.lower()
    if intentos_login.esta_bloqueado(email):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos fallidos. Probá de nuevo en unos minutos.",
        )

    admin = db.query(Admin).filter(Admin.email == email).first()
    if not admin or not verify_password(body.password, admin.password_hash):
        intentos_login.registrar_fallo(email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    intentos_login.limpiar(email)
    token = create_access_token({"sub": str(admin.id)})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=AdminOut)
def me(current_admin: Admin = Depends(get_current_admin)):
    return current_admin
