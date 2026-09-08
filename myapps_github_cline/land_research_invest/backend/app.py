"""Flask aplikacia - Land Research Invest
========================================
Application factory pattern - create_app() vytvori Flask instanciu
s registrovanymi Blueprints a CORS.

Spustenie:
  cd backend
  python app.py
  -> http://localhost:5001
"""

import os
from flask import Flask
from flask_cors import CORS


def create_app(test_config=None):
    """
    Application factory.

    Args:
        test_config: dict na prepisanie configu pre testy (napr. TESTING=True)

    Returns:
        Flask aplikacia s registrovanymi routes
    """
    app = Flask(__name__)

    # --- Zakladna konfiguracia ---
    app.config["JSON_SORT_KEYS"]  = False
    app.config["TESTING"]         = False

    if test_config:
        app.config.update(test_config)

    # --- CORS (pre Leaflet.js frontend) ---
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # --- Registracia Blueprints ---
    from routes.health_routes import health_bp
    from routes.config_routes import config_bp
    from routes.parcel_routes import parcel_bp

    app.register_blueprint(health_bp,  url_prefix="/api")
    app.register_blueprint(config_bp,  url_prefix="/api/config")
    app.register_blueprint(parcel_bp,  url_prefix="/api")

    return app


if __name__ == "__main__":
    port  = int(os.environ.get("PORT", 5001))
    debug = os.environ.get("FLASK_DEBUG", "True").lower() == "true"
    app   = create_app()
    app.run(host="0.0.0.0", port=port, debug=debug)
