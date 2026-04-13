from fastmcp import FastMCP

from ._api import get_base_info, get_norma, get_schema, search_normas

mcp = FastMCP("mcp-impo")


@mcp.tool()
def schema(ttl: int | None = None) -> dict[str, object]:
    """Retrieve IMPO JSON schema documentation.

    Returns the JSON schema defining the structure for normas and avisos
    from IMPO's datos abiertos API. This schema describes all available
    fields for Uruguayan legislation and official notices.

    Args:
        ttl: Optional TTL in seconds for cache. Defaults to 24 hours (86400s).
             Use 0 to bypass cache.

    Returns:
        Dictionary containing the JSON schema from IMPO.

    Example:
        >>> schema = schema()
        >>> schema.get("title")
        "Esquema JSON de las bases de IMPO"
    """
    return get_schema(ttl=ttl)


@mcp.tool()
def norma(
    tipo: str,
    anio: int,
    nro: str,
    sec: str | None = None,
    ttl: int | None = None,
) -> dict[str, object] | None:
    """Get a specific norma or aviso from IMPO.

    Retrieves detailed information about a specific legal norm or notice
    from IMPO's database in JSON format.

    Args:
        tipo: Type of norm (e.g., "ley", "decreto", "resolucion", "aviso",
              "convenio", "contrato", "licitacion")
        anio: Year of the norm (e.g., 2024)
        nro: Number of the norm (e.g., "19850")
        sec: Optional sequence identifier
        ttl: Optional TTL in seconds for cache. Defaults to 1 hour (3600s).
             Use 0 to bypass cache.

    Returns:
        Dictionary containing the norma data, or None if not found.

    Example:
        >>> norma = norma("ley", 2024, "19850")
        >>> norma.get("nombreNorma") if norma else "Not found"
    """
    return get_norma(tipo=tipo, anio=anio, nro=nro, sec=sec, ttl=ttl)


@mcp.tool()
def search(
    query: str,
    tipo: str | None = None,
    anio: int | None = None,
    limit: int = 50,
    ttl: int | None = None,
) -> list[dict[str, object]]:
    """Search for normas or avisos in IMPO database.

    Performs a search across IMPO's database of Uruguayan legislation
    and official notices. Results can be filtered by type and year.

    Args:
        query: Search query string (searches in norm titles and content)
        tipo: Optional filter by norm type (e.g., "ley", "decreto", "resolucion")
        anio: Optional filter by year
        limit: Maximum number of results (default: 50, max: 100)
        ttl: Optional TTL in seconds for cache. Defaults to 10 minutes (600s).
             Use 0 to bypass cache.

    Returns:
        List of dictionaries containing matching normas.

    Example:
        >>> results = search("seguridad social", tipo="ley", limit=10)
        >>> len(results)
        10
    """
    return search_normas(query=query, tipo=tipo, anio=anio, limit=limit, ttl=ttl)


@mcp.tool()
def bases(ttl: int | None = None) -> list[dict[str, object]]:
    """Get information about available bases in IMPO.

    Returns metadata about the available databases and their structure
    from IMPO's datos abiertos service.

    Args:
        ttl: Optional TTL in seconds for cache. Defaults to 1 hour (3600s).
             Use 0 to bypass cache.

    Returns:
        List of dictionaries containing base information.

    Example:
        >>> bases = bases()
        >>> len(bases)
    """
    return get_base_info(ttl=ttl)
