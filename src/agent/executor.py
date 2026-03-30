from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.tools import BaseTool
from langgraph.prebuilt import create_react_agent
from .tools.registry import ToolRegistry
from config import Config


class AgentExecutor:
    """Agent执行器"""

    def __init__(self):
        """初始化Agent执行器"""
        self.llm = ChatOpenAI(
            model=Config.DEFAULT_MODEL,
            temperature=Config.TEMPERATURE,
            api_key=Config.OPENAI_API_KEY,
            base_url=Config.OPENAI_BASE_URL  # 使用配置的base_url
        )

        # 注册所有工具
        self.tool_registry = ToolRegistry()
        self.tools = self.tool_registry.get_all_tools()

        # 创建代理
        self.executor = create_react_agent(self.llm, self.tools)

    def execute(self, user_input: str) -> Dict[str, Any]:
        """
        执行分析任务

        Args:
            user_input: 用户输入

        Returns:
            分析结果
        """
        try:
            # 执行代理
            result = self.executor.invoke(
                {
                    "messages": [
                        ("user", f"请对以下APP进行详细行业分析：{user_input}")
                    ]
                }
            )
            return result
        except Exception as e:
            print(f"执行分析任务时出错: {e}")
            return {"error": str(e)}

