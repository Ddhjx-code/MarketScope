from typing import List, Type
from langchain_core.tools import BaseTool
from .search_tools import (
    SearchMarketSizeTool,
    SearchCompetitorsTool,
    SearchTrendsTool,
    AnalyzeUserDemandTool
)
from .national_stats_tools import (
    SearchNationalStatsTool,
    GetStatsCategoriesTool,
    GetStatsLeafCategoriesTool,
    GetStatsTimeOptionsTool,
    GetStatsDataTool,
    BatchGetStatsTool
)


class ToolRegistry:
    """工具注册表"""

    def __init__(self):
        """初始化工具注册表"""
        self._tools = {}
        self._register_default_tools()

    def _register_default_tools(self):
        """注册默认工具"""
        default_tools = [
            SearchMarketSizeTool,
            SearchCompetitorsTool,
            SearchTrendsTool,
            AnalyzeUserDemandTool,
            SearchNationalStatsTool,
            GetStatsCategoriesTool,
            GetStatsLeafCategoriesTool,
            GetStatsTimeOptionsTool,
            GetStatsDataTool,
            BatchGetStatsTool
        ]

        for tool_class in default_tools:
            self.register_tool(tool_class)

    def register_tool(self, tool_class: Type[BaseTool]):
        """注册工具类"""
        instance = tool_class()
        self._tools[instance.name] = instance

    def get_tool(self, name: str) -> BaseTool:
        """获取工具实例"""
        return self._tools.get(name)

    def get_all_tools(self) -> List[BaseTool]:
        """获取所有工具实例"""
        return list(self._tools.values())