import pytest
from src.search_service import get_search_service


class TestSearchService:
    """搜索服务测试类"""

    def setup_method(self):
        """测试前设置"""
        self.search_service = get_search_service()

    def test_search_service_initialization(self):
        """测试搜索服务初始化"""
        assert self.search_service is not None
        assert hasattr(self.search_service, 'is_available')
        # 检查是否配置了API密钥（如果已配置，则服务应可用）
        # 由于API密钥在配置中，我们主要检查对象是否正确创建

    def test_search_market_size(self):
        """测试搜索市场规模功能"""
        response = self.search_service.search_market_size("社交媒体")
        # 检查返回类型是 SearchResponse 对象
        from src.search_service import SearchResponse
        assert isinstance(response, SearchResponse)
        # 检查基本属性
        assert hasattr(response, 'query')
        assert hasattr(response, 'results')
        assert hasattr(response, 'provider')
        assert hasattr(response, 'success')
        assert hasattr(response, 'error_message')
        assert hasattr(response, 'search_time')

    def test_search_competitors(self):
        """测试搜索竞争对手功能"""
        response = self.search_service.search_competitors("社交媒体")
        # 检查返回类型是 SearchResponse 对象
        from src.search_service import SearchResponse
        assert isinstance(response, SearchResponse)
        # 检查基本属性
        assert hasattr(response, 'query')
        assert hasattr(response, 'results')
        assert hasattr(response, 'provider')
        assert hasattr(response, 'success')
        assert hasattr(response, 'error_message')
        assert hasattr(response, 'search_time')

    def test_search_trends(self):
        """测试搜索行业趋势功能"""
        response = self.search_service.search_trends("人工智能")
        # 检查返回类型是 SearchResponse 对象
        from src.search_service import SearchResponse
        assert isinstance(response, SearchResponse)
        # 检查基本属性
        assert hasattr(response, 'query')
        assert hasattr(response, 'results')
        assert hasattr(response, 'provider')
        assert hasattr(response, 'success')
        assert hasattr(response, 'error_message')
        assert hasattr(response, 'search_time')

    def test_analyze_user_demand(self):
        """测试分析用户需求功能"""
        response = self.search_service.analyze_user_demand("电商APP")
        # 检查返回类型是 SearchResponse 对象
        from src.search_service import SearchResponse
        assert isinstance(response, SearchResponse)
        # 检查基本属性
        assert hasattr(response, 'query')
        assert hasattr(response, 'results')
        assert hasattr(response, 'provider')
        assert hasattr(response, 'success')
        assert hasattr(response, 'error_message')
        assert hasattr(response, 'search_time')

    def test_comprehensive_intel_search(self):
        """测试多维度情报搜索功能"""
        intel_results = self.search_service.search_comprehensive_intel("社交媒体", "社交媒体行业", max_searches=3)
        
        # 检查返回类型是字典
        assert isinstance(intel_results, dict)
        
        # 检查是否至少有一个搜索维度的结果
        assert len(intel_results) > 0
        
        # 检查每个结果是否是 SearchResponse 对象
        from src.search_service import SearchResponse
        for dim_name, response in intel_results.items():
            assert isinstance(response, SearchResponse)
            # 检查基本属性
            assert hasattr(response, 'query')
            assert hasattr(response, 'results')
            assert hasattr(response, 'provider')
            assert hasattr(response, 'success')
            assert hasattr(response, 'error_message')
            assert hasattr(response, 'search_time')

    def test_format_intel_report(self):
        """测试格式化情报报告功能"""
        # 先获取一些搜索结果
        intel_results = self.search_service.search_comprehensive_intel("社交媒体", "社交媒体行业", max_searches=2)
        
        # 格式化报告
        report = self.search_service.format_intel_report(intel_results, "社交媒体APP")
        
        # 检查返回类型是字符串
        assert isinstance(report, str)
        
        # 检查报告是否包含APP类型
        assert "社交媒体APP" in report
        
        # 检查报告长度（至少有内容）
        assert len(report) > 0

    def test_search_with_context_formatting(self):
        """测试搜索结果上下文格式化功能"""
        response = self.search_service.search_market_size("人工智能")
        
        # 测试上下文格式化
        context = response.to_context()
        
        # 检查返回类型是字符串
        assert isinstance(context, str)
        
        # 检查是否包含查询关键字
        if response.success and response.results:
            assert response.query in context
            assert response.provider in context

    def test_search_service_availability(self):
        """测试搜索服务可用性"""
        is_available = self.search_service.is_available
        # 检查返回类型是布尔值
        assert isinstance(is_available, bool)


class TestSearchServiceCache:
    """Test SearchService caching behavior with mocked providers."""

    def _make_service(self):
        """Create SearchService with no real providers."""
        from src.search_service import SearchService
        return SearchService(tavily_keys=None)

    def test_cache_key_includes_all_params(self):
        """Cache key should include query, max_results, and days."""
        service = self._make_service()
        key1 = service._cache_key("test", 5, 7)
        key2 = service._cache_key("test", 10, 7)
        key3 = service._cache_key("test", 5, 14)
        assert key1 != key2
        assert key1 != key3
        assert key2 != key3

    def test_cache_hit_returns_cached_response(self):
        """Should return cached response on cache hit."""
        from src.search_service import SearchResponse
        import time

        service = self._make_service()
        # Manually put a response in cache
        cached_response = SearchResponse(query="test", results=[], provider="Test", success=True)
        key = service._cache_key("test", 5, 7)
        service._cache[key] = (time.time(), cached_response)

        result = service._get_cached(key)
        assert result is not None
        assert result.success is True

    def test_cache_miss_returns_none(self):
        """Should return None on cache miss."""
        service = self._make_service()
        result = service._get_cached("nonexistent_key")
        assert result is None

    def test_cache_ttl_expiry(self):
        """Should expire cached entries after TTL."""
        from src.search_service import SearchResponse
        import time

        service = self._make_service()
        service._cache_ttl = 1  # 1 second TTL
        cached_response = SearchResponse(query="test", results=[], provider="Test", success=True)
        key = service._cache_key("test", 5, 7)
        # Insert with expired timestamp
        service._cache[key] = (time.time() - 2, cached_response)

        result = service._get_cached(key)
        assert result is None
        assert key not in service._cache  # Should have been deleted

    def test_cache_eviction_on_overflow(self):
        """Should evict oldest entries when cache exceeds max size."""
        from src.search_service import SearchResponse
        import time

        service = self._make_service()
        # The cache limit is 500 (hardcoded in _put_cache)
        MAX_CACHE_SIZE = 500
        # Fill cache to the limit
        for i in range(MAX_CACHE_SIZE):
            key = f"key_{i}"
            response = SearchResponse(query=f"q{i}", results=[], provider="Test", success=True)
            service._cache[key] = (time.time(), response)

        assert len(service._cache) == MAX_CACHE_SIZE

        # Adding one more should trigger eviction
        extra_key = "extra_key"
        extra_response = SearchResponse(query="extra", results=[], provider="Test", success=True)
        service._put_cache(extra_key, extra_response)

        assert len(service._cache) <= MAX_CACHE_SIZE
        assert extra_key in service._cache  # New entry should be present

    def test_put_cache_stores_response(self):
        """Should store response in cache."""
        from src.search_service import SearchResponse

        service = self._make_service()
        response = SearchResponse(query="test", results=[], provider="Test", success=True)
        key = "test_key"
        service._put_cache(key, response)

        assert key in service._cache
        stored_ts, stored_response = service._cache[key]
        assert stored_response.success is True
        assert stored_response.query == "test"