from typing import Dict, List, Any
from tavily import TavilyClient
from config import Config


class SearchService:
    """搜索服务类"""

    def __init__(self):
        """初始化搜索服务"""
        if not Config.TAVILY_API_KEY:
            raise ValueError("TAVILY_API_KEY 未配置")
        
        self.client = TavilyClient(api_key=Config.TAVILY_API_KEY)

    def search(self, query: str, max_results: int = None) -> List[Dict[str, Any]]:
        """
        执行搜索
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
            
        Returns:
            搜索结果列表
        """
        if max_results is None:
            max_results = Config.MAX_SEARCH_RESULTS
            
        try:
            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth="advanced"
            )
            return response.get('results', [])
        except Exception as e:
            print(f"搜索出错: {e}")
            return []

    def search_market_size(self, industry: str) -> List[Dict[str, Any]]:
        """搜索市场规模数据"""
        query = f"{industry} 市场规模 市场数据 用户数量 增长率"
        return self.search(query)

    def search_competitors(self, app_type: str) -> List[Dict[str, Any]]:
        """搜索竞争对手信息"""
        query = f"{app_type} 主要竞争对手 竞品分析 市场份额"
        return self.search(query)

    def search_trends(self, industry: str) -> List[Dict[str, Any]]:
        """搜索行业趋势"""
        query = f"{industry} 行业趋势 发展方向 技术趋势 未来预测"
        return self.search(query)

    def analyze_user_demand(self, app_type: str) -> List[Dict[str, Any]]:
        """分析用户需求"""
        query = f"{app_type} 用户痛点 需求变化 用户行为 满意度"
        return self.search(query)