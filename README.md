# mcp-impo

MCP server for IMPO Uruguay datos abiertos API with SQLite caching.

[![PyPI](https://img.shields.io/pypi/v/mcp-impo.svg)](https://pypi.org/project/mcp-impo/)
[![Python](https://img.shields.io/pypi/pyversions/mcp-impo.svg)](https://pypi.org/project/mcp-impo/)

## Install

```bash
pip install mcp-impo
```

## Usage

```python
from mcp_impo import get_schema, get_norma, search_normas, get_base_info

# Get schema
schema = get_schema()

# Get specific norm
norma = get_norma("ley", 2024, "19850")

# Search
results = search_normas("seguridad social", tipo="ley", limit=10)

# Get available bases
bases = get_base_info()
```

## CLI

```bash
mcp-impo --help
```

## MCP Tools

- `schema` - Retrieve IMPO JSON schema documentation
- `norma` - Get a specific norma or aviso
- `search` - Search normas/avisos
- `bases` - Get information about available bases

## Cache

The server uses SQLite caching with configurable TTL:
- Schema: 24 hours
- Base info: 1 hour
- Norma data: 1 hour
- Search results: 10 minutes

Override TTL per request by passing `ttl` parameter (seconds).

mcp-name: io.github.daedalus/mcp-impo

## Development

```bash
git clone https://github.com/daedalus/mcp-impo.git
cd mcp-impo
pip install -e ".[test]"

# run tests
pytest

# format
ruff format src/ tests/

# lint
ruff check src/ tests/

# type check
mypy src/
```