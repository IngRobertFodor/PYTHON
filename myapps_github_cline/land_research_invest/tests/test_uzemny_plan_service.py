import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "backend"))
import pytest
from unittest.mock import patch, MagicMock
from services.uzemny_plan_service import (
    normalize_obec, build_up_links, get_checklist,
    is_gisplan_available, _gisplan_cache, _cache_lock,
)


class TestNormalizeObec:
    def test_simple(self):           assert normalize_obec("Senec") == "senec"
    def test_diacritics(self):       assert normalize_obec("Bernolákovo") == "bernolakovo"
    def test_multiword(self):        assert normalize_obec("Ivanka pri Dunaji") == "ivanka-pri-dunaji"
    def test_with_kraj(self):        assert normalize_obec("Senec, Bratislavský kraj") == "senec"
    def test_with_okr(self):         assert normalize_obec("Kamený Most, okr. Šahy") == "kameny-most"
    def test_empty(self):            assert normalize_obec("") == ""
    def test_none_like(self):        assert normalize_obec(None) == ""
    def test_malacky(self):          assert normalize_obec("Malacky") == "malacky"
    def test_modra(self):            assert normalize_obec("Modrá") == "modra"
    def test_double_space(self):     assert normalize_obec("Vel'ký  Biel") == "velky-biel"

    def test_hyphen_velky_meder(self):   assert normalize_obec("Velky-Meder") == "velky-meder"
    def test_hyphen_nova_vieska(self):   assert normalize_obec("Nova-Vieska") == "nova-vieska"
    def test_hyphen_with_diacritics(self): assert normalize_obec("Ivanka-pri-Dunaji") == "ivanka-pri-dunaji"
    def test_hyphen_in_first_part(self): assert normalize_obec("Velky-Meder, okr. Komarno") == "velky-meder"
    def test_keeps_numbers(self):    assert normalize_obec("Bratislava IV") == "bratislava-iv"
    def test_pezinok(self):          assert normalize_obec("Pezinok, Slovakia") == "pezinok"


class TestBuildUpLinks:
    def test_returns_all_keys(self):
        r = build_up_links("Senec")
        for k in ["obec","obec_slug","has_gisplan","gisplan_up_url","gisplan_base_url","fallback_links","checklist"]:
            assert k in r, f"chybajuci kluc: {k}"

    def test_gisplan_url_format(self):
        r = build_up_links("Malacky")
        assert r["gisplan_up_url"] == "https://malacky.gisplan.sk/mapa/uzemny-plan/"

    def test_gisplan_base_format(self):
        r = build_up_links("Bernolákovo")
        assert r["gisplan_base_url"] == "https://bernolakovo.gisplan.sk"

    def test_has_gisplan_none_without_check(self):
        import services.uzemny_plan_service as svc
        with _cache_lock:
            svc._gisplan_cache.pop("senec", None)
        r = build_up_links("Senec", check_gisplan=False)
        assert r["has_gisplan"] is None

    def test_fallback_links_nonempty(self):
        r = build_up_links("Senec")
        assert len(r["fallback_links"]) >= 3

    def test_fallback_contains_google(self):
        r = build_up_links("Senec")
        urls = [l["url"] for l in r["fallback_links"]]
        assert any("google" in u for u in urls)

    def test_fallback_contains_gisplan(self):
        r = build_up_links("Senec")
        urls = [l["url"] for l in r["fallback_links"]]
        assert any("gisplan" in u for u in urls)

    def test_fallback_count(self):
        r = build_up_links("Senec")
        assert len(r["fallback_links"]) >= 5

    def test_fallback_contains_obec_sk(self):
        r = build_up_links("Senec")
        urls = [l["url"] for l in r["fallback_links"]]
        assert any("senec.sk" in u for u in urls)

    def test_fallback_contains_zbgis(self):
        r = build_up_links("Senec")
        urls = [l["url"] for l in r["fallback_links"]]
        assert any("zbgis" in u for u in urls)

    def test_obec_name_preserved(self):
        r = build_up_links("Malacky, okres Malacky")
        assert r["obec"] == "Malacky"

    def test_empty_location(self):
        r = build_up_links("")
        assert r["obec_slug"] == ""
        assert r["gisplan_up_url"] == ""


class TestGetChecklist:
    def test_not_empty(self):
        c = get_checklist()
        assert len(c) >= 5

    def test_has_required_keys(self):
        for item in get_checklist():
            assert "id" in item
            assert "otazka" in item
            assert "kriticka" in item

    def test_has_kriticke_items(self):
        assert any(i["kriticka"] for i in get_checklist())

    def test_zona_byvania_je_kriticka(self):
        ids = {i["id"]: i["kriticka"] for i in get_checklist()}
        assert ids.get("zona_byvania") is True

    def test_zmena_up_je_kriticka(self):
        ids = {i["id"]: i["kriticka"] for i in get_checklist()}
        assert ids.get("zmena_up") is True


class TestIsGisplanAvailable:
    def _mock_resp(self, text, status=200):
        m = MagicMock()
        m.status_code = status
        m.text = text
        return m

    @patch("services.uzemny_plan_service.requests.get")
    def test_has_gisplan_marker(self, mock_req):
        import services.uzemny_plan_service as svc
        with _cache_lock: svc._gisplan_cache.pop("malacky", None)
        mock_req.return_value = self._mock_resp("GISPLAN mesta MALACKY")
        assert is_gisplan_available("malacky") is True

    @patch("services.uzemny_plan_service.requests.get")
    def test_no_gisplan_rocky(self, mock_req):
        import services.uzemny_plan_service as svc
        with _cache_lock: svc._gisplan_cache.pop("senec", None)
        mock_req.return_value = self._mock_resp("HTTP Server Test Page powered by: Rocky")
        assert is_gisplan_available("senec") is False

    @patch("services.uzemny_plan_service.requests.get")
    def test_404_returns_false(self, mock_req):
        import services.uzemny_plan_service as svc
        with _cache_lock: svc._gisplan_cache.pop("xyz", None)
        mock_req.return_value = self._mock_resp("", status=404)
        assert is_gisplan_available("xyz") is False

    @patch("services.uzemny_plan_service.requests.get")
    def test_exception_returns_false(self, mock_req):
        import services.uzemny_plan_service as svc
        with _cache_lock: svc._gisplan_cache.pop("err", None)
        mock_req.side_effect = Exception("connection error")
        assert is_gisplan_available("err") is False

    @patch("services.uzemny_plan_service.requests.get")
    def test_cached_result(self, mock_req):
        import services.uzemny_plan_service as svc
        with _cache_lock: svc._gisplan_cache["cached"] = True
        # get by sa nemal volat (z cache)
        assert is_gisplan_available("cached") is True
        mock_req.assert_not_called()

    @patch("services.uzemny_plan_service.requests.get")
    def test_build_up_links_with_check(self, mock_req):
        import services.uzemny_plan_service as svc
        with _cache_lock: svc._gisplan_cache.pop("modra", None)
        mock_req.return_value = self._mock_resp("Gisplan mesta Modra t-wist")
        r = build_up_links("Modrá", check_gisplan=True)
        assert r["has_gisplan"] is True
        assert r["gisplan_up_url"] == "https://modra.gisplan.sk/mapa/uzemny-plan/"
