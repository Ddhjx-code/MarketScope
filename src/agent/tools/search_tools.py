from typing import Optional, Type
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from src.search_service import get_search_service


class SearchMarketSizeInput(BaseModel):
    industry: str = Field(description="行业名称")


class SearchMarketSizeTool(BaseTool):
    """搜索市场规模数据的工具"""
    name: str = "search_market_size"
    description: str = "获取特定行业的市场规模、用户数量、增长率等数据"
    args_schema: Type[BaseModel] = SearchMarketSizeInput
    
    def _run(self, industry: str) -> str:
        """执行工具"""
        search_service = get_search_service()
        if not search_service.is_available:
            return "搜索服务不可用（未配置API Key）"

        response = search_service.search_market_size(industry)
        if response.success:
            return response.to_context()
        else:
            return f"搜索失败: {response.error_message}"


class SearchCompetitorsInput(BaseModel):
    app_type: str = Field(description="APP类型")


class SearchCompetitorsTool(BaseTool):
    """搜索竞争对手信息的工具"""
    name: str = "search_competitors"
    description: str = "获取特定类型APP的主要竞争对手、功能对比、市场份额等信息"
    args_schema: Type[BaseModel] = SearchCompetitorsInput
    
    def _run(self, app_type: str) -> str:
        """执行工具"""
        search_service = get_search_service()
        if not search_service.is_available:
            return "搜索服务不可用（未配置API Key）"

        response = search_service.search_competitors(app_type)
        if response.success:
            return response.to_context()
        else:
            return f"搜索失败: {response.error_message}"


class SearchTrendsInput(BaseModel):
    industry: str = Field(description="行业名称")


class SearchTrendsTool(BaseTool):
    """搜索行业趋势的工具"""
    name: str = "search_trends"
    description: str = "获取特定行业的发展趋势、技术方向、未来预测等信息"
    args_schema: Type[BaseModel] = SearchTrendsInput
    
    def _run(self, industry: str) -> str:
        """执行工具"""
        search_service = get_search_service()
        if not search_service.is_available:
            return "搜索服务不可用（未配置API Key）"

        response = search_service.search_trends(industry)
        if response.success:
            return response.to_context()
        else:
            return f"搜索失败: {response.error_message}"


class AnalyzeUserDemandInput(BaseModel):
    app_type: str = Field(description="APP类型")


class AnalyzeUserDemandTool(BaseTool):
    """分析用户需求的工具"""
    name: str = "analyze_user_demand"
    description: str = "分析特定类型APP的用户痛点、需求变化、用户行为等信息"
    args_schema: Type[BaseModel] = AnalyzeUserDemandInput
    
    def _run(self, app_type: str) -> str:
        """执行工具"""
        search_service = get_search_service()
        if not search_service.is_available:
            return "搜索服务不可用（未配置API Key）"

        response = search_service.analyze_user_demand(app_type)
        if response.success:
            return response.to_context()
        else:
            return f"搜索失败: {response.error_message}"