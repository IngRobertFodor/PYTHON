"""Testy - Notifikacna sluzba
==============================
Testuje rozhodovanie, formatovanie sprav a odosielanie.
100% offline - requests a smtplib su mocknutelne.
"""

import pytest
from unittest.mock import patch, MagicMock
from models.parcel  import Parcel
from models.result  import ServiceResult
from services.notifier_service import (
    notify_parcel,
    should_notify,
    format_telegram_message,
    format_email_message,
    send_telegram,
    send_email,
    _get_env,
)

MODULE = "services.notifier_service"


# ----------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------

def make_parcel(score=82.0, rec="INVESTIGATE", **kw):
    defaults = dict(
        title="Pozemok Senec",
        url="https://example.com/1234",
        location_text="Senec",
        price_eur=35000.0,
        area_sqm=800.0,
        final_score=score,
        recommendation=rec,
    )
    defaults.update(kw)
    return Parcel(**defaults)


def notif_cfg(min_score=75, telegram=False, email=False):
    return {
        "min_score_to_notify": min_score,
        "channels": {"telegram": telegram, "email": email},
        "telegram": {
            "bot_token_env": "TELEGRAM_BOT_TOKEN",
            "chat_id_env":   "TELEGRAM_CHAT_ID",
        },
        "email": {
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "from_env":     "EMAIL_FROM",
            "to_env":       "EMAIL_TO",
            "password_env": "EMAIL_PASSWORD",
        },
    }


# ----------------------------------------------------------------
# TestGetEnv
# ----------------------------------------------------------------

class TestGetEnv:
    def test_returns_value_when_set(self):
        with patch.dict("os.environ", {"MY_VAR": "hello"}):
            assert _get_env("MY_VAR") == "hello"

    def test_returns_none_when_missing(self):
        with patch.dict("os.environ", {}, clear=True):
            assert _get_env("NONEXISTENT_VAR") is None

    def test_returns_none_for_empty_name(self):
        assert _get_env("") is None

    def test_returns_none_for_none_name(self):
        assert _get_env(None) is None


# ----------------------------------------------------------------
# TestShouldNotify
# ----------------------------------------------------------------

class TestShouldNotify:
    def test_score_above_threshold_telegram_on(self):
        p = make_parcel(score=80.0)
        reason, result = should_notify(p, notif_cfg(min_score=75, telegram=True))
        assert result is True

    def test_score_below_threshold(self):
        p = make_parcel(score=60.0)
        reason, result = should_notify(p, notif_cfg(min_score=75, telegram=True))
        assert result is False
        assert "60" in reason or "75" in reason

    def test_score_equal_threshold(self):
        p = make_parcel(score=75.0)
        reason, result = should_notify(p, notif_cfg(min_score=75, telegram=True))
        assert result is True

    def test_no_channels_enabled(self):
        p = make_parcel(score=90.0)
        reason, result = should_notify(p, notif_cfg(min_score=75, telegram=False, email=False))
        assert result is False
        assert "kanal" in reason.lower()

    def test_email_channel_sufficient(self):
        p = make_parcel(score=80.0)
        reason, result = should_notify(p, notif_cfg(min_score=75, telegram=False, email=True))
        assert result is True

    def test_both_channels_enabled(self):
        p = make_parcel(score=90.0)
        reason, result = should_notify(p, notif_cfg(min_score=75, telegram=True, email=True))
        assert result is True


# ----------------------------------------------------------------
# TestFormatTelegramMessage
# ----------------------------------------------------------------

class TestFormatTelegramMessage:
    def test_returns_string(self):
        assert isinstance(format_telegram_message(make_parcel()), str)

    def test_contains_score(self):
        assert "82.0" in format_telegram_message(make_parcel(score=82.0))

    def test_contains_recommendation(self):
        assert "INVESTIGATE" in format_telegram_message(make_parcel(rec="INVESTIGATE"))

    def test_contains_price(self):
        p = make_parcel()
        assert "35" in format_telegram_message(p)

    def test_contains_location(self):
        p = make_parcel(location_text="Senec")
        assert "Senec" in format_telegram_message(p)

    def test_contains_url(self):
        p = make_parcel(url="https://example.com/xyz")
        assert "https://example.com/xyz" in format_telegram_message(p)

    def test_strong_buy_icon(self):
        p = make_parcel(rec="STRONG BUY")
        assert "[**]" in format_telegram_message(p)

    def test_skip_icon(self):
        p = make_parcel(rec="SKIP")
        assert "[XX]" in format_telegram_message(p)


# ----------------------------------------------------------------
# TestFormatEmailMessage
# ----------------------------------------------------------------

class TestFormatEmailMessage:
    def test_returns_tuple(self):
        result = format_email_message(make_parcel())
        assert isinstance(result, tuple) and len(result) == 2

    def test_subject_contains_recommendation(self):
        subject, _ = format_email_message(make_parcel(rec="STRONG BUY"))
        assert "STRONG BUY" in subject

    def test_subject_contains_score(self):
        subject, _ = format_email_message(make_parcel(score=88.0))
        assert "88.0" in subject

    def test_subject_contains_location(self):
        subject, _ = format_email_message(make_parcel(location_text="Pezinok"))
        assert "Pezinok" in subject

    def test_body_is_string(self):
        _, body = format_email_message(make_parcel())
        assert isinstance(body, str) and len(body) > 0

    def test_body_contains_score_section(self):
        _, body = format_email_message(make_parcel())
        assert "CELKOVE SKORE" in body or "SKORE" in body


# ----------------------------------------------------------------
# TestSendTelegram
# ----------------------------------------------------------------

class TestSendTelegram:
    def test_raises_when_token_missing(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="TELEGRAM_BOT_TOKEN"):
                send_telegram("test", {"bot_token_env": "TELEGRAM_BOT_TOKEN",
                                         "chat_id_env": "TELEGRAM_CHAT_ID"})

    def test_raises_when_chat_id_missing(self):
        with patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "tok123"}):
            with pytest.raises(ValueError, match="TELEGRAM_CHAT_ID"):
                send_telegram("test", {"bot_token_env": "TELEGRAM_BOT_TOKEN",
                                         "chat_id_env": "TELEGRAM_CHAT_ID"})

    def test_calls_requests_post(self):
        env = {"TELEGRAM_BOT_TOKEN": "tok123", "TELEGRAM_CHAT_ID": "chat456"}
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        with patch.dict("os.environ", env):
            with patch(MODULE + ".requests.post", return_value=mock_resp) as mock_post:
                send_telegram("hello", {"bot_token_env": "TELEGRAM_BOT_TOKEN",
                                          "chat_id_env": "TELEGRAM_CHAT_ID"})
                mock_post.assert_called_once()

    def test_raises_on_http_error(self):
        env = {"TELEGRAM_BOT_TOKEN": "tok123", "TELEGRAM_CHAT_ID": "chat456"}
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = Exception("HTTP 429")
        with patch.dict("os.environ", env):
            with patch(MODULE + ".requests.post", return_value=mock_resp):
                with pytest.raises(Exception, match="HTTP 429"):
                    send_telegram("hello", {"bot_token_env": "TELEGRAM_BOT_TOKEN",
                                              "chat_id_env": "TELEGRAM_CHAT_ID"})


# ----------------------------------------------------------------
# TestSendEmail
# ----------------------------------------------------------------

class TestSendEmail:
    def test_raises_when_credentials_missing(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="EMAIL_FROM"):
                send_email("subj", "body",
                           {"from_env": "EMAIL_FROM", "to_env": "EMAIL_TO",
                            "password_env": "EMAIL_PASSWORD"})

    def test_calls_smtp(self):
        env = {"EMAIL_FROM": "a@b.com", "EMAIL_TO": "c@d.com",
               "EMAIL_PASSWORD": "pass123"}
        mock_smtp = MagicMock()
        mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
        mock_smtp.__exit__  = MagicMock(return_value=False)
        with patch.dict("os.environ", env):
            with patch(MODULE + ".smtplib.SMTP", return_value=mock_smtp):
                send_email("subj", "body",
                           {"smtp_host": "smtp.gmail.com", "smtp_port": 587,
                            "from_env": "EMAIL_FROM", "to_env": "EMAIL_TO",
                            "password_env": "EMAIL_PASSWORD"})
                mock_smtp.login.assert_called_once()
                mock_smtp.sendmail.assert_called_once()


# ----------------------------------------------------------------
# TestNotifyParcel
# ----------------------------------------------------------------

class TestNotifyParcel:
    def test_skip_when_feature_off(self):
        with patch(MODULE + ".is_feature_enabled", return_value=False):
            r = notify_parcel(make_parcel(score=90.0))
        assert r.data.get("skipped") is True

    def test_not_notified_below_threshold(self):
        cfg = notif_cfg(min_score=75, telegram=True)
        with patch(MODULE + ".is_feature_enabled", return_value=True), \
             patch(MODULE + ".get_notifications", return_value=cfg):
            r = notify_parcel(make_parcel(score=60.0))
        assert r.ok is True
        assert r.data["notified"] is False

    def test_not_notified_no_channels(self):
        cfg = notif_cfg(min_score=75, telegram=False, email=False)
        with patch(MODULE + ".is_feature_enabled", return_value=True), \
             patch(MODULE + ".get_notifications", return_value=cfg):
            r = notify_parcel(make_parcel(score=90.0))
        assert r.data["notified"] is False

    def test_notified_via_telegram(self):
        cfg = notif_cfg(min_score=75, telegram=True)
        with patch(MODULE + ".is_feature_enabled", return_value=True), \
             patch(MODULE + ".get_notifications", return_value=cfg), \
             patch(MODULE + ".send_telegram") as mock_tg:
            r = notify_parcel(make_parcel(score=85.0))
        assert r.ok is True
        assert r.data["notified"] is True
        assert "telegram" in r.data["channels"]
        mock_tg.assert_called_once()

    def test_notified_via_email(self):
        cfg = notif_cfg(min_score=75, email=True)
        with patch(MODULE + ".is_feature_enabled", return_value=True), \
             patch(MODULE + ".get_notifications", return_value=cfg), \
             patch(MODULE + ".send_email") as mock_em:
            r = notify_parcel(make_parcel(score=85.0))
        assert r.ok is True
        assert "email" in r.data["channels"]
        mock_em.assert_called_once()

    def test_both_channels_called(self):
        cfg = notif_cfg(min_score=75, telegram=True, email=True)
        with patch(MODULE + ".is_feature_enabled", return_value=True), \
             patch(MODULE + ".get_notifications", return_value=cfg), \
             patch(MODULE + ".send_telegram") as mock_tg, \
             patch(MODULE + ".send_email") as mock_em:
            r = notify_parcel(make_parcel(score=90.0))
        assert len(r.data["channels"]) == 2
        mock_tg.assert_called_once()
        mock_em.assert_called_once()

    def test_telegram_error_falls_back_to_email(self):
        cfg = notif_cfg(min_score=75, telegram=True, email=True)
        with patch(MODULE + ".is_feature_enabled", return_value=True), \
             patch(MODULE + ".get_notifications", return_value=cfg), \
             patch(MODULE + ".send_telegram", side_effect=ValueError("no token")), \
             patch(MODULE + ".send_email"):
            r = notify_parcel(make_parcel(score=90.0))
        assert r.ok is True
        assert "email" in r.data["channels"]
        assert len(r.data["errors"]) == 1

    def test_all_channels_fail_returns_error(self):
        cfg = notif_cfg(min_score=75, telegram=True)
        with patch(MODULE + ".is_feature_enabled", return_value=True), \
             patch(MODULE + ".get_notifications", return_value=cfg), \
             patch(MODULE + ".send_telegram", side_effect=RuntimeError("down")):
            r = notify_parcel(make_parcel(score=90.0))
        assert r.ok is False

    def test_returns_service_result(self):
        with patch(MODULE + ".is_feature_enabled", return_value=False):
            assert isinstance(notify_parcel(make_parcel()), ServiceResult)

    def test_source_is_notifier_service(self):
        with patch(MODULE + ".is_feature_enabled", return_value=False):
            assert notify_parcel(make_parcel()).source == "notifier_service"
