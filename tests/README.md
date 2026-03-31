# MarketScope 测试指南

## TDD 工作流

本项目遵循 **TDD（测试驱动开发）** 原则：

1. **RED** - 先写一个失败的测试，描述期望行为
2. **GREEN** - 写最少的实现代码让测试通过
3. **REFACTOR** - 重构代码，保持测试通过

### 新功能的 TDD 流程

```bash
# 1. 写测试（会失败）
pytest tests/test_new_feature.py -v

# 2. 写实现（会通过）
pytest tests/test_new_feature.py -v

# 3. 重构（保持通过）
pytest tests/test_new_feature.py -v
```

## 测试分类

| 类型 | 文件 | 用途 | 标记 |
|------|------|------|------|
| Unit | `test_tool_registry.py`, `test_search_provider.py`, `test_config.py` | 测试单个函数/类 | 无 |
| Integration | `test_search_service.py`, `test_tool_contracts.py` | 测试组件交互 | 无 |
| E2E | `test_e2e_pipeline.py` | 测试完整流水线 | 部分 `@pytest.mark.slow` |
| Prompt Quality | `test_prompt_quality.py` | 测试提示词质量 | `@pytest.mark.slow` |

## 运行命令

```bash
# 运行所有快速测试（推荐，CI 使用此命令）
pytest tests/ -v -m "not slow"

# 运行所有测试（包括 LLM 调用，需要 API key）
pytest tests/ -v

# 运行特定测试文件
pytest tests/test_search_service.py -v

# 运行特定测试类
pytest tests/test_search_service.py::TestSearchServiceCache -v

# 查看覆盖率
pytest tests/ -v -m "not slow" --cov=src --cov-report=term-missing

# 只运行失败的测试
pytest tests/ --lf

# 运行最慢的 10 个测试
pytest tests/ -v --durations=10
```

## 编写新测试

### 单元测试模板

```python
def test_function_does_what_expected(self):
    """描述期望的行为。"""
    # Arrange
    service = SomeService()

    # Act
    result = service.do_something("input")

    # Assert
    assert result == expected_value
```

### 使用 Mock

```python
from unittest.mock import patch, MagicMock

def test_with_mock_provider(self):
    """测试使用 mock provider 的服务。"""
    from src.search_service import SearchService, SearchResponse

    service = SearchService(tavily_keys=None)
    # 手动操作内部方法或使用 mock
    with patch.object(service, '_get_cached', return_value=None):
        result = service.search("test")
```

### 使用 Fixtures

所有共享 fixture 在 `conftest.py` 中定义：
- `sample_user_input` - 标准测试输入
- `mock_search_results` - 固定搜索结果
- `mock_raw_data` - Research Agent 输出
- `mock_structured_analysis` - Analysis Agent 输出
- `mock_final_report` - Report Agent 输出
- `tool_registry` - ToolRegistry 实例
- `mock_llm` / `mock_executor` - Mock 对象

## 覆盖率目标

- **最低覆盖率**: 80%
- **核心模块**: 90%+（search_service, analyzer, registry）
- 配置在 `pyproject.toml` 中：`fail_under = 80`
