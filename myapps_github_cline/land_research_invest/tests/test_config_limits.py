"""Testy - POST /api/config/limits
===================================
100% offline - criteria.yaml sa pise do tmp adresara (fixture).
Povodny criteria.yaml zostava nedotknuty.
"""
import os
import shutil
import pytest
from app import create_app


@pytest.fixture
def tmp_config(tmp_path):
    """Kopiruje criteria.yaml do tmp; patchne config_loader._CONFIG_PATH."""
    import config_loader as cl
    real_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "config", "criteria.yaml"))
    tmp_yaml = str(tmp_path / "criteria.yaml")
    shutil.copy2(real_path, tmp_yaml)
    orig_path, orig_cache = cl._CONFIG_PATH, cl._config_cache
    cl._CONFIG_PATH  = tmp_yaml
    cl._config_cache = None
    yield tmp_yaml
    cl._CONFIG_PATH  = orig_path
    cl._config_cache = None


@pytest.fixture
def client(tmp_config):
    app = create_app({"TESTING": True})
    with app.test_client() as c:
        yield c


def _post(client, payload):
    import json
    return client.post("/api/config/limits",
                       data=json.dumps(payload),
                       content_type="application/json")


class TestUpdateLimitsBasic:

    def test_200_single_field(self, client):
        assert _post(client, {"max_eur": 50000}).status_code == 200

    def test_ok_true(self, client):
        assert _post(client, {"max_eur": 50000}).get_json()["ok"] is True

    def test_saved_field_present(self, client):
        d = _post(client, {"max_eur": 60000}).get_json()
        assert d["saved"]["max_eur"] == 60000

    def test_criteria_in_response(self, client):
        assert "criteria" in _post(client, {"max_distance_km": 70}).get_json()

    def test_all_four_fields(self, client):
        p = {"max_eur": 45000, "min_area_sqm": 400,
             "max_area_sqm": 900, "max_distance_km": 60}
        d = _post(client, p).get_json()
        assert d["ok"] is True and d["saved"] == p

    def test_get_config_reflects_saved(self, client):
        _post(client, {"max_eur": 77777})
        assert client.get("/api/config/").get_json()["criteria"]["price"]["max_eur"] == 77777

    def test_value_persisted_in_yaml(self, client, tmp_config):
        import yaml
        _post(client, {"max_distance_km": 55})
        with open(tmp_config, encoding="utf-8") as f:
            assert yaml.safe_load(f)["criteria"]["location"]["max_distance_km"] == 55

    def test_bak_file_created(self, client, tmp_config):
        _post(client, {"max_eur": 30000})
        assert os.path.exists(tmp_config + ".bak")


class TestUpdateLimitsValidation:

    def test_empty_body_400(self, client):
        assert _post(client, {}).status_code == 400

    def test_empty_body_ok_false(self, client):
        assert _post(client, {}).get_json()["ok"] is False

    def test_unknown_field_only_400(self, client):
        assert _post(client, {"weights": {"price": 0.99}}).status_code == 400

    def test_string_value_400(self, client):
        assert _post(client, {"max_eur": "vela"}).status_code == 400

    def test_negative_max_eur_400(self, client):
        assert _post(client, {"max_eur": -1}).status_code == 400

    def test_min_area_greater_than_max_400(self, client):
        assert _post(client, {"min_area_sqm": 900, "max_area_sqm": 100}).status_code == 400

    def test_zero_distance_400(self, client):
        assert _post(client, {"max_distance_km": 0}).status_code == 400

    def test_invalid_does_not_modify_yaml(self, client, tmp_config):
        import yaml
        with open(tmp_config, encoding="utf-8") as f:
            before = yaml.safe_load(f)["criteria"]["price"]["max_eur"]
        _post(client, {"max_eur": -999})
        with open(tmp_config, encoding="utf-8") as f:
            after = yaml.safe_load(f)["criteria"]["price"]["max_eur"]
        assert before == after

    def test_non_json_400(self, client):
        r = client.post("/api/config/limits", data="max_eur=50000",
                        content_type="application/x-www-form-urlencoded")
        assert r.status_code == 400


class TestUpdateLimitsWhitelist:

    def test_weights_not_changed(self, client, tmp_config):
        import yaml
        with open(tmp_config, encoding="utf-8") as f:
            orig = yaml.safe_load(f)["scoring"]["weights"].copy()
        _post(client, {"max_eur": 40000, "weights": {"price": 0.99}})
        with open(tmp_config, encoding="utf-8") as f:
            assert yaml.safe_load(f)["scoring"]["weights"] == orig

    def test_sources_not_changed(self, client, tmp_config):
        import yaml
        with open(tmp_config, encoding="utf-8") as f:
            orig = yaml.safe_load(f)["sources"]
        _post(client, {"max_eur": 40000,
                       "sources": {"facebook_marketplace": {"enabled": True}}})
        with open(tmp_config, encoding="utf-8") as f:
            assert yaml.safe_load(f)["sources"] == orig

    def test_unknown_key_not_in_saved(self, client):
        d = _post(client, {"max_eur": 50000, "hacker": "evil"}).get_json()
        if d.get("ok"):
            assert "hacker" not in d["saved"]


class TestExistingEndpointsUnchanged:

    def test_get_config_200(self, client):
        assert client.get("/api/config/").status_code == 200

    def test_get_config_has_scoring(self, client):
        assert "scoring" in client.get("/api/config/").get_json()

    def test_get_config_has_criteria(self, client):
        assert "criteria" in client.get("/api/config/").get_json()

    def test_get_validate_200(self, client):
        assert client.get("/api/config/validate").status_code == 200

    def test_get_validate_has_valid(self, client):
        assert "valid" in client.get("/api/config/validate").get_json()
