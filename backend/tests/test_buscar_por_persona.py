"""Busqueda de "que me regalo fulano" desde la barra del admin."""

from app.models.item import Item
from app.models.regalo import OrigenRegalo, Regalo


def _con_regalo(db, nombre_item: str, persona: str) -> Item:
    item = Item(nombre=nombre_item, cantidad=1)
    db.add(item)
    db.flush()
    db.add(
        Regalo(
            item_id=item.id,
            persona=persona,
            origen=OrigenRegalo.REGALO,
            cantidad=1,
        )
    )
    db.commit()
    return item


class TestBuscarPorPersona:
    def test_trae_lo_que_regalo_esa_persona(self, client, auth_headers, db):
        _con_regalo(db, "Body manga corta", "Hannia Solano")
        _con_regalo(db, "Cuna colecho", "Alexandra Rey")

        r = client.get("/items/buscar?persona=Hannia", headers=auth_headers)
        assert r.status_code == 200
        nombres = [i["nombre"] for i in r.json()]
        assert nombres == ["Body manga corta"]

    def test_coincidencia_parcial_por_el_apellido(self, client, auth_headers, db):
        _con_regalo(db, "Mecedora", "Hannia Solano")

        r = client.get("/items/buscar?persona=solano", headers=auth_headers)
        assert [i["nombre"] for i in r.json()] == ["Mecedora"]

    def test_ignora_acentos(self, client, auth_headers, db):
        _con_regalo(db, "Cambiador", "Lucía Pérez")

        r = client.get("/items/buscar?persona=lucia", headers=auth_headers)
        assert [i["nombre"] for i in r.json()] == ["Cambiador"]

    def test_no_trae_lo_que_compraron_ellos(self, client, auth_headers, db):
        # Los items sin regalo asociado no deben colarse
        item = Item(nombre="Comprado por nosotros", cantidad=1)
        db.add(item)
        db.commit()

        r = client.get("/items/buscar?persona=a", headers=auth_headers)
        assert [i["nombre"] for i in r.json()] == []

    def test_se_puede_combinar_con_el_texto(self, client, auth_headers, db):
        _con_regalo(db, "Body manga corta", "Hannia Solano")
        _con_regalo(db, "Cuna colecho", "Hannia Solano")

        r = client.get("/items/buscar?q=cuna&persona=Hannia", headers=auth_headers)
        assert [i["nombre"] for i in r.json()] == ["Cuna colecho"]

    def test_sin_texto_ni_persona_es_invalido(self, client, auth_headers):
        r = client.get("/items/buscar", headers=auth_headers)
        assert r.status_code == 422

    def test_la_busqueda_por_texto_sigue_andando(self, client, auth_headers, db):
        _con_regalo(db, "Body manga corta", "Hannia Solano")

        r = client.get("/items/buscar?q=body", headers=auth_headers)
        assert [i["nombre"] for i in r.json()] == ["Body manga corta"]


class TestMiniaturaEnResultados:
    def test_la_busqueda_devuelve_las_fotos(self, client, auth_headers, db):
        from app.models.item import FotoItem

        item = _con_regalo(db, "Mecedora", "Hannia Solano")
        db.add(FotoItem(item_id=item.id, url="https://r2.dev/x.webp", orden=0))
        db.commit()

        r = client.get("/items/buscar?q=mecedora", headers=auth_headers)
        assert r.json()[0]["fotos"][0]["url"] == "https://r2.dev/x.webp"

    def test_sin_fotos_devuelve_lista_vacia(self, client, auth_headers, db):
        _con_regalo(db, "Cambiador", "Ana")

        r = client.get("/items/buscar?q=cambiador", headers=auth_headers)
        assert r.json()[0]["fotos"] == []
