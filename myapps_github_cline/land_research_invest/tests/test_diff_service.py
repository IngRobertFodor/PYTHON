import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "backend"))
import pytest
from services.diff_service import compute_diff, DROP_PCT

def p(url, price=5000, score=70, src="nehnutelnosti_sk"):
    return {"url": url, "price_eur": price, "preliminary_score": score,
            "source_portal": src, "title": url, "location_text": "Senec"}

A1 = p("http://x/1", 5000, 90)
A2 = p("http://x/2", 3000, 75)
A3 = p("http://x/3", 8000, 60)
A1_cheap = dict(A1, price_eur=4000)   # zlacnenie o 20 %
A1_tiny  = dict(A1, price_eur=4950)   # pokles 1 % -> pod DROP_PCT

PREV = [A1, A2]
CURR_SAME = [A1, A2]
CURR_NEW  = [A1, A2, A3]          # A3 je nova
CURR_DEL  = [A1]                   # A2 zmizla
CURR_DROP = [A1_cheap, A2]         # A1 zlacnela
CURR_TINY = [A1_tiny,  A2]         # A1 len mierne zlacnela


class TestComputeDiffSummary:
    def test_same_no_changes(self):
        d = compute_diff(PREV, CURR_SAME)
        s = d["summary"]
        assert s["new"] == 0 and s["removed"] == 0 and s["price_dropped"] == 0

    def test_new_detected(self):
        d = compute_diff(PREV, CURR_NEW)
        assert d["summary"]["new"] == 1
        assert d["new"][0]["url"] == "http://x/3"

    def test_removed_detected(self):
        d = compute_diff(PREV, CURR_DEL)
        assert d["summary"]["removed"] == 1
        assert d["removed"][0]["url"] == "http://x/2"

    def test_price_drop_detected(self):
        d = compute_diff(PREV, CURR_DROP)
        assert d["summary"]["price_dropped"] == 1
        e = d["price_dropped"][0]
        assert e["url"] == "http://x/1"
        assert e["price_prev"] == 5000
        assert e["price_curr"] == 4000
        assert e["drop_pct"] == pytest.approx(20.0, abs=0.1)

    def test_tiny_price_drop_ignored(self):
        d = compute_diff(PREV, CURR_TINY)
        assert d["summary"]["price_dropped"] == 0

    def test_still_here_count(self):
        d = compute_diff(PREV, CURR_SAME)
        assert d["still_here"] == 2

    def test_still_here_minus_dropped(self):
        d = compute_diff(PREV, CURR_DROP)
        # A1 je dropped, A2 je still_here -> 1
        assert d["still_here"] == 1


class TestComputeDiffContent:
    def test_new_sorted_by_score(self):
        curr = [p("http://x/4", score=50), p("http://x/5", score=90), A1, A2]
        d = compute_diff(PREV, curr)
        scores = [n["preliminary_score"] for n in d["new"]]
        assert scores == sorted(scores, reverse=True)

    def test_price_dropped_sorted_by_drop_pct(self):
        a1_big  = dict(A1, price_eur=2000)   # pokles 60 %
        a2_small = dict(A2, price_eur=2700)  # pokles 10 %
        d = compute_diff([A1, A2], [a1_big, a2_small])
        pcts = [e["drop_pct"] for e in d["price_dropped"]]
        assert pcts == sorted(pcts, reverse=True)

    def test_removed_contains_prev_data(self):
        d = compute_diff(PREV, CURR_DEL)
        assert d["removed"][0]["price_eur"] == 3000

    def test_empty_prev(self):
        d = compute_diff([], CURR_NEW)
        assert d["summary"]["new"] == 3
        assert d["summary"]["removed"] == 0

    def test_empty_curr(self):
        d = compute_diff(PREV, [])
        assert d["summary"]["removed"] == 2
        assert d["summary"]["new"] == 0

    def test_both_empty(self):
        d = compute_diff([], [])
        assert d["summary"] == {"new": 0, "removed": 0, "price_dropped": 0, "still_here": 0}

    def test_price_increase_not_reported(self):
        a1_expensive = dict(A1, price_eur=6000)
        d = compute_diff(PREV, [a1_expensive, A2])
        assert d["summary"]["price_dropped"] == 0

    def test_zero_price_not_reported_as_drop(self):
        a1_zero = dict(A1, price_eur=0)
        d = compute_diff(PREV, [a1_zero, A2])
        assert d["summary"]["price_dropped"] == 0

    def test_parcels_missing_url_skipped(self):
        bad = {"title": "bez url", "price_eur": 1000}
        d = compute_diff([bad], [bad])
        assert d["summary"]["new"] == 0

    def test_drop_pct_boundary(self):
        # presne DROP_PCT % -> musi byt zahrnuty
        exact_drop = dict(A1, price_eur=round(5000 * (1 - DROP_PCT / 100), 2))
        d = compute_diff([A1], [exact_drop])
        assert d["summary"]["price_dropped"] == 1
