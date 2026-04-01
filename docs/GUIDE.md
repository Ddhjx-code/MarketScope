# MarketScope 使用指南

## 快速开始

### 1. 安装

```bash
pip install -r requirements.txt
```

### 2. 配置

```bash
cp .env.example .env
```

编辑 `.env` 文件，填写必要的 API Key：

```env
# OpenAI 兼容 API（必填）
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://your-api-endpoint/v1
DEFAULT_MODEL=qwen3-coder-plus

# Tavily 搜索（可选）
TAVILY_API_KEY=your_tavily_key_here
```

### 3. 运行

```bash
python main.py
```

`main.py` 默认会对"社交类APP，主要功能是兴趣小组聊天"进行分析。如需自定义输入，修改 `main.py` 中的 `user_input` 变量即可。

## 架构

### 三阶段流水线

```
用户输入 → [Research Agent] → 原始数据 → [Analysis Agent] → 结构化分析 → [Report Agent] → JSON 报告
```

1. **Research Stage**：调用 4 个核心搜索工具（市场规模、竞品、趋势、用户需求）收集数据
2. **Analysis Stage**：将原始数据整理为结构化多维度分析
3. **Report Stage**：格式化为标准 JSON 报告

### 搜索服务

- **多 Provider 支持**：TavilySearchProvider + 可扩展其他搜索引擎
- **API Key 轮询**：自动轮换多个 API Key，失败 Key 自动跳过
- **缓存机制**：500 条容量，TTL 过期淘汰
- **重试机制**：临时错误自动重试

### 工具列表

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

## 国家统计局数据工具

已集成 6 个国家统计局 MCP 工具，提供对中国官方统计数据的访问能力：

- **search_national_stats**：关键词搜索指标和数据
- **get_stats_categories**：获取统计指标分类树
- **get_stats_leaf_categories**：获取所有叶子指标节点
- **get_stats_time_options**：获取可选时间范围
- **get_stats_data**：获取特定指标数据
- **batch_get_stats**：批量获取多个指标

使用场景：经济数据分析、行业研究、政策影响评估、市场规模估算。

## 测试

项目采用 TDD 开发方式。

```bash
# 运行所有非 slow 测试（约 45 秒）
pytest tests/ -v -m "not slow"

# 运行完整测试套件（包括 LLM 调用，约 7-8 分钟）
pytest tests/ -v

# 查看覆盖率
pytest tests/ -v -m "not slow" --cov=src --cov-report=term-missing
```

## 注意事项

- 本项目暂不支持 Docker 部署，需在本地或服务器上直接运行
- 分析结果仅供参考，不构成投资或商业决策依据
- 国家统计局工具需要网络连接才能查询实时数据
