import os, json, pytest
from unittest.mock import patch
from app import create_app
FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures')
def _fix(f):
    with open(os.path.join(FIXTURES, f), encoding='utf-8') as fh: return fh.read()
@pytest.fixture
def client():
    app = create_app({'TESTING': True})
    with app.test_client() as c: yield c

class TestDetectPortal:
    def test_nehnutelnosti(self):
        from services.url_fetch_service import _detect_portal
        assert _detect_portal("https://www.nehnutelnosti.sk/detail/x") == "nehnutelnosti_sk"
    def test_topreality(self):
        from services.url_fetch_service import _detect_portal
        assert _detect_portal("https://www.topreality.sk/r123.html") == "topreality_sk"
    def test_reality(self):
        from services.url_fetch_service import _detect_portal
        assert _detect_portal("https://www.reality.sk/x/") == "reality_sk"
    def test_unknown_raises(self):
        from services.url_fetch_service import _detect_portal
        import pytest as _p
        with _p.raises(ValueError): _detect_portal("https://www.bazos.sk/x")
    def test_invalid_scheme_raises(self):
        from services.url_fetch_service import fetch_parcel_from_url
        import pytest as _p
        with _p.raises(ValueError): fetch_parcel_from_url("not-a-url")


class TestNormalizePrice:
    def _n(self, s):
        from services.url_fetch_service import _normalize_price
        return _normalize_price(s)
    def test_dot_thousands(self):    assert self._n("145.000") == 145000.0
    def test_comma_thousands(self):  assert self._n("125,000") == 125000.0
    def test_space_thousands(self):  assert self._n("100 980") == 100980.0
    def test_with_eur(self):         assert self._n("145.000 €") == 145000.0
    def test_empty(self):            assert self._n("") == 0.0
    def test_none(self):             assert self._n(None) == 0.0


class TestParseNehnutelnosti:
    URL_S = "https://www.nehnutelnosti.sk/detail/JuX4T7tOPvS/pozemok-pod-sandbergom-v-devinskej-novej-vsi-na-predaj"
    URL_D = "https://www.nehnutelnosti.sk/detail/Ju7J_rBgI2V/stavebne-pozemky-624m2-a-625m2-pre-rodinne-domy-v-oblubenej-lokalite-florida-park-dunajska-streda"
    def _r(self, fname, url):
        from services.url_fetch_service import _parse_nehnutelnosti
        return _parse_nehnutelnosti(_fix(fname), url)
    def test_sandberg_price(self):
        assert abs(self._r("nehnutelnosti_detail_sandberg.html", self.URL_S)["price_eur"] - 145000) < 500
    def test_sandberg_area(self):
        assert abs(self._r("nehnutelnosti_detail_sandberg.html", self.URL_S)["area_sqm"] - 984) < 20
    def test_sandberg_location_devinska(self):
        assert "dev" in self._r("nehnutelnosti_detail_sandberg.html", self.URL_S)["location_text"].lower()
    def test_sandberg_structured(self):
        assert self._r("nehnutelnosti_detail_sandberg.html", self.URL_S)["parse_quality"] == "structured"
    def test_sandberg_portal(self):
        assert self._r("nehnutelnosti_detail_sandberg.html", self.URL_S)["source_portal"] == "nehnutelnosti_sk"
    def test_dunstreda_area_over_600(self):
        assert self._r("nehnutelnosti_detail_dunstreda.html", self.URL_D)["area_sqm"] >= 600
    def test_dunstreda_location(self):
        assert "streda" in self._r("nehnutelnosti_detail_dunstreda.html", self.URL_D)["location_text"].lower()
    def test_ppsm_computed(self):
        assert self._r("nehnutelnosti_detail_sandberg.html", self.URL_S)["price_per_sqm"] > 0

class TestParseTopreality:
    URL_SE = "https://www.topreality.sk/stavebne-pozemky-senica-uz-mozete-stavat-rezort-vinohrady-r8804772.html"
    URL_LE = "https://www.topreality.sk/na-predaj-stavebne-pozemky-pre-rodinne-domy-od-560-m2-do-1-019-m2-lehnice-r9376059.html"
    def _r(self, fname, url):
        from services.url_fetch_service import _parse_topreality
        return _parse_topreality(_fix(fname), url)
    def test_senica_price(self):
        assert abs(self._r("topreality_detail_senica.html", self.URL_SE)["price_eur"] - 100980) < 500
    def test_senica_area(self):
        assert abs(self._r("topreality_detail_senica.html", self.URL_SE)["area_sqm"] - 594) < 20
    def test_senica_location(self):
        assert "senica" in self._r("topreality_detail_senica.html", self.URL_SE)["location_text"].lower()
    def test_senica_structured(self):
        assert self._r("topreality_detail_senica.html", self.URL_SE)["parse_quality"] == "structured"
    def test_lehnice_area(self):
        assert abs(self._r("topreality_detail_lehnice.html", self.URL_LE)["area_sqm"] - 560) < 20
    def test_lehnice_price_from_ppsm(self):
        assert self._r("topreality_detail_lehnice.html", self.URL_LE)["price_eur"] > 50000
    def test_lehnice_location(self):
        assert "lehnic" in self._r("topreality_detail_lehnice.html", self.URL_LE)["location_text"].lower()


class TestParseReality:
    URL_SE = "https://www.reality.sk/pozemky/predaj-stavebne-pozemky-novy-svet-senec/JusUKKrulL9/"
    URL_NI = "https://www.reality.sk/pozemky/pozemok-urceny-na-vystavbu-rodinneho-domu-nitra-sudol-655-m2/JuyvXJaySXn/"
    def _r(self, fname, url):
        from services.url_fetch_service import _parse_reality
        return _parse_reality(_fix(fname), url)
    def test_nitra_price(self):
        assert abs(self._r("reality_detail_nitra.html", self.URL_NI)["price_eur"] - 125000) < 500
    def test_nitra_area(self):
        assert abs(self._r("reality_detail_nitra.html", self.URL_NI)["area_sqm"] - 655) < 20
    def test_nitra_location(self):
        assert "nitra" in self._r("reality_detail_nitra.html", self.URL_NI)["location_text"].lower()
    def test_nitra_structured(self):
        assert self._r("reality_detail_nitra.html", self.URL_NI)["parse_quality"] == "structured"
    def test_senec_area(self):
        assert abs(self._r("reality_detail_senec.html", self.URL_SE)["area_sqm"] - 551) < 20
    def test_senec_price_from_ppsm(self):
        assert self._r("reality_detail_senec.html", self.URL_SE)["price_eur"] > 50000
    def test_senec_location_not_empty(self):
        assert self._r("reality_detail_senec.html", self.URL_SE)["location_text"] != ""


class TestFetchUrlEndpoint:
    def _post(self, client, payload):
        import json
        return client.post("/api/parcels/fetch-url",
                           data=json.dumps(payload),
                           content_type="application/json")
    def test_missing_url_400(self, client):
        assert self._post(client, {}).status_code == 400
    def test_empty_url_400(self, client):
        assert self._post(client, {"url": ""}).status_code == 400
    def test_unsupported_portal_400(self, client):
        assert self._post(client, {"url": "https://www.bazos.sk/x"}).status_code == 400
    def test_invalid_scheme_400(self, client):
        assert self._post(client, {"url": "not-a-url"}).status_code == 400
    def test_ok_nehnutelnosti(self, client):
        from unittest.mock import patch as _patch
        url  = "https://www.nehnutelnosti.sk/detail/JuX4T7tOPvS/sandberg"
        html = _fix("nehnutelnosti_detail_sandberg.html")
        with _patch("services.url_fetch_service._fetch_html", return_value=html):
            r = self._post(client, {"url": url})
        assert r.status_code == 200
        assert r.get_json()["parcel"]["price_eur"] > 0
    def test_ok_topreality(self, client):
        from unittest.mock import patch as _patch
        url  = "https://www.topreality.sk/senica-r8804772.html"
        html = _fix("topreality_detail_senica.html")
        with _patch("services.url_fetch_service._fetch_html", return_value=html):
            r = self._post(client, {"url": url})
        assert r.status_code == 200
        assert r.get_json()["parcel"]["area_sqm"] > 0
    def test_ok_reality(self, client):
        from unittest.mock import patch as _patch
        url  = "https://www.reality.sk/pozemky/nitra/JuyvXJaySXn/"
        html = _fix("reality_detail_nitra.html")
        with _patch("services.url_fetch_service._fetch_html", return_value=html):
            r = self._post(client, {"url": url})
        assert r.status_code == 200
        assert abs(r.get_json()["parcel"]["price_eur"] - 125000) < 500
    def test_network_error_502(self, client):
        import requests
        from unittest.mock import patch as _patch
        url = "https://www.nehnutelnosti.sk/detail/x/y"
        with _patch("services.url_fetch_service._fetch_html",
                    side_effect=requests.ConnectionError("refused")):
            r = self._post(client, {"url": url})
        assert r.status_code == 502
    def test_required_fields(self, client):
        from unittest.mock import patch as _patch
        url  = "https://www.reality.sk/pozemky/nitra/JuyvXJaySXn/"
        html = _fix("reality_detail_nitra.html")
        with _patch("services.url_fetch_service._fetch_html", return_value=html):
            parcel = self._post(client, {"url": url}).get_json()["parcel"]
        for fld in ["title","price_eur","area_sqm","location_text",
                    "source_portal","url","price_per_sqm","parse_quality"]:
            assert fld in parcel
