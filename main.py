from src.analyzer import IndustryAnalyzer
from config import Config

def main():
    """主入口函数"""
    # 验证配置
    Config.validate()
    
    # 创建分析器实例
    analyzer = IndustryAnalyzer()
    
    # 示例使用
    user_input = "社交类APP，主要功能是兴趣小组聊天"
    result = analyzer.analyze(user_input)
    
    print("分析结果:")
    print(result)

if __name__ == "__main__":
    main()