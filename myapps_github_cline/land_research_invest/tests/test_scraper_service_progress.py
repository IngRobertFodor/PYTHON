"""Testy - scraper_service progress (thread-safe stav)
======================================================
Testuje: _reset_progress, _update_progress, _finish_progress,
         get_scrape_progress, percent vypocet, thread-safety.
100% offline - bez sieťových volaní.
"""

import pytest
import threading
from unittest.mock import patch, MagicMock

from services.scraper_service import (
    get_scrape_progress,
    _reset_progress,
    _update_progress,
    _finish_progress,
    _progress,
    _progress_lock,
)


def _clean():
    """Resetuj progress do vychodzieho stavu pred kazdym testom."""
    with _progress_lock:
        _progress["running"]       = False
        _progress["total"]         = 0
        _progress["done"]          = 0
        _progress["percent"]       = 0
        _progress["sources"]       = []
        _progress["per_source"]    = {}
        _progress["elapsed_s"]     = 0.0
        _progress["finished"]      = False
        _progress["total_parcels"] = 0


class TestResetProgress:
    def setup_method(self):
        _clean()

    def test_running_true_after_reset(self):
        _reset_progress(["a", "b"])
        assert get_scrape_progress()["running"] is True

    def test_total_set(self):
        _reset_progress(["a", "b", "c"])
        assert get_scrape_progress()["total"] == 3

    def test_done_zero(self):
        _reset_progress(["a", "b"])
        assert get_scrape_progress()["done"] == 0

    def test_percent_zero(self):
        _reset_progress(["a", "b"])
        assert get_scrape_progress()["percent"] == 0

    def test_sources_set(self):
        _reset_progress(["x", "y"])
        assert get_scrape_progress()["sources"] == ["x", "y"]

    def test_per_source_all_none(self):
        _reset_progress(["a", "b"])
        ps = get_scrape_progress()["per_source"]
        assert ps["a"] is None and ps["b"] is None

    def test_finished_false(self):
        _reset_progress(["a"])
        assert get_scrape_progress()["finished"] is False

    def test_total_parcels_zero(self):
        _reset_progress(["a"])
        assert get_scrape_progress()["total_parcels"] == 0

    def test_empty_sources(self):
        _reset_progress([])
        p = get_scrape_progress()
        assert p["total"] == 0 and p["sources"] == []


class TestUpdateProgress:
    def setup_method(self):
        _clean()
        _reset_progress(["a", "b", "c", "d"])

    def test_done_increments(self):
        _update_progress("a", 10, 5.0)
        assert get_scrape_progress()["done"] == 1

    def test_per_source_updated(self):
        _update_progress("b", 42, 3.0)
        assert get_scrape_progress()["per_source"]["b"] == 42

    def test_percent_1_of_4(self):
        _update_progress("a", 0, 1.0)
        assert get_scrape_progress()["percent"] == 25

    def test_percent_2_of_4(self):
        _update_progress("a", 0, 1.0)
        _update_progress("b", 0, 2.0)
        assert get_scrape_progress()["percent"] == 50

    def test_percent_4_of_4(self):
        for s in ["a", "b", "c", "d"]:
            _update_progress(s, 0, 1.0)
        assert get_scrape_progress()["percent"] == 100

    def test_total_parcels_accumulates(self):
        _update_progress("a", 100, 1.0)
        _update_progress("b", 50, 2.0)
        assert get_scrape_progress()["total_parcels"] == 150

    def test_elapsed_updated(self):
        _update_progress("a", 0, 7.5)
        assert get_scrape_progress()["elapsed_s"] == 7.5


class TestFinishProgress:
    def setup_method(self):
        _clean()
        _reset_progress(["a", "b"])
        for s in ["a", "b"]:
            _update_progress(s, 10, 1.0)

    def test_running_false(self):
        _finish_progress(15.0)
        assert get_scrape_progress()["running"] is False

    def test_finished_true(self):
        _finish_progress(15.0)
        assert get_scrape_progress()["finished"] is True

    def test_elapsed_set(self):
        _finish_progress(15.0)
        assert get_scrape_progress()["elapsed_s"] == 15.0

    def test_percent_100(self):
        _finish_progress(15.0)
        assert get_scrape_progress()["percent"] == 100


class TestGetScrapeProgress:
    def setup_method(self):
        _clean()

    def test_returns_dict(self):
        assert isinstance(get_scrape_progress(), dict)

    def test_has_required_keys(self):
        p = get_scrape_progress()
        for key in ["running", "total", "done", "percent", "sources",
                    "per_source", "elapsed_s", "finished", "total_parcels"]:
            assert key in p, f"Chybajuci kluc: {key}"

    def test_returns_copy(self):
        """Zmena vrateného dict nesmie zmeniť interný stav."""
        p = get_scrape_progress()
        p["running"] = True
        assert get_scrape_progress()["running"] is False

    def test_thread_safe_concurrent_reads(self):
        """Sučasné čítanie z viacerých threadov nesmie crashnúť."""
        results = []
        def reader():
            for _ in range(50):
                results.append(get_scrape_progress())
        threads = [threading.Thread(target=reader) for _ in range(5)]
        for t in threads: t.start()
        for t in threads: t.join()
        assert len(results) == 250
        assert all(isinstance(r, dict) for r in results)
