import json
import time
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from mcp_impo._cache import CacheManager


@pytest.fixture
def cache_db(tmp_path):
    db_path = tmp_path / "test_cache.db"
    return str(db_path)


@pytest.fixture
def cache(cache_db):
    return CacheManager(db_path=cache_db)


class TestCacheManager:
    def test_init_creates_db(self, cache_db):
        CacheManager(db_path=cache_db)
        assert Path(cache_db).exists()

    def test_set_and_get(self, cache):
        url = "https://example.com/test"
        data = b'{"key": "value"}'
        cache.set(url, data, ttl=3600)

        result = cache.get(url, ttl=3600)
        assert result == data

    def test_get_cache_miss(self, cache):
        url = "https://example.com/missing"
        result = cache.get(url, ttl=3600)
        assert result is None

    def test_expired_cache(self, cache):
        url = "https://example.com/expired"
        data = b'{"key": "value"}'
        cache.set(url, data, ttl=2)

        time.sleep(0.1)
        result = cache.get(url, ttl=1)
        assert result == data

        time.sleep(3)
        result = cache.get(url, ttl=1)
        assert result is None

    def test_params_hash(self, cache):
        params1 = {"a": "1", "b": "2"}
        params2 = {"b": "2", "a": "1"}
        params3 = {"a": "1"}

        assert cache._get_params_hash(params1) == cache._get_params_hash(params2)
        assert cache._get_params_hash(params1) != cache._get_params_hash(params3)

    def test_cache_with_params(self, cache):
        url = "https://example.com/search"
        params = {"q": "test", "limit": "10"}
        data = b'{"results": []}'
        cache.set(url, data, ttl=3600, params=params)

        result = cache.get(url, ttl=3600, params=params)
        assert result == data

    def test_cache_different_params(self, cache):
        url = "https://example.com/search"
        data1 = b'{"results": [1]}'
        data2 = b'{"results": [2]}'

        cache.set(url, data1, ttl=3600, params={"q": "test1"})
        cache.set(url, data2, ttl=3600, params={"q": "test2"})

        result1 = cache.get(url, ttl=3600, params={"q": "test1"})
        result2 = cache.get(url, ttl=3600, params={"q": "test2"})

        assert result1 == data1
        assert result2 == data2

    def test_clear_cache(self, cache):
        url = "https://example.com/test"
        cache.set(url, b"data", ttl=3600)

        cache.clear()

        result = cache.get(url, ttl=3600)
        assert result is None
