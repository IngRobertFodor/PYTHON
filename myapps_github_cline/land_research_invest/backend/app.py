"""Flask aplikacia - Land Research Invest
========================================
Application factory - create_app() vytvori Flask instanciu
s registrovanymi Blueprints, CORS a servovanim frontendu.

Spustenie:
  cd backend && python app.py
  -> http://localhost:5001
"""

import os
from flask import Flask, send_from_directory, request
from flask_cors import CORS


def create_app(test_config=None):
    """Application factory."""
    _fe_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "frontend")
    )
    app = Flask(__name__,
                static_folder=_fe_dir,
                static_url_path="/static")

    app.config["JSON_SORT_KEYS"] = False
    app.config["TESTING"]        = False
    if test_config:
        app.config.update(test_config)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    from routes.health_routes import health_bp
    from routes.config_routes import config_bp
    from routes.parcel_routes import parcel_bp
    from routes.monitor_routes import monitor_bp
    from routes.scrape_routes import scrape_bp

    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(config_bp, url_prefix="/api/config")
    app.register_blueprint(parcel_bp,  url_prefix="/api")
    app.register_blueprint(monitor_bp, url_prefix="/api/monitor")
    app.register_blueprint(scrape_bp,  url_prefix="/api/scrape")

    # Monitor start (ak use_monitoring=true)
    from config_loader import is_feature_enabled as _ife
    if _ife("use_monitoring"):
        from services.monitor_service import start as _sm
        _sm()

    # Frontend route - musime ulozit referenciu mimo closure
    # aby create_app() volane viackrat (v testoch) nevytvaralo
    # duplicitne funkcie s rovnakym nazvom endpointu.
    fe_dir = _fe_dir  # local var pre closure

    def _serve_frontend():
        return send_from_directory(fe_dir, "index.html")

    # Registruj len ak este neexistuje (bezpecne pre viaceré create_app() volania)
    if "/" not in [r.rule for r in app.url_map.iter_rules()]:
        app.add_url_rule("/", endpoint="frontend_index",
                          view_func=_serve_frontend)

    # No-cache pre staticke subory (JS/CSS/HTML) - zakazuje starovanie v prehliadaci
    # Dolezite pri vyvoji: prehliadac vzdy nacita najnovsiu verziu
    @app.after_request
    def _no_cache(resp):
        if request.path.startswith("/static/") or request.path == "/":
            resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            resp.headers["Pragma"]        = "no-cache"
            resp.headers["Expires"]       = "0"
        return resp

    return app


if __name__ == "__main__":
    port  = int(os.environ.get("PORT", 5001))
    debug = os.environ.get("FLASK_DEBUG", "True").lower() == "true"
    create_app().run(host="0.0.0.0", port=port, debug=debug)
