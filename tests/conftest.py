"""共享测试 fixture - 为所有测试提供样本数据和 mock 对象。

提供的 fixture：
- sample_user_input: 标准测试输入
- mock_search_results: 固定搜索结果
- mock_raw_data: Research Agent 输出
- mock_structured_analysis: Analysis Agent 输出
- mock_final_report: Report Agent 输出
- tool_registry/search_service: 实例 fixture
- mock_llm/mock_executor: Mock 对象
"""
import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def sample_user_input():
    """Standard test input for industry analysis."""
    return "社交类APP，主要功能是兴趣小组聊天"


@pytest.fixture
def sample_tool_input():
    """Standard tool input for search tools."""
    return {"query": "中国社交类APP市场规模"}


@pytest.fixture
def mock_search_results():
    """Fixed search results for testing."""
    return {
        "market_size": "中国社交类APP市场规模约500亿元，年增长率15%...",
        "competitors": "主要竞争者：微信、QQ、Soul、陌陌...",
        "trends": "社交行业趋势：AI驱动内容推荐、垂直社交崛起...",
        "user_demand": "用户需求痛点：隐私保护、兴趣匹配、高质量社交..."
    }


@pytest.fixture
def mock_raw_data(mock_search_results):
    """Research Agent output: raw collected data."""
    return {
        "market_size": [{"title": "市场规模报告", "content": mock_search_results["market_size"]}],
        "competitors": [{"title": "竞品分析", "content": mock_search_results["competitors"]}],
        "trends": [{"title": "行业趋势", "content": mock_search_results["trends"]}],
        "user_demand": [{"title": "用户需求", "content": mock_search_results["user_demand"]}]
    }


@pytest.fixture
def mock_structured_analysis():
    """Analysis Agent output: structured multi-dimensional analysis."""
    return {
        "market_analysis": {
            "size": "约500亿元",
            "growth_rate": "年增长率15%",
            "user_base": "超过8亿用户"
        },
        "competitor_analysis": {
            "top_players": ["微信", "QQ", "Soul", "陌陌"],
            "feature_comparison": "各平台功能差异化明显...",
            "market_share": "微信占据主导地位..."
        },
        "trend_analysis": {
            "technology_trends": "AI驱动内容推荐",
            "user_behavior": "垂直社交崛起",
            "policy_impact": "数据安全法规趋严"
        },
        "opportunity_assessment": {
            "entry_opportunities": "垂直领域兴趣社交",
            "differentiation_points": "AI匹配算法",
            "barriers": "用户获取成本高"
        }
    }


@pytest.fixture
def mock_final_report():
    """Report Agent output: final structured report."""
    return {
        "app_type": "社交类APP，主要功能是兴趣小组聊天",
        "market_analysis": {
            "size": "约500亿元",
            "growth_rate": "年增长率15%",
            "user_base": "超过8亿用户"
        },
        "competitor_analysis": {
            "top_players": ["微信", "QQ", "Soul", "陌陌"],
            "feature_comparison": "各平台功能差异化明显...",
            "market_share": "微信占据主导地位..."
        },
        "trend_analysis": {
            "technology_trends": "AI驱动内容推荐",
            "user_behavior": "垂直社交崛起",
            "policy_impact": "数据安全法规趋严"
        },
        "opportunity_assessment": {
            "entry_opportunities": "垂直领域兴趣社交",
            "differentiation_points": "AI匹配算法",
            "barriers": "用户获取成本高"
        },
        "recommendations": {
            "feasibility": "中等偏上，垂直领域有机会",
            "strategy": "聚焦兴趣匹配，差异化竞争",
            "risks": "用户获取成本高，头部平台竞争激烈"
        }
    }


@pytest.fixture
def tool_registry():
    """Create a ToolRegistry instance."""
    from src.agent.tools.registry import ToolRegistry
    return ToolRegistry()


@pytest.fixture
def search_service():
    """Create a SearchService instance."""
    from src.search_service import get_search_service
    return get_search_service()


@pytest.fixture
def mock_llm():
    """Mock LLM for testing without real API calls."""
    mock = MagicMock()
    mock.invoke.return_value = MagicMock(content="分析结果")
    return mock


@pytest.fixture
def mock_executor():
    """Mock AgentExecutor for pipeline testing."""
    mock = MagicMock()
    mock.execute.return_value = {"result": "mocked"}
    return mock
