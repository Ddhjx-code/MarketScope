from typing import Dict, Any
from src.agent.executor import AgentExecutor
from src.agent.pipeline import AnalysisPipeline
from src.search_service import SearchService, get_search_service


class IndustryAnalyzer:
    """行业分析器主类"""

    def __init__(self):
        """初始化分析器"""
        self.search_service = get_search_service()
        self.pipeline = AnalysisPipeline()

    def analyze(self, user_input: str) -> Dict[str, Any]:
        """
        执行行业分析

        Args:
            user_input: 用户输入的APP类型和功能描述

        Returns:
            分析结果字典
        """
        try:
            analysis_result = self.pipeline.run(user_input)
            return analysis_result
        except Exception as e:
            return {"error": str(e)}