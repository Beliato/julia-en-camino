"""Cabeceras defensivas en las respuestas de la API."""

from app.core.config import settings


def test_van_en_una_respuesta_normal(client):
    r = client.get("/health")
    assert r.headers["x-content-type-options"] == "nosniff"
    assert r.headers["x-frame-options"] == "DENY"
    assert r.headers["referrer-policy"] == "no-referrer"
    assert "max-age=" in r.headers["strict-transport-security"]


def test_van_tambien_cuando_la_respuesta_es_un_error(client):
    """Un 401 sale por otro camino que un 200; es justo donde estas cosas
    se suelen perder."""
    r = client.get("/auth/me", headers={"Authorization": "Bearer basura"})
    assert r.status_code == 401
    assert r.headers["x-content-type-options"] == "nosniff"


def test_la_csp_sigue_el_modo_debug(client):
    """En local queda fuera porque /docs carga Swagger desde un CDN y
    default-src 'none' lo dejaria en blanco."""
    r = client.get("/health")
    if settings.DEBUG:
        assert "content-security-policy" not in r.headers
    else:
        assert r.headers["content-security-policy"] == (
            "default-src 'none'; frame-ancestors 'none'"
        )
