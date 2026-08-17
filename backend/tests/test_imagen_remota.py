"""Extraccion de la imagen del producto desde el link de la tienda.

Lo que mas importa aca es el guardado contra SSRF: el pedido sale del
servidor con una URL que elige quien entra al admin, asi que apuntarla
a la red interna tiene que fallar antes de abrir la conexion.
"""

import pytest

from app.core import imagen_remota


class TestGuardadoSSRF:
    @pytest.mark.parametrize(
        "url",
        [
            "http://localhost/admin",
            "http://127.0.0.1:8000/health",
            "http://169.254.169.254/latest/meta-data/",  # metadata de la nube
            "http://10.0.0.5/interno",
            "http://192.168.1.1/router",
            "http://[::1]/loopback",
        ],
    )
    def test_rechaza_direcciones_no_publicas(self, url):
        with pytest.raises(imagen_remota.ImagenRemotaError) as e:
            imagen_remota._validar_url(url)
        assert "no publica" in str(e.value) or "no pública" in str(e.value)

    @pytest.mark.parametrize(
        "url",
        [
            "file:///etc/passwd",
            "ftp://tienda.com/foto.jpg",
            "gopher://x",
            "javascript:1",
        ],
    )
    def test_rechaza_esquemas_que_no_son_http(self, url):
        with pytest.raises(imagen_remota.ImagenRemotaError):
            imagen_remota._validar_url(url)

    def test_acepta_un_host_publico(self):
        assert imagen_remota._validar_url("https://example.com/x.jpg")


class TestBusquedaEnHtml:
    def test_encuentra_og_image(self):
        html = '<meta property="og:image" content="https://t.com/foto.jpg">'
        assert (
            imagen_remota.buscar_imagen_en_html(html, "https://t.com/p/1")
            == "https://t.com/foto.jpg"
        )

    def test_encuentra_og_image_con_atributos_al_reves(self):
        html = '<meta content="https://t.com/foto.jpg" property="og:image">'
        assert (
            imagen_remota.buscar_imagen_en_html(html, "https://t.com/p/1")
            == "https://t.com/foto.jpg"
        )

    def test_resuelve_una_ruta_relativa_contra_la_pagina(self):
        html = '<meta property="og:image" content="/img/foto.jpg">'
        assert (
            imagen_remota.buscar_imagen_en_html(html, "https://t.com/p/1")
            == "https://t.com/img/foto.jpg"
        )

    def test_desescapa_las_entidades_html(self):
        html = '<meta property="og:image" content="https://t.com/f.jpg?a=1&amp;b=2">'
        assert (
            imagen_remota.buscar_imagen_en_html(html, "https://t.com/")
            == "https://t.com/f.jpg?a=1&b=2"
        )

    def test_cae_a_twitter_image_si_no_hay_open_graph(self):
        html = '<meta name="twitter:image" content="https://t.com/tw.jpg">'
        assert (
            imagen_remota.buscar_imagen_en_html(html, "https://t.com/")
            == "https://t.com/tw.jpg"
        )

    def test_amazon_sale_por_el_patron_de_media_amazon(self):
        # Amazon no publica Open Graph: se raspa la URL de la imagen.
        html = (
            '<div><img src="https://m.media-amazon.com/images/I/61e9Si044bL.jpg"></div>'
        )
        assert (
            imagen_remota.buscar_imagen_en_html(html, "https://www.amazon.com/dp/X")
            == "https://m.media-amazon.com/images/I/61e9Si044bL.jpg"
        )

    def test_amazon_saca_el_sufijo_de_tamano_para_traer_el_original(self):
        # En el HTML hay diez veces mas URLs con recorte (._AC_SX300_)
        # que desnudas, y las primeras son versiones chicas.
        html = (
            '<img src="https://m.media-amazon.com/images/I/61e9Si044bL._AC_SX300_.jpg">'
        )
        assert (
            imagen_remota.buscar_imagen_en_html(html, "https://www.amazon.com/dp/X")
            == "https://m.media-amazon.com/images/I/61e9Si044bL.jpg"
        )

    def test_devuelve_none_cuando_no_hay_nada(self):
        assert (
            imagen_remota.buscar_imagen_en_html(
                "<html><body>hola</body></html>", "https://t.com/"
            )
            is None
        )


class TestEndpoint:
    def test_requiere_autenticacion(self, client):
        r = client.post(
            "/items/1/fotos/desde-url", json={"url": "https://example.com/x.jpg"}
        )
        assert r.status_code in (401, 403)

    def test_rechaza_una_url_invalida(self, client, auth_headers):
        r = client.post(
            "/items/1/fotos/desde-url",
            json={"url": "no-es-una-url"},
            headers=auth_headers,
        )
        assert r.status_code == 422
