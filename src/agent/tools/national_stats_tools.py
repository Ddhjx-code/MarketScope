from typing import Optional, Type, Dict, List
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
import json


class SearchNationalStatsInput(BaseModel):
    keyword: str = Field(description="搜索关键词，如 'GDP'、'人均可支配收入' 等")
    db: Optional[str] = Field(None, description="数据库筛选，空=全部, 可选 '年度数据' 或 '季度数据'")
    page: Optional[int] = Field(0, description="页码,从0开始")


class SearchNationalStatsTool(BaseTool):
    """搜索国家统计局指标和数据的工具"""
    name: str = "search_national_stats"
    description: str = "通过关键词搜索国家统计局指标和数据，可以快速查找指标及其最新值"
    args_schema: Type[BaseModel] = SearchNationalStatsInput

    def _run(self, keyword: str, db: str = None, page: int = 0) -> str:
        """执行工具 - 在Claude环境中调用MCP工具"""
        # 这个方法将在Claude环境中执行，其中MCP工具已注册
        # 一旦Agent决定需要调用此工具，Claude将执行底层的MCP工具
        result = {
            # 正在调用MCP工具的指示，实际调用由Claude环境处理
            "status": "MCP_CALL_REQUESTED",
            "tool": "mcp__national-stats-mcp__search_statistics",
            "parameters": {
                "keyword": keyword,
                "db": db,
                "page": page
            }
        }
        return json.dumps(result, ensure_ascii=False, indent=2)


class GetStatsCategoriesInput(BaseModel):
    dbcode: str = Field(description="数据库代码,指定数据类型:hgnd(年度数据), hgjd(季度数据)等")
    wdcode: Optional[str] = Field("zb", description="维度代码，默认为zb(指标)")


class GetStatsCategoriesTool(BaseTool):
    """获取国家统计局统计指标分类的工具"""
    name: str = "get_stats_categories"
    description: str = "获取国家统计局的统计指标分类,返回分类树结构(第一层)"
    args_schema: Type[BaseModel] = GetStatsCategoriesInput

    def _run(self, dbcode: str, wdcode: str = "zb") -> str:
        """执行工具 - 在Claude环境中调用MCP工具"""
        result = {
            "status": "MCP_CALL_REQUESTED",
            "tool": "mcp__national-stats-mcp__get_statistics_categories",
            "parameters": {
                "dbcode": dbcode,
                "wdcode": wdcode
            }
        }
        return json.dumps(result, ensure_ascii=False, indent=2)


class GetStatsLeafCategoriesInput(BaseModel):
    dbcode: str = Field(description="数据库代码,指定数据类型:hgnd(年度数据), hgjd(季度数据)等")


class GetStatsLeafCategoriesTool(BaseTool):
    """获取国家统计局特定数据库的所有叶子指标节点的工具"""
    name: str = "get_stats_leaf_categories"
    description: str = "递归获取国家统计局特定数据库的所有叶子指标节点(可查看分类下所有可查询指标)"
    args_schema: Type[BaseModel] = GetStatsLeafCategoriesInput

    def _run(self, dbcode: str) -> str:
        """执行工具 - 在Claude环境中调用MCP工具"""
        result = {
            "status": "MCP_CALL_REQUESTED",
            "tool": "mcp__national-stats-mcp__get_statistics_leaf_categories",
            "parameters": {
                "dbcode": dbcode
            }
        }
        return json.dumps(result, ensure_ascii=False, indent=2)


class GetStatsTimeOptionsInput(BaseModel):
    dbcode: str = Field(description="数据库代码,指定数据类型:hgnd(年度数据), hgjd(季度数据)等")


class GetStatsTimeOptionsTool(BaseTool):
    """获取指定数据库可选的时间范围维度的工具"""
    name: str = "get_stats_time_options"
    description: str = "获取指定数据库可选的时间范围维度"
    args_schema: Type[BaseModel] = GetStatsTimeOptionsInput

    def _run(self, dbcode: str) -> str:
        """执行工具 - 在Claude环境中调用MCP工具"""
        result = {
            "status": "MCP_CALL_REQUESTED",
            "tool": "mcp__national-stats-mcp__get_statistics_time_options",
            "parameters": {
                "dbcode": dbcode
            }
        }
        return json.dumps(result, ensure_ascii=False, indent=2)


class GetStatsDataInput(BaseModel):
    zb: str = Field(description="指标代码,通过分类或搜索获取")
    dbcode: str = Field(description="数据库代码,指定数据类型:hgnd(年度数据), hgjd(季度数据)等")
    sj: Optional[str] = Field("LAST30", description="时间范围,例如 LAST6 (最近6季度), 2025 (指定年份), LAST30 (最近30年) 等")


class GetStatsDataTool(BaseTool):
    """获取国家统计局特定指标的数据的工具"""
    name: str = "get_stats_data"
    description: str = "获取国家统计局特定指标的数据"
    args_schema: Type[BaseModel] = GetStatsDataInput

    def _run(self, zb: str, dbcode: str, sj: str = "LAST30") -> str:
        """执行工具 - 在Claude环境中调用MCP工具"""
        result = {
            "status": "MCP_CALL_REQUESTED",
            "tool": "mcp__national-stats-mcp__get_statistics_data",
            "parameters": {
                "zb": zb,
                "dbcode": dbcode,
                "sj": sj
            }
        }
        return json.dumps(result, ensure_ascii=False, indent=2)


class BatchGetStatsInput(BaseModel):
    queries: List[Dict[str, str]] = Field(description="查询参数数组，每个元素包含zb、dbcode和sj字段")


class BatchGetStatsTool(BaseTool):
    """批量获取国家统计局多个指标的数据的工具"""
    name: str = "batch_get_stats"
    description: str = "批量获取国家统计局多个指标的数据"
    args_schema: Type[BaseModel] = BatchGetStatsInput

    def _run(self, queries: List[Dict[str, str]]) -> str:
        """执行工具 - 在Claude环境中调用MCP工具"""
        result = {
            "status": "MCP_CALL_REQUESTED",
            "tool": "mcp__national-stats-mcp__batch_get_statistics",
            "parameters": {
                "queries": queries
            }
        }
        return json.dumps(result, ensure_ascii=False, indent=2)