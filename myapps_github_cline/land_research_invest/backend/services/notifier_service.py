"""Notifikacna sluzba
===================
Posle upozornenie (Telegram / email) ked pozemok dosiahne
konfigurovany prah skore.

Aktivacia:
  features -> use_notifications: true
  notifications -> channels -> telegram: true  (+ .env TELEGRAM_BOT_TOKEN)
  notifications -> channels -> email:    true  (+ .env EMAIL_FROM atd.)

Bezpecnost:
  Tokeny a heslá sa nikdy neukladaju do criteria.yaml.
  Citaju sa z env premennych (napr. python-dotenv).

Automatizacia: AUTO (po aktivacii bezi bez zasahu)
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import requests

from models.result import ServiceResult
from config_loader import get_notifications, is_feature_enabled
import services.report_service as _report

SERVICE_NAME = "notifier_service"
TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"


def notify_parcel(parcel):
    """
    Hlavna funkcia - odosle notifikaciu ak su splnene podmienky.

    Podmienky:
      1. use_notifications = true  (feature flag)
      2. parcel.final_score >= min_score_to_notify  (config prah)
      3. aspon jeden kanal je zapnuty (telegram alebo email)

    Args:
        parcel: Parcel s final_score a recommendation

    Returns:
        ServiceResult:
          ok=True, data={notified: True/False, channels: [...], reason: str}
          ok=False ak doslo k chybe odoslania
    """
    if not is_feature_enabled("use_notifications"):
        return ServiceResult.skip_result(SERVICE_NAME, "use_notifications=false")

    notif_cfg = get_notifications()
    reason, do_notify = should_notify(parcel, notif_cfg)
    if not do_notify:
        return ServiceResult(
            ok=True, score=0.0,
            data={"notified": False, "reason": reason},
            source=SERVICE_NAME,
        )

    channels_sent = []
    errors = []

    if notif_cfg.get("channels", {}).get("telegram"):
        try:
            text = format_telegram_message(parcel)
            send_telegram(text, notif_cfg.get("telegram", {}))
            channels_sent.append("telegram")
        except Exception as exc:
            errors.append(f"telegram: {exc}")

    if notif_cfg.get("channels", {}).get("email"):
        try:
            subject, body = format_email_message(parcel)
            send_email(subject, body, notif_cfg.get("email", {}))
            channels_sent.append("email")
        except Exception as exc:
            errors.append(f"email: {exc}")

    if errors and not channels_sent:
        return ServiceResult.error_result(
            SERVICE_NAME,
            "Vsetky kanaly zlyhali: " + "; ".join(errors)
        )

    return ServiceResult(
        ok=True, score=100.0,
        data={
            "notified": True,
            "channels": channels_sent,
            "errors": errors,
            "score": round(parcel.final_score, 2),
            "recommendation": parcel.recommendation,
        },
        source=SERVICE_NAME,
    )


def should_notify(parcel, notif_cfg=None):
    """
    Rozhodovacia logika - vrati (reason_str, bool).

    Returns:
        (reason, True)  ak treba notifikovat
        (reason, False) ak nie
    """
    if notif_cfg is None:
        notif_cfg = get_notifications()

    min_score = notif_cfg.get("min_score_to_notify", 75)
    channels  = notif_cfg.get("channels", {})

    if parcel.final_score < min_score:
        return f"score {parcel.final_score:.1f} < min {min_score}", False

    if not channels.get("telegram") and not channels.get("email"):
        return "ziadny kanal nie je zapnuty", False

    return "ok", True


def format_telegram_message(parcel):
    """
    Kratky SK text pre Telegram (max ~500 znakov).
    Obsahuje: verdikt, skore, cena, EUR/m2, lokalita, URL.
    """
    from services.report_service import build_investment_view, _verdict_icon
    inv  = build_investment_view(parcel)
    icon = _verdict_icon(parcel.recommendation)

    price_per_sqm = inv.get("price_per_sqm", 0.0)
    lines = [
        f"{icon} {parcel.recommendation} | Skore: {parcel.final_score:.1f}/100",
        f"Lokalita:  {parcel.location_text or 'N/A'}",
        f"Cena:      {parcel.price_eur:,.0f} EUR",
        f"EUR/m2:    {price_per_sqm:.2f}",
        f"Plocha:    {parcel.area_sqm:,.0f} m2",
    ]
    if parcel.url:
        lines.append(f"URL: {parcel.url}")
    return "\n".join(lines)


def format_email_message(parcel):
    """
    Predmet + telo emailu (plny text report).

    Returns:
        (subject_str, body_str)
    """
    subject = (
        f"[LandResearch] {parcel.recommendation} | "
        f"{parcel.final_score:.1f}/100 | {parcel.location_text or parcel.title}"
    )
    body = _report.format_text_report(parcel)
    return subject, body


def send_telegram(text, cfg):
    """
    Odosle spravu cez Telegram Bot API.

    Args:
        text: text spravy
        cfg:  dict telegram sekcie z config (bot_token_env, chat_id_env)

    Raises:
        ValueError: ak chyba token alebo chat_id
        requests.HTTPError: ak API vrati chybu
    """
    token   = _get_env(cfg.get("bot_token_env", "TELEGRAM_BOT_TOKEN"))
    chat_id = _get_env(cfg.get("chat_id_env",   "TELEGRAM_CHAT_ID"))

    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN nie je nastaveny v .env")
    if not chat_id:
        raise ValueError("TELEGRAM_CHAT_ID nie je nastaveny v .env")

    url  = TELEGRAM_API.format(token=token)
    resp = requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)
    resp.raise_for_status()


def send_email(subject, body, cfg):
    """
    Odosle email cez SMTP.

    Args:
        subject: predmet
        body:    telo (plaintext)
        cfg:     dict email sekcie z config

    Raises:
        ValueError: ak chybaju credentials
        smtplib.SMTPException: ak odoslanie zlyhalo
    """
    smtp_host = cfg.get("smtp_host", "smtp.gmail.com")
    smtp_port = int(cfg.get("smtp_port", 587))
    from_addr = _get_env(cfg.get("from_env",     "EMAIL_FROM"))
    to_addr   = _get_env(cfg.get("to_env",       "EMAIL_TO"))
    password  = _get_env(cfg.get("password_env", "EMAIL_PASSWORD"))

    if not from_addr or not to_addr or not password:
        raise ValueError("Chybaju EMAIL_FROM / EMAIL_TO / EMAIL_PASSWORD v .env")

    msg = MIMEMultipart()
    msg["From"]    = from_addr
    msg["To"]      = to_addr
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP(smtp_host, smtp_port) as srv:
        srv.ehlo()
        srv.starttls()
        srv.login(from_addr, password)
        srv.sendmail(from_addr, to_addr, msg.as_string())


def _get_env(name):
    """Bezpecne nacita env premennu (vrati None ak neexistuje)."""
    return os.environ.get(name) if name else None
