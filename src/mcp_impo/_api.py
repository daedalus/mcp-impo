from typing import Any

import httpx

from ._cache import CacheManager

DEFAULT_TTL = 3600
SCHEMA_TTL = 86400
BASE_INFO_TTL = 3600
NORMAS_TTL = 3600
SEARCH_TTL = 600

BASE_URL = "https://www.impo.com.uy"
SCHEMA_URL = f"{BASE_URL}/resources/basesIMPO.json"
BASE_INFO_URL = f"{BASE_URL}/bases"


def get_cache_manager() -> CacheManager:
    return CacheManager()


def get_schema(ttl: int | None = None) -> dict[str, Any]:
    """Retrieve IMPO JSON schema documentation.

    Returns the JSON schema defining the structure for normas and avisos
    from IMPO's datos abiertos API.

    Args:
        ttl: Optional TTL in seconds for cache. Defaults to 24 hours (86400s).

    Returns:
        Dictionary containing the JSON schema from IMPO.

    Example:
        >>> schema = get_schema()
        >>> schema.get("title")
        "Esquema JSON de las bases de IMPO"
    """
    cache = get_cache_manager()
    ttl_value = ttl if ttl is not None else SCHEMA_TTL

    cached = cache.get(SCHEMA_URL, ttl_value)
    if cached:
        import json

        return json.loads(cached)  # type: ignore[no-any-return]  # type: ignore[no-any-return]

    response = httpx.get(SCHEMA_URL, timeout=30.0)
    response.raise_for_status()
    data: dict[str, Any] = response.json()

    cache.set(SCHEMA_URL, response.content, ttl_value)
    return data


def get_norma(
    tipo: str,
    anio: int,
    nro: str,
    sec: str | None = None,
    ttl: int | None = None,
) -> dict[str, Any] | None:
    """Get a specific norma or aviso from IMPO.

    Retrieves detailed information about a specific legal norm or notice
    from IMPO's database in JSON format.

    Args:
        tipo: Type of norm (e.g., "ley", "decreto", "resolucion", "aviso")
        anio: Year of the norm (e.g., 2024)
        nro: Number of the norm (e.g., "19850")
        sec: Optional sequence identifier
        ttl: Optional TTL in seconds for cache. Defaults to 1 hour (3600s).

    Returns:
        Dictionary containing the norma data, or None if not found.

    Example:
        >>> norma = get_norma("ley", 2024, "19850")
        >>> norma.get("nombreNorma")
    """
    cache = get_cache_manager()

    parts = [tipo, f"{anio}-{nro}"]
    if sec:
        parts.append(sec)
    path = "/".join(parts)

    url = f"{BASE_URL}/bases/{path}?json=true"
    ttl_value = ttl if ttl is not None else NORMAS_TTL

    cached = cache.get(url, ttl_value)
    if cached:
        import json

        return json.loads(cached)  # type: ignore[no-any-return]

    try:
        response = httpx.get(url, timeout=30.0)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        data: dict[str, Any] = response.json()
        cache.set(url, response.content, ttl_value)
        return data
    except httpx.HTTPStatusError:
        return None


def search_normas(
    query: str,
    tipo: str | None = None,
    anio: int | None = None,
    limit: int = 50,
    ttl: int | None = None,
) -> list[dict[str, Any]]:
    """Search for normas or avisos in IMPO database.

    Performs a search across IMPO's database of Uruguayan legislation
    and official notices.

    Args:
        query: Search query string
        tipo: Optional filter by norm type (e.g., "ley", "decreto")
        anio: Optional filter by year
        limit: Maximum number of results (default: 50, max: 100)
        ttl: Optional TTL in seconds for cache. Defaults to 10 minutes (600s).

    Returns:
        List of dictionaries containing matching normas.

    Example:
        >>> results = search_normas("seguridad social", tipo="ley", limit=10)
        >>> len(results)
        10
    """
    cache = get_cache_manager()

    limit = min(limit, 100)

    params: dict[str, str | int] = {"q": query, "limit": limit}
    if tipo:
        params["tipo"] = tipo
    if anio:
        params["anio"] = anio

    url = f"{BASE_URL}/bases/search"
    ttl_value = ttl if ttl is not None else SEARCH_TTL

    cached = cache.get(url, ttl_value, params=params)
    if cached:
        import json

        return json.loads(cached)  # type: ignore[no-any-return]

    response = httpx.get(url, params=params, timeout=30.0)
    response.raise_for_status()
    data: list[dict[str, Any]] = response.json()

    cache.set(url, response.content, ttl_value, params=params)
    return data


def get_base_info(ttl: int | None = None) -> list[dict[str, Any]]:
    """Get information about available bases in IMPO.

    Returns metadata about the available databases and their structure
    from IMPO's datos abiertos service.

    Args:
        ttl: Optional TTL in seconds for cache. Defaults to 1 hour (3600s).

    Returns:
        List of dictionaries containing base information.

    Example:
        >>> bases = get_base_info()
        >>> bases[0].get("nombre")
    """
    cache = get_cache_manager()
    ttl_value = ttl if ttl is not None else BASE_INFO_TTL

    cached = cache.get(BASE_INFO_URL, ttl_value)
    if cached:
        import json

        return json.loads(cached)  # type: ignore[no-any-return]

    response = httpx.get(BASE_INFO_URL, timeout=30.0)
    response.raise_for_status()
    data: list[dict[str, Any]] = response.json()

    cache.set(BASE_INFO_URL, response.content, ttl_value)
    return data
