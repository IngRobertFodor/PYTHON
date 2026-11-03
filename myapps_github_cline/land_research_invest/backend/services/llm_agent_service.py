"""
llm_agent_service.py — AI Orchestrátor pre Land Research Invest
================================================================
LLM agent s tool-calling cez Google Gemini (google-genai SDK).

Použitie:
    from services.llm_agent_service import ask, is_available

    if is_available():
        result = ask("Nájdi mi 5 pozemkov do 25 km od BA s indexom nad 70")
        print(result["answer"])

Tooly (9):
    1. get_parcels           — filtruje pozemky z posledného behu
    2. get_run_summary       — súhrn posledného behu
    3. analyze_parcel_gis    — spustí GIS pipeline pre pozemok
    4. get_peer_statistics   — peer stats pre obec
    5. get_up_coverage       — pokrytie územných plánov
    6. explain_investment    — zdôvodnenie investičného indexu
    7. get_diff              — diff medzi dvoma poslednými behmi
    8. get_backup_status     — stav zálohy
    9. export_csv_filtered   — vygeneruje CSV so zúženým zoznamom

Konfigurácia modelov (priorita):
    1. .env  LLM_MODEL          (runtime override)
    2. hardcoded DEFAULT_MODEL  (zmeniť tu pri deprecation)

Modely (stav 2026-11):
    Primárny:  gemini-3.5-flash      (stabilný, free tier)
    Záložný:   gemini-3.1-flash-lite (rýchlejší, lacnejší)
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Konfigurácia modelov
# ---------------------------------------------------------------------------

DEFAULT_MODEL    = "gemini-3.5-flash"
FALLBACK_MODEL   = "gemini-3.1-flash-lite"

# Interná cache: model_name -> {"status": ok|failed|deprecated, "ts": float}
_model_health_cache: dict[str, dict] = {}
_health_lock = threading.Lock()

# Cache dostupných modelov (hybrid: Google API + hardcoded)
_models_cache: dict | None = None
_models_cache_ts: float    = 0.0
_MODELS_CACHE_TTL          = 3600.0  # 1 hodina

# Hardcoded fallback zoznam (aktualizuj pri väčšej zmene portfólia Gemini)
# Stav: 2026-11-03
_KNOWN_MODELS = [
    {"id": "gemini-3.5-flash",       "label": "Gemini 3.5 Flash (odporúčaný)",  "recommended": True},
    {"id": "gemini-3.1-flash-lite",  "label": "Gemini 3.1 Flash Lite (rýchly)", "recommended": False},
    {"id": "gemini-3.7-flash",       "label": "Gemini 3.7 Flash",               "recommended": False},
    {"id": "gemini-3.8-flash",       "label": "Gemini 3.8 Flash (najnovší)",    "recommended": False},
    {"id": "gemini-flash-latest",    "label": "Gemini Flash Latest (alias)",     "recommended": False},
]

# ---------------------------------------------------------------------------
# Exports cleanup (pri importe modulu)
# ---------------------------------------------------------------------------

_EXPORTS_DIR = Path(__file__).parent.parent.parent / "data" / "exports"


def _cleanup_old_exports() -> None:
    """Zmaže CSV exporty staršie ako 24 hodín."""
    if not _EXPORTS_DIR.exists():
        return
    cutoff = time.time() - 86400
    for f in _EXPORTS_DIR.glob("export_*.csv"):
        try:
            if f.stat().st_mtime < cutoff:
                f.unlink()
                logger.debug("[llm_agent] cleaned up old export: %s", f.name)
        except OSError:
            pass


try:
    _cleanup_old_exports()
except Exception:
    pass


# ---------------------------------------------------------------------------
# Pomocné funkcie
# ---------------------------------------------------------------------------

def is_available() -> bool:
    """True ak GOOGLE_API_KEY je nastavený v prostredí."""
    _load_env()
    return bool(os.environ.get("GOOGLE_API_KEY"))


def _load_env() -> None:
    """Načíta .env ak ešte nie je načítaný."""
    try:
        from dotenv import load_dotenv
        _env = Path(__file__).parent.parent.parent / ".env"
        if _env.exists():
            load_dotenv(str(_env), override=False)
    except ImportError:
        pass


def _resolve_model(override: str | None = None) -> str:
    """Vráti meno modelu: override > .env LLM_MODEL > DEFAULT_MODEL."""
    if override:
        return override
    _load_env()
    return os.environ.get("LLM_MODEL", DEFAULT_MODEL)


def _resolve_fallback() -> str:
    """Vráti meno záložného modelu."""
    _load_env()
    return os.environ.get("LLM_FALLBACK_MODEL", FALLBACK_MODEL)


def _get_client():
    """Vráti google-genai Client s API kľúčom."""
    from google import genai as _genai
    _load_env()
    key = os.environ.get("GOOGLE_API_KEY", "")
    if not key:
        raise RuntimeError("GOOGLE_API_KEY nie je nastavený.")
    return _genai.Client(api_key=key)


def _extract_text(content: Any) -> str:
    """Extrahuje čistý text z Gemini response (str alebo list[dict])."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(item.get("text", ""))
            elif isinstance(item, str):
                parts.append(item)
        return "".join(parts)
    return str(content)


def _classify_error(exc: Exception) -> str:
    """Klasifikuje chybu: deprecated|quota|not_found|network|unknown."""
    msg = str(exc).lower()
    if "no longer available" in msg or "deprecated" in msg:
        return "deprecated"
    if "resource_exhausted" in msg or "429" in msg or "quota" in msg:
        return "quota"
    if "not_found" in msg or "404" in msg:
        return "not_found"
    if "unavailable" in msg or "503" in msg or "connection" in msg or "timeout" in msg:
        return "network"
    return "unknown"


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

def check_model_health(model: str) -> dict:
    """Otestuje model ping volaním. Cache 24h."""
    with _health_lock:
        cached = _model_health_cache.get(model)
        if cached and (time.monotonic() - cached["ts"]) < 86400:
            return {**cached["result"], "cached": True}

    result: dict = {"model": model, "status": "unknown", "message_sk": "", "cached": False}
    try:
        client = _get_client()
        from google.genai import types as _types
        client.models.generate_content(
            model=model,
            contents="OK",
            config=_types.GenerateContentConfig(max_output_tokens=5),
        )
        result["status"]     = "ok"
        result["message_sk"] = f"Model {model} funguje."
    except Exception as exc:
        err_type = _classify_error(exc)
        result["status"] = err_type
        _SK = {
            "deprecated": f"Model {model} bol zrušený. Vyber iný model.",
            "quota":      f"Model {model} je momentálne preťažený. Skús neskôr.",
            "not_found":  f"Model {model} nie je dostupný pre tvoj účet.",
            "network":    f"Model {model} — problém so sieťou.",
            "unknown":    f"Model {model} — neznáma chyba: {str(exc)[:100]}",
        }
        result["message_sk"] = _SK.get(err_type, _SK["unknown"])
        logger.warning("[llm_agent] health check failed %s: %s", model, err_type)

    with _health_lock:
        _model_health_cache[model] = {"result": result, "ts": time.monotonic()}
    return result


# ---------------------------------------------------------------------------
# Dostupné modely (Hybrid: Google API + hardcoded fallback)
# ---------------------------------------------------------------------------

def list_available_models() -> dict:
    """Google API (3s timeout) → hardcoded fallback. Cache 1h."""
    global _models_cache, _models_cache_ts
    now = time.monotonic()
    if _models_cache and (now - _models_cache_ts) < _MODELS_CACHE_TTL:
        return {**_models_cache, "cached": True}

    try:
        import urllib.request
        _load_env()
        key = os.environ.get("GOOGLE_API_KEY", "")
        if not key:
            raise RuntimeError("no key")
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read())
        chat_models = [
            m for m in data.get("models", [])
            if "generateContent" in m.get("supportedGenerationMethods", [])
            and m.get("name", "").startswith("models/gemini")
        ]
        models = [
            {
                "id":          m["name"].replace("models/", ""),
                "label":       m.get("displayName", m["name"].replace("models/", "")),
                "recommended": m["name"].replace("models/", "") == DEFAULT_MODEL,
            }
            for m in chat_models
        ]
        result = {
            "source": "google-api", "models": models,
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }
        _models_cache, _models_cache_ts = result, now
        return {**result, "cached": False}
    except Exception as exc:
        logger.info("[llm_agent] models.list() failed (%s), using hardcoded", type(exc).__name__)

    result = {
        "source":  "hardcoded",
        "models":  _KNOWN_MODELS,
        "warning": "Google API nedostupné, zobrazujem známe modely z 2026-11-03",
        "last_updated": "2026-11-03T00:00:00+00:00",
    }
    _models_cache, _models_cache_ts = result, now
    return {**result, "cached": False}


# ---------------------------------------------------------------------------
# Tool definície — časť 1 (get_parcels, get_run_summary, analyze_parcel_gis)
# ---------------------------------------------------------------------------

def _tool_get_parcels(
    min_index: int = 0,
    max_distance_km: int = 999,
    source_type: str = "all",
    obec_substring: str = "",
    has_signal: str = "",
    limit: int = 20,
) -> list[dict]:
    """Filtruje pozemky z posledného behu."""
    try:
        from routes.scrape_routes import _get_last_results
        items = _get_last_results()
    except Exception as exc:
        logger.warning("[llm_agent] get_parcels: %s", exc)
        return []
    _DRAZBY   = {"ske_drazobne_vyhlasky", "notarske_drazby", "obchodny_vestnik"}
    _INZERATY = {"nehnutelnosti_sk", "topreality_sk", "reality_sk"}
    result = []
    for p in items:
        if p.get("investment_index", 0) < min_index:
            continue
        src = p.get("source_portal", "")
        if source_type == "drazby"   and src not in _DRAZBY:   continue
        if source_type == "inzeraty" and src not in _INZERATY: continue
        if obec_substring:
            if obec_substring.lower() not in (p.get("location_text") or "").lower():
                continue
        if has_signal:
            sigs = {s.get("kod") for s in (p.get("signals") or [])}
            if has_signal.upper() not in sigs:
                continue
        if max_distance_km < 999:
            try:
                from services.scoring_service import _estimate_distance_km
                km = _estimate_distance_km(p.get("location_text", ""))
                if km is not None and km > max_distance_km:
                    continue
            except Exception:
                pass
        result.append({
            "url":              p.get("url", ""),
            "title":            p.get("title", ""),
            "location_text":    p.get("location_text", ""),
            "price_eur":        p.get("price_eur", 0),
            "area_sqm":         p.get("area_sqm", 0),
            "price_per_sqm":    p.get("price_per_sqm", 0),
            "investment_index": p.get("investment_index", 0),
            "source_portal":    p.get("source_portal", ""),
            "signals":          [s.get("kod") for s in (p.get("signals") or [])],
        })
    result.sort(key=lambda x: x["investment_index"], reverse=True)
    return result[:limit]


def _tool_get_run_summary() -> dict:
    """Súhrn posledného scrape behu."""
    try:
        from services.scraper_service import get_scrape_progress
        from services.storage_service import list_runs
        prog = get_scrape_progress()
        runs = list_runs(limit=1)
        last = runs[0] if runs else {}
        return {
            "last_run_id":       last.get("id"),
            "started_at":        last.get("started_at"),
            "parcel_count":      last.get("parcel_count", 0),
            "per_source_status": prog.get("per_source_status", {}),
            "failed_sources":    prog.get("failed_sources", []),
            "elapsed_s":         prog.get("elapsed_s", 0),
        }
    except Exception as exc:
        return {"error": str(exc)}


def _tool_analyze_parcel_gis(url: str) -> dict:
    """GIS analýza pozemku podľa URL (~20s)."""
    if not url or not url.startswith("http"):
        return {"error": "Neplatná URL."}
    try:
        from routes.scrape_routes import _get_last_results
        from models.parcel import Parcel
        from services.pipeline_service import analyze_parcel
        items = _get_last_results()
        pd    = next((p for p in items if p.get("url") == url), None)
        if not pd:
            return {"error": f"Pozemok '{url}' nebol nájdený v poslednom behu."}
        p = Parcel(
            url=pd.get("url", ""), title=pd.get("title", ""),
            price_eur=float(pd.get("price_eur", 0) or 0),
            area_sqm=float(pd.get("area_sqm", 0) or 0),
            location_text=pd.get("location_text", ""),
            source_portal=pd.get("source_portal", ""),
            parcel_number=pd.get("parcel_number", ""),
        )
        analyze_parcel(p)
        return {
            "url": p.url, "final_score": p.final_score,
            "recommendation": p.recommendation, "signals": p.signals,
            "results_summary": {k: {"ok": v.ok, "score": v.score}
                                for k, v in p.results.items()},
        }
    except Exception as exc:
        return {"error": str(exc)}


# ---------------------------------------------------------------------------
# Tool definície — časť 2a (peer, up_coverage, explain)
# ---------------------------------------------------------------------------

def _tool_get_peer_statistics(obec: str) -> dict:
    """Peer stats pre obec: median €/m², počet, min/max."""
    if not obec:
        return {"error": "Chýba názov obce."}
    try:
        from routes.scrape_routes import _get_last_results
        from services.peer_analysis_service import compute_obec_stats
        from services.uzemny_plan_service import normalize_obec
        items = _get_last_results()
        stats = compute_obec_stats(items)
        slug  = normalize_obec(obec)
        if slug not in stats:
            matches = {k: v for k, v in stats.items() if obec.lower() in k}
            if not matches:
                return {"obec": obec, "found": False,
                        "message": f"Obec '{obec}' nemá dostatok pozemkov (min. 4)."}
            slug, stat = next(iter(matches.items()))
        else:
            stat = stats[slug]
        return {
            "obec": obec, "slug": slug, "found": True,
            "median_ppsm": round(stat.median_ppsm, 2), "count": stat.count,
            "min_ppsm": round(stat.min_ppsm, 2), "max_ppsm": round(stat.max_ppsm, 2),
        }
    except Exception as e2:
        return {"error": str(e2)}


def _tool_get_up_coverage() -> dict:
    """Pokrytie územných plánov pre obce z posledného behu."""
    try:
        from routes.scrape_routes import _get_last_results
        from services.uzemny_plan_service import _gisplan_cache, _cache_lock, normalize_obec
        items = _get_last_results()
        seen: dict[str, str] = {}
        for p in items:
            loc = p.get("location_text", "")
            if loc:
                slug = normalize_obec(loc)
                if slug and slug not in seen:
                    seen[slug] = loc.split(",")[0].strip()
        with _cache_lock:
            snap = dict(_gisplan_cache)
        has_up, no_up, unc = [], [], 0
        for slug, obec in seen.items():
            v = snap.get(slug)
            if v is True: has_up.append(obec)
            elif v is False: no_up.append(obec)
            else: unc += 1
        chk = len(has_up) + len(no_up)
        return {
            "total_obci": len(seen), "has_up_count": len(has_up),
            "no_up_count": len(no_up), "unchecked": unc,
            "coverage_pct": round(100 * len(has_up) / chk) if chk > 0 else 0,
            "has_up_sample": sorted(has_up)[:10],
        }
    except Exception as e3:
        return {"error": str(e3)}


def _tool_explain_investment(url: str) -> str:
    """Textové zdôvodnenie investičného indexu pozemku."""
    if not url:
        return "Chýba URL pozemku."
    try:
        from routes.scrape_routes import _get_last_results
        from services.opportunity_service import explain, investment_index
        items  = _get_last_results()
        parcel = next((p for p in items if p.get("url") == url), None)
        if not parcel:
            return f"Pozemok '{url}' nebol nájdený."
        text = explain(parcel)
        return text if text else f"Index: {investment_index(parcel)}/100. Príliš nízky."
    except Exception as e4:
        return f"Chyba: {e4}"


# ---------------------------------------------------------------------------
# Tool definície — časť 2b (diff, backup, export_csv)
# ---------------------------------------------------------------------------

def _tool_get_diff() -> dict:
    """Diff medzi dvoma poslednými scrape behmi."""
    try:
        from services.storage_service import list_runs, load_run
        from services.diff_service import compute_diff
        runs = list_runs(limit=2)
        if len(runs) < 2:
            return {"message": "Nie sú dostatok behov na porovnanie (min. 2)."}
        diff = compute_diff(load_run(runs[0]["id"]), load_run(runs[1]["id"]))
        return {
            "run_current_id":  runs[0]["id"],
            "run_previous_id": runs[1]["id"],
            "new_count":      len(diff.get("new", [])),
            "cheaper_count":  len(diff.get("cheaper", [])),
            "gone_count":     len(diff.get("gone", [])),
            "same_count":     len(diff.get("same", [])),
            "new_sample":     diff.get("new", [])[:5],
            "cheaper_sample": diff.get("cheaper", [])[:5],
        }
    except Exception as e5:
        return {"error": str(e5)}


def _tool_get_backup_status() -> dict:
    """Stav zálohy DB."""
    try:
        from services.backup_service import backup_status
        return backup_status()
    except Exception as e6:
        return {"error": str(e6)}


def _tool_export_csv_filtered(
    min_index: int = 0,
    obec_substring: str = "",
    has_signal: str = "",
) -> dict:
    """Vygeneruje CSV a vráti URL na stiahnutie (platné 24h)."""
    try:
        import csv, io
        parcels = _tool_get_parcels(
            min_index=min_index, obec_substring=obec_substring,
            has_signal=has_signal, limit=500,
        )
        if not parcels:
            return {"ok": False, "message": "Žiadne pozemky nevyhovujú kritériám."}
        _EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
        ts       = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"export_{ts}.csv"
        output   = io.StringIO()
        writer   = csv.DictWriter(output, fieldnames=[
            "location_text", "price_eur", "area_sqm", "price_per_sqm",
            "investment_index", "source_portal", "signals", "url",
        ], extrasaction="ignore")
        writer.writeheader()
        for p in parcels:
            writer.writerow({**p, "signals": ", ".join(p.get("signals", []))})
        (_EXPORTS_DIR / filename).write_text(output.getvalue(), encoding="utf-8-sig")
        return {
            "ok": True, "count": len(parcels), "filename": filename,
            "download_url": f"/api/agent/exports/{filename}",
            "message": f"CSV: {len(parcels)} pozemkov. Platné 24 hodín.",
        }
    except Exception as e7:
        return {"ok": False, "error": str(e7)}


# ---------------------------------------------------------------------------
# Tool registry + Gemini function_declarations
# ---------------------------------------------------------------------------

_TOOL_REGISTRY = {
    "get_parcels":          _tool_get_parcels,
    "get_run_summary":      _tool_get_run_summary,
    "analyze_parcel_gis":   _tool_analyze_parcel_gis,
    "get_peer_statistics":  _tool_get_peer_statistics,
    "get_up_coverage":      _tool_get_up_coverage,
    "explain_investment":   _tool_explain_investment,
    "get_diff":             _tool_get_diff,
    "get_backup_status":    _tool_get_backup_status,
    "export_csv_filtered":  _tool_export_csv_filtered,
}

_TOOL_DECLARATIONS = [
    {
        "name": "get_parcels",
        "description": (
            "Filtruje pozemky z posledného scrape behu. "
            "Použi na hľadanie podľa ceny, vzdialenosti, obce, signálov alebo indexu."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "min_index":       {"type": "integer", "description": "Minimálny investment index 0–100"},
                "max_distance_km": {"type": "integer", "description": "Max vzdialenosť od BA v km"},
                "source_type":     {"type": "string",  "description": "'all' | 'drazby' | 'inzeraty'"},
                "obec_substring":  {"type": "string",  "description": "Časť názvu obce, napr. 'Senec'"},
                "has_signal":      {"type": "string",  "description": "Kód signálu, napr. HORICE alebo BLIZKO_BA"},
                "limit":           {"type": "integer", "description": "Max počet výsledkov (default 20)"},
            },
        },
    },
    {
        "name": "get_run_summary",
        "description": "Súhrn posledného scrape behu: počty pozemkov, stav zdrojov, čas.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "analyze_parcel_gis",
        "description": "Spustí plnú GIS analýzu pre pozemok. Trvá ~20s. Vyžaduje URL.",
        "parameters": {
            "type": "object",
            "properties": {"url": {"type": "string", "description": "URL pozemku z posledného behu"}},
            "required": ["url"],
        },
    },
    {
        "name": "get_peer_statistics",
        "description": "Peer comparison štatistiky pre obec: medián €/m², počet, min/max.",
        "parameters": {
            "type": "object",
            "properties": {"obec": {"type": "string", "description": "Názov obce"}},
            "required": ["obec"],
        },
    },
    {
        "name": "get_up_coverage",
        "description": "Pokrytie územných plánov (gisplan.sk) pre obce z posledného behu.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "explain_investment",
        "description": "Textové zdôvodnenie prečo je pozemok zaujímavý. Vyžaduje URL.",
        "parameters": {
            "type": "object",
            "properties": {"url": {"type": "string", "description": "URL pozemku"}},
            "required": ["url"],
        },
    },
    {
        "name": "get_diff",
        "description": "Porovnanie dvoch posledných behov: nové / zlacneli / zmizli pozemky.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "get_backup_status",
        "description": "Stav zálohy databázy: posledná záloha, veľkosť, počty.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "export_csv_filtered",
        "description": "Vygeneruje CSV so zúženým zoznamom pozemkov a vráti odkaz na stiahnutie.",
        "parameters": {
            "type": "object",
            "properties": {
                "min_index":      {"type": "integer", "description": "Minimálny investment index"},
                "obec_substring": {"type": "string",  "description": "Časť názvu obce"},
                "has_signal":     {"type": "string",  "description": "Kód signálu"},
            },
        },
    },
]

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """Si AI asistent pre aplikáciu Land Research Invest.
Pomáhaš analyzovať investičné príležitosti v pozemkoch na Slovensku.

PRAVIDLÁ:
1. Odpovedaj VŽDY v slovenčine.
2. Ak otázka nesúvisí s pozemkami alebo investíciami, zdvorilo odmietni.
3. Nikdy nevymýšľaj dáta — vždy zavolaj tool, nie hádaj.
4. Pri zoznamoch zobraz max 10 položiek + "a ďalších N..." ak je viac.
5. Investment index 0–100: 85+=silná kúpa, 70–84=preveriť, 50–69=zvážiť, <50=preskočiť.
6. Platné kódy signálov: BLIZKO_BA, PRILIS_DALEKO, HORICE, DRAZBA_POD_ZNALECKOU,
   DRAZBA_OPAKOVANA, LACNEJSI_AKO_OKOLIE, DLHO_V_PONUKE, CENA_KLESA,
   CENA_PODOZRIVA, PODIEL_ALEBO_CHYBNE_DATA.
7. Buď stručný a konkrétny. Čísla zaokrúhľuj rozumne.
8. Ak DB je prázdna alebo scraping nebol spustený, povedz to jasne.
"""


# ---------------------------------------------------------------------------
# Hlavná ask() funkcia + agentic loop
# ---------------------------------------------------------------------------

def ask(question: str, model_override: str | None = None) -> dict:
    """
    Odošle otázku AI agentovi.
    Vracia: {ok, answer, tool_calls, model_used, error_type}
    """
    if not is_available():
        return {
            "ok": False,
            "answer": "AI asistent nie je nakonfigurovaný. Pridaj GOOGLE_API_KEY do .env a reštartuj appku.",
            "tool_calls": [], "model_used": None, "error_type": "no_api_key",
        }
    if not question or not question.strip():
        return {
            "ok": False, "answer": "Otázka je prázdna.",
            "tool_calls": [], "model_used": None, "error_type": "empty_question",
        }

    primary  = _resolve_model(model_override)
    fallback = _resolve_fallback()
    to_try   = [primary] + ([fallback] if fallback != primary else [])
    last_exc: Exception | None = None

    for model in to_try:
        try:
            return _run_agent(question.strip(), model)
        except Exception as exc:
            err_type = _classify_error(exc)
            logger.warning("[llm_agent] ask() %s failed (%s), trying next", model, err_type)
            last_exc = exc
            if err_type == "quota":
                time.sleep(2)

    err_type = _classify_error(last_exc) if last_exc else "unknown"
    _SK = {
        "deprecated": "Primárny AI model bol zrušený. Otvor AI chat → ⚙️ a vyber nový model.",
        "quota":      "AI je momentálne preťažená (rate-limit). Skús o chvíľu.",
        "not_found":  "AI model nie je dostupný pre tvoj účet.",
        "network":    "Problém so sieťou — nedá sa pripojiť k AI.",
        "unknown":    "AI dočasne nedostupné. Skús neskôr.",
    }
    return {
        "ok": False, "answer": _SK.get(err_type, _SK["unknown"]),
        "tool_calls": [], "model_used": None, "error_type": err_type,
    }


def _run_agent(question: str, model: str) -> dict:
    """Agentic loop pre jeden model. Max 5 kôl tool-calling."""
    from google import genai as _genai
    from google.genai import types as _types

    client      = _get_client()
    tool_config = _types.Tool(function_declarations=_TOOL_DECLARATIONS)
    messages    = [
        _types.Content(role="user", parts=[
            _types.Part.from_text(text=_SYSTEM_PROMPT),
            _types.Part.from_text(text=question),
        ])
    ]
    tool_calls_log: list[dict] = []

    for _round in range(5):
        resp      = client.models.generate_content(
            model=model, contents=messages,
            config=_types.GenerateContentConfig(
                tools=[tool_config], max_output_tokens=2048, temperature=0.1,
            ),
        )
        candidate = resp.candidates[0]
        parts     = candidate.content.parts if candidate.content else []
        fn_calls  = [p for p in parts if hasattr(p, "function_call") and p.function_call]

        if not fn_calls:
            text = ""
            for part in parts:
                if hasattr(part, "text") and part.text:
                    text += part.text
                elif isinstance(part, dict) and part.get("type") == "text":
                    text += part.get("text", "")
            return {
                "ok": True, "answer": text.strip() or "(prázdna odpoveď)",
                "tool_calls": tool_calls_log, "model_used": model, "error_type": None,
            }

        messages.append(candidate.content)
        tool_results = []
        for fc_part in fn_calls:
            fn   = fc_part.function_call
            name = fn.name
            args = dict(fn.args) if fn.args else {}
            tool_calls_log.append({"name": name, "args": args})
            logger.info("[llm_agent] tool: %s(%s)", name, args)
            if name in _TOOL_REGISTRY:
                try:
                    result = _TOOL_REGISTRY[name](**args)
                except TypeError as te:
                    result = {"error": f"Zlé argumenty pre {name}: {te}"}
            else:
                result = {"error": f"Neznámy tool: {name}"}
            tool_results.append(
                _types.Part.from_function_response(
                    name=name, response={"result": result},
                )
            )
        messages.append(_types.Content(role="user", parts=tool_results))

    logger.warning("[llm_agent] MAX_ROUNDS prekročený: %s...", question[:50])
    return {
        "ok": True,
        "answer": "AI nedokončila analýzu. Skús preformulovať otázku.",
        "tool_calls": tool_calls_log, "model_used": model, "error_type": "max_rounds",
    }

