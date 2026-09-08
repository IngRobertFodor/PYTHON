"""Monitor sluzba - Periodicky scan pozemkov
===========================================
APScheduler BackgroundScheduler automaticky spusta scan:
  scrape_all() -> analyze_parcel() -> notify_parcel()

Aktivacia:
  features -> use_monitoring: true
  periodic_scan -> interval_minutes: 60 (nastavit v criteria.yaml)

Singleton: _scheduler je globalna premenna, start() je idempotentne.
Odolnost: vynimka pri 1 pozemku nezastavi cely scan.
"""

import time
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    APSCHEDULER_AVAILABLE = True
except ImportError:
    APSCHEDULER_AVAILABLE = False
    BackgroundScheduler = None

from config_loader  import is_feature_enabled, get_periodic_scan
from services.scraper_service  import scrape_all
from services.pipeline_service import analyze_parcel
from services.notifier_service import notify_parcel

SERVICE_NAME = "monitor_service"

# ----------------------------------------------------------------
# ScanResult dataclass
# ----------------------------------------------------------------

@dataclass
class ScanResult:
    """Vysledok jedneho behu skenu."""
    scanned:    int   = 0      # pocet analyzovanych pozemkov
    notified:   int   = 0      # pocet odoslanych notifikacii
    errors:     int   = 0      # pocet chyb
    duration_s: float = 0.0    # cas behu v sekundach
    timestamp:  str   = ""   # ISO timestamp spustenia

    def to_dict(self):
        return {
            "scanned":    self.scanned,
            "notified":   self.notified,
            "errors":     self.errors,
            "duration_s": round(self.duration_s, 2),
            "timestamp":  self.timestamp,
        }


# ----------------------------------------------------------------
# Globalny stav (singleton)
# ----------------------------------------------------------------

_scheduler  = None
_lock       = threading.Lock()
_last_result: ScanResult | None = None


def start(parcels_provider=None):
    """
    Spusti APScheduler BackgroundScheduler.
    Idempotentne - druhe volanie nema efekt ak uz bezi.

    Args:
        parcels_provider: callable() -> list[Parcel] (default: scrape_all)
    """
    global _scheduler

    if not is_feature_enabled("use_monitoring"):
        return

    if not APSCHEDULER_AVAILABLE:
        print("[monitor_service] APScheduler nie je nainstalovany - pip install apscheduler")
        return

    with _lock:
        if _scheduler is not None and _scheduler.running:
            return  # uz bezi

        cfg      = get_periodic_scan()
        interval = max(int(cfg.get("interval_minutes", 60)), 5)
        provider = parcels_provider or scrape_all

        _scheduler = BackgroundScheduler()
        _scheduler.add_job(
            func     = lambda: run_scan(provider),
            trigger  = "interval",
            minutes  = interval,
            id       = "periodic_scan",
            replace_existing = True,
        )
        _scheduler.start()

        if cfg.get("run_on_start", False):
            run_scan(provider)


def stop():
    """Zastavi scheduler ak bezi."""
    global _scheduler
    with _lock:
        if _scheduler is not None and _scheduler.running:
            _scheduler.shutdown(wait=False)
        _scheduler = None


def get_status():
    """
    Vrati stav monitora.

    Returns:
        dict: running, interval_minutes, next_run_iso, last_result
    """
    cfg     = get_periodic_scan()
    running = _scheduler is not None and _scheduler.running if APSCHEDULER_AVAILABLE else False

    next_run = None
    if running and _scheduler:
        job = _scheduler.get_job("periodic_scan")
        if job and job.next_run_time:
            next_run = job.next_run_time.isoformat()

    return {
        "running":          running,
        "interval_minutes": cfg.get("interval_minutes", 60),
        "next_run_iso":     next_run,
        "last_result":      _last_result.to_dict() if _last_result else None,
        "apscheduler_available": APSCHEDULER_AVAILABLE,
    }


def run_scan(parcels_provider=None):
    """
    Vykona jeden cely scan:
      1. Ziska pozemky (scrape_all alebo vlastny provider)
      2. Pre kazdy: analyze_parcel + notify_parcel
      3. Ulozi ScanResult do _last_result

    Odolnost: vynimka pri 1 pozemku nezastavi ostatnych.

    Args:
        parcels_provider: callable() -> list[Parcel] alebo list[dict]
                          default: scrape_all

    Returns:
        ScanResult
    """
    global _last_result

    cfg      = get_periodic_scan()
    max_p    = int(cfg.get("max_parcels_per_scan", 50))
    provider = parcels_provider or scrape_all
    ts       = datetime.now(timezone.utc).isoformat()
    t_start  = time.monotonic()

    scanned = notified = errors = 0

    try:
        raw_parcels = provider()
    except Exception as exc:
        print(f"[monitor_service] Provider chyba: {exc}")
        result = ScanResult(errors=1, timestamp=ts,
                            duration_s=time.monotonic() - t_start)
        _last_result = result
        return result

    if max_p > 0:
        raw_parcels = raw_parcels[:max_p]

    for item in raw_parcels:
        try:
            # Ak je item dict (napr. z JSON), konvertuj na Parcel
            from models.parcel import Parcel
            if isinstance(item, dict):
                parcel = Parcel(
                    title         = item.get("title", ""),
                    url           = item.get("url", ""),
                    price_eur     = float(item.get("price_eur", 0)),
                    area_sqm      = float(item.get("area_sqm", 0)),
                    location_text = item.get("location_text", ""),
                    source_portal = item.get("source_portal", ""),
                )
            else:
                parcel = item

            analyze_parcel(parcel)
            scanned += 1

            notif = notify_parcel(parcel)
            if notif.ok and notif.data.get("notified"):
                notified += 1

        except Exception as exc:
            errors += 1
            print(f"[monitor_service] Chyba pri pozemku: {exc}")

    result = ScanResult(
        scanned    = scanned,
        notified   = notified,
        errors     = errors,
        duration_s = time.monotonic() - t_start,
        timestamp  = ts,
    )
    _last_result = result
    return result
