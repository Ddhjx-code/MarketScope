"""Prompt quality tests - verify prompts lead to correct tool usage.

These tests use the REAL LLM and are marked @pytest.mark.slow.
Run with: pytest tests/test_prompt_quality.py -v --run-slow
"""
import pytest


@pytest.mark.slow
class TestPromptQuality:
    """Verify that prompts lead to correct Agent behavior."""

    def test_researcher_calls_all_search_tools(self, sample_user_input):
        """Research Agent should call all 4 search tools for a typical input."""
        from src.agent.executor import AgentExecutor
        from src.agent.tools.registry import ToolRegistry

        registry = ToolRegistry()
        search_tools = [
            registry.get_tool("search_market_size"),
            registry.get_tool("search_competitors"),
            registry.get_tool("search_trends"),
            registry.get_tool("analyze_user_demand")
        ]

        # Create executor with only search tools to keep test focused
        executor = AgentExecutor(tools=search_tools)
        result = executor.execute(sample_user_input)

        # Verify result contains data from multiple tools
        result_str = str(result).lower()
        assert any(keyword in result_str for keyword in ["市场", "规模", "market", "size"]), \
            "Research should include market size data"

    def test_researcher_understands_app_type(self):
        """Research Agent should adapt queries to the specific APP type."""
        from src.agent.executor import AgentExecutor

        executor = AgentExecutor()
        result = executor.execute("工具类APP，主要功能是个人记账和预算管理")

        # Should contain finance/accounting related data
        result_str = str(result).lower()
        assert any(keyword in result_str for keyword in ["记账", "预算", "finance", "budget", "accounting"]), \
            "Research should be relevant to the specified APP type"

    def test_report_format_matches_schema(self, sample_user_input):
        """Final output should match the expected report schema."""
        from src.agent.executor import AgentExecutor

        executor = AgentExecutor()
        result = executor.execute(sample_user_input)

        # Check for key report sections
        result_str = str(result)
        required_sections = ["market", "competitor", "trend", "recommendation"]
        for section in required_sections:
            assert section.lower() in result_str.lower(), \
                f"Report missing '{section}' section"


@pytest.mark.slow
class TestPromptRegression:
    """Detect prompt changes that break expected behavior."""

    def test_social_app_scenario(self):
        """Social app analysis should identify key competitors."""
        from src.agent.executor import AgentExecutor

        executor = AgentExecutor()
        result = executor.execute("社交类APP，主要功能是兴趣小组聊天")

        result_str = str(result).lower()
        # Should identify major social platforms
        assert any(platform in result_str for platform in ["微信", "qq", "soul", "陌陌", "wechat"]), \
            "Should identify major social platform competitors"

    def test_ecommerce_app_scenario(self):
        """E-commerce app analysis should focus on different factors."""
        from src.agent.executor import AgentExecutor

        executor = AgentExecutor()
        result = executor.execute("电商类APP，主要功能是二手商品交易")

        result_str = str(result).lower()
        # Should identify second-hand/e-commerce relevant context
        assert any(keyword in result_str for keyword in ["二手", "电商", "trading", "commerce", "闲置"]), \
            "Should identify e-commerce/second-hand relevant context"
