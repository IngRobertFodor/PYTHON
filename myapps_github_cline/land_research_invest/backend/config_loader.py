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
    """Vrati sekciu criteria (vsetky kriteria vyhladavania)."""
    return get_config().get("criteria", {})


def get_criteria_section(section: str) -> dict:
    """
    Vrati konkretnu sekciu z criteria.

    Args:
        section: napr. 'location', 'terrain', 'cadastral', 'protected_zones'

    Returns:
        dict so sekciou, alebo prazdny dict ak neexistuje
    """
    return get_criteria().get(section, {})


def get_enabled_sources() -> dict:
    """Vrati len zapnute zdroje inzeratov (enabled: true)."""
    return {
        name: cfg
        for name, cfg in get_sources().items()
        if cfg.get("enabled", False)
    }


def get_green_sources() -> dict:
    """Vrati len GREEN zona zdroje (bezpecne automatizovat)."""
    return {
        name: cfg
        for name, cfg in get_enabled_sources().items()
        if cfg.get("zone") == "GREEN"
    }


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
