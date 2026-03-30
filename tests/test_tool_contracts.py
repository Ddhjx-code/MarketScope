"""Tool contract tests - verify each tool's interface and return format."""
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

    def test_search_tools_accept_query_parameter(self):
        """All search tools should accept a 'query' parameter."""
        search_tools = ["search_market_size", "search_competitors", "search_trends", "analyze_user_demand"]
        for tool_name in search_tools:
            tool = self.registry.get_tool(tool_name)
            assert tool is not None
            # Check the tool has an args_schema with query field
            if hasattr(tool, "args_schema") and tool.args_schema is not None:
                schema_fields = tool.args_schema.model_fields if hasattr(tool.args_schema, "model_fields") else {}
                assert "query" in schema_fields, f"{tool_name} missing 'query' parameter"


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
        stats_tools = [
            "search_national_stats",
            "get_stats_categories",
            "get_stats_leaf_categories",
            "get_stats_time_options",
            "get_stats_data",
            "batch_get_stats"
        ]
        for tool_name in stats_tools:
            tool = self.registry.get_tool(tool_name)
            result = tool.invoke({"query": "test"})
            parsed = json.loads(result)
            assert parsed["status"] == "MCP_CALL_REQUESTED"
            assert "tool" in parsed
            assert "mcp__" in parsed["tool"]


class TestToolReturnFormats:
    """Verify tools return data in expected formats."""

    def test_search_tools_return_non_empty_strings(self):
        """Search tools should return non-empty strings when invoked."""
        registry = ToolRegistry()
        search_tools = ["search_market_size", "search_competitors", "search_trends", "analyze_user_demand"]
        for tool_name in search_tools:
            tool = registry.get_tool(tool_name)
            result = tool.invoke({"query": "test"})
            assert isinstance(result, str), f"{tool_name} should return string"
            assert len(result) > 0, f"{tool_name} returned empty string"
