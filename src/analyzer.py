from typing import Dict, Any
from src.agent.executor import AgentExecutor
from src.search_service import SearchService


class IndustryAnalyzer:
    """行业分析器主类"""

    def __init__(self):
        """初始化分析器"""
        self.search_service = SearchService()
        self.agent_executor = AgentExecutor()

    def analyze(self, user_input: str) -> Dict[str, Any]:
        """
        执行行业分析
        
        Args:
            user_input: 用户输入的APP类型和功能描述
            
        Returns:
            分析结果字典
        """
        # 使用Agent执行分析任务
        analysis_result = self.agent_executor.execute(user_input)
        
        return analysis_result