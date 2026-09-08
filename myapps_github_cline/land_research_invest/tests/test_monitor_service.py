"""Testy - Monitor sluzba (periodicky scan)
==========================================
Testuje ScanResult, run_scan, start/stop, get_status a monitor routes.
100% offline - APScheduler a scraper_service su mocknutelne.
"""

import pytest
import time
from unittest.mock import patch, MagicMock
from models.parcel import Parcel
from models.result import ServiceResult
from services.monitor_service import (
    ScanResult, run_scan, get_status, start, stop,
    APSCHEDULER_AVAILABLE,
)
from app import create_app

MODULE = "services.monitor_service"


@pytest.fixture
def client():
    app = create_app({"TESTING": True})
    with app.test_client() as c:
        yield c


def make_parcel(score=80.0):
    p = Parcel(
        title="Test", url="https://x.com/1",
        price_eur=35000, area_sqm=800,
        location_text="Senec",
    )
    p.final_score    = score
    p.recommendation = "INVESTIGATE"
    return p


def ok_provider(n=3):
    return [make_parcel(80.0 + i) for i in range(n)]


def empty_provider():
    return []


def crash_provider():
    raise RuntimeError("network down")


# ----------------------------------------------------------------
# TestScanResult
# ----------------------------------------------------------------

class TestScanResult:
    def test_defaults(self):
        r = ScanResult()
        assert r.scanned == 0
        assert r.notified == 0
        assert r.errors == 0
        assert r.duration_s == 0.0
        assert r.timestamp == ""

    def test_to_dict_keys(self):
        r = ScanResult(scanned=3, notified=1, errors=0, duration_s=1.5, timestamp="2026-01-01T00:00:00")
        d = r.to_dict()
        assert set(d.keys()) == {"scanned", "notified", "errors", "duration_s", "timestamp"}

    def test_to_dict_values(self):
        r = ScanResult(scanned=5, notified=2, errors=1)
        d = r.to_dict()
        assert d["scanned"] == 5
        assert d["notified"] == 2
        assert d["errors"] == 1

    def test_to_dict_duration_rounded(self):
        r = ScanResult(duration_s=1.23456)
        assert r.to_dict()["duration_s"] == pytest.approx(1.23, abs=0.01)


# ----------------------------------------------------------------
# TestRunScan
# ----------------------------------------------------------------

class TestRunScan:
    def test_empty_provider_returns_result(self):
        result = run_scan(empty_provider)
        assert isinstance(result, ScanResult)
        assert result.scanned == 0

    def test_n_parcels_scanned(self):
        with patch(MODULE + ".analyze_parcel") as mock_analyze, \
             patch(MODULE + ".notify_parcel",
                   return_value=ServiceResult.skip_result("notifier_service", "test")):
            mock_analyze.side_effect = lambda p: p
            result = run_scan(lambda: ok_provider(3))
        assert result.scanned == 3

    def test_errors_counted(self):
        def bad_analyze(p):
            raise ValueError("bad parcel")
        with patch(MODULE + ".analyze_parcel", side_effect=bad_analyze):
            result = run_scan(lambda: ok_provider(2))
        assert result.errors == 2
        assert result.scanned == 0

    def test_one_error_does_not_stop_others(self):
        call_count = {"n": 0}
        def sometimes_fail(p):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise ValueError("first fails")
        with patch(MODULE + ".analyze_parcel", side_effect=sometimes_fail), \
             patch(MODULE + ".notify_parcel",
                   return_value=ServiceResult.skip_result("notifier_service", "t")):
            result = run_scan(lambda: ok_provider(3))
        assert result.errors == 1
        assert result.scanned == 2

    def test_provider_crash_returns_error_result(self):
        result = run_scan(crash_provider)
        assert result.errors >= 1
        assert result.scanned == 0

    def test_result_has_timestamp(self):
        with patch(MODULE + ".analyze_parcel"), \
             patch(MODULE + ".notify_parcel",
                   return_value=ServiceResult.skip_result("notifier_service", "t")):
            result = run_scan(empty_provider)
        assert result.timestamp != ""

    def test_notified_counted(self):
        notif_result = ServiceResult(
            ok=True, score=100.0,
            data={"notified": True, "channels": ["telegram"]},
            source="notifier_service"
        )
        with patch(MODULE + ".analyze_parcel") as ma, \
             patch(MODULE + ".notify_parcel", return_value=notif_result):
            ma.side_effect = lambda p: p
            result = run_scan(lambda: ok_provider(2))
        assert result.notified == 2

    def test_max_parcels_respected(self):
        analyzed = []
        with patch(MODULE + ".analyze_parcel", side_effect=lambda p: analyzed.append(p)), \
             patch(MODULE + ".notify_parcel",
                   return_value=ServiceResult.skip_result("notifier_service", "t")), \
             patch(MODULE + ".get_periodic_scan", return_value={"max_parcels_per_scan": 2, "interval_minutes": 60}):
            run_scan(lambda: ok_provider(10))
        assert len(analyzed) <= 2

    def test_duration_positive(self):
        with patch(MODULE + ".analyze_parcel"), \
             patch(MODULE + ".notify_parcel",
                   return_value=ServiceResult.skip_result("notifier_service", "t")):
            result = run_scan(empty_provider)
        assert result.duration_s >= 0.0


# ----------------------------------------------------------------
# TestGetStatus
# ----------------------------------------------------------------

class TestGetStatus:
    def test_returns_dict(self):
        assert isinstance(get_status(), dict)

    def test_has_required_keys(self):
        s = get_status()
        assert "running" in s
        assert "interval_minutes" in s
        assert "next_run_iso" in s
        assert "last_result" in s

    def test_not_running_by_default(self):
        stop()  # ensure stopped
        assert get_status()["running"] is False

    def test_last_result_none_before_scan(self):
        import services.monitor_service as ms
        ms._last_result = None
        assert get_status()["last_result"] is None

    def test_last_result_after_scan(self):
        with patch(MODULE + ".analyze_parcel"), \
             patch(MODULE + ".notify_parcel",
                   return_value=ServiceResult.skip_result("notifier_service", "t")):
            run_scan(empty_provider)
        assert get_status()["last_result"] is not None


# ----------------------------------------------------------------
# TestStartStop
# ----------------------------------------------------------------

class TestStartStop:
    def test_start_does_nothing_when_monitoring_disabled(self):
        with patch(MODULE + ".is_feature_enabled", return_value=False):
            start()  # nema hodit vynimku
        assert get_status()["running"] is False

    def test_stop_safe_when_not_running(self):
        stop()  # nema hodit vynimku
        stop()  # druhe volanie tiez bezpecne


# ----------------------------------------------------------------
# TestMonitorRoutes
# ----------------------------------------------------------------

class TestMonitorRoutes:
    def test_status_returns_200(self, client):
        r = client.get("/api/monitor/status")
        assert r.status_code == 200

    def test_status_has_running_key(self, client):
        data = client.get("/api/monitor/status").get_json()
        assert "running" in data

    def test_status_has_interval(self, client):
        data = client.get("/api/monitor/status").get_json()
        assert "interval_minutes" in data

    def test_scan_endpoint_returns_200(self, client):
        with patch("routes.monitor_routes.run_scan",
                   return_value=ScanResult(scanned=2, notified=0, errors=0,
                                           duration_s=0.5, timestamp="2026-01-01T00:00:00")):
            r = client.post("/api/monitor/scan")
        assert r.status_code == 200

    def test_scan_endpoint_returns_scan_result(self, client):
        with patch("routes.monitor_routes.run_scan",
                   return_value=ScanResult(scanned=3, notified=1, errors=0,
                                           duration_s=1.2, timestamp="2026-01-01T00:00:00")):
            data = client.post("/api/monitor/scan").get_json()
        assert data["scanned"] == 3
        assert data["notified"] == 1

    def test_scan_endpoint_error_returns_500(self, client):
        with patch("routes.monitor_routes.run_scan", side_effect=RuntimeError("crash")):
            r = client.post("/api/monitor/scan")
        assert r.status_code == 500
