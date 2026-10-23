"""
POI Cache Service
=================
Thread-safe in-memory TTL cache for POI search results.
Prevents repeated Overpass API calls for the same location/tags.

Cache key: (rounded_lat, rounded_lon, radius_km_int, sorted_tags_tuple, lang)
Precision: coords rounded to 2 decimal places (~1.1km precision at equator)
TTL: 15 minutes (configurable)
"""
import time
import threading


class TTLCache:
    """Thread-safe in-memory cache with TTL expiry."""

    def __init__(self, default_ttl=900):
        self._store = {}          # key -> (expires_at, value)
        self._lock = threading.Lock()
        self.default_ttl = default_ttl

    def get(self, key):
        """Return cached value or None if missing / expired."""
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            expires, value = entry
            if time.time() > expires:
                del self._store[key]
                return None
            return value

    def set(self, key, value, ttl=None):
        """Store value with TTL."""
        with self._lock:
            self._store[key] = (time.time() + (ttl or self.default_ttl), value)

    def clear(self):
        """Remove all entries."""
        with self._lock:
            self._store.clear()

    def stats(self):
        """Return basic statistics."""
        with self._lock:
            now = time.time()
            valid = sum(1 for exp, _ in self._store.values() if now <= exp)
            return {'size': len(self._store), 'valid': valid}


def make_poi_cache_key(lat, lon, radius_km, custom_tags, lang):
    """
    Build a cache key for a POI search request.
    Coords are rounded to 2 decimal places (~1.1km precision) so that
    nearby clicks within ~1km share the same cache entry.
    """
    return (
        round(lat, 2),
        round(lon, 2),
        int(radius_km),
        tuple(sorted(custom_tags)) if custom_tags else (),
        lang,
    )


# Global singleton – lives for the lifetime of the Flask process
poi_cache = TTLCache(default_ttl=900)
