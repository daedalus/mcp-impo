# IMPO MCP Server - Technical Findings

## Summary

The IMPO (Impresiones y Publicaciones Oficiales) website changed their API endpoints, breaking the MCP server's search functionality.

## Issues Found

### 1. Search Endpoint Redirect (301)

**Problem:** The `/bases/search` endpoint now returns HTTP 301 redirecting to `/search_gcse/`.

- Old URL: `https://www.impo.com.uy/bases/search?q=query&limit=50`
- New URL: `https://www.impo.com.uy/search_gcse/?q=query&limit=50`

**Impact:** The MCP server was failing with "Redirect response '301 Moved Permanently'" error.

**Status:** Fixed by adding `follow_redirects=True` to httpx calls.

### 2. Search Returns HTML Instead of JSON

**Problem:** The `/search_gcse/` endpoint returns HTML instead of JSON.

- Content-Type: `text/html; charset=UTF-8`
- Expected: `application/json`

**Impact:** When following the redirect, the response cannot be parsed as JSON.

**Workaround Implemented:** Added fallback logic in `search_normas()` to detect non-JSON responses and use `_search_via_base_info()` as fallback.

### 3. Base Info Endpoint Changed

**Problem:** The `/bases` endpoint now redirects to `/cgi-bin/bases/consultaBasesBS.cgi?tipoServicio=3` which returns HTML, not JSON.

- Original URL: `https://www.impo.com.uy/bases`
- New URL: `https://www.impo.com.uy/cgi-bin/bases/consultaBasesBS.cgi?tipoServicio=3`
- Content-Type: `text/html; charset=ISO-8859-1`

**Impact:** The `_search_via_base_info()` fallback cannot work because the base info endpoint returns HTML.

**Status:** Not yet fixed - needs different approach.

### 4. Individual Norma JSON API Works

**Confirmed:** Getting individual normas still works via `?json=true` parameter.

- Example: `https://www.impo.com.uy/bases/codigo-aeronautico/14305-1974?json=true`
- Returns proper JSON with all article content

## Current State

- `search_normas()` tries original endpoint, follows redirect, detects non-JSON, falls back to `_search_via_base_info()`
- `_search_via_base_info()` uses `get_base_info()` but that's also broken
- **Search is currently broken** until IMPO fixes their API

## Code Changes Made in `_api.py`

1. Added `follow_redirects=True` to all httpx.get() calls
2. Added fallback detection in `search_normas()` for non-JSON responses
3. Added `_search_via_base_info()` function as fallback (but depends on working get_base_info)

## Recommendations

1. **Contact IMPO**: Ask them to restore JSON support at `/bases/search` or provide new API endpoint
2. **Alternative**: Use web scraping approach to parse HTML results from `/search_gcse/`
3. **Alternative**: Use `mcp-impo_norma()` to get specific norms directly if user knows the identifier

## Test Commands

```python
# Test specific norma (works)
mcp_impo_norma(tipo="ley", anio=2024, nro="19850")

# Test schema (works)
mcp_impo_schema()

# Test search (broken)
mcp_impo_search(query="código aeronautico")
```

## Last Tested

April 13, 2026