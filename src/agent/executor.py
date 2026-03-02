from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.tools import BaseTool
from langchain_core.agents import AgentExecutor as LangChainAgentExecutor
from langchain import hub
from langchain.agents import create_openai_functions_agent
from .tools.registry import ToolRegistry
from config import Config


class AgentExecutor:
    """Agent执行器"""

    def __init__(self):
        """初始化Agent执行器"""
        self.llm = ChatOpenAI(
            model=Config.DEFAULT_MODEL,
            temperature=Config.TEMPERATURE,
            api_key=Config.OPENAI_API_KEY
        )
        
        # 注册所有工具
        self.tool_registry = ToolRegistry()
        self.tools = self.tool_registry.get_all_tools()
        
        # 创建代理
        self.agent = self._create_agent()
        self.executor = LangChainAgentExecutor.from_agent_and_tools(
            agent=self.agent,
            tools=self.tools,
            verbose=True
        )

    def _create_agent(self):
        """创建代理"""
        # 获取默认的OpenAI函数代理提示
        prompt = hub.pull("hwchase17/openai-functions-agent")
        return create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )

    def execute(self, user_input: str) -> Dict[str, Any]:
        """
        执行分析任务
        
        Args:
            user_input: 用户输入
            
        Returns:
            分析结果
        """
        try:
            result = self.executor.invoke({
                "input": f"请对以下APP进行详细行业分析：{user_input}"
            })
            return result
        except Exception as e:
            print(f"执行分析任务时出错: {e}")
            return {"error": str(e)}