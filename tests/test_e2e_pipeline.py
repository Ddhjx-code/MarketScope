"""端到端流水线测试 - 验证完整分析流程。

测试内容：
- 3 种典型 APP（社交/工具/电商）的报告 schema 验证
- 报告是否包含可执行的建议
- 是否正确识别竞争对手
- Mock 模式下的快速流水线测试

注意：完整测试使用真实 LLM，标记 @pytest.mark.slow
运行方式: pytest tests/test_e2e_pipeline.py -v --run-slow
"""
import pytest
import os

REPORT_SCHEMA_KEYS = {
    "app_type",
    "market_analysis",
    "competitor_analysis",
    "trend_analysis",
    "opportunity_assessment",
    "recommendations"
}

MARKET_ANALYSIS_KEYS = {"size", "growth_rate", "user_base"}
COMPETITOR_ANALYSIS_KEYS = {"top_players", "feature_comparison", "market_share"}
TREND_ANALYSIS_KEYS = {"technology_trends", "user_behavior", "policy_impact"}
OPPORTUNITY_KEYS = {"entry_opportunities", "differentiation_points", "barriers"}
RECOMMENDATION_KEYS = {"feasibility", "strategy", "risks"}


def validate_report_schema(report: dict) -> list:
    """Validate report against expected schema. Returns list of missing fields."""
    errors = []

    for key in REPORT_SCHEMA_KEYS:
        if key not in report:
            errors.append(f"Missing top-level key: {key}")

    if "market_analysis" in report:
        for key in MARKET_ANALYSIS_KEYS:
            if key not in report["market_analysis"]:
                errors.append(f"Missing market_analysis.{key}")

    if "competitor_analysis" in report:
        for key in COMPETITOR_ANALYSIS_KEYS:
            if key not in report["competitor_analysis"]:
                errors.append(f"Missing competitor_analysis.{key}")

    if "trend_analysis" in report:
        for key in TREND_ANALYSIS_KEYS:
            if key not in report["trend_analysis"]:
                errors.append(f"Missing trend_analysis.{key}")

    if "opportunity_assessment" in report:
        for key in OPPORTUNITY_KEYS:
            if key not in report["opportunity_assessment"]:
                errors.append(f"Missing opportunity_assessment.{key}")

    if "recommendations" in report:
        for key in RECOMMENDATION_KEYS:
            if key not in report["recommendations"]:
                errors.append(f"Missing recommendations.{key}")

    return errors


@pytest.mark.slow
@pytest.mark.skipif(not os.environ.get("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
class TestE2EPipeline:
    """End-to-end tests for complete analysis pipeline."""

    def test_social_app_report_schema(self):
        """Social app analysis should produce a valid report."""
        from src.agent.executor import AgentExecutor

        executor = AgentExecutor()
        result = executor.execute("社交类APP，主要功能是兴趣小组聊天")

        errors = validate_report_schema(result)
        assert len(errors) == 0, f"Report schema validation failed: {errors}"

    def test_tool_app_report_schema(self):
        """Tool app analysis should produce a valid report."""
        from src.agent.executor import AgentExecutor

        executor = AgentExecutor()
        result = executor.execute("工具类APP，主要功能是个人记账和预算管理")

        errors = validate_report_schema(result)
        assert len(errors) == 0, f"Report schema validation failed: {errors}"

    def test_ecommerce_app_report_schema(self):
        """E-commerce app analysis should produce a valid report."""
        from src.agent.executor import AgentExecutor

        executor = AgentExecutor()
        result = executor.execute("电商类APP，主要功能是二手商品交易")

        errors = validate_report_schema(result)
        assert len(errors) == 0, f"Report schema validation failed: {errors}"

    def test_report_contains_actionable_recommendations(self):
        """Report should contain specific, actionable recommendations."""
        from src.agent.executor import AgentExecutor

        executor = AgentExecutor()
        result = executor.execute("社交类APP，主要功能是兴趣小组聊天")

        recommendations = result.get("recommendations", {})
        assert len(str(recommendations.get("strategy", ""))) > 20, \
            "Strategy recommendation should be detailed"
        assert len(str(recommendations.get("risks", ""))) > 20, \
            "Risk assessment should be detailed"

    def test_report_identifies_competitors(self):
        """Report should identify real competitors for the given APP type."""
        from src.agent.executor import AgentExecutor

        executor = AgentExecutor()
        result = executor.execute("社交类APP，主要功能是兴趣小组聊天")

        competitors = result.get("competitor_analysis", {}).get("top_players", [])
        assert isinstance(competitors, list), "top_players should be a list"
        assert len(competitors) >= 2, "Should identify at least 2 competitors"


class TestPipelineWithMockedLLM:
    """Pipeline tests with mocked LLM for fast feedback."""

    def test_analyzer_returns_result(self, sample_user_input, mock_raw_data):
        """IndustryAnalyzer should return a result dict."""
        from src.analyzer import IndustryAnalyzer
        from unittest.mock import patch, MagicMock

        analyzer = IndustryAnalyzer()
        with patch.object(analyzer.agent_executor, 'execute', return_value=mock_raw_data):
            result = analyzer.analyze(sample_user_input)
        assert isinstance(result, dict)

    def test_analyzer_handles_error(self, sample_user_input):
        """IndustryAnalyzer should handle errors gracefully."""
        from src.analyzer import IndustryAnalyzer
        from unittest.mock import patch

        analyzer = IndustryAnalyzer()
        with patch.object(analyzer.agent_executor, 'execute', side_effect=Exception("Test error")):
            result = analyzer.analyze(sample_user_input)
        assert "error" in result
