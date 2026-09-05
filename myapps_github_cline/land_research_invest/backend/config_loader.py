"""
Config Loader
=============
Jedno miesto pravdy pre nacitanie criteria.yaml.
Vsetky sluzby citaju config odtialto - nie priamo zo suborov.
"""

import os
import yaml

_CONFIG_PATH = os.path.join(
    os.path.dirname(__file__),   # backend/
    "..",                        # projekt root
    "config",
    "criteria.yaml"
)

_config_cache = None


def get_config() -> dict:
    """
    Nacita a cachuje criteria.yaml.
    Vrati kompletny config ako dict.
    """
    global _config_cache
    if _config_cache is None:
        path = os.path.abspath(_CONFIG_PATH)
        with open(path, "r", encoding="utf-8") as f:
            _config_cache = yaml.safe_load(f)
    return _config_cache


def reload_config() -> dict:
    """
    Vynuti znovunacitanie configu (napr. po zmene YAML za behu).
    """
    global _config_cache
    _config_cache = None
    return get_config()


def get_criteria() -> dict:
    """Vrati sekciu search_criteria."""
    return get_config().get("search_criteria", {})


def get_scoring() -> dict:
    """Vrati sekciu scoring (vahy + prahy)."""
    return get_config().get("scoring", {})


def get_features() -> dict:
    """Vrati feature flags."""
    return get_config().get("features", {})


def get_sources() -> dict:
    """Vrati konfiguraciu zdrojov inzeratov."""
    return get_config().get("sources", {})


def get_endpoints() -> dict:
    """Vrati externe endpointy (WMS/WFS/API)."""
    return get_config().get("endpoints", {})


def is_feature_enabled(feature_name: str) -> bool:
    """
    Overi ci je dana feature zapnuta.

    Args:
        feature_name: napr. 'use_terrain', 'use_flood'

    Returns:
        True ak zapnuta, False ak vypnuta alebo neexistuje
    """
    return get_features().get(feature_name, False)
