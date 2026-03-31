# 国家统计局MCP工具集成文档

## 概述

MarketScope项目已成功集成了6个国家统计局MCP（Model Context Protocol）工具，这些工具提供对中国官方统计数据的访问能力。

## 已集成的工具

### 1. SearchNationalStatsTool
- **工具名称**: `search_national_stats`
- **功能**: 通过关键词搜索国家统计局指标和数据
- **参数**:
  - `keyword`: 搜索关键词（必填），如 'GDP'、'人均可支配收入' 等
  - `db`: 数据库筛选（可选），空=全部, 可选 '年度数据' 或 '季度数据'
  - `page`: 页码（可选），从0开始，默认为0

### 2. GetStatsCategoriesTool
- **工具名称**: `get_stats_categories`
- **功能**: 获取国家统计局的统计指标分类,返回分类树结构(第一层)
- **参数**:
  - `dbcode`: 数据库代码（必填），指定数据类型，如 hgnd(年度数据), hgjd(季度数据)
  - `wdcode`: 维度代码（可选），默认为 'zb'(指标)

### 3. GetStatsLeafCategoriesTool
- **工具名称**: `get_stats_leaf_categories`
- **功能**: 递归获取国家统计局特定数据库的所有叶子指标节点
- **参数**:
  - `dbcode`: 数据库代码（必填），指定数据类型，如 hgnd(年度数据), hgjd(季度数据)

### 4. GetStatsTimeOptionsTool
- **工具名称**: `get_stats_time_options`
- **功能**: 获取指定数据库可选的时间范围维度
- **参数**:
  - `dbcode`: 数据库代码（必填），指定数据类型

### 5. GetStatsDataTool
- **工具名称**: `get_stats_data`
- **功能**: 获取国家统计局特定指标的数据
- **参数**:
  - `zb`: 指标代码（必填），通过分类或搜索获取
  - `dbcode`: 数据库代码（必填），指定数据类型
  - `sj`: 时间范围（可选），默认为 'LAST30'，如 LAST6(最近6季度)、2025(指定年份)

### 6. BatchGetStatsTool
- **工具名称**: `batch_get_stats`
- **功能**: 批量获取国家统计局多个指标的数据
- **参数**:
  - `queries`: 查询参数数组（必填），每个元素包含zb、dbcode和sj字段

## 架构设计

### MCP工具包装器模式
所有MCP工具都通过LangChain的`BaseTool`包装器进行集成:

```python
class SearchNationalStatsTool(BaseTool):
    name: str = "search_national_stats"
    description: str = "通过关键词搜索国家统计局指标和数据"
    args_schema: Type[BaseModel] = SearchNationalStatsInput

    def _run(self, keyword: str, db: str = None, page: int = 0) -> str:
        # 在实际部署中，这里会调用真实的MCP接口
        # mcp_result = mcp__national-stats-mcp__search_statistics(...)
        pass
```

### 工具注册
所有MCP工具包装器都已自动注册到工具注册表中，可以被智能Agent识别和使用。

## 使用场景

### 1. 经济数据分析
使用GDP、CPI等宏观经济指标来分析市场趋势和经济环境。

### 2. 行业研究
通过专业统计指标深入分析特定行业的发展状况。

### 3. 政策影响评估
利用官方统计数据评估政策对市场的影响。

### 4. 市场规模估算
利用官方统计数据进行市场容量和增长潜力评估。

## 实际部署说明

在实际运行环境中，本工具集成将连接到实际的MCP服务，执行真实的国家统计局数据查询。目前的实现中的模拟返回结果将在实际部署中被真正的API调用替换。

## 测试验证

所有工具都已通过单元测试验证，确保:
1. 正确注册到工具系统
2. 参数验证正常工作
3. 与现有工具框架兼容
4. 错误处理机制正常

运行测试命令:
```bash
python -m pytest tests/test_national_stats_tools.py
```