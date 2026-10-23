"""
Unit Tests - Cache Service
===========================
Tests the in-memory TTL cache used to prevent repeated Overpass API calls.
"""

import time
import threading
import pytest
from services.cache_service import TTLCache, make_poi_cache_key, poi_cache


class TestTTLCache:
    """Tests for TTLCache class."""

    def test_set_and_get(self):
        """Basic set/get should work."""
        cache = TTLCache(default_ttl=60)
        cache.set('key1', {'data': 'value'})
        result = cache.get('key1')
        assert result == {'data': 'value'}

    def test_missing_key_returns_none(self):
        """Getting a key that was never set returns None."""
        cache = TTLCache(default_ttl=60)
        assert cache.get('nonexistent') is None

    def test_expired_entry_returns_none(self):
        """Entry should expire after TTL passes."""
        cache = TTLCache(default_ttl=60)
        # Use a very small positive TTL and wait for it to expire
        cache.set('expiring', 'value', ttl=0.05)
        time.sleep(0.1)  # wait longer than TTL
        assert cache.get('expiring') is None

    def test_not_yet_expired_returns_value(self):
        """Entry with long TTL should still be accessible."""
        cache = TTLCache(default_ttl=900)
        cache.set('fresh', 'data')
        assert cache.get('fresh') == 'data'

    def test_clear_removes_all_entries(self):
        """clear() should remove all cached entries."""
        cache = TTLCache(default_ttl=60)
        cache.set('a', 1)
        cache.set('b', 2)
        cache.set('c', 3)
        cache.clear()
        assert cache.get('a') is None
        assert cache.get('b') is None
        assert cache.get('c') is None

    def test_stats_shows_valid_count(self):
        """stats() should return correct count of valid (non-expired) entries."""
        cache = TTLCache(default_ttl=60)
        cache.set('x', 1)
        cache.set('y', 2)
        stats = cache.stats()
        assert stats['valid'] == 2
        assert stats['size'] == 2

    def test_thread_safety(self):
        """Concurrent writes should not corrupt the cache."""
        cache = TTLCache(default_ttl=60)
        errors = []

        def writer(prefix):
            try:
                for i in range(50):
                    cache.set(f'{prefix}_{i}', i)
                    cache.get(f'{prefix}_{i}')
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=writer, args=(f't{j}',)) for j in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == [], f"Thread-safety errors: {errors}"


class TestMakePoiCacheKey:
    """Tests for make_poi_cache_key helper."""

    def test_rounds_coordinates(self):
        """Coordinates within ~1km should produce same cache key (rounded to 2 decimals)."""
        # 37.9755 → 37.98, 37.9801 → 37.98 → same lat
        # 23.7348 → 23.73, 23.7399 → 23.74 → DIFFERENT lon – so use same lon
        key1 = make_poi_cache_key(37.9755, 23.7348, 25, ['historic=castle'], 'sk')
        key2 = make_poi_cache_key(37.9801, 23.7301, 25, ['historic=castle'], 'sk')
        # Both round to (37.98, 23.73) → same key
        assert key1 == key2

    def test_different_locations_different_keys(self):
        """Locations >1km apart should have different keys."""
        key_athens = make_poi_cache_key(37.97, 23.73, 25, ['tourism=museum'], 'sk')
        key_bratislava = make_poi_cache_key(48.14, 17.11, 25, ['tourism=museum'], 'sk')
        assert key_athens != key_bratislava

    def test_different_tags_different_keys(self):
        """Same location, different tags → different key."""
        key1 = make_poi_cache_key(37.97, 23.73, 25, ['historic=castle'], 'sk')
        key2 = make_poi_cache_key(37.97, 23.73, 25, ['tourism=museum'], 'sk')
        assert key1 != key2

    def test_tag_order_doesnt_matter(self):
        """Tags are sorted → same tags in different order = same key."""
        key1 = make_poi_cache_key(37.97, 23.73, 25, ['historic=castle', 'tourism=museum'], 'sk')
        key2 = make_poi_cache_key(37.97, 23.73, 25, ['tourism=museum', 'historic=castle'], 'sk')
        assert key1 == key2

    def test_different_lang_different_keys(self):
        """Same location + tags but different lang → different key."""
        key_sk = make_poi_cache_key(37.97, 23.73, 25, ['tourism=museum'], 'sk')
        key_en = make_poi_cache_key(37.97, 23.73, 25, ['tourism=museum'], 'en')
        assert key_sk != key_en

    def test_none_tags_handled(self):
        """None custom_tags should produce valid key (empty tuple)."""
        key = make_poi_cache_key(37.97, 23.73, 25, None, 'sk')
        assert key is not None
        assert key[3] == ()
