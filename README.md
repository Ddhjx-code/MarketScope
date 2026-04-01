# MarketScope

> AI 驱动的行业分析工具，通过多 Agent 协作自动完成指定 APP 类型的市场研究、竞争分析和战略建议。

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-73%20passing-brightgreen.svg)](https://github.com/Ddhjx-code/MarketScope)
[![Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen.svg)](https://github.com/Ddhjx-code/MarketScope)

## 功能特性

| 模块 | 功能 | 说明 |
|------|------|------|
| AI 分析 | 三阶段流水线 | Research（数据收集）→ Analysis（结构化）→ Report（格式化输出） |
| 搜索 | Tavily 搜索引擎 | 实时搜索市场规模、竞品、趋势、用户需求 |
| 数据 | 国家统计局接口 | 10 种官方统计工具，覆盖宏观经济指标查询 |
| 工具 | 10 种可用工具 | 市场搜索、竞品分析、趋势搜索、用户需求、国家统计数据 |
| 缓存 | 智能缓存系统 | 500 条容量，TTL 过期，自动淘汰 |
| 容错 | API Key 轮询 | 多 Key 自动轮换，失败 Key 自动跳过 |

### 技术栈

| 类型 | 支持 |
|------|------|
| AI 模型 | OpenAI 兼容 API（qwen3-coder-plus 等），通过 LangChain + LangGraph 调用 |
| 搜索 | Tavily Search API |
| 官方数据 | 国家统计局 MCP 接口 |
| 框架 | LangGraph（ReAct Agent）、LangChain |

## 快速开始

### 环境要求

- Python 3.11+
- OpenAI 兼容 API Key
- Tavily API Key（可选）

### 安装

```bash
git clone https://github.com/Ddhjx-code/MarketScope.git
cd MarketScope
pip install -r requirements.txt
```

### 配置

```bash
cp .env.example .env
# 编辑 .env 填写 API Key
```

### 使用

```python
from src.analyzer import IndustryAnalyzer

analyzer = IndustryAnalyzer()
result = analyzer.analyze("社交类APP，主要功能是兴趣小组聊天")
print(result)
```

或命令行运行：

```bash
python main.py
```

## 架构

### 三阶段流水线

```
用户输入 → [Research Agent] → 原始数据 → [Analysis Agent] → 结构化分析 → [Report Agent] → JSON 报告
              ↓                      ↓                        ↓
         调用搜索工具           整理数据维度              格式化输出
```

1. **Research Stage**：使用 4 个核心搜索工具收集市场规模、竞品、趋势、用户需求
2. **Analysis Stage**：将原始搜索数据整理为结构化多维度分析
3. **Report Stage**：将结构化分析格式化为标准 JSON 报告

### 项目结构

```
MarketScope/
├── src/
│   ├── agent/
│   │   ├── executor.py          # LangGraph ReAct Agent 执行器
│   │   ├── pipeline.py          # 三阶段流水线编排
│   │   ├── prompts/             # 各 Agent 系统提示词
│   │   │   ├── researcher.py
│   │   │   ├── analyst.py
│   │   │   └── reporter.py
│   │   └── tools/
│   │       ├── registry.py      # 工具注册表
│   │       ├── search_tools.py  # Tavily 搜索工具
│   │       └── national_stats_tools.py  # 国家统计局工具
│   ├── analyzer.py              # 统一分析入口
│   └── search_service.py        # 搜索服务（缓存 + 多 Provider）
├── tests/                       # 测试套件（73 个测试）
├── config.py                    # 配置管理
├── main.py                      # 入口文件
└── pyproject.toml               # 项目配置
```

## 测试

项目采用 TDD 开发方式，所有功能先写测试再实现。

```bash
# 运行所有非 slow 测试（约 45 秒）
pytest tests/ -v -m "not slow"

# 运行完整测试套件（包括 LLM 调用，约 7-8 分钟）
pytest tests/ -v

# 查看覆盖率
pytest tests/ -v -m "not slow" --cov=src --cov-report=term-missing
```

**当前状态：73/73 全部通过，覆盖率 ~90%**

## 可用工具

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

## License

[MIT License](LICENSE)

## 免责声明

本项目仅供学习和研究使用，不构成任何商业建议。分析结果仅供参考，不构成投资或商业决策依据。
