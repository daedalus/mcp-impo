import hashlib
import sqlite3
import time
from pathlib import Path
from typing import Any


class CacheManager:
    """SQLite-based cache manager with TTL support.

    Provides a simple caching layer for HTTP responses using SQLite.
    Each cached entry has a TTL that can be specified per-request.
    """

    def __init__(self, db_path: str | None = None) -> None:
        """Initialize the cache manager.

        Args:
            db_path: Optional path to SQLite database file.
                     Defaults to .impo_cache.db in user's data directory.
        """
        if db_path is None:
            home = Path.home()
            db_path = str(home / ".impo_cache.db")

        self._db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the SQLite database with required tables."""
        conn = sqlite3.connect(self._db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cache (
                url TEXT NOT NULL,
                params_hash TEXT NOT NULL,
                response BLOB NOT NULL,
                cached_at INTEGER NOT NULL,
                ttl INTEGER NOT NULL,
                PRIMARY KEY (url, params_hash)
            )
        """
        )
        conn.commit()
        conn.close()

    def _get_params_hash(self, params: dict[str, Any] | None) -> str:
        """Generate a hash for URL parameters.

        Args:
            params: Dictionary of query parameters.

        Returns:
            Hex string of MD5 hash of the params.
        """
        if not params:
            return ""
        param_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
        return hashlib.md5(param_str.encode()).hexdigest()

    def get(
        self, url: str, ttl: int, params: dict[str, Any] | None = None
    ) -> bytes | None:
        """Get a cached response if it is still valid.

        Args:
            url: The URL that was cached.
            ttl: Default TTL to use for cache validation (can be overridden).
            params: Optional query parameters used with the URL.

        Returns:
            Cached response as bytes, or None if expired/not found.
        """
        params_hash = self._get_params_hash(params)
        now = int(time.time())

        conn = sqlite3.connect(self._db_path)
        cursor = conn.execute(
            """
            SELECT response, cached_at, ttl FROM cache
            WHERE url = ? AND params_hash = ?
        """,
            (url, params_hash),
        )
        row = cursor.fetchone()
        conn.close()

        if row is None:
            return None

        response, cached_at, stored_ttl = row

        effective_ttl = stored_ttl if stored_ttl > 0 else ttl
        if now - cached_at > effective_ttl:
            self._delete(url, params_hash)
            return None

        return response  # type: ignore[no-any-return]

    def set(
        self,
        url: str,
        response: bytes,
        ttl: int,
        params: dict[str, Any] | None = None,
    ) -> None:
        """Store a response in the cache.

        Args:
            url: The URL being cached.
            response: The response content to cache.
            ttl: TTL in seconds for this entry.
            params: Optional query parameters used with the URL.
        """
        params_hash = self._get_params_hash(params)
        cached_at = int(time.time())

        conn = sqlite3.connect(self._db_path)
        conn.execute(
            """
            INSERT OR REPLACE INTO cache (url, params_hash, response, cached_at, ttl)
            VALUES (?, ?, ?, ?, ?)
        """,
            (url, params_hash, response, cached_at, ttl),
        )
        conn.commit()
        conn.close()

    def _delete(self, url: str, params_hash: str) -> None:
        """Delete a cache entry.

        Args:
            url: The URL to delete.
            params_hash: Hash of the parameters.
        """
        conn = sqlite3.connect(self._db_path)
        conn.execute(
            "DELETE FROM cache WHERE url = ? AND params_hash = ?",
            (url, params_hash),
        )
        conn.commit()
        conn.close()

    def clear(self) -> None:
        """Clear all cache entries."""
        conn = sqlite3.connect(self._db_path)
        conn.execute("DELETE FROM cache")
        conn.commit()
        conn.close()
