"""Freno de fuerza bruta para el login, contado por email.

Por que no alcanza con limitar por IP. slowapi usa `get_remote_address`,
que lee `request.client.host`. Detras del proxy de Railway eso es la IP
del proxy, no la de quien entra: uvicorn arranca sin
`--forwarded-allow-ips`, asi que su default (`127.0.0.1`) no confia en el
proxy y `X-Forwarded-For` ni se mira. Un limite "por IP" seria entonces
un unico balde compartido por todo el mundo: no aislaria al atacante, y
cualquiera podria agotarlo y dejar a los admins sin poder entrar.

Subir el default a `*` tampoco sirve. En esta version de uvicorn, cuando
confia en todos, toma el PRIMER valor de `X-Forwarded-For`, que lo
escribe el cliente: falsear la IP y saltarse el limite pasaria a ser
trivial.

Por eso el freno va por email. Cada cuenta tiene su ventana, quien
ataca solo se bloquea a si mismo, y el limite por IP de slowapi queda
como freno grueso de respaldo.

Vive en memoria a proposito: hay una sola instancia y los intentos no
valen la pena persistirlos. Con mas de un worker esto habria que moverlo
a la base o a Redis, porque cada proceso llevaria su propia cuenta.
"""

from datetime import UTC, datetime, timedelta

VENTANA = timedelta(minutes=15)
MAX_INTENTOS = 8
# Tope de cuentas vigiladas a la vez. Sin esto, alguien podria hacer
# crecer el diccionario probando un email distinto cada vez.
MAX_EMAILS = 1000

_fallos: dict[str, list[datetime]] = {}


def _vigentes(email: str, ahora: datetime) -> list[datetime]:
    """Fallos de esa cuenta dentro de la ventana, descartando los viejos."""
    recientes = [t for t in _fallos.get(email, []) if ahora - t < VENTANA]
    if recientes:
        _fallos[email] = recientes
    else:
        _fallos.pop(email, None)
    return recientes


def _purgar(ahora: datetime) -> None:
    for email in list(_fallos):
        _vigentes(email, ahora)


def esta_bloqueado(email: str) -> bool:
    return len(_vigentes(email, datetime.now(UTC))) >= MAX_INTENTOS


def registrar_fallo(email: str) -> None:
    ahora = datetime.now(UTC)
    if len(_fallos) >= MAX_EMAILS:
        _purgar(ahora)
    _fallos.setdefault(email, []).append(ahora)


def limpiar(email: str) -> None:
    """Un login exitoso borra el historial: la cuenta no arrastra fallos."""
    _fallos.pop(email, None)


def reiniciar() -> None:
    """Solo para los tests, que necesitan arrancar de cero."""
    _fallos.clear()
