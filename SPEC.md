# SPEC.md — mcp-impo

## Purpose
MCP server that interfaces with https://www.impo.com.uy/datos-abiertos/ API, providing tools to query Uruguayan legislation and official notices. Includes SQLite caching with configurable TTL per request.

## Scope
- **In scope:**
  - Query IMPO bases (normas/avisos) via JSON API
  - Get schema documentation from IMPO
  - SQLite caching layer with per-request TTL support
  - FastMCP-based stdio transport for MCP protocol
- **Not in scope:**
  - Writing/publishing to IMPO
  - Authentication handling
  - Rate limiting (relies on server)

## Public API / Interface

### MCP Tools

1. `get_schema()` - Retrieve IMPO JSON schema documentation
   - Returns: JSON schema object from https://www.impo.com.uy/resources/basesIMPO.json

2. `get_norma(tipo: str, anio: int, nro: str, sec: str | None, ttl: int | None)` - Get a specific norma/aviso
   - Args:
     - tipo: Type of norm (e.g., "ley", "decreto", "resolucion")
     - anio: Year (e.g., 2024)
     - nro: Number (e.g., "19850")
     - sec: Optional sequence
     - ttl: Optional TTL in seconds for cache (default: server default)
   - Returns: JSON data of the norma/aviso

3. `search_normas(query: str, tipo: str | None, anio: int | None, limit: int, ttl: int | None)` - Search normas/avisos
   - Args:
     - query: Search query string
     - tipo: Optional filter by type
     - anio: Optional filter by year
     - limit: Maximum results (default: 50)
     - ttl: Optional TTL in seconds for cache
   - Returns: List of matching normas

4. `get_base_info( ttl: int | None)` - Get information about available bases
   - Args:
     - ttl: Optional TTL in seconds for cache
   - Returns: List of available bases

### Cache API

- `CacheManager.get(url: str, ttl: int | None) -> Response | None` - Get cached response if valid
- `CacheManager.set(url: str, response: bytes, ttl: int) -> None` - Store response in cache

## Data Formats
- URL format: `https://www.impo.com.uy/bases/{tipo}/{anio}-{nro}` with `?json=true` parameter
- Response format: JSON matching basesIMPO.json schema
- SQLite cache schema: url (TEXT PK), response (BLOB), cached_at (INTEGER), ttl (INTEGER)

## Edge Cases
1. Norma not found -> return empty/null with appropriate message
2. Network timeout -> raise exception or return cached if available
3. Invalid JSON response -> raise exception with error details
4. Empty search results -> return empty list
5. Cache miss -> fetch from server and cache

## Performance & Constraints
- Default TTL: 3600 seconds (1 hour)
- SQLite uses WAL mode for concurrency
- No connection pooling (simple single-connection approach)
- Target Python: 3.11+

## Default Cache TTL
- Schema: 86400 seconds (24 hours)
- Base info: 3600 seconds (1 hour)
- Norma data: 3600 seconds (1 hour)
- Search results: 600 seconds (10 minutes)