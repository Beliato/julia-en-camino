"""Confirmacion de asistencia al baby shower."""

from app.models.rsvp import Rsvp
from app.models.wishlist_config import WishlistConfig


def _token(db) -> str:
    config = db.query(WishlistConfig).first()
    if not config:
        config = WishlistConfig()
        db.add(config)
        db.commit()
    return config.share_token


class TestResponder:
    def test_alguien_con_el_link_puede_confirmar(self, client, db):
        r = client.post(
            f"/w/{_token(db)}/rsvp",
            json={"nombre": "Hannia Solano", "asistira": True},
        )
        assert r.status_code == 201
        assert r.json()["nombre"] == "Hannia Solano"
        assert r.json()["asistira"] is True

    def test_tambien_se_puede_decir_que_no(self, client, db):
        r = client.post(
            f"/w/{_token(db)}/rsvp", json={"nombre": "Ana", "asistira": False}
        )
        assert r.status_code == 201
        assert r.json()["asistira"] is False

    def test_un_token_inventado_no_sirve(self, client):
        r = client.post(
            "/w/token-que-no-existe/rsvp",
            json={"nombre": "Colado", "asistira": True},
        )
        assert r.status_code == 404

    def test_el_nombre_no_puede_ser_espacios(self, client, db):
        r = client.post(
            f"/w/{_token(db)}/rsvp", json={"nombre": "   ", "asistira": True}
        )
        assert r.status_code == 422

    def test_el_nombre_se_guarda_sin_espacios_de_sobra(self, client, db):
        r = client.post(
            f"/w/{_token(db)}/rsvp",
            json={"nombre": "  Marta  ", "asistira": True},
        )
        assert r.json()["nombre"] == "Marta"


class TestConsultaDelAdmin:
    def test_lista_con_los_totales(self, client, auth_headers, db):
        db.add(Rsvp(nombre="Ana", asistira=True))
        db.add(Rsvp(nombre="Beto", asistira=True))
        db.add(Rsvp(nombre="Caro", asistira=False))
        db.commit()

        r = client.get("/rsvps", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["asisten"] == 2
        assert r.json()["no_asisten"] == 1
        assert len(r.json()["respuestas"]) == 3

    def test_sin_sesion_no_se_puede_ver_quien_viene(self, client, db):
        db.add(Rsvp(nombre="Ana", asistira=True))
        db.commit()

        r = client.get("/rsvps")
        assert r.status_code in (401, 403)

    def test_se_puede_borrar_una_respuesta_cargada_por_error(
        self, client, auth_headers, db
    ):
        rsvp = Rsvp(nombre="Duplicada", asistira=True)
        db.add(rsvp)
        db.commit()

        r = client.delete(f"/rsvps/{rsvp.id}", headers=auth_headers)
        assert r.status_code == 204
        assert db.query(Rsvp).filter(Rsvp.id == rsvp.id).first() is None

    def test_borrar_algo_que_no_existe_da_404(self, client, auth_headers):
        assert client.delete("/rsvps/9999", headers=auth_headers).status_code == 404


class TestDatosDelEvento:
    def test_la_config_publica_los_devuelve(self, client, auth_headers):
        client.patch(
            "/config",
            json={
                "evento_lugar": "Salón El Jardín",
                "evento_fecha": "Sábado 15 de noviembre",
                "evento_hora": "De 4 a 7",
                "evento_texto": "Acompañanos a celebrar",
            },
            headers=auth_headers,
        )
        datos = client.get("/config").json()
        assert datos["evento_lugar"] == "Salón El Jardín"
        assert datos["evento_fecha"] == "Sábado 15 de noviembre"

    def test_se_puede_cambiar_solo_uno_sin_pisar_los_demas(self, client, auth_headers):
        client.patch(
            "/config",
            json={"evento_lugar": "Casa", "evento_hora": "5 pm"},
            headers=auth_headers,
        )
        client.patch("/config", json={"evento_hora": "6 pm"}, headers=auth_headers)

        datos = client.get("/config").json()
        assert datos["evento_lugar"] == "Casa"
        assert datos["evento_hora"] == "6 pm"

    def test_vaciar_un_campo_lo_borra(self, client, auth_headers):
        client.patch("/config", json={"evento_hora": "5 pm"}, headers=auth_headers)
        client.patch("/config", json={"evento_hora": ""}, headers=auth_headers)

        assert client.get("/config").json()["evento_hora"] is None

    def test_el_nombre_de_la_app_sigue_andando(self, client, auth_headers):
        r = client.patch(
            "/config", json={"nombre_app": "Otro nombre"}, headers=auth_headers
        )
        assert r.json()["nombre_app"] == "Otro nombre"

    def test_sin_sesion_no_se_puede_cambiar(self, client):
        r = client.patch("/config", json={"evento_lugar": "Colado"})
        assert r.status_code in (401, 403)
