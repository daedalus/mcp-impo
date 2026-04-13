import json
from unittest.mock import MagicMock, Mock, patch

import pytest

from mcp_impo._api import (
    BASE_URL,
    SCHEMA_URL,
    get_base_info,
    get_norma,
    get_schema,
    search_normas,
)


class TestGetSchema:
    @patch("mcp_impo._api.get_cache_manager")
    @patch("mcp_impo._api.httpx.get")
    def test_get_schema_returns_data(self, mock_get, mock_cache):
        mock_cache_instance = MagicMock()
        mock_cache.return_value = mock_cache_instance
        mock_cache_instance.get.return_value = None

        mock_response = Mock()
        mock_response.json.return_value = {"title": "Test Schema"}
        mock_response.content = b'{"title": "Test Schema"}'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = get_schema()

        assert result == {"title": "Test Schema"}
        mock_get.assert_called_once()

    @patch("mcp_impo._api.get_cache_manager")
    @patch("mcp_impo._api.httpx.get")
    def test_get_schema_uses_cache(self, mock_get, mock_cache):
        mock_cache_instance = MagicMock()
        mock_cache.return_value = mock_cache_instance
        mock_cache_instance.get.return_value = b'{"title": "Cached Schema"}'

        result = get_schema()

        assert result == {"title": "Cached Schema"}
        mock_get.assert_not_called()


class TestGetNorma:
    @patch("mcp_impo._api.get_cache_manager")
    @patch("mcp_impo._api.httpx.get")
    def test_get_norma_returns_data(self, mock_get, mock_cache):
        mock_cache_instance = MagicMock()
        mock_cache.return_value = mock_cache_instance
        mock_cache_instance.get.return_value = None

        mock_response = Mock()
        mock_response.json.return_value = {"tipoNorma": "ley", "nroNorma": "123"}
        mock_response.content = b'{"tipoNorma": "ley", "nroNorma": "123"}'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = get_norma("ley", 2024, "123")

        assert result == {"tipoNorma": "ley", "nroNorma": "123"}

    @patch("mcp_impo._api.get_cache_manager")
    @patch("mcp_impo._api.httpx.get")
    def test_get_norma_not_found(self, mock_get, mock_cache):
        mock_cache_instance = MagicMock()
        mock_cache.return_value = mock_cache_instance
        mock_cache_instance.get.return_value = None

        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = get_norma("ley", 2024, "999999")

        assert result is None

    @patch("mcp_impo._api.get_cache_manager")
    @patch("mcp_impo._api.httpx.get")
    def test_get_norma_with_sequence(self, mock_get, mock_cache):
        mock_cache_instance = MagicMock()
        mock_cache.return_value = mock_cache_instance
        mock_cache_instance.get.return_value = None

        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.content = b"{}"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        get_norma("ley", 2024, "123", sec="A")

        call_url = mock_get.call_args[0][0]
        assert "2024-123/A" in call_url


class TestSearchNormas:
    @patch("mcp_impo._api.get_cache_manager")
    @patch("mcp_impo._api.httpx.get")
    def test_search_returns_results(self, mock_get, mock_cache):
        mock_cache_instance = MagicMock()
        mock_cache.return_value = mock_cache_instance
        mock_cache_instance.get.return_value = None

        mock_response = Mock()
        mock_response.json.return_value = [{"tipoNorma": "ley"}]
        mock_response.content = b'[{"tipoNorma": "ley"}]'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = search_normas("test")

        assert len(result) == 1
        assert result[0]["tipoNorma"] == "ley"

    @patch("mcp_impo._api.get_cache_manager")
    @patch("mcp_impo._api.httpx.get")
    def test_search_with_filters(self, mock_get, mock_cache):
        mock_cache_instance = MagicMock()
        mock_cache.return_value = mock_cache_instance
        mock_cache_instance.get.return_value = None

        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.content = b"[]"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        search_normas("test", tipo="ley", anio=2024, limit=10)

        call_args = mock_get.call_args
        params = call_args.kwargs.get("params", {})
        assert params["q"] == "test"
        assert params["tipo"] == "ley"
        assert params["anio"] == 2024
        assert params["limit"] == 10


class TestGetBaseInfo:
    @patch("mcp_impo._api.get_cache_manager")
    @patch("mcp_impo._api.httpx.get")
    def test_get_base_info_returns_data(self, mock_get, mock_cache):
        mock_cache_instance = MagicMock()
        mock_cache.return_value = mock_cache_instance
        mock_cache_instance.get.return_value = None

        mock_response = Mock()
        mock_response.json.return_value = [{"name": "bases"}]
        mock_response.content = b'[{"name": "bases"}]'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = get_base_info()

        assert result == [{"name": "bases"}]
