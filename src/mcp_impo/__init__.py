__version__ = "0.1.0"
__all__ = [
    "mcp",
    "CacheManager",
    "get_schema",
    "get_norma",
    "search_normas",
    "get_base_info",
]

from typing import TYPE_CHECKING

from ._api import get_base_info, get_norma, get_schema, search_normas
from ._cache import CacheManager
from ._mcp import mcp

if TYPE_CHECKING:
    from ._api import *
    from ._cache import *
    from ._mcp import *
