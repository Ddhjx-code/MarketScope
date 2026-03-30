"""ToolRegistry unit tests - pure code logic, no LLM calls."""
import pytest
from src.agent.tools.registry import ToolRegistry


class TestToolRegistry:
    """Test ToolRegistry CRUD operations."""

    def test_registry_initializes_with_tools(self):
        """Registry should auto-register all default tools."""
        registry = ToolRegistry()
        tools = registry.get_all_tools()
        assert len(tools) == 10

    def test_registry_has_search_tools(self):
        """Should have all 4 search tools registered."""
        registry = ToolRegistry()
        assert registry.get_tool("search_market_size") is not None
        assert registry.get_tool("search_competitors") is not None
        assert registry.get_tool("search_trends") is not None
        assert registry.get_tool("analyze_user_demand") is not None

    def test_registry_has_national_stats_tools(self):
        """Should have all 6 national stats tools registered."""
        registry = ToolRegistry()
        assert registry.get_tool("search_national_stats") is not None
        assert registry.get_tool("get_stats_categories") is not None
        assert registry.get_tool("get_stats_leaf_categories") is not None
        assert registry.get_tool("get_stats_time_options") is not None
        assert registry.get_tool("get_stats_data") is not None
        assert registry.get_tool("batch_get_stats") is not None

    def test_get_nonexistent_tool_returns_none(self):
        """Getting a tool that doesn't exist should return None."""
        registry = ToolRegistry()
        assert registry.get_tool("nonexistent_tool") is None

    def test_register_custom_tool(self):
        """Should be able to register additional tools."""
        registry = ToolRegistry()
        initial_count = len(registry.get_all_tools())

        class CustomTool:
            def __init__(self):
                self.name = "custom_tool"

        registry.register_tool(CustomTool)
        assert len(registry.get_all_tools()) == initial_count + 1
        assert registry.get_tool("custom_tool") is not None

    def test_tool_names_are_unique(self):
        """All registered tools should have unique names."""
        registry = ToolRegistry()
        tools = registry.get_all_tools()
        names = [tool.name for tool in tools]
        assert len(names) == len(set(names)), f"Duplicate tool names: {names}"

    def test_tool_has_name_attribute(self):
        """All tools should have a name attribute."""
        registry = ToolRegistry()
        for tool in registry.get_all_tools():
            assert hasattr(tool, "name"), f"Tool missing 'name' attribute: {tool}"
            assert isinstance(tool.name, str)
            assert len(tool.name) > 0

    def test_tool_has_description_attribute(self):
        """All tools should have a description attribute."""
        registry = ToolRegistry()
        for tool in registry.get_all_tools():
            assert hasattr(tool, "description"), f"Tool missing 'description': {tool.name}"
            assert isinstance(tool.description, str)
            assert len(tool.description) > 0
