import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """系统配置类"""
    
    # API 配置
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    
    # Agent 配置
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4-turbo-preview")
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))
    
    # 搜索配置
    MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "5"))
    SEARCH_TIMEOUT = int(os.getenv("SEARCH_TIMEOUT", "10"))
    
    # 系统配置
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # 验证必需的API密钥
    @classmethod
    def validate(cls):
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY 环境变量未设置")
        if not cls.TAVILY_API_KEY:
            raise ValueError("TAVILY_API_KEY 环境变量未设置")