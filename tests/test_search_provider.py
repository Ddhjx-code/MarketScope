"""搜索 Provider 测试 - 验证 BaseSearchProvider 密钥轮换和 Tavily 解析逻辑。

测试内容：
- BaseSearchProvider: 密钥轮询、错误跳过、重置逻辑
- TavilySearchProvider: 结果解析、配额处理、模块缺失
"""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from src.search_service import (
    BaseSearchProvider,
    TavilySearchProvider,
    SearchResponse,
    SearchResult,
)


class ConcreteTestProvider(BaseSearchProvider):
    """Concrete implementation of BaseSearchProvider for testing."""

    def __init__(self, api_keys=None, name="TestProvider"):
        super().__init__(api_keys or [], name)
        self._search_impl = None  # Will be set by tests

    def _do_search(self, query, api_key, max_results, days=7):
        if self._search_impl:
            return self._search_impl(query, api_key, max_results, days)
        return SearchResponse(
            query=query, results=[], provider=self.name, success=True
        )


class TestBaseSearchProviderKeyRotation:
    """Test API key rotation and error handling in BaseSearchProvider."""

    def test_get_next_key_round_robin(self):
        """Should rotate through keys in round-robin fashion."""
        provider = ConcreteTestProvider(api_keys=["key1", "key2", "key3"])
        keys = [provider._get_next_key() for _ in range(6)]
        assert keys == ["key1", "key2", "key3", "key1", "key2", "key3"]

    def test_skip_keys_with_errors(self):
        """Should skip keys that have more than 3 errors."""
        provider = ConcreteTestProvider(api_keys=["key1", "key2", "key3"])
        # Simulate key2 having too many errors
        provider._key_errors["key2"] = 4
        # Should skip key2 and return key3
        key = provider._get_next_key()
        assert key == "key1"  # First iteration returns key1
        # Advance past key1
        provider._key_errors["key1"] = 4
        key = provider._get_next_key()
        assert key == "key3"

    def test_reset_errors_when_all_keys_blocked(self):
        """Should reset error counts when all keys are blocked."""
        provider = ConcreteTestProvider(api_keys=["key1", "key2"])
        provider._key_errors["key1"] = 5
        provider._key_errors["key2"] = 5
        key = provider._get_next_key()
        assert key == "key1"
        assert provider._key_errors["key1"] == 0
        assert provider._key_errors["key2"] == 0

    def test_record_success_reduces_errors(self):
        """Should reduce error count on success."""
        provider = ConcreteTestProvider(api_keys=["key1"])
        provider._key_errors["key1"] = 3
        provider._record_success("key1")
        assert provider._key_errors["key1"] == 2

    def test_search_returns_error_when_no_keys(self):
        """Should return error response when no API keys configured."""
        provider = ConcreteTestProvider(api_keys=[])
        response = provider.search("test query")
        assert not response.success
        assert "未配置" in response.error_message

    def test_search_fallback_on_provider_error(self):
        """Should return error response when _do_search raises exception."""
        provider = ConcreteTestProvider(api_keys=["key1"])
        provider._search_impl = lambda *args: (_ for _ in ()).throw(Exception("Network error"))
        response = provider.search("test query")
        assert not response.success
        assert "Network error" in response.error_message

    def test_search_records_success_on_successful_call(self):
        """Should record success and return results."""
        provider = ConcreteTestProvider(api_keys=["key1"])
        provider._search_impl = lambda q, k, mr, d: SearchResponse(
            query=q, results=[SearchResult("title", "snippet", "url", "source")], provider="Test", success=True
        )
        response = provider.search("test query")
        assert response.success
        assert len(response.results) == 1
        assert provider._key_errors["key1"] == 0


class TestTavilySearchProvider:
    """Test TavilySearchProvider parsing and error handling."""

    def test_tavily_parses_results(self):
        """Should correctly parse Tavily API response."""
        provider = TavilySearchProvider(api_keys=["test_key"])
        mock_response = {
            "results": [
                {
                    "title": "Test Article",
                    "content": "Test content here",
                    "url": "https://example.com/article",
                    "published_date": "2024-01-15",
                }
            ]
        }
        with patch("tavily.TavilyClient") as MockClient:
            mock_client = MagicMock()
            mock_client.search.return_value = mock_response
            MockClient.return_value = mock_client

            response = provider._do_search("test query", "test_key", 5)

        assert response.success
        assert len(response.results) == 1
        result = response.results[0]
        assert result.title == "Test Article"
        assert result.snippet == "Test content here"
        assert result.url == "https://example.com/article"
        assert result.source == "example.com"

    def test_tavily_handles_rate_limit(self):
        """Should handle rate limit errors gracefully."""
        provider = TavilySearchProvider(api_keys=["test_key"])
        with patch("tavily.TavilyClient") as MockClient:
            mock_client = MagicMock()
            mock_client.search.side_effect = Exception("rate limit exceeded")
            MockClient.return_value = mock_client

            response = provider._do_search("test query", "test_key", 5)

        assert not response.success
        assert "配额" in response.error_message or "rate limit" in response.error_message.lower()

    def test_tavily_handles_missing_module(self):
        """Should return helpful error when tavily-python is not installed."""
        provider = TavilySearchProvider(api_keys=["test_key"])
        import sys
        # Temporarily hide the tavily module
        real_tavily = sys.modules.get("tavily")
        if "tavily" in sys.modules:
            del sys.modules["tavily"]

        with patch.dict("sys.modules", {"tavily": None}):
            response = provider._do_search("test query", "test_key", 5)

        assert not response.success
        assert "tavily-python" in response.error_message

        # Restore
        if real_tavily is not None:
            sys.modules["tavily"] = real_tavily

    def test_tavily_extract_domain(self):
        """Should extract domain from URL correctly."""
        assert TavilySearchProvider._extract_domain("https://www.example.com/path") == "example.com"
        assert TavilySearchProvider._extract_domain("https://api.service.io/v1") == "api.service.io"
        assert TavilySearchProvider._extract_domain("invalid_url") == "未知来源"
        assert TavilySearchProvider._extract_domain("") == "未知来源"
