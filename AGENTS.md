# MarketScope - 行业分析AI应用

## 项目概述

MarketScope 是一个基于多 Agent 协作的行业分析AI应用。用户输入APP类型和功能描述，系统自动调用搜索工具收集市场数据，经过三阶段流水线处理，输出结构化行业分析报告。

## 核心功能

- 根据用户描述自动分析相关行业
- 获取实时市场数据和竞争情况
- 生成专业的行业分析报告（JSON格式）
- 提供市场进入的可行性评估和建议

## 技术架构

### 三阶段流水线

```
用户输入 → [Research Agent] → 原始数据 → [Analysis Agent] → 结构化分析 → [Report Agent] → JSON 报告
```

1. **Research Stage**：调用 4 个核心搜索工具收集市场规模、竞品、趋势、用户需求数据
2. **Analysis Stage**：将原始搜索数据整理为结构化多维度分析
3. **Report Stage**：将结构化分析格式化为标准 JSON 报告

### 数据工具

| 工具 | 说明 |
|------|------|
| search_market_size | 搜索行业市场规模数据 |
| search_competitors | 搜索竞争对手信息 |
| search_trends | 搜索行业趋势 |
| analyze_user_demand | 分析用户需求和痛点 |
| search_national_stats | 搜索国家统计局数据 |
| get_stats_categories | 获取统计指标分类 |
| get_stats_leaf_categories | 获取叶子指标节点 |
| get_stats_time_options | 获取可选时间范围 |
| get_stats_data | 获取特定指标数据 |
| batch_get_stats | 批量获取统计数据 |

### 搜索服务

- 多 Provider 支持（TavilySearchProvider + 可扩展）
- API Key 轮询（多 Key 自动轮换，失败 Key 自动跳过）
- 缓存机制（500 条容量，TTL 过期淘汰）
- 重试机制（临时错误自动重试）

## 项目结构

```
MarketScope/
├── main.py                 # 主入口（支持命令行参数）
├── requirements.txt        # 依赖
├── config.py              # 配置管理
├── pyproject.toml         # 项目配置（pytest + coverage）
├── .env.example           # 环境变量模板
├── LICENSE                # MIT 许可证
├── README.md              # 项目说明
├── src/
│   ├── analyzer.py        # 核心分析器（统一入口）
│   ├── search_service.py  # 搜索服务（缓存 + 多 Provider）
│   └── agent/
│       ├── executor.py    # LangGraph ReAct Agent 执行器
│       ├── pipeline.py    # 三阶段流水线编排
│       ├── prompts/       # 各 Agent 系统提示词
│       │   ├── researcher.py
│       │   ├── analyst.py
│       │   └── reporter.py
│       └── tools/
│           ├── registry.py       # 工具注册
│           ├── search_tools.py   # Tavily 搜索工具
│           └── national_stats_tools.py  # 国家统计局工具
├── tests/                 # 测试套件（73 个测试）
│   └── README.md          # TDD 工作流说明
└── docs/
    └── GUIDE.md           # 使用指南
```

## 分析报告格式

```json
{
    "app_type": "APP类型",
    "market_analysis": {
        "size": "市场规模",
        "growth_rate": "增长率",
        "user_base": "用户基数"
    },
    "competitor_analysis": {
        "top_players": ["主要竞争者列表"],
        "feature_comparison": "功能对比",
        "market_share": "市场份额"
    },
    "trend_analysis": {
        "technology_trends": "技术趋势",
        "user_behavior": "用户行为变化",
        "policy_impact": "政策影响"
    },
    "opportunity_assessment": {
        "entry_opportunities": "进入机会",
        "differentiation_points": "差异化方向",
        "barriers": "进入壁垒"
    },
    "recommendations": {
        "feasibility": "可行性评估",
        "strategy": "建议策略",
        "risks": "风险提示"
    }
}
```

## 开发规范

### TDD 工作流

1. 先写测试（RED）
2. 实现代码使测试通过（GREEN）
3. 重构优化（IMPROVE）
4. 验证覆盖率（80%+）

### 运行测试

```bash
# 快速测试（非 slow，约 45 秒）
pytest tests/ -v -m "not slow"

# 完整测试（包括 LLM 调用，约 7-8 分钟）
pytest tests/ -v

# 查看覆盖率
pytest tests/ -v -m "not slow" --cov=src --cov-report=term-missing
```

### 代码审查

所有代码变更后应进行审查，确保：
- 代码可读性良好，命名清晰
- 函数简洁（<50 行）
- 文件专注（<800 行）
- 无深层嵌套（>4 层）
- 错误处理完善
- 无硬编码值

## 技术栈

- **Python 3.11+**：主要开发语言
- **LangGraph**：ReAct Agent 框架
- **LangChain**：LLM 集成
- **Tavily**：搜索引擎
- **国家统计局 MCP**：官方统计数据
- **pytest**：测试框架
- **pyproject.toml**：项目配置
