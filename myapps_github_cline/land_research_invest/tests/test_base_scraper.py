"""Testy - BaseScraper (retry logika, timeout, user-agent)
==========================================================
Testuje:
  - fetch_html retry pri ReadTimeout / ConnectTimeout / ConnectionError
  - MAX_RETRIES = 2 opakovania, exponencialny backoff
  - per-source timeout (timeout_sec z config, default DEFAULT_TIMEOUT)
  - user_agent prepinanie (neutral vs AI-bot)
100% offline - mocked requests.
"""

import pytest
from unittest.mock import patch, MagicMock
from requests.exceptions import ReadTimeout, ConnectTimeout
from requests.exceptions import ConnectionError as ReqConnectionError

from services.scrapers.base_scraper import (
    BaseScraper,
    DEFAULT_USER_AGENT,
    AI_BOT_USER_AGENT,
    RETRY_DELAY,
    RETRY_DELAY2,
    MAX_RETRIES,
    DEFAULT_TIMEOUT,
)


class DummyScraper(BaseScraper):
    SOURCE_NAME = "dummy_test"
    BASE_URL    = "https://example.com"
    def parse_listings(self, html):
        return []


def _make(rate_limit=0, neutral_ua=False, timeout=DEFAULT_TIMEOUT):
    s = DummyScraper.__new__(DummyScraper)
    s.rate_limit = rate_limit
    s.neutral_ua = neutral_ua
    s.timeout    = timeout
    s._last_call = 0.0
    return s


class TestUserAgent:
    def test_neutral_ua_is_mozilla(self):
        assert "Mozilla" in _make(neutral_ua=True).user_agent

    def test_non_neutral_ua_is_ai_bot(self):
        assert "LandResearch" in _make(neutral_ua=False).user_agent

    def test_neutral_ua_equals_default_ua(self):
        assert _make(neutral_ua=True).user_agent == DEFAULT_USER_AGENT

    def test_non_neutral_ua_equals_ai_bot_ua(self):
        assert _make(neutral_ua=False).user_agent == AI_BOT_USER_AGENT



class TestRetryReadTimeout:
    def _ok_resp(self):
        r = MagicMock(); r.text = "<html>OK</html>"; r.raise_for_status = MagicMock()
        return r

    def test_success_on_first_try(self):
        with patch("requests.get", return_value=self._ok_resp()) as mg:
            assert _make().fetch_html("https://example.com/") == "<html>OK</html>"
        assert mg.call_count == 1

    def test_retry_on_read_timeout(self):
        with patch("requests.get", side_effect=[ReadTimeout(), self._ok_resp()]) as mg:
            with patch("time.sleep"):
                assert _make().fetch_html("https://example.com/") == "<html>OK</html>"
        assert mg.call_count == 2

    def test_retry_on_connect_timeout(self):
        with patch("requests.get", side_effect=[ConnectTimeout(), self._ok_resp()]) as mg:
            with patch("time.sleep"):
                _make().fetch_html("https://example.com/")
        assert mg.call_count == 2

    def test_retry_on_connection_error(self):
        with patch("requests.get", side_effect=[ReqConnectionError(), self._ok_resp()]) as mg:
            with patch("time.sleep"):
                _make().fetch_html("https://example.com/")
        assert mg.call_count == 2

    def test_two_retries_second_succeeds(self):
        with patch("requests.get", side_effect=[ReadTimeout(), ReadTimeout(), self._ok_resp()]) as mg:
            with patch("time.sleep") as ms:
                _make().fetch_html("https://example.com/")
        assert mg.call_count == 3
        sleep_vals = [c.args[0] for c in ms.call_args_list]
        assert RETRY_DELAY in sleep_vals
        assert RETRY_DELAY2 in sleep_vals

    def test_raises_after_max_retries(self):
        with patch("requests.get", side_effect=[ReadTimeout()] * (MAX_RETRIES + 1)):
            with patch("time.sleep"):
                with pytest.raises(ReadTimeout):
                    _make().fetch_html("https://example.com/")

    def test_total_attempts_max_retries_plus_one(self):
        with patch("requests.get", side_effect=[ReadTimeout()] * (MAX_RETRIES + 1)) as mg:
            with patch("time.sleep"):
                with pytest.raises(ReadTimeout):
                    _make().fetch_html("https://example.com/")
        assert mg.call_count == MAX_RETRIES + 1


class TestPerSourceTimeout:
    def _ok(self):
        r = MagicMock(); r.text = "OK"; r.raise_for_status = MagicMock()
        return r

    def test_uses_custom_timeout_30(self):
        with patch("requests.get", return_value=self._ok()) as mg:
            _make(timeout=30).fetch_html("https://example.com/")
        assert mg.call_args[1]["timeout"] == 30

    def test_uses_default_timeout_20(self):
        with patch("requests.get", return_value=self._ok()) as mg:
            _make(timeout=DEFAULT_TIMEOUT).fetch_html("https://example.com/")
        assert mg.call_args[1]["timeout"] == DEFAULT_TIMEOUT

    def test_default_timeout_value(self):
        assert DEFAULT_TIMEOUT == 20


class TestRetryConstants:
    def test_max_retries_is_2(self):
        assert MAX_RETRIES == 2

    def test_retry_delay2_gt_delay1(self):
        assert RETRY_DELAY2 > RETRY_DELAY

    def test_retry_delay_positive(self):
        assert RETRY_DELAY > 0
