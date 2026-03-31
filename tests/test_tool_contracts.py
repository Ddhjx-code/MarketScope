"""工具契约测试 - 验证每个工具的接口和返回格式。

测试内容：
- 4 个搜索工具的 name/description/args_schema 正确性
- 6 个国家统计工具的接口完整性
- 统计工具返回 MCP_REQUEST JSON 格式
- 搜索工具返回非空字符串
"""
import pytest
from src.agent.tools.registry import ToolRegistry


class TestSearchToolContracts:
    """Verify search tools have correct interface."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.registry = ToolRegistry()

    def test_search_market_size_interface(self):
        tool = self.registry.get_tool("search_market_size")
        assert tool is not None
        assert tool.name == "search_market_size"
        assert "市场规模" in tool.description or "market" in tool.description.lower()
        assert hasattr(tool, "args_schema")

    def test_search_competitors_interface(self):
        tool = self.registry.get_tool("search_competitors")
        assert tool is not None
        assert tool.name == "search_competitors"
        assert "竞争" in tool.description or "competitor" in tool.description.lower()
        assert hasattr(tool, "args_schema")

    def test_search_trends_interface(self):
        tool = self.registry.get_tool("search_trends")
        assert tool is not None
        assert tool.name == "search_trends"
        assert "趋势" in tool.description or "trend" in tool.description.lower()
        assert hasattr(tool, "args_schema")

    def test_analyze_user_demand_interface(self):
        tool = self.registry.get_tool("analyze_user_demand")
        assert tool is not None
        assert tool.name == "analyze_user_demand"
        assert "需求" in tool.description or "demand" in tool.description.lower()
        assert hasattr(tool, "args_schema")

    def test_search_tools_accept_correct_parameters(self):
        """Search tools should accept their specific parameters (industry or app_type)."""
        # Tools that use 'industry' parameter
        industry_tools = ["search_market_size", "search_trends"]
        for tool_name in industry_tools:
            tool = self.registry.get_tool(tool_name)
            assert tool is not None
            if hasattr(tool, "args_schema") and tool.args_schema is not None:
                schema_fields = tool.args_schema.model_fields if hasattr(tool.args_schema, "model_fields") else {}
                assert "industry" in schema_fields, f"{tool_name} missing 'industry' parameter"

        # Tools that use 'app_type' parameter
        app_type_tools = ["search_competitors", "analyze_user_demand"]
        for tool_name in app_type_tools:
            tool = self.registry.get_tool(tool_name)
            assert tool is not None
            if hasattr(tool, "args_schema") and tool.args_schema is not None:
                schema_fields = tool.args_schema.model_fields if hasattr(tool.args_schema, "model_fields") else {}
                assert "app_type" in schema_fields, f"{tool_name} missing 'app_type' parameter"


class TestNationalStatsToolContracts:
    """Verify national stats tools have correct interface."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.registry = ToolRegistry()

    def test_search_national_stats_interface(self):
        tool = self.registry.get_tool("search_national_stats")
        assert tool is not None
        assert tool.name == "search_national_stats"
        assert hasattr(tool, "args_schema")

    def test_get_stats_categories_interface(self):
        tool = self.registry.get_tool("get_stats_categories")
        assert tool is not None
        assert tool.name == "get_stats_categories"
        assert hasattr(tool, "args_schema")

    def test_get_stats_leaf_categories_interface(self):
        tool = self.registry.get_tool("get_stats_leaf_categories")
        assert tool is not None
        assert tool.name == "get_stats_leaf_categories"
        assert hasattr(tool, "args_schema")

    def test_get_stats_time_options_interface(self):
        tool = self.registry.get_tool("get_stats_time_options")
        assert tool is not None
        assert tool.name == "get_stats_time_options"
        assert hasattr(tool, "args_schema")

    def test_get_stats_data_interface(self):
        tool = self.registry.get_tool("get_stats_data")
        assert tool is not None
        assert tool.name == "get_stats_data"
        assert hasattr(tool, "args_schema")

    def test_batch_get_stats_interface(self):
        tool = self.registry.get_tool("batch_get_stats")
        assert tool is not None
        assert tool.name == "batch_get_stats"
        assert hasattr(tool, "args_schema")

    def test_national_stats_tools_return_mcp_request_format(self):
        """National stats tools should return MCP request JSON when invoked."""
        import json
        # Each tool has different required parameters
        tool_params = {
            "search_national_stats": {"keyword": "test"},
            "get_stats_categories": {"dbcode": "hgnd"},
            "get_stats_leaf_categories": {"dbcode": "hgnd"},
            "get_stats_time_options": {"dbcode": "hgnd"},
            "get_stats_data": {"zb": "test", "dbcode": "hgnd"},
            "batch_get_stats": {"queries": [{"zb": "test", "dbcode": "hgnd"}]},
        }
        for tool_name, params in tool_params.items():
            tool = self.registry.get_tool(tool_name)
            result = tool.invoke(params)
            parsed = json.loads(result)
            assert parsed["status"] == "MCP_CALL_REQUESTED"
            assert "tool" in parsed
            assert "mcp__" in parsed["tool"]


class TestToolReturnFormats:
    """Verify tools return data in expected formats."""

    def test_search_tools_return_non_empty_strings(self):
        """Search tools should return non-empty strings when invoked."""
        registry = ToolRegistry()
        # Industry-based tools
        for tool_name in ["search_market_size", "search_trends"]:
            tool = registry.get_tool(tool_name)
            result = tool.invoke({"industry": "test"})
            assert isinstance(result, str), f"{tool_name} should return string"
            assert len(result) > 0, f"{tool_name} returned empty string"
        # App-type-based tools
        for tool_name in ["search_competitors", "analyze_user_demand"]:
            tool = registry.get_tool(tool_name)
            result = tool.invoke({"app_type": "test"})
            assert isinstance(result, str), f"{tool_name} should return string"
            assert len(result) > 0, f"{tool_name} returned empty string"
