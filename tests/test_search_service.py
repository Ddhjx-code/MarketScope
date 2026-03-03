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