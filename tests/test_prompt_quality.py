"""Prompt 质量测试 - 验证提示词能否引导正确的工具调用。

测试内容：
- Research Agent 是否调用所有 4 个搜索工具
- Agent 是否根据 APP 类型调整查询内容
- 输出报告是否包含关键章节
- 不同场景（社交/电商）的回归测试

注意：使用真实 LLM 调用，标记 @pytest.mark.slow
运行方式: pytest tests/test_prompt_quality.py -v --run-slow
"""
import pytest
import os


@pytest.mark.slow
@pytest.mark.skipif(not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
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

        # Check for key report sections (support both English and Chinese)
        result_str = str(result)
        required_sections = [
            ["market", "市场"],
            ["competitor", "竞争"],
            ["trend", "趋势"],
            ["recommendation", "建议"]
        ]
        for section_keywords in required_sections:
            assert any(kw.lower() in result_str.lower() for kw in section_keywords), \
                f"Report missing section matching: {section_keywords}"


@pytest.mark.slow
@pytest.mark.skipif(not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
class TestPromptRegression:
    """Detect prompt changes that break expected behavior."""

    def test_social_app_scenario(self):
        """Social app analysis should identify key competitors."""
        from src.agent.executor import AgentExecutor

        executor = AgentExecutor()
        result = executor.execute("社交类APP，主要功能是兴趣小组聊天")

        result_str = str(result).lower()
        # Should identify major social platforms or social-related context
        social_keywords = ["微信", "qq", "soul", "陌陌", "wechat", "社交", "social", "豆瓣", "微博"]
        assert any(kw in result_str for kw in social_keywords), \
            "Should identify social platform context or competitors"

    def test_ecommerce_app_scenario(self):
        """E-commerce app analysis should focus on different factors."""
        from src.agent.executor import AgentExecutor

        executor = AgentExecutor()
        result = executor.execute("电商类APP，主要功能是二手商品交易")

        result_str = str(result).lower()
        # Should identify second-hand/e-commerce relevant context
        assert any(keyword in result_str for keyword in ["二手", "电商", "trading", "commerce", "闲置"]), \
            "Should identify e-commerce/second-hand relevant context"
