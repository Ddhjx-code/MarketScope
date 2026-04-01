# -*- coding: utf-8 -*-
"""三阶段分析流水线 - Research → Analysis → Report。

编排三个独立的 Agent 对话，每个 Agent 有专注的上下文：
1. Research Agent: 调用搜索工具收集原始数据
2. Analysis Agent: 将原始数据结构化为多维度分析
3. Report Agent: 将分析结果格式化为 JSON 报告
"""
import logging
from typing import Dict, Any, Optional

from .executor import AgentExecutor
from .prompts.researcher import SYSTEM_PROMPT as RESEARCHER_PROMPT
from .prompts.analyst import SYSTEM_PROMPT as ANALYST_PROMPT
from .prompts.reporter import SYSTEM_PROMPT as REPORTER_PROMPT

logger = logging.getLogger(__name__)


def run_research_stage(
    executor: AgentExecutor,
    user_input: str,
) -> Dict[str, Any]:
    """执行 Research 阶段：收集原始市场数据。

    Args:
        executor: Agent 执行器（已配置 Research system prompt 和搜索工具）
        user_input: 用户输入的 APP 类型描述

    Returns:
        raw_data 字典，包含各维度的搜索结果
    """
    logger.info(f"[Pipeline] Research stage: {user_input}")
    result = executor.execute(user_input)
    if isinstance(result, dict) and "error" in result:
        logger.error(f"[Pipeline] Research stage failed: {result['error']}")
    return result


def run_analysis_stage(
    executor: AgentExecutor,
    user_input: str,
    raw_data: Dict[str, Any],
) -> Dict[str, Any]:
    """执行 Analysis 阶段：将原始数据结构化为多维度分析。

    Args:
        executor: Agent 执行器（已配置 Analysis system prompt，无工具）
        user_input: 用户输入的 APP 类型描述
        raw_data: Research 阶段的输出

    Returns:
        structured_analysis 字典
    """
    logger.info(f"[Pipeline] Analysis stage: processing {len(raw_data)} dimensions")
    analysis_input = f"用户输入: {user_input}\n\n研究数据:\n{raw_data}"
    result = executor.execute(analysis_input)
    if isinstance(result, dict) and "error" in result:
        logger.error(f"[Pipeline] Analysis stage failed: {result['error']}")
    return result


def run_report_stage(
    executor: AgentExecutor,
    user_input: str,
    structured_analysis: Dict[str, Any],
) -> Dict[str, Any]:
    """执行 Report 阶段：将分析结果格式化为 JSON 报告。

    Args:
        executor: Agent 执行器（已配置 Report system prompt，无工具）
        user_input: 用户输入的 APP 类型描述
        structured_analysis: Analysis 阶段的输出

    Returns:
        final_report 字典，匹配预定义的 JSON schema
    """
    logger.info(f"[Pipeline] Report stage: formatting final report")
    report_input = f"APP类型: {user_input}\n\n分析数据:\n{structured_analysis}"
    result = executor.execute(report_input)
    if isinstance(result, dict) and "error" in result:
        logger.error(f"[Pipeline] Report stage failed: {result['error']}")
    return result


class AnalysisPipeline:
    """三阶段分析流水线编排器。

    按顺序执行 Research → Analysis → Report 三个阶段，
    每个阶段使用独立的 AgentExecutor 和专用的 system prompt。
    """

    def __init__(self):
        pass

    def _create_research_executor(self) -> AgentExecutor:
        """创建 Research Agent 执行器。"""
        from .tools.registry import ToolRegistry
        registry = ToolRegistry()
        return AgentExecutor(
            system_prompt=RESEARCHER_PROMPT,
            tools=registry.get_all_tools(),
        )

    def _create_analysis_executor(self) -> AgentExecutor:
        """创建 Analysis Agent 执行器（无工具）。"""
        return AgentExecutor(
            system_prompt=ANALYST_PROMPT,
            tools=[],
        )

    def _create_report_executor(self) -> AgentExecutor:
        """创建 Report Agent 执行器（无工具）。"""
        return AgentExecutor(
            system_prompt=REPORTER_PROMPT,
            tools=[],
        )

    def run(self, user_input: str) -> Dict[str, Any]:
        """执行完整的三阶段分析流水线。

        Args:
            user_input: 用户输入的 APP 类型和功能描述

        Returns:
            最终报告字典，或包含 "error" 键的错误响应
        """
        logger.info(f"[Pipeline] Starting analysis for: {user_input}")

        # Stage 1: Research
        research_executor = self._create_research_executor()
        raw_data = run_research_stage(research_executor, user_input)
        if isinstance(raw_data, dict) and "error" in raw_data:
            return raw_data

        # Stage 2: Analysis
        analysis_executor = self._create_analysis_executor()
        structured_analysis = run_analysis_stage(analysis_executor, user_input, raw_data)
        if isinstance(structured_analysis, dict) and "error" in structured_analysis:
            return structured_analysis

        # Stage 3: Report
        report_executor = self._create_report_executor()
        final_report = run_report_stage(report_executor, user_input, structured_analysis)

        logger.info(f"[Pipeline] Analysis complete for: {user_input}")
        return final_report