from typing import Optional
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from src.search_service import SearchService


class SearchMarketSizeInput(BaseModel):
    industry: str = Field(description="行业名称")


class SearchMarketSizeTool(BaseTool):
    """搜索市场规模数据的工具"""
    name = "search_market_size"
    description = "获取特定行业的市场规模、用户数量、增长率等数据"
    args_schema = SearchMarketSizeInput
    
    def __init__(self):
        super().__init__()
        self.search_service = SearchService()

    def _run(self, industry: str) -> str:
        """执行工具"""
        results = self.search_service.search_market_size(industry)
        return f"关于{industry}市场规模的搜索结果: {results}"


class SearchCompetitorsInput(BaseModel):
    app_type: str = Field(description="APP类型")


class SearchCompetitorsTool(BaseTool):
    """搜索竞争对手信息的工具"""
    name = "search_competitors"
    description = "获取特定类型APP的主要竞争对手、功能对比、市场份额等信息"
    args_schema = SearchCompetitorsInput
    
    def __init__(self):
        super().__init__()
        self.search_service = SearchService()

    def _run(self, app_type: str) -> str:
        """执行工具"""
        results = self.search_service.search_competitors(app_type)
        return f"关于{app_type}竞品的搜索结果: {results}"


class SearchTrendsInput(BaseModel):
    industry: str = Field(description="行业名称")


class SearchTrendsTool(BaseTool):
    """搜索行业趋势的工具"""
    name = "search_trends"
    description = "获取特定行业的发展趋势、技术方向、未来预测等信息"
    args_schema = SearchTrendsInput
    
    def __init__(self):
        super().__init__()
        self.search_service = SearchService()

    def _run(self, industry: str) -> str:
        """执行工具"""
        results = self.search_service.search_trends(industry)
        return f"关于{industry}趋势的搜索结果: {results}"


class AnalyzeUserDemandInput(BaseModel):
    app_type: str = Field(description="APP类型")


class AnalyzeUserDemandTool(BaseTool):
    """分析用户需求的工具"""
    name = "analyze_user_demand"
    description = "分析特定类型APP的用户痛点、需求变化、用户行为等信息"
    args_schema = AnalyzeUserDemandInput
    
    def __init__(self):
        super().__init__()
        self.search_service = SearchService()

    def _run(self, app_type: str) -> str:
        """执行工具"""
        results = self.search_service.analyze_user_demand(app_type)
        return f"关于{app_type}用户需求的分析结果: {results}"