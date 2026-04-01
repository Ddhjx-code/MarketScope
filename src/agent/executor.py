from typing import Dict, Any, List, Optional
import json
import re
from langchain_openai import ChatOpenAI
from langchain_core.tools import BaseTool
from langgraph.prebuilt import create_react_agent
from .tools.registry import ToolRegistry
from config import Config


class AgentExecutor:
    """Agent执行器"""

    def __init__(
        self,
        system_prompt: Optional[str] = None,
        tools: Optional[List[BaseTool]] = None,
    ):
        """初始化Agent执行器

        Args:
            system_prompt: 自定义系统提示词，不传则使用默认prompt
            tools: 自定义工具列表，不传则使用注册表中的所有工具
        """
        self.llm = ChatOpenAI(
            model=Config.DEFAULT_MODEL,
            temperature=Config.TEMPERATURE,
            api_key=Config.OPENAI_API_KEY,
            base_url=Config.OPENAI_BASE_URL
        )

        self._system_prompt = system_prompt

        if tools is not None:
            self.tools = tools
        else:
            self.tool_registry = ToolRegistry()
            self.tools = self.tool_registry.get_all_tools()

        self.executor = create_react_agent(self.llm, self.tools)

    def execute(self, user_input: str) -> Dict[str, Any]:
        """
        执行分析任务

        Args:
            user_input: 用户输入

        Returns:
            分析结果
        """
        messages = []
        if self._system_prompt:
            messages.append(("system", self._system_prompt))
        messages.append(("user", f"请对以下APP进行详细行业分析：{user_input}"))

        try:
            result = self.executor.invoke({"messages": messages})
            return self._parse_response(result)
        except Exception as e:
            print(f"执行分析任务时出错: {e}")
            return {"error": str(e)}

    def _parse_response(self, raw_result: Dict[str, Any]) -> Dict[str, Any]:
        """解析 LangGraph 响应，提取结构化数据。

        LangGraph 返回 {'messages': [...]}，最后一个 AIMessage 的 content
        可能是 JSON 字符串或 markdown 文本。
        """
        msgs = raw_result.get("messages", [])
        if not msgs:
            return {"error": "No response from agent"}

        # 获取最后一个 AI message
        last_msg = msgs[-1]
        content = getattr(last_msg, "content", str(last_msg))

        if not content:
            return {"error": "Empty response from agent"}

        # 尝试从内容中提取 JSON
        parsed = self._extract_json(content)
        if parsed is not None:
            return parsed

        # 无法解析为 JSON，返回文本包装
        return {"content": content}

    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """从文本中提取 JSON 对象。

        支持以下格式：
        - 纯 JSON: {"key": "value"}
        - Markdown code block: ```json\n{...}\n```
        - Markdown code block: ```\n{...}\n```
        - Nested JSON within content strings
        """
        # 尝试直接解析
        try:
            result = json.loads(text)
            if isinstance(result, dict):
                # If it's a simple {"content": "..."} wrapper, try to extract
                # JSON from within the content string
                if set(result.keys()) == {"content"} and isinstance(result["content"], str):
                    inner = self._extract_json_from_content(result["content"])
                    if inner is not None:
                        return inner
                return result
        except json.JSONDecodeError:
            pass

        # 尝试从 markdown code block 中提取
        json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', text, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group(1))
                if isinstance(result, dict):
                    return result
            except json.JSONDecodeError:
                pass

        # 尝试找到第一个 { 到最后一个 } 之间的内容
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            try:
                result = json.loads(text[start:end + 1])
                if isinstance(result, dict):
                    return result
            except json.JSONDecodeError:
                pass

        return None

    def _extract_json_from_content(self, content: str) -> Optional[Dict[str, Any]]:
        """从内容字符串中提取 JSON 对象。

        尝试在 markdown 文本中找到符合报告结构的 JSON。
        """
        # Look for JSON-like structures in the content
        # Try to find objects with expected report keys
        report_keys = {"market_analysis", "competitor_analysis", "recommendations"}
        research_keys = {"market_size", "competitors", "trends", "user_demand"}

        # Try to find JSON objects by scanning for { and } pairs
        depth = 0
        start_idx = None
        for i, ch in enumerate(content):
            if ch == '{':
                if depth == 0:
                    start_idx = i
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0 and start_idx is not None:
                    candidate = content[start_idx:i + 1]
                    try:
                        result = json.loads(candidate)
                        if isinstance(result, dict):
                            keys = set(result.keys())
                            if keys & report_keys or keys & research_keys:
                                return result
                    except json.JSONDecodeError:
                        pass
                    start_idx = None

        return None

