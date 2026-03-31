"""Config 验证测试 - 验证配置加载和验证逻辑。

测试内容：
- Config 正常加载
- 缺少必需配置时的行为
"""
import pytest
import os
from unittest.mock import patch


class TestConfigValidation:
    """Test Config loading and validation."""

    def test_config_loads_successfully(self):
        """Config should load without errors when env vars are set."""
        # This test verifies the config module can be imported
        from config import Config
        assert Config is not None

    def test_config_raises_on_missing_openai_key(self):
        """Config.validate should raise ValueError when OPENAI_API_KEY is missing."""
        from config import Config
        # Mock the class attribute directly to avoid module reload issues
        original_key = Config.OPENAI_API_KEY
        try:
            Config.OPENAI_API_KEY = None
            with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                Config.validate()
        finally:
            Config.OPENAI_API_KEY = original_key
