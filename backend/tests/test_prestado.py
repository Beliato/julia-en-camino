"""Objetos prestados: resuelven la necesidad pero hay que devolverlos."""

from app.models.item import Item, OrigenAdquisicion
from app.models.regalo import OrigenRegalo, Regalo


def _item(db, nombre="Moises", cantidad=1) -> Item:
    item = Item(nombre=nombre, cantidad=cantidad)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


class TestMarcarComoPrestado:
    def test_se_puede_marcar_adquirido_como_prestado(self, client, auth_headers, db):
        item = _item(db)
        r = client.post(
            f"/items/{item.id}/adquirir",
            json={"origen": "PRESTADO", "gifter_name": "Tia Ana"},
            headers=auth_headers,
        )
        assert r.status_code == 200
        assert r.json()["origen_adquisicion"] == "PRESTADO"

    def test_guarda_quien_lo_presto(self, client, auth_headers, db):
        item = _item(db)
        client.post(
            f"/items/{item.id}/adquirir",
            json={"origen": "PRESTADO", "gifter_name": "Tia Ana"},
            headers=auth_headers,
        )
        regalo = db.query(Regalo).filter(Regalo.item_id == item.id).first()
        assert regalo.origen == OrigenRegalo.PRESTADO
        assert regalo.persona == "Tia Ana"

    def test_cuenta_como_adquirido(self, client, auth_headers, db):
        """Lo prestado tambien resuelve la necesidad: no hay que comprarlo."""
        item = _item(db)
        r = client.post(
            f"/items/{item.id}/adquirir",
            json={"origen": "PRESTADO", "gifter_name": "Ana"},
            headers=auth_headers,
        )
        assert r.json()["estado"] == "ADQUIRIDO"


class TestRegistrarPrestamo:
    def test_se_registra_desde_el_modal_de_regalos(self, client, auth_headers, db):
        item = _item(db)
        r = client.post(
            "/regalos",
            json={
                "item_id": item.id,
                "persona": "Prima Sofia",
                "origen": "PRESTADO",
                "cantidad": 1,
            },
            headers=auth_headers,
        )
        assert r.status_code == 201
        assert r.json()["origen"] == "PRESTADO"

    def test_exige_saber_quien_lo_presto(self, client, auth_headers, db):
        """Sin nombre no se sabe a quien devolverselo."""
        item = _item(db)
        r = client.post(
            "/regalos",
            json={"item_id": item.id, "persona": "", "origen": "PRESTADO"},
            headers=auth_headers,
        )
        assert r.status_code == 422

    def test_no_se_puede_vaciar_el_nombre_al_corregir(self, client, auth_headers, db):
        item = _item(db)
        creado = client.post(
            "/regalos",
            json={"item_id": item.id, "persona": "Ana", "origen": "PRESTADO"},
            headers=auth_headers,
        ).json()
        r = client.patch(
            f"/regalos/{creado['id']}", json={"persona": "  "}, headers=auth_headers
        )
        assert r.status_code == 422


class TestOrigenDerivado:
    def test_un_regalo_le_gana_al_prestamo(self, client, auth_headers, db):
        """Con unidades de los dos origenes, el item cuenta como regalo:
        es lo mas definitivo que le paso."""
        item = _item(db, cantidad=2)
        for origen, persona in (("PRESTADO", "Ana"), ("REGALO", "Beto")):
            client.post(
                "/regalos",
                json={
                    "item_id": item.id,
                    "persona": persona,
                    "origen": origen,
                    "cantidad": 1,
                },
                headers=auth_headers,
            )
        db.refresh(item)
        assert item.origen_adquisicion == OrigenAdquisicion.REGALO

    def test_el_prestamo_le_gana_a_lo_comprado(self, client, auth_headers, db):
        item = _item(db, cantidad=2)
        client.post(
            "/regalos",
            json={"item_id": item.id, "persona": "", "origen": "NOSOTROS"},
            headers=auth_headers,
        )
        client.post(
            "/regalos",
            json={"item_id": item.id, "persona": "Ana", "origen": "PRESTADO"},
            headers=auth_headers,
        )
        db.refresh(item)
        assert item.origen_adquisicion == OrigenAdquisicion.PRESTADO


class TestNoEsUnRegalo:
    def test_lo_prestado_no_va_al_muro_de_agradecimiento(
        self, client, auth_headers, db
    ):
        """El muro es de regalos recibidos; un prestamo no lo es."""
        from app.models.wishlist_config import WishlistConfig

        config = db.query(WishlistConfig).first()
        if not config:
            config = WishlistConfig()
            db.add(config)
            db.commit()
            db.refresh(config)

        item = _item(db)
        client.post(
            "/regalos",
            json={"item_id": item.id, "persona": "Ana", "origen": "PRESTADO"},
            headers=auth_headers,
        )
        recibidos = client.get(f"/w/{config.share_token}").json()["recibidos"]
        assert all(r["persona"] != "Ana" for r in recibidos)
