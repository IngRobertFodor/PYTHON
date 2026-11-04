"""
agent_routes.py — AI Orchestrátor REST API
==========================================
POST /api/agent/ask              -> odošle otázku AI agentovi
GET  /api/agent/status           -> dostupnosť + aktuálny model
GET  /api/agent/health           -> detailný stav modelov
GET  /api/agent/available-models -> zoznam dostupných Gemini modelov
POST /api/agent/select-model     -> override modelu pre session (S1: whitelist)
POST /api/agent/clear-model      -> vymaže model override
GET  /api/agent/exports/<name>   -> stiahne vygenerovaný CSV export (S2: realpath guard)

Security:
    S1: select-model — model musí byť v whitelist (z available-models)
    S2: exports — realpath guard voči path traversal
    S4: /ask — rate limit 10 req/min per IP
"""

import logging
import time
import threading
from pathlib import Path
from flask import Blueprint, jsonify, request, send_file, session

logger = logging.getLogger(__name__)
agent_bp     = Blueprint("agent", __name__)
_EXPORTS_DIR = Path(__file__).parent.parent.parent / "data" / "exports"
_SESSION_KEY = "ai_agent_model"

# S4: Rate limit pre /ask — 10 req/min per IP (in-memory, single-process)
_rl_lock     = threading.Lock()
_rl_buckets: dict[str, list[float]] = {}  # ip -> [timestamps]
_RL_MAX      = 10
_RL_WINDOW   = 60.0


def _rate_limit_ok(ip: str) -> bool:
    """Vráti True ak IP neprekročila limit. Thread-safe."""
    now = time.monotonic()
    with _rl_lock:
        ts = _rl_buckets.get(ip, [])
        ts = [t for t in ts if now - t < _RL_WINDOW]
        if len(ts) >= _RL_MAX:
            _rl_buckets[ip] = ts
            return False
        ts.append(now)
        _rl_buckets[ip] = ts
        return True


def _svc():
    """Lazy import llm_agent_service."""
    try:
        import services.llm_agent_service as s
        return s
    except ImportError:
        return None


@agent_bp.route("/ask", methods=["POST"])
def ask_endpoint():
    """POST /api/agent/ask  { question } -> { ok, answer, tool_calls, model_used }"""
    # S4: rate limit 10 req/min per IP
    ip = request.remote_addr or "unknown"
    if not _rate_limit_ok(ip):
        return jsonify({
            "ok": False,
            "answer": "Príliš veľa otázok. Počkaj minútu.",
            "error_type": "rate_limit",
        }), 429

    data     = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify({"ok": False, "error": "Chýba 'question'."}), 400
    if len(question) > 500:
        return jsonify({"ok": False, "error": "Otázka príliš dlhá (max 500 znakov)."}), 400
    svc = _svc()
    if not svc:
        return jsonify({"ok": False, "error": "AI modul nie je nainštalovaný."}), 503
    try:
        return jsonify(svc.ask(question, model_override=session.get(_SESSION_KEY))), 200
    except Exception as exc:
        logger.error("[agent_routes] ask(): %s", exc)
        return jsonify({"ok": False, "answer": "Nastala neočakávaná chyba.", "error": str(exc)}), 500


@agent_bp.route("/status", methods=["GET"])
def status_endpoint():
    """GET /api/agent/status -> { available, model, fallback_model, model_override }"""
    svc = _svc()
    if not svc:
        return jsonify({"available": False, "reason": "modul nie je nainštalovaný"}), 200
    override = session.get(_SESSION_KEY)
    return jsonify({
        "available":      svc.is_available(),
        "model":          override or svc._resolve_model(),
        "fallback_model": svc._resolve_fallback(),
        "model_override": override,
        "default_model":  svc.DEFAULT_MODEL,
    }), 200


@agent_bp.route("/health", methods=["GET"])
def health_endpoint():
    """GET /api/agent/health -> { primary, fallback, active_model, warning_sk? }"""
    svc = _svc()
    if not svc or not svc.is_available():
        return jsonify({
            "available": False,
            "primary":   {"model": svc.DEFAULT_MODEL if svc else "?", "status": "unknown"},
            "fallback":  {"model": svc.FALLBACK_MODEL if svc else "?", "status": "unknown"},
            "active_model": None,
        }), 200
    p_name  = svc._resolve_model(session.get(_SESSION_KEY))
    fb_name = svc._resolve_fallback()
    p_h     = svc.check_model_health(p_name)
    fb_h    = svc.check_model_health(fb_name) if fb_name != p_name else None
    active  = p_name if p_h["status"] == "ok" else (
        fb_name if (fb_h and fb_h["status"] == "ok") else None
    )
    result: dict = {"available": True, "primary": p_h, "active_model": active}
    if fb_h:
        result["fallback"] = fb_h
    if p_h["status"] != "ok":
        result["warning_sk"] = p_h.get("message_sk", "")
    return jsonify(result), 200


@agent_bp.route("/available-models", methods=["GET"])
def available_models_endpoint():
    """GET /api/agent/available-models -> { source, models, cached, last_updated }"""
    svc = _svc()
    if not svc:
        return jsonify({"source": "unavailable", "models": [], "cached": False}), 200
    return jsonify(svc.list_available_models()), 200


@agent_bp.route("/select-model", methods=["POST"])
def select_model_endpoint():
    """POST /api/agent/select-model { model } -> { ok, model, health }
    S1: model musí byť v whitelist (available-models zoznam).
    """
    data  = request.get_json(silent=True) or {}
    model = (data.get("model") or "").strip()
    if not model:
        return jsonify({"ok": False, "error": "Chýba 'model'."}), 400
    svc = _svc()
    if not svc or not svc.is_available():
        return jsonify({"ok": False, "error": "AI nie je k dispozícii."}), 400

    # S1: whitelist — model musí byť v known/available zozname
    available = svc.list_available_models()
    known_ids = {m["id"] for m in available.get("models", [])}
    if model not in known_ids:
        logger.warning("[agent_routes] select-model: rejected unknown model '%s'", model)
        return jsonify({
            "ok": False,
            "error": f"Model '{model}' nie je v zozname povolených modelov.",
        }), 400

    health = svc.check_model_health(model)
    if health["status"] not in ("ok", "quota"):
        return jsonify({
            "ok": False,
            "error": health.get("message_sk", f"Model {model} nie je použiteľný."),
            "health": health,
        }), 400
    session[_SESSION_KEY] = model
    session.permanent = False
    return jsonify({"ok": True, "model": model, "health": health}), 200


@agent_bp.route("/clear-model", methods=["POST"])
def clear_model_endpoint():
    """POST /api/agent/clear-model -> { ok, model }"""
    session.pop(_SESSION_KEY, None)
    svc = _svc()
    return jsonify({"ok": True, "model": svc._resolve_model() if svc else None}), 200


@agent_bp.route("/exports/<filename>", methods=["GET"])
def download_export(filename: str):
    """GET /api/agent/exports/<filename> -> stiahne CSV export.
    S2: realpath guard — súbor musí byť v _EXPORTS_DIR.
    """
    if not filename.startswith("export_") or not filename.endswith(".csv"):
        return jsonify({"error": "Neplatný názov súboru."}), 400
    if "/" in filename or "\\" in filename or ".." in filename:
        return jsonify({"error": "Neplatný názov súboru."}), 400
    filepath = _EXPORTS_DIR / filename
    # S2: realpath check — zabraňuje path traversal aj cez symlinky
    try:
        resolved = filepath.resolve()
        export_dir_resolved = _EXPORTS_DIR.resolve()
        if not str(resolved).startswith(str(export_dir_resolved)):
            logger.warning("[agent_routes] path traversal attempt: %s", filename)
            return jsonify({"error": "Neplatný názov súboru."}), 400
    except Exception:
        return jsonify({"error": "Neplatný názov súboru."}), 400
    if not filepath.exists():
        return jsonify({"error": "Súbor neexistuje alebo vypršal (platnosť 24h)."}), 404
    return send_file(str(filepath), mimetype="text/csv",
                     as_attachment=True, download_name=filename)
