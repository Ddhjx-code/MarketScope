import pytest
from src.search_service import get_search_service


class TestSearchService:
    """搜索服务测试类"""

    def setup_method(self):
        """测试前设置"""
        self.search_service = get_search_service()

    def test_search_market_size(self):
        """测试搜索市场规模功能"""
        response = self.search_service.search_market_size("社交媒体")
        # 检查返回类型是 SearchResponse 对象
        from src.search_service import SearchResponse
        assert isinstance(response, SearchResponse)

    def test_search_competitors(self):
        """测试搜索竞争对手功能"""
        response = self.search_service.search_competitors("社交媒体")
        # 检查返回类型是 SearchResponse 对象
        from src.search_service import SearchResponse
        assert isinstance(response, SearchResponse)

    def test_search_trends(self):
        """测试搜索行业趋势功能"""
        response = self.search_service.search_trends("社交媒体")
        # 检查返回类型是 SearchResponse 对象
        from src.search_service import SearchResponse
        assert isinstance(response, SearchResponse)

    def test_analyze_user_demand(self):
        """测试分析用户需求功能"""
        response = self.search_service.analyze_user_demand("社交媒体")
        # 检查返回类型是 SearchResponse 对象
        from src.search_service import SearchResponse
        assert isinstance(response, SearchResponse)