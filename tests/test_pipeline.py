"""三阶段 Pipeline 测试 - 验证 Research/Analysis/Report 流水线。

测试内容（TDD RED → GREEN → REFACTOR）：
- Pipeline 编排：三阶段数据流、端到端、错误处理
- Executor 扩展：自定义 system_prompt、tools 覆盖
- Prompt 内容：各 Agent 的 system prompt 包含必要信息
"""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock

REPORT_SCHEMA_KEYS = {
    "app_type", "market_analysis", "competitor_analysis",
    "trend_analysis", "opportunity_assessment", "recommendations"
}


class TestPrompts:
    """System prompt 内容测试。"""

    def test_researcher_prompt_mentions_tools(self):
        """Researcher prompt should mention available tools."""
        from src.agent.prompts.researcher import SYSTEM_PROMPT
        assert "tool" in SYSTEM_PROMPT.lower() or "搜索" in SYSTEM_PROMPT

    def test_analyst_prompt_mentions_dimensions(self):
        """Analyst prompt should mention analysis dimensions."""
        from src.agent.prompts.analyst import SYSTEM_PROMPT
        assert "market" in SYSTEM_PROMPT.lower() or "市场" in SYSTEM_PROMPT

    def test_reporter_prompt_mentions_schema(self):
        """Reporter prompt should mention output schema."""
        from src.agent.prompts.reporter import SYSTEM_PROMPT
        assert "json" in SYSTEM_PROMPT.lower() or "report" in SYSTEM_PROMPT.lower()


class TestExecutorWithCustomPrompt:
    """Executor 自定义 prompt 测试。"""

    def test_executor_accepts_system_prompt(self):
        """Executor should accept a custom system_prompt parameter."""
        from src.agent.executor import AgentExecutor
        with patch("src.agent.executor.ChatOpenAI"), \
             patch("src.agent.executor.create_react_agent"):
            executor = AgentExecutor(system_prompt="You are a researcher")
            assert executor._system_prompt == "You are a researcher"

    def test_executor_accepts_tools_override(self):
        """Executor should use provided tools instead of all registry tools."""
        from src.agent.executor import AgentExecutor
        from unittest.mock import MagicMock
        mock_tool = MagicMock()
        mock_tool.name = "mock_tool"
        with patch("src.agent.executor.ChatOpenAI"), \
             patch("src.agent.executor.create_react_agent"):
            executor = AgentExecutor(tools=[mock_tool])
            assert executor.tools == [mock_tool]

    def test_executor_default_uses_all_tools(self):
        """Executor without tools param should use all registry tools."""
        from src.agent.executor import AgentExecutor
        with patch("src.agent.executor.ChatOpenAI"), \
             patch("src.agent.executor.create_react_agent"):
            executor = AgentExecutor()
            assert len(executor.tools) > 0


class TestPipelineOrchestration:
    """Pipeline 编排测试 — 验证三阶段数据流。"""

    def _make_raw_data(self):
        return {
            "market_size": [{"title": "Market Report", "content": "市场规模500亿"}],
            "competitors": [{"title": "Competitor Analysis", "content": "主要竞争者：微信、QQ"}],
            "trends": [{"title": "Industry Trends", "content": "AI驱动内容推荐"}],
            "user_demand": [{"title": "User Demand", "content": "隐私保护需求高"}],
        }

    def _make_structured_analysis(self):
        return {
            "market_analysis": {"size": "500亿", "growth_rate": "15%", "user_base": "8亿"},
            "competitor_analysis": {"top_players": ["微信", "QQ"], "feature_comparison": "功能差异化", "market_share": "微信主导"},
            "trend_analysis": {"technology_trends": "AI推荐", "user_behavior": "垂直社交", "policy_impact": "数据安全法规"},
            "opportunity_assessment": {"entry_opportunities": "垂直兴趣社交", "differentiation_points": "AI匹配", "barriers": "获客成本高"},
        }

    def _make_final_report(self):
        return {
            "app_type": "社交类APP",
            "market_analysis": {"size": "500亿", "growth_rate": "15%", "user_base": "8亿"},
            "competitor_analysis": {"top_players": ["微信", "QQ"], "feature_comparison": "功能差异化", "market_share": "微信主导"},
            "trend_analysis": {"technology_trends": "AI推荐", "user_behavior": "垂直社交", "policy_impact": "数据安全"},
            "opportunity_assessment": {"entry_opportunities": "垂直兴趣社交", "differentiation_points": "AI匹配", "barriers": "获客成本高"},
            "recommendations": {"feasibility": "中等偏上", "strategy": "聚焦兴趣匹配", "risks": "获客成本高"},
        }

    def test_research_stage_produces_raw_data(self):
        """Research stage should return raw_data with search results."""
        from src.agent.pipeline import run_research_stage
        mock_executor = MagicMock()
        mock_executor.execute.return_value = self._make_raw_data()

        raw_data = run_research_stage(mock_executor, "社交类APP")
        assert "market_size" in raw_data
        assert "competitors" in raw_data
        assert "trends" in raw_data
        assert "user_demand" in raw_data

    def test_analysis_stage_structures_data(self):
        """Analysis stage should produce structured_analysis dict."""
        from src.agent.pipeline import run_analysis_stage
        mock_executor = MagicMock()
        mock_executor.execute.return_value = self._make_structured_analysis()

        result = run_analysis_stage(mock_executor, "社交类APP", self._make_raw_data())
        assert "market_analysis" in result
        assert "competitor_analysis" in result
        assert "trend_analysis" in result

    def test_report_stage_formats_output(self):
        """Report stage should produce final report matching schema."""
        from src.agent.pipeline import run_report_stage
        mock_executor = MagicMock()
        mock_executor.execute.return_value = self._make_final_report()

        result = run_report_stage(mock_executor, "社交类APP", self._make_structured_analysis())
        for key in REPORT_SCHEMA_KEYS:
            assert key in result, f"Missing key: {key}"

    def test_pipeline_end_to_end(self):
        """Full pipeline should chain all three stages."""
        from src.agent.pipeline import AnalysisPipeline
        pipeline = AnalysisPipeline()

        with patch.object(pipeline, "_create_research_executor") as mock_research, \
             patch.object(pipeline, "_create_analysis_executor") as mock_analysis, \
             patch.object(pipeline, "_create_report_executor") as mock_report:

            mock_research.return_value.execute.return_value = self._make_raw_data()
            mock_analysis.return_value.execute.return_value = self._make_structured_analysis()
            mock_report.return_value.execute.return_value = self._make_final_report()

            result = pipeline.run("社交类APP")

        assert result["app_type"] == "社交类APP"
        assert "recommendations" in result
        assert "market_analysis" in result

    def test_pipeline_handles_research_failure(self):
        """Pipeline should propagate errors from failed research stage."""
        from src.agent.pipeline import AnalysisPipeline
        pipeline = AnalysisPipeline()

        with patch.object(pipeline, "_create_research_executor") as mock_research:
            mock_research.return_value.execute.return_value = {"error": "Research failed"}

            result = pipeline.run("社交类APP")

        assert "error" in result

    def test_pipeline_handles_analysis_failure(self):
        """Pipeline should propagate errors from failed analysis stage."""
        from src.agent.pipeline import AnalysisPipeline
        pipeline = AnalysisPipeline()

        with patch.object(pipeline, "_create_research_executor") as mock_research, \
             patch.object(pipeline, "_create_analysis_executor") as mock_analysis:
            mock_research.return_value.execute.return_value = self._make_raw_data()
            mock_analysis.return_value.execute.return_value = {"error": "Analysis failed"}

            result = pipeline.run("社交类APP")

        assert "error" in result
