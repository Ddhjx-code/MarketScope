import pytest
from src.search_service import SearchService


class TestSearchService:
    """搜索服务测试类"""

    def setup_method(self):
        """测试前设置"""
        self.search_service = SearchService()

    def test_search_market_size(self):
        """测试搜索市场规模功能"""
        results = self.search_service.search_market_size("社交媒体")
        assert isinstance(results, list)
        # 由于需要API调用，我们只检查返回类型

    def test_search_competitors(self):
        """测试搜索竞争对手功能"""
        results = self.search_service.search_competitors("社交媒体")
        assert isinstance(results, list)

    def test_search_trends(self):
        """测试搜索行业趋势功能"""
        results = self.search_service.search_trends("社交媒体")
        assert isinstance(results, list)

    def test_analyze_user_demand(self):
        """测试分析用户需求功能"""
        results = self.search_service.analyze_user_demand("社交媒体")
        assert isinstance(results, list)